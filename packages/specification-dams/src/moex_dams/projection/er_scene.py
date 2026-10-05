"""Structured ER scene projection for the Publication Viewer custom renderer."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml

from moex_dams.projection.dbml import _ident, effective_attr_type
from moex_dams.projection.er_common import (
    MANY,
    attr_keys_for_entity,
    cardinality_kind,
    fk_roles_for_entity,
    is_structure_node_ref,
    relation_term_label,
    unique_table_name,
)
from moex_dams.rules.data_structure import (
    scalar_nodes_for_carrier,
    structures_by_id,
)

Profile = Literal["logical", "physical", "conceptual"]

GENERATOR = "moex-dams-er-scene/0.1"


@dataclass(frozen=True)
class ErSceneManifest:
    content_digest: str
    profile: str
    source_path: str
    generator: str = GENERATOR

    def to_dict(self) -> dict[str, str]:
        return {
            "content_digest": self.content_digest,
            "profile": self.profile,
            "source_path": self.source_path,
            "generator": self.generator,
        }


def _column(
    *,
    name: str,
    type_name: str,
    element_id: str,
    keys: list[str],
    comment: str | None,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "name": name,
        "type": type_name,
        "element_id": element_id,
        "keys": keys,
    }
    if comment:
        out["comment"] = comment
    return out


def project_model_package_to_er_scene(
    data: dict[str, Any],
    *,
    profile: Profile,
) -> dict[str, Any]:
    """Project a ModelPackage into a structured ER scene (nodes + edges)."""
    if profile not in ("logical", "physical", "conceptual"):
        raise ValueError(f"unsupported profile: {profile}")

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    entity_table: dict[str, str] = {}
    col_index: dict[str, tuple[str, str]] = {}
    table_names: set[str] = set()
    fk_field_ids: set[str] = set()

    relationships = [
        r for r in (data.get("relationships") or []) if isinstance(r, dict)
    ]
    mappings = [m for m in (data.get("mappings") or []) if isinstance(m, dict)]

    if profile == "physical":
        for mapping in mappings:
            if mapping.get("mapping_type") != "field_mapping":
                continue
            sources = [str(x) for x in (mapping.get("source_refs") or [])]
            targets = [str(x) for x in (mapping.get("target_refs") or [])]
            for src in sources:
                for tgt in targets:
                    if is_structure_node_ref(src) and is_structure_node_ref(tgt):
                        fk_field_ids.add(src)

    if profile == "conceptual":
        terms_by_id = {
            str(t.get("element_id")): t
            for t in (data.get("relation_terms") or [])
            if isinstance(t, dict) and t.get("element_id")
        }
        for entity in data.get("conceptual_entities") or []:
            if not isinstance(entity, dict):
                continue
            tname = unique_table_name(
                entity.get("name"), fallback="ConceptualEntity", used=table_names
            )
            eid = str(entity.get("element_id") or "")
            if eid:
                entity_table[eid] = tname
            nodes.append(
                {
                    "name": tname,
                    "title": str(entity.get("title") or entity.get("name") or tname),
                    "element_id": eid,
                    "columns": [],
                }
            )
        for rel in relationships:
            src_id = str(rel.get("source_entity_ref") or "")
            tgt_id = str(rel.get("target_entity_ref") or "")
            if src_id not in entity_table or tgt_id not in entity_table:
                continue
            rid = str(rel.get("element_id") or "")
            edges.append(
                {
                    "id": rid or f"{entity_table[src_id]}->{entity_table[tgt_id]}",
                    "source": entity_table[src_id],
                    "target": entity_table[tgt_id],
                    "element_id": rid,
                    "label": relation_term_label(rel, terms_by_id),
                    "source_cardinality": cardinality_kind(
                        min_card=rel.get("source_min_cardinality"),
                        max_card=rel.get("source_max_cardinality", MANY),
                    ),
                    "target_cardinality": cardinality_kind(
                        min_card=rel.get("target_min_cardinality"),
                        max_card=rel.get("target_max_cardinality", 1),
                    ),
                }
            )
        return {
            "version": 1,
            "profile": profile,
            "generator": GENERATOR,
            "package_id": str(data.get("element_id") or data.get("name") or ""),
            "nodes": nodes,
            "edges": edges,
        }

    if profile == "logical":
        for entity in data.get("logical_entities") or []:
            if not isinstance(entity, dict):
                continue
            tname = unique_table_name(
                entity.get("name"), fallback="LogicalEntity", used=table_names
            )
            eid = str(entity.get("element_id") or "")
            if eid:
                entity_table[eid] = tname
            key_refs = attr_keys_for_entity(entity)
            fk_roles = fk_roles_for_entity(eid, relationships)
            columns: list[dict[str, Any]] = []
            for attr in entity.get("attributes") or []:
                if not isinstance(attr, dict):
                    continue
                cname = _ident(attr.get("name"), fallback="attr")
                ctype = _ident(effective_attr_type(attr), fallback="string")
                aid = str(attr.get("element_id") or "")
                pk = (
                    effective_attr_type(attr) == "identifier"
                    or (aid and aid in key_refs)
                    or bool(attr.get("business_key_kind"))
                )
                fk = str(attr.get("name") or "") in fk_roles
                if fk and effective_attr_type(attr) == "identifier" and not (
                    aid in key_refs or attr.get("business_key_kind")
                ):
                    pk = False
                keys: list[str] = []
                if pk:
                    keys.append("PK")
                if fk:
                    keys.append("FK")
                if attr.get("unique"):
                    keys.append("UQ")
                comment = attr.get("title")
                columns.append(
                    _column(
                        name=cname,
                        type_name=ctype,
                        element_id=aid,
                        keys=keys,
                        comment=str(comment) if comment else None,
                    )
                )
                if aid:
                    col_index[aid] = (tname, cname)
            nodes.append(
                {
                    "name": tname,
                    "title": str(entity.get("title") or entity.get("name") or tname),
                    "element_id": eid,
                    "columns": columns,
                }
            )
        for rel in relationships:
            src_id = str(rel.get("source_entity_ref") or "")
            tgt_id = str(rel.get("target_entity_ref") or "")
            if src_id not in entity_table or tgt_id not in entity_table:
                continue
            rid = str(rel.get("element_id") or "")
            edges.append(
                {
                    "id": rid or f"{entity_table[src_id]}->{entity_table[tgt_id]}",
                    "source": entity_table[src_id],
                    "target": entity_table[tgt_id],
                    "element_id": rid,
                    "label": str(rel.get("name") or "rel"),
                    "source_cardinality": cardinality_kind(
                        min_card=rel.get("source_min_cardinality"),
                        max_card=rel.get("source_max_cardinality", MANY),
                    ),
                    "target_cardinality": cardinality_kind(
                        min_card=rel.get("target_min_cardinality"),
                        max_card=rel.get("target_max_cardinality", 1),
                    ),
                }
            )
    else:
        by_structure = structures_by_id(data)
        for obj in data.get("data_carriers") or []:
            if not isinstance(obj, dict):
                continue
            tname = unique_table_name(
                obj.get("name"), fallback="DataCarrier", used=table_names
            )
            oid = str(obj.get("element_id") or "")
            if oid:
                entity_table[oid] = tname
            columns = []
            for node_ref, field in scalar_nodes_for_carrier(obj, by_structure):
                cname = _ident(
                    field.get("native_name") or field.get("local_key"),
                    fallback="field",
                )
                ctype = _ident(field.get("native_type"), fallback="string")
                pk = bool(field.get("is_primary_key")) or (
                    field.get("native_name") == "id"
                    or field.get("local_key") == "id"
                )
                fk = bool(node_ref in fk_field_ids)
                if fk:
                    pk = False
                keys = []
                if pk:
                    keys.append("PK")
                if fk:
                    keys.append("FK")
                if field.get("is_unique") or field.get("unique"):
                    keys.append("UQ")
                comment = field.get("title") or field.get("description")
                columns.append(
                    _column(
                        name=cname,
                        type_name=ctype,
                        element_id=node_ref,
                        keys=keys,
                        comment=str(comment) if comment else None,
                    )
                )
                col_index[node_ref] = (tname, cname)
            nodes.append(
                {
                    "name": tname,
                    "title": str(obj.get("title") or obj.get("name") or tname),
                    "element_id": oid,
                    "columns": columns,
                }
            )
        seen_edges: set[tuple[str, str, str]] = set()
        for mapping in mappings:
            mtype = mapping.get("mapping_type")
            sources = [str(x) for x in (mapping.get("source_refs") or [])]
            targets = [str(x) for x in (mapping.get("target_refs") or [])]
            mname = str(mapping.get("name") or "map")
            mid = str(mapping.get("element_id") or "")

            if mtype == "field_mapping":
                for src in sources:
                    for tgt in targets:
                        if src not in col_index or tgt not in col_index:
                            continue
                        st, _sc = col_index[src]
                        tt, _tc = col_index[tgt]
                        key = (st, tt, mname)
                        if key in seen_edges:
                            continue
                        seen_edges.add(key)
                        edges.append(
                            {
                                "id": mid or f"{st}->{tt}:{mname}",
                                "source": st,
                                "target": tt,
                                "element_id": mid,
                                "label": mname,
                                "source_cardinality": "zeroOrMore",
                                "target_cardinality": "zeroOrOne",
                            }
                        )
            elif mtype in {"object_mapping", "entity_mapping"}:
                for src in sources:
                    for tgt in targets:
                        if src not in entity_table or tgt not in entity_table:
                            continue
                        st = entity_table[src]
                        tt = entity_table[tgt]
                        key = (st, tt, mname)
                        if key in seen_edges:
                            continue
                        seen_edges.add(key)
                        edges.append(
                            {
                                "id": mid or f"{st}->{tt}:{mname}",
                                "source": st,
                                "target": tt,
                                "element_id": mid,
                                "label": mname,
                                "source_cardinality": "zeroOrMore",
                                "target_cardinality": "zeroOrOne",
                            }
                        )

    return {
        "version": 1,
        "profile": profile,
        "generator": GENERATOR,
        "package_id": str(data.get("element_id") or data.get("name") or ""),
        "nodes": nodes,
        "edges": edges,
    }


def write_er_scene_artifact(
    *,
    implementation_path: Path,
    out_path: Path,
    profile: Profile,
) -> ErSceneManifest:
    """Load ModelPackage YAML, write ``*.scene.json`` + sidecar manifest."""
    raw = yaml.safe_load(implementation_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"expected ModelPackage mapping in {implementation_path}")
    scene = project_model_package_to_er_scene(raw, profile=profile)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(scene, indent=2, ensure_ascii=False) + "\n"
    data = text.encode("utf-8")
    out_path.write_bytes(data)
    digest = "sha256:" + hashlib.sha256(data).hexdigest()
    manifest = ErSceneManifest(
        content_digest=digest,
        profile=profile,
        source_path=str(implementation_path),
    )
    manifest_path = out_path.with_name(out_path.name + ".manifest.json")
    manifest_path.write_text(
        json.dumps(manifest.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest
