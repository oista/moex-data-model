"""Compute and apply ModelPatch from projected DBML (ADR-006 policy)."""

from __future__ import annotations

import copy
import uuid
from typing import Any

from moex_drawdb.domain import (
    ModelPatch,
    PatchOp,
    PatchOpKind,
    Profile,
    ProjectedDiagram,
    ProjectedTable,
    RejectCode,
    RejectedOp,
)

_LOGICAL_TYPES = frozenset(
    {
        "identifier",
        "string",
        "integer",
        "decimal",
        "boolean",
        "date",
        "datetime",
        "uri",
        "json",
    }
)


def _new_id(prefix: str) -> str:
    return f"{prefix}/{uuid.uuid4().hex[:8]}"


def _index_by_id(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in items:
        eid = item.get("element_id")
        if eid:
            out[str(eid)] = item
    return out


def _index_by_name(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(i.get("name")): i for i in items if i.get("name")}


def compute_model_patch(
    base_package: dict[str, Any],
    diagram: ProjectedDiagram,
    *,
    profile: Profile,
) -> ModelPatch:
    """Diff projected diagram against base package; emit allowed ops + rejections."""
    ops: list[PatchOp] = []
    rejected: list[RejectedOp] = []

    if profile == "logical":
        _patch_logical(base_package, diagram, ops, rejected)
    else:
        _patch_physical(base_package, diagram, ops, rejected)

    return ModelPatch(profile=profile, ops=tuple(ops), rejected=tuple(rejected))


def _patch_logical(
    base: dict[str, Any],
    diagram: ProjectedDiagram,
    ops: list[PatchOp],
    rejected: list[RejectedOp],
) -> None:
    entities = list(base.get("logical_entities") or [])
    by_id = _index_by_id(entities)
    by_name = _index_by_name(entities)
    seen_ids: set[str] = set()
    table_to_entity_id: dict[str, str] = {}

    for table in diagram.tables:
        if table.element_id and table.element_id in by_id:
            existing = by_id[table.element_id]
            if existing.get("name") != table.name or (
                table.title and existing.get("title") != table.title
            ):
                ops.append(
                    PatchOp(
                        kind=PatchOpKind.UPDATE_ENTITY,
                        path=f"logical_entities[{table.element_id}]",
                        payload={
                            "element_id": table.element_id,
                            "name": table.name,
                            "title": table.title or existing.get("title"),
                        },
                    )
                )
            seen_ids.add(table.element_id)
            table_to_entity_id[table.name] = table.element_id
            _patch_attributes(existing, table, ops, rejected)
        elif table.element_id and table.element_id not in by_id:
            # Unknown element_id claiming identity — reject rewrite / invent
            rejected.append(
                RejectedOp(
                    code=RejectCode.ELEMENT_ID_REWRITE,
                    message=f"unknown element_id on table {table.name}",
                    path=table.name,
                )
            )
        else:
            # Match by name or add
            existing = by_name.get(table.name)
            if existing and existing.get("element_id"):
                # Diagram dropped element_id — reject rewrite
                rejected.append(
                    RejectedOp(
                        code=RejectCode.ELEMENT_ID_REWRITE,
                        message=(
                            f"table {table.name} must keep element_id="
                            f"{existing['element_id']}"
                        ),
                        path=table.name,
                    )
                )
                seen_ids.add(str(existing["element_id"]))
                table_to_entity_id[table.name] = str(existing["element_id"])
                _patch_attributes(existing, table, ops, rejected)
            else:
                eid = _new_id("dams:logical/diagram")
                payload = {
                    "element_id": eid,
                    "name": table.name,
                    "title": table.title or table.name,
                    "attributes": [
                        _attr_from_col(c, eid) for c in table.columns
                    ],
                }
                ops.append(
                    PatchOp(
                        kind=PatchOpKind.ADD_ENTITY,
                        path=f"logical_entities[{eid}]",
                        payload=payload,
                    )
                )
                table_to_entity_id[table.name] = eid

    for ent in entities:
        eid = ent.get("element_id")
        if eid and eid not in seen_ids and eid not in table_to_entity_id.values():
            # Only delete if not present under any table name still in diagram
            if not any(t.name == ent.get("name") for t in diagram.tables):
                ops.append(
                    PatchOp(
                        kind=PatchOpKind.DELETE_ENTITY,
                        path=f"logical_entities[{eid}]",
                        payload={"element_id": eid},
                    )
                )

    _patch_relationships(base, diagram, table_to_entity_id, ops, rejected)


def _attr_type_leaf(attr: dict[str, Any]) -> str:
    dtr = str(attr.get("data_type_ref") or "").strip()
    if dtr:
        return dtr.rsplit("/", 1)[-1]
    return "string"


def _attr_from_col(col: Any, owner_eid: str) -> dict[str, Any]:
    ltype = col.type_name if col.type_name in _LOGICAL_TYPES else "string"
    return {
        "element_id": col.element_id or _new_id(f"{owner_eid}"),
        "name": col.name,
        "data_type_ref": f"dams:datatype/{ltype}",
        "required": col.required,
        "multivalued": False,
    }


def _patch_attributes(
    entity: dict[str, Any],
    table: ProjectedTable,
    ops: list[PatchOp],
    rejected: list[RejectedOp],
) -> None:
    eid = str(entity["element_id"])
    attrs = list(entity.get("attributes") or [])
    by_id = _index_by_id(attrs)
    by_name = _index_by_name(attrs)
    seen: set[str] = set()

    for col in table.columns:
        if col.element_id and col.element_id in by_id:
            existing = by_id[col.element_id]
            want_type = (
                col.type_name if col.type_name in _LOGICAL_TYPES else _attr_type_leaf(existing)
            )
            if (
                existing.get("name") == col.name
                and bool(existing.get("required")) == col.required
                and _attr_type_leaf(existing) == want_type
            ):
                seen.add(col.element_id)
                continue
            # Detect rewrite: same name different element_id claimed
            ops.append(
                PatchOp(
                    kind=PatchOpKind.UPDATE_ATTRIBUTE,
                    path=f"logical_entities[{eid}].attributes[{col.element_id}]",
                    payload={
                        "owner_element_id": eid,
                        "element_id": col.element_id,
                        "name": col.name,
                        "data_type_ref": (
                            f"dams:datatype/{col.type_name}"
                            if col.type_name in _LOGICAL_TYPES
                            else existing.get("data_type_ref")
                            or f"dams:datatype/{_attr_type_leaf(existing)}"
                        ),
                        "required": col.required,
                    },
                )
            )
            seen.add(col.element_id)
        elif col.element_id and col.element_id not in by_id:
            rejected.append(
                RejectedOp(
                    code=RejectCode.ELEMENT_ID_REWRITE,
                    message=f"unknown attribute element_id {col.element_id}",
                    path=f"{table.name}.{col.name}",
                )
            )
        else:
            existing = by_name.get(col.name)
            if existing and existing.get("element_id"):
                rejected.append(
                    RejectedOp(
                        code=RejectCode.ELEMENT_ID_REWRITE,
                        message=(
                            f"column {table.name}.{col.name} must keep "
                            f"element_id={existing['element_id']}"
                        ),
                        path=f"{table.name}.{col.name}",
                    )
                )
                seen.add(str(existing["element_id"]))
            else:
                new_id = _new_id(f"{eid}")
                ops.append(
                    PatchOp(
                        kind=PatchOpKind.ADD_ATTRIBUTE,
                        path=f"logical_entities[{eid}].attributes[{new_id}]",
                        payload={
                            "owner_element_id": eid,
                            "element_id": new_id,
                            "name": col.name,
                            "data_type_ref": (
                                f"dams:datatype/{col.type_name}"
                                if col.type_name in _LOGICAL_TYPES
                                else "dams:datatype/string"
                            ),
                            "required": col.required,
                            "multivalued": False,
                        },
                    )
                )

    for attr in attrs:
        aid = attr.get("element_id")
        if aid and aid not in seen:
            if not any(c.name == attr.get("name") for c in table.columns):
                ops.append(
                    PatchOp(
                        kind=PatchOpKind.DELETE_ATTRIBUTE,
                        path=f"logical_entities[{eid}].attributes[{aid}]",
                        payload={
                            "owner_element_id": eid,
                            "element_id": aid,
                        },
                    )
                )


def _patch_relationships(
    base: dict[str, Any],
    diagram: ProjectedDiagram,
    table_to_entity_id: dict[str, str],
    ops: list[PatchOp],
    rejected: list[RejectedOp],
) -> None:
    rels = list(base.get("relationships") or [])
    by_id = _index_by_id(rels)
    seen: set[str] = set()

    for ref in diagram.refs:
        src = table_to_entity_id.get(ref.source_table)
        tgt = table_to_entity_id.get(ref.target_table)
        if not src or not tgt:
            rejected.append(
                RejectedOp(
                    code=RejectCode.MISSING_END,
                    message=f"ref {ref.name} missing entity ends",
                    path=ref.name,
                )
            )
            continue
        if ref.element_id and ref.element_id in by_id:
            existing = by_id[ref.element_id]
            if (
                existing.get("source_entity_ref") != src
                or existing.get("target_entity_ref") != tgt
                or (ref.name and existing.get("name") != ref.name)
            ):
                ops.append(
                    PatchOp(
                        kind=PatchOpKind.UPDATE_RELATIONSHIP,
                        path=f"relationships[{ref.element_id}]",
                        payload={
                            "element_id": ref.element_id,
                            "name": ref.name or existing.get("name"),
                            "source_entity_ref": src,
                            "target_entity_ref": tgt,
                        },
                    )
                )
            seen.add(ref.element_id)
        elif ref.element_id and ref.element_id not in by_id:
            rejected.append(
                RejectedOp(
                    code=RejectCode.ELEMENT_ID_REWRITE,
                    message=f"unknown relationship element_id {ref.element_id}",
                    path=ref.name,
                )
            )
        else:
            rid = _new_id("dams:rel/diagram")
            ops.append(
                PatchOp(
                    kind=PatchOpKind.ADD_RELATIONSHIP,
                    path=f"relationships[{rid}]",
                    payload={
                        "element_id": rid,
                        "name": ref.name or f"{ref.source_table}_{ref.target_table}",
                        "source_entity_ref": src,
                        "target_entity_ref": tgt,
                    },
                )
            )

    for rel in rels:
        rid = rel.get("element_id")
        if rid and rid not in seen:
            ops.append(
                PatchOp(
                    kind=PatchOpKind.DELETE_RELATIONSHIP,
                    path=f"relationships[{rid}]",
                    payload={"element_id": rid},
                )
            )


def _patch_physical(
    base: dict[str, Any],
    diagram: ProjectedDiagram,
    ops: list[PatchOp],
    rejected: list[RejectedOp],
) -> None:
    objects = list(base.get("data_carriers") or [])
    by_id = _index_by_id(objects)
    by_name = _index_by_name(objects)
    seen_ids: set[str] = set()
    table_to_obj: dict[str, str] = {}

    for table in diagram.tables:
        kind = table.asset_kind or table.object_kind or "relational_table"
        if table.element_id and table.element_id in by_id:
            existing = by_id[table.element_id]
            if existing.get("name") != table.name or (
                table.title and existing.get("title") != table.title
            ) or (kind and existing.get("asset_kind") != kind):
                ops.append(
                    PatchOp(
                        kind=PatchOpKind.UPDATE_PHYSICAL_OBJECT,
                        path=f"data_carriers[{table.element_id}]",
                        payload={
                            "element_id": table.element_id,
                            "name": table.name,
                            "asset_kind": kind,
                            "title": table.title or existing.get("title"),
                        },
                    )
                )
            seen_ids.add(table.element_id)
            table_to_obj[table.name] = table.element_id
            _patch_fields(existing, table, ops, rejected)
        elif table.element_id and table.element_id not in by_id:
            rejected.append(
                RejectedOp(
                    code=RejectCode.ELEMENT_ID_REWRITE,
                    message=f"unknown element_id on table {table.name}",
                    path=table.name,
                )
            )
        else:
            existing = by_name.get(table.name)
            if existing and existing.get("element_id"):
                rejected.append(
                    RejectedOp(
                        code=RejectCode.ELEMENT_ID_REWRITE,
                        message=(
                            f"table {table.name} must keep element_id="
                            f"{existing['element_id']}"
                        ),
                        path=table.name,
                    )
                )
                seen_ids.add(str(existing["element_id"]))
                table_to_obj[table.name] = str(existing["element_id"])
                _patch_fields(existing, table, ops, rejected)
            else:
                oid = _new_id("dams:physical/diagram")
                ops.append(
                    PatchOp(
                        kind=PatchOpKind.ADD_PHYSICAL_OBJECT,
                        path=f"data_carriers[{oid}]",
                        payload={
                            "element_id": oid,
                            "name": table.name,
                            "asset_kind": kind,
                            "title": table.title or table.name,
                            "physical_fields": [
                                {
                                    "element_id": c.element_id
                                    or _new_id(oid),
                                    "name": c.name,
                                    "native_name": c.name,
                                    "native_type": c.type_name,
                                    "required": c.required,
                                    "carrier_ref": oid,
                                }
                                for c in table.columns
                            ],
                        },
                    )
                )
                table_to_obj[table.name] = oid

    for obj in objects:
        oid = obj.get("element_id")
        if oid and oid not in seen_ids and oid not in table_to_obj.values():
            if not any(t.name == obj.get("name") for t in diagram.tables):
                ops.append(
                    PatchOp(
                        kind=PatchOpKind.DELETE_PHYSICAL_OBJECT,
                        path=f"data_carriers[{oid}]",
                        payload={"element_id": oid},
                    )
                )

    # Physical FK refs as field_mapping add/delete (both ends physical)
    _patch_physical_refs(base, diagram, table_to_obj, ops, rejected)


def _patch_fields(
    obj: dict[str, Any],
    table: ProjectedTable,
    ops: list[PatchOp],
    rejected: list[RejectedOp],
) -> None:
    oid = str(obj["element_id"])
    fields = list(obj.get("physical_fields") or [])
    by_id = _index_by_id(fields)
    by_name = _index_by_name(fields)
    seen: set[str] = set()

    for col in table.columns:
        if col.element_id and col.element_id in by_id:
            existing = by_id[col.element_id]
            if (
                (existing.get("native_name") or existing.get("name")) == col.name
                and bool(existing.get("required")) == col.required
                and existing.get("native_type") == col.type_name
            ):
                seen.add(col.element_id)
                continue
            ops.append(
                PatchOp(
                    kind=PatchOpKind.UPDATE_FIELD,
                    path=f"data_carriers[{oid}].physical_fields[{col.element_id}]",
                    payload={
                        "owner_element_id": oid,
                        "element_id": col.element_id,
                        "name": col.name,
                        "native_name": col.name,
                        "native_type": col.type_name,
                        "required": col.required,
                    },
                )
            )
            seen.add(col.element_id)
        elif col.element_id and col.element_id not in by_id:
            rejected.append(
                RejectedOp(
                    code=RejectCode.ELEMENT_ID_REWRITE,
                    message=f"unknown field element_id {col.element_id}",
                    path=f"{table.name}.{col.name}",
                )
            )
        else:
            existing = by_name.get(col.name)
            if existing and existing.get("element_id"):
                rejected.append(
                    RejectedOp(
                        code=RejectCode.ELEMENT_ID_REWRITE,
                        message=(
                            f"column {table.name}.{col.name} must keep "
                            f"element_id={existing['element_id']}"
                        ),
                        path=f"{table.name}.{col.name}",
                    )
                )
                seen.add(str(existing["element_id"]))
            else:
                fid = _new_id(oid)
                ops.append(
                    PatchOp(
                        kind=PatchOpKind.ADD_FIELD,
                        path=f"data_carriers[{oid}].physical_fields[{fid}]",
                        payload={
                            "owner_element_id": oid,
                            "element_id": fid,
                            "name": col.name,
                            "native_name": col.name,
                            "native_type": col.type_name,
                            "required": col.required,
                            "carrier_ref": oid,
                        },
                    )
                )

    for field in fields:
        fid = field.get("element_id")
        if fid and fid not in seen:
            fname = field.get("native_name") or field.get("name")
            if not any(c.name == fname for c in table.columns):
                ops.append(
                    PatchOp(
                        kind=PatchOpKind.DELETE_FIELD,
                        path=f"data_carriers[{oid}].physical_fields[{fid}]",
                        payload={"owner_element_id": oid, "element_id": fid},
                    )
                )


def _patch_physical_refs(
    base: dict[str, Any],
    diagram: ProjectedDiagram,
    table_to_obj: dict[str, str],
    ops: list[PatchOp],
    rejected: list[RejectedOp],
) -> None:
    mappings = [
        m
        for m in (base.get("mappings") or [])
        if isinstance(m, dict) and m.get("mapping_type") == "field_mapping"
    ]
    # Index fields by table.column via objects
    objects = list(base.get("data_carriers") or [])
    # After adds we don't have new fields in base; resolve columns from diagram
    col_eid: dict[tuple[str, str], str] = {}
    for table in diagram.tables:
        for col in table.columns:
            if col.element_id:
                col_eid[(table.name, col.name)] = col.element_id

    for obj in objects:
        tname = str(obj.get("name"))
        for field in obj.get("physical_fields") or []:
            fname = str(field.get("native_name") or field.get("name"))
            if field.get("element_id"):
                col_eid.setdefault((tname, fname), str(field["element_id"]))

    by_id = _index_by_id(mappings)
    seen: set[str] = set()

    for ref in diagram.refs:
        src_col = col_eid.get((ref.source_table, ref.source_column))
        tgt_col = col_eid.get((ref.target_table, ref.target_column))
        if not src_col or not tgt_col:
            rejected.append(
                RejectedOp(
                    code=RejectCode.MISSING_END,
                    message=f"physical ref {ref.name} unresolved columns",
                    path=ref.name,
                )
            )
            continue
        if ref.element_id and ref.element_id in by_id:
            seen.add(ref.element_id)
            continue
        if ref.element_id and ref.element_id not in by_id:
            rejected.append(
                RejectedOp(
                    code=RejectCode.ELEMENT_ID_REWRITE,
                    message=f"unknown mapping element_id {ref.element_id}",
                    path=ref.name,
                )
            )
            continue
        mid = _new_id("dams:map/diagram")
        ops.append(
            PatchOp(
                kind=PatchOpKind.ADD_MAPPING_REF,
                path=f"mappings[{mid}]",
                payload={
                    "element_id": mid,
                    "name": ref.name or f"{ref.source_table}_{ref.target_table}",
                    "mapping_type": "field_mapping",
                    "source_refs": [src_col],
                    "target_refs": [tgt_col],
                    "mapping_cardinality": "one_to_one",
                },
            )
        )

    # Do not auto-delete unrelated cross-layer mappings (logical→physical).
    # Only delete field_mappings that were projected as physical-physical Refs.
    for m in mappings:
        mid = m.get("element_id")
        if not mid or mid in seen:
            continue
        sources = m.get("source_refs") or []
        targets = m.get("target_refs") or []
        # Heuristic: both ends physical ids
        if sources and targets and all(
            str(x).startswith("dams:physical/") for x in list(sources) + list(targets)
        ):
            # if not in diagram refs by element_id, delete
            if not any(r.element_id == mid for r in diagram.refs):
                ops.append(
                    PatchOp(
                        kind=PatchOpKind.DELETE_MAPPING_REF,
                        path=f"mappings[{mid}]",
                        payload={"element_id": mid},
                    )
                )


def apply_model_patch(
    base_package: dict[str, Any],
    patch: ModelPatch,
) -> dict[str, Any]:
    """Apply patch ops; preserve non-projected sections."""
    out = copy.deepcopy(base_package)

    for op in patch.ops:
        kind = op.kind
        p = op.payload
        if kind is PatchOpKind.ADD_ENTITY:
            out.setdefault("logical_entities", []).append(p)
        elif kind is PatchOpKind.UPDATE_ENTITY:
            for ent in out.get("logical_entities") or []:
                if ent.get("element_id") == p["element_id"]:
                    ent["name"] = p["name"]
                    if p.get("title") is not None:
                        ent["title"] = p["title"]
        elif kind is PatchOpKind.DELETE_ENTITY:
            out["logical_entities"] = [
                e
                for e in (out.get("logical_entities") or [])
                if e.get("element_id") != p["element_id"]
            ]
            # drop relationships pointing at deleted entity
            out["relationships"] = [
                r
                for r in (out.get("relationships") or [])
                if r.get("source_entity_ref") != p["element_id"]
                and r.get("target_entity_ref") != p["element_id"]
            ]
        elif kind is PatchOpKind.ADD_ATTRIBUTE:
            for ent in out.get("logical_entities") or []:
                if ent.get("element_id") == p["owner_element_id"]:
                    attr = {
                        k: v
                        for k, v in p.items()
                        if k != "owner_element_id"
                    }
                    ent.setdefault("attributes", []).append(attr)
        elif kind is PatchOpKind.UPDATE_ATTRIBUTE:
            for ent in out.get("logical_entities") or []:
                if ent.get("element_id") != p["owner_element_id"]:
                    continue
                for attr in ent.get("attributes") or []:
                    if attr.get("element_id") == p["element_id"]:
                        attr["name"] = p["name"]
                        if p.get("data_type_ref"):
                            attr["data_type_ref"] = p["data_type_ref"]
                        attr["required"] = p["required"]
                        attr.pop("logical_type", None)
        elif kind is PatchOpKind.DELETE_ATTRIBUTE:
            for ent in out.get("logical_entities") or []:
                if ent.get("element_id") != p["owner_element_id"]:
                    continue
                ent["attributes"] = [
                    a
                    for a in (ent.get("attributes") or [])
                    if a.get("element_id") != p["element_id"]
                ]
        elif kind is PatchOpKind.ADD_RELATIONSHIP:
            out.setdefault("relationships", []).append(p)
        elif kind is PatchOpKind.UPDATE_RELATIONSHIP:
            for rel in out.get("relationships") or []:
                if rel.get("element_id") == p["element_id"]:
                    rel.update(
                        {
                            k: v
                            for k, v in p.items()
                            if k != "element_id"
                        }
                    )
                    rel["element_id"] = p["element_id"]
        elif kind is PatchOpKind.DELETE_RELATIONSHIP:
            out["relationships"] = [
                r
                for r in (out.get("relationships") or [])
                if r.get("element_id") != p["element_id"]
            ]
        elif kind is PatchOpKind.ADD_PHYSICAL_OBJECT:
            out.setdefault("data_carriers", []).append(p)
        elif kind is PatchOpKind.UPDATE_PHYSICAL_OBJECT:
            for obj in out.get("data_carriers") or []:
                if obj.get("element_id") == p["element_id"]:
                    obj["name"] = p["name"]
                    if p.get("asset_kind"):
                        obj["asset_kind"] = p["asset_kind"]
                    elif p.get("object_kind"):
                        obj["asset_kind"] = p["object_kind"]
                    if p.get("title") is not None:
                        obj["title"] = p["title"]
        elif kind is PatchOpKind.DELETE_PHYSICAL_OBJECT:
            out["data_carriers"] = [
                o
                for o in (out.get("data_carriers") or [])
                if o.get("element_id") != p["element_id"]
            ]
        elif kind is PatchOpKind.ADD_FIELD:
            for obj in out.get("data_carriers") or []:
                if obj.get("element_id") == p["owner_element_id"]:
                    field = {
                        k: v
                        for k, v in p.items()
                        if k != "owner_element_id"
                    }
                    field.setdefault("carrier_ref", p["owner_element_id"])
                    obj.setdefault("physical_fields", []).append(field)
        elif kind is PatchOpKind.UPDATE_FIELD:
            for obj in out.get("data_carriers") or []:
                if obj.get("element_id") != p["owner_element_id"]:
                    continue
                for field in obj.get("physical_fields") or []:
                    if field.get("element_id") == p["element_id"]:
                        field["name"] = p["name"]
                        field["native_name"] = p["native_name"]
                        field["native_type"] = p["native_type"]
                        field["required"] = p["required"]
        elif kind is PatchOpKind.DELETE_FIELD:
            for obj in out.get("data_carriers") or []:
                if obj.get("element_id") != p["owner_element_id"]:
                    continue
                obj["physical_fields"] = [
                    f
                    for f in (obj.get("physical_fields") or [])
                    if f.get("element_id") != p["element_id"]
                ]
        elif kind is PatchOpKind.ADD_MAPPING_REF:
            out.setdefault("mappings", []).append(p)
        elif kind is PatchOpKind.DELETE_MAPPING_REF:
            out["mappings"] = [
                m
                for m in (out.get("mappings") or [])
                if m.get("element_id") != p["element_id"]
            ]

    return out
