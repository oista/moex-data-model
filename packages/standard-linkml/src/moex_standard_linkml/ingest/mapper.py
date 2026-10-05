"""Map ER-dictionary tables to a DAMS ModelPackage dict."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from moex_standard_linkml.ingest import ids
from moex_standard_linkml.ingest.profile import IngestProfile
from moex_standard_linkml.ingest.technical_asset import (
    CARRIER_COLLECTIONS,
    ensure_container,
    heuristic_namespace,
    infer_parent_names,
    resolve_kind,
)
from moex_standard_linkml.ingest.workbook import WorkbookTables

_CARD_RE = re.compile(
    r"^\s*(\d+)\s*(?:\.\.\s*(\d+|\*|n|N))?\s*$"
)
_LOCAL_KEY_RE = re.compile(r"^[a-z0-9_.-]+$")
_HTTP_URI_RE = re.compile(r"^https?://", re.IGNORECASE)
_ROOT_KEY = "root"


@dataclass
class MapperError:
    sheet: str
    row: int
    message: str

    def __str__(self) -> str:
        return f"{self.sheet} row {self.row}: {self.message}"


@dataclass
class MapResult:
    package: dict[str, Any]
    errors: list[MapperError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


class MappingFailed(ValueError):
    def __init__(self, errors: list[MapperError]) -> None:
        self.errors = errors
        super().__init__("; ".join(str(e) for e in errors))


def map_er_dictionary(
    tables: WorkbookTables,
    profile: IngestProfile,
    *,
    raise_on_error: bool = True,
) -> MapResult:
    errors: list[MapperError] = []
    warnings = list(tables.warnings)
    prefix = profile.id_prefix
    slug = profile.solution_slug
    defaults = profile.defaults

    context_curie = ids.context_id(prefix, slug)
    conceptual: list[dict[str, Any]] = []
    concept_by_name: dict[str, str] = {}  # Conceptual.name → CURIE
    has_conceptual_sheet = (
        tables.conceptual is not None and len(tables.conceptual.rows) > 0
    )
    # Sheet configured and present (even empty) disables stub mode when
    # the file existed — plan: "if Conceptual sheet exists, no stubs".
    # Empty SheetTable from missing optional file still has rows=[] but
    # source was not found. Detect via: conceptual is not None AND
    # either has rows OR the sheet was found (we can't distinguish easily).
    # Plan: "если листа Conceptual нет" — meaning file/sheet absent.
    # When optional sheet not found, workbook returns empty SheetTable with
    # a warning. When found with rows, has data. When found empty, also
    # "sheet exists".
    # Use: stub mode iff conceptual sheet had no rows AND no Conceptual.csv
    # was loaded. Warning "Optional sheet 'Conceptual' not found" means absent.
    conceptual_sheet_absent = (
        tables.conceptual is None
        or (
            len(tables.conceptual.rows) == 0
            and any(
                "Conceptual" in w and "not found" in w for w in tables.warnings
            )
        )
    )
    # Also: if profile has no conceptual sheet config
    if profile.sheets.conceptual is None:
        conceptual_sheet_absent = True

    if tables.conceptual is not None and not conceptual_sheet_absent:
        for i, row in enumerate(tables.conceptual.rows, start=2):
            name = _req_str(row.get("name"), "conceptual", i, "name", errors)
            if name is None:
                continue
            if name in concept_by_name:
                errors.append(
                    MapperError(
                        "conceptual", i, f"duplicate concept name '{name}'"
                    )
                )
                continue
            title = _opt_str(row.get("title")) or name
            description = _opt_str(row.get("description")) or title
            concept_curie = ids.concept_id(prefix, name)
            concept_by_name[name] = concept_curie
            conceptual.append(
                {
                    "element_id": concept_curie,
                    "name": name,
                    "title": title,
                    "description": description,
                    "lifecycle_status": defaults.lifecycle_status,
                    "entity_type": defaults.entity_type,
                    "data_class": defaults.data_class,
                    "business_importance": defaults.business_importance,
                }
            )

    use_compat_stub = conceptual_sheet_absent

    logical: list[dict[str, Any]] = []
    entity_by_name: dict[str, str] = {}  # entity name → logical CURIE

    for i, row in enumerate(tables.entities.rows, start=2):
        name = _req_str(row.get("name"), "entities", i, "name", errors)
        if name is None:
            continue
        title = _opt_str(row.get("title")) or name
        description = _opt_str(row.get("description")) or title
        logical_curie = ids.logical_entity_id(prefix, slug, name)
        if name in entity_by_name:
            errors.append(
                MapperError("entities", i, f"duplicate entity name '{name}'")
            )
            continue
        entity_by_name[name] = logical_curie

        refs = _parse_pipe_list(_opt_str(row.get("conceptual_ref")))
        conceptual_entity_refs: list[str] = []

        if use_compat_stub and not refs:
            concept_curie = ids.concept_id(prefix, name)
            if name not in concept_by_name:
                concept_by_name[name] = concept_curie
                conceptual.append(
                    {
                        "element_id": concept_curie,
                        "name": name,
                        "title": title,
                        "description": description,
                        "lifecycle_status": defaults.lifecycle_status,
                        "entity_type": defaults.entity_type,
                        "data_class": defaults.data_class,
                        "business_importance": defaults.business_importance,
                    }
                )
            conceptual_entity_refs = [concept_by_name[name]]
        else:
            for ref_name in refs:
                curie = concept_by_name.get(ref_name)
                if curie is None:
                    # Compat: allow conceptual_ref to name a concept that
                    # will be stub-created only when sheet absent.
                    if use_compat_stub:
                        curie = ids.concept_id(prefix, ref_name)
                        if ref_name not in concept_by_name:
                            concept_by_name[ref_name] = curie
                            conceptual.append(
                                {
                                    "element_id": curie,
                                    "name": ref_name,
                                    "title": ref_name,
                                    "description": ref_name,
                                    "lifecycle_status": defaults.lifecycle_status,
                                    "entity_type": defaults.entity_type,
                                    "data_class": defaults.data_class,
                                    "business_importance": defaults.business_importance,
                                }
                            )
                        conceptual_entity_refs.append(curie)
                    else:
                        errors.append(
                            MapperError(
                                "entities",
                                i,
                                f"unknown conceptual_ref '{ref_name}' "
                                f"(not in Conceptual sheet)",
                            )
                        )
                else:
                    conceptual_entity_refs.append(curie)

        logical.append(
            {
                "element_id": logical_curie,
                "name": name,
                "title": title,
                "description": description,
                "lifecycle_status": defaults.lifecycle_status,
                "context_ref": context_curie,
                "conceptual_entity_refs": conceptual_entity_refs,
                "solution_ref": profile.solution_ref,
                "solution_data_role": defaults.solution_data_role,
                "entity_type": defaults.entity_type,
                "data_class": defaults.data_class,
                "business_importance": defaults.business_importance,
                "attributes": [],
                "key_attribute_refs": [],
            }
        )

    logical_by_curie = {e["element_id"]: e for e in logical}
    attr_by_dotted: dict[str, str] = {}  # Entity.attr → CURIE

    for i, row in enumerate(tables.attributes.rows, start=2):
        entity_name = _req_str(row.get("entity"), "attributes", i, "entity", errors)
        attr_name = _req_str(row.get("name"), "attributes", i, "name", errors)
        if entity_name is None or attr_name is None:
            continue
        owner = entity_by_name.get(entity_name)
        if owner is None:
            errors.append(
                MapperError(
                    "attributes",
                    i,
                    f"unknown entity '{entity_name}' (not in Entities sheet)",
                )
            )
            continue
        title = _opt_str(row.get("title")) or attr_name
        description = _opt_str(row.get("description")) or title
        is_pk = _as_bool(row.get("pk"))
        required = _as_bool(row.get("required"))
        if is_pk:
            required = True
        type_leaf = profile.map_type(_opt_str(row.get("type")), is_pk=is_pk)
        attr_curie = ids.logical_attr_id(prefix, slug, entity_name, attr_name)
        attr = {
            "element_id": attr_curie,
            "name": attr_name,
            "title": title,
            "description": description,
            "lifecycle_status": defaults.lifecycle_status,
            "owner_entity_ref": owner,
            "data_type_ref": f"dams:datatype/{type_leaf}",
            "required": required,
            "multivalued": False,
        }
        owner_entity = logical_by_curie[owner]
        owner_entity["attributes"].append(attr)
        if is_pk:
            owner_entity["key_attribute_refs"].append(attr_curie)
        attr_by_dotted[f"{entity_name}.{attr_name}"] = attr_curie

    relationships: list[dict[str, Any]] = []
    if tables.relationships is not None:
        for i, row in enumerate(tables.relationships.rows, start=2):
            rel_name = _req_str(row.get("name"), "relationships", i, "name", errors)
            source_name = _req_str(
                row.get("source"), "relationships", i, "source", errors
            )
            target_name = _req_str(
                row.get("target"), "relationships", i, "target", errors
            )
            if rel_name is None or source_name is None or target_name is None:
                continue
            source_curie = entity_by_name.get(source_name)
            target_curie = entity_by_name.get(target_name)
            if source_curie is None:
                errors.append(
                    MapperError(
                        "relationships",
                        i,
                        f"unknown source entity '{source_name}'",
                    )
                )
                continue
            if target_curie is None:
                errors.append(
                    MapperError(
                        "relationships",
                        i,
                        f"unknown target entity '{target_name}'",
                    )
                )
                continue
            source_min, source_max = _parse_cardinality(
                row.get("source_card"), "relationships", i, "source_card", errors
            )
            target_min, target_max = _parse_cardinality(
                row.get("target_card"), "relationships", i, "target_card", errors
            )
            rel: dict[str, Any] = {
                "element_id": ids.relationship_id(prefix, slug, rel_name),
                "name": rel_name,
                "title": rel_name,
                "description": f"Relationship {rel_name}",
                "lifecycle_status": defaults.lifecycle_status,
                "source_entity_ref": source_curie,
                "target_entity_ref": target_curie,
            }
            source_role = _opt_str(row.get("source_role"))
            target_role = _opt_str(row.get("target_role"))
            if source_role:
                rel["source_role"] = source_role
            if target_role:
                rel["target_role"] = target_role
            if source_min is not None:
                rel["source_min_cardinality"] = source_min
            if source_max is not None:
                rel["source_max_cardinality"] = source_max
            if target_min is not None:
                rel["target_min_cardinality"] = target_min
            if target_max is not None:
                rel["target_max_cardinality"] = target_max
            if row.get("identifying") is not None:
                rel["identifying"] = _as_bool(row.get("identifying"))
            relationships.append(rel)

    # TechnicalAsset collections (Variant B). Rows use asset_kind (or legacy object_kind).
    collections: dict[str, list[dict[str, Any]]] = {
        "data_carriers": [],
        "access_points": [],
        "data_containers": [],
        "execution_assets": [],
    }
    phys_obj_by_name: dict[str, dict[str, Any]] = {}
    containers_by_name: dict[str, dict[str, Any]] = {}
    field_by_dotted: dict[str, str] = {}

    if tables.data_carriers is not None:
        for i, row in enumerate(tables.data_carriers.rows, start=2):
            name = _req_str(
                row.get("name"), "data_carriers", i, "name", errors
            )
            description = _req_str(
                row.get("description"), "data_carriers", i, "description", errors
            )
            kind_raw = _opt_str(row.get("asset_kind")) or _opt_str(
                row.get("object_kind")
            )
            if kind_raw is None:
                errors.append(
                    MapperError(
                        "data_carriers",
                        i,
                        "missing required field 'asset_kind' (or legacy object_kind)",
                    )
                )
            resolved = resolve_kind(kind_raw) if kind_raw else None
            if kind_raw and resolved is None:
                errors.append(
                    MapperError(
                        "data_carriers",
                        i,
                        f"unknown asset_kind/object_kind '{kind_raw}'",
                    )
                )
            qualified_name = _req_str(
                row.get("qualified_name"),
                "data_carriers",
                i,
                "qualified_name",
                errors,
            )
            system_ref = _req_str(
                row.get("system_ref"), "data_carriers", i, "system_ref", errors
            )
            technology = _req_str(
                row.get("technology"), "data_carriers", i, "technology", errors
            )
            # direction required for carriers/access_points; optional for containers
            direction = _opt_str(row.get("direction"))
            native_schema_ref = _opt_str(row.get("native_schema_ref")) or _opt_str(
                row.get("structure_ref")
            )
            if (
                name is None
                or description is None
                or resolved is None
                or qualified_name is None
                or system_ref is None
                or technology is None
            ):
                continue
            coll, asset_kind = resolved
            if coll in ("data_carriers", "access_points") and not direction:
                errors.append(
                    MapperError(
                        "data_carriers",
                        i,
                        "missing required field 'direction'",
                    )
                )
                continue
            if name in phys_obj_by_name:
                errors.append(
                    MapperError(
                        "data_carriers",
                        i,
                        f"duplicate technical asset name '{name}'",
                    )
                )
                continue
            title = _opt_str(row.get("title")) or name
            obj_curie = ids.physical_object_id(prefix, slug, name)
            ns = (
                _opt_str(row.get("asset_namespace"))
                or heuristic_namespace(technology, system_ref)
            )
            obj: dict[str, Any] = {
                "element_id": obj_curie,
                "name": name,
                "title": title,
                "description": description,
                "lifecycle_status": defaults.lifecycle_status,
                "solution_ref": profile.solution_ref,
                "system_ref": system_ref,
                "asset_kind": asset_kind,
                "asset_namespace": ns,
                "qualified_name": qualified_name,
                "technology": technology,
            }
            if direction and coll not in ("data_containers", "execution_assets"):
                obj["direction"] = direction

            # ADR-033: create parent DataContainer when schema/DB present in source
            db_name, schema_name = infer_parent_names(
                qualified_name=qualified_name,
                native_schema_ref=native_schema_ref,
                schema=_opt_str(row.get("db_schema")) or _opt_str(row.get("schema")),
                database=_opt_str(row.get("database")),
            )
            parent_ref: str | None = None
            if coll in CARRIER_COLLECTIONS and (db_name or schema_name):
                db_obj = None
                if db_name:
                    db_obj = ensure_container(
                        collections["data_containers"],
                        containers_by_name,
                        name=db_name,
                        asset_kind="database",
                        prefix=prefix,
                        slug=slug,
                        technology=technology,
                        system_ref=system_ref,
                        solution_ref=profile.solution_ref,
                        lifecycle_status=defaults.lifecycle_status,
                        description=f"Database {db_name}",
                    )
                if schema_name:
                    sch_obj = ensure_container(
                        collections["data_containers"],
                        containers_by_name,
                        name=schema_name,
                        asset_kind="schema",
                        prefix=prefix,
                        slug=slug,
                        technology=technology,
                        system_ref=system_ref,
                        solution_ref=profile.solution_ref,
                        lifecycle_status=defaults.lifecycle_status,
                        parent_ref=db_obj["element_id"] if db_obj else None,
                        description=f"Schema {schema_name}",
                    )
                    parent_ref = str(sch_obj["element_id"])
                elif db_obj is not None:
                    parent_ref = str(db_obj["element_id"])
            if parent_ref:
                obj["parent_ref"] = parent_ref
            elif _opt_str(row.get("parent_ref")):
                obj["parent_ref"] = _opt_str(row.get("parent_ref"))

            if coll in CARRIER_COLLECTIONS:
                # URI schema refs become DataStructure.source_artifact_ref when
                # fields are ingested; otherwise leave as provisional structure_ref.
                if native_schema_ref:
                    if _HTTP_URI_RE.match(native_schema_ref):
                        obj["_source_artifact_ref"] = native_schema_ref
                    else:
                        obj["structure_ref"] = native_schema_ref

            collections[coll].append(obj)
            phys_obj_by_name[name] = obj

    # StructureFields sheet (legacy workbook name also accepted) → DataStructure
    fields_sheet = getattr(tables, "structure_fields", None)
    fields_by_carrier: dict[str, list[dict[str, Any]]] = {}
    if fields_sheet is not None:
        sheet_label = "structure_fields"
        for i, row in enumerate(fields_sheet.rows, start=2):
            object_name = _req_str(
                row.get("object"), sheet_label, i, "object", errors
            )
            field_name = _req_str(
                row.get("name"), sheet_label, i, "name", errors
            )
            if object_name is None or field_name is None:
                continue
            owner = phys_obj_by_name.get(object_name)
            if owner is None:
                errors.append(
                    MapperError(
                        sheet_label,
                        i,
                        f"unknown data carrier '{object_name}'",
                    )
                )
                continue
            carrier_ids = {c["element_id"] for c in collections["data_carriers"]}
            if owner["element_id"] not in carrier_ids:
                errors.append(
                    MapperError(
                        sheet_label,
                        i,
                        f"'{object_name}' is not a DataCarrier",
                    )
                )
                continue
            description = (
                _opt_str(row.get("description"))
                or _opt_str(row.get("native_name"))
                or field_name
            )
            native_name = _opt_str(row.get("native_name")) or field_name
            native_type = _req_str(
                row.get("native_type"), sheet_label, i, "native_type", errors
            )
            if native_type is None:
                continue
            field_row: dict[str, Any] = {
                "name": field_name,
                "description": description,
                "native_name": native_name,
                "native_type": native_type,
                "required": _as_bool(row.get("required")),
            }
            schema_path = _opt_str(row.get("schema_path"))
            if schema_path:
                field_row["schema_path"] = schema_path
            fields_by_carrier.setdefault(object_name, []).append(field_row)

    data_structures: list[dict[str, Any]] = []
    for object_name, field_rows in fields_by_carrier.items():
        owner = phys_obj_by_name[object_name]
        structure_curie = ids.data_structure_id(prefix, slug, object_name)
        nodes, leaf_keys = _build_relational_nodes(field_rows)
        structure: dict[str, Any] = {
            "element_id": structure_curie,
            "name": object_name,
            "title": owner.get("title") or object_name,
            "description": (
                f"Structure for {object_name}"
            ),
            "lifecycle_status": defaults.lifecycle_status,
            "schema_format": "relational",
            "structure_version": "1.0.0",
            "root_local_key": _ROOT_KEY,
            "nodes": nodes,
        }
        src_art = owner.pop("_source_artifact_ref", None)
        if src_art:
            structure["source_artifact_ref"] = src_art
        data_structures.append(structure)
        owner["structure_ref"] = structure_curie
        for field_name, local_key in leaf_keys.items():
            field_by_dotted[f"{object_name}.{field_name}"] = (
                f"{structure_curie}#{local_key}"
            )

    # Drop provisional private keys on carriers without fields
    for obj in phys_obj_by_name.values():
        obj.pop("_source_artifact_ref", None)

    mappings: list[dict[str, Any]] = []
    if tables.mappings is not None:
        for i, row in enumerate(tables.mappings.rows, start=2):
            map_name = _req_str(row.get("name"), "mappings", i, "name", errors)
            source_raw = _req_str(row.get("source"), "mappings", i, "source", errors)
            target_raw = _req_str(row.get("target"), "mappings", i, "target", errors)
            if map_name is None or source_raw is None or target_raw is None:
                continue
            source_refs = _resolve_mapping_refs(
                source_raw,
                "mappings",
                i,
                "source",
                errors,
                entity_by_name=entity_by_name,
                attr_by_dotted=attr_by_dotted,
                phys_obj_by_name=phys_obj_by_name,
                field_by_dotted=field_by_dotted,
            )
            target_refs = _resolve_mapping_refs(
                target_raw,
                "mappings",
                i,
                "target",
                errors,
                entity_by_name=entity_by_name,
                attr_by_dotted=attr_by_dotted,
                phys_obj_by_name=phys_obj_by_name,
                field_by_dotted=field_by_dotted,
            )
            if not source_refs or not target_refs:
                continue
            mapping_type = _opt_str(row.get("mapping_type")) or "field_mapping"
            mapping_cardinality = (
                _opt_str(row.get("mapping_cardinality")) or "one_to_one"
            )
            mappings.append(
                {
                    "element_id": ids.mapping_id(prefix, slug, map_name),
                    "name": map_name,
                    "description": f"Mapping {map_name}",
                    "lifecycle_status": defaults.lifecycle_status,
                    "source_refs": source_refs,
                    "target_refs": target_refs,
                    "mapping_type": mapping_type,
                    "mapping_cardinality": mapping_cardinality,
                }
            )

    package: dict[str, Any] = {
        "element_id": ids.package_id(prefix, slug, profile.model_version),
        "name": profile.package_name,
        "title": profile.package_title,
        "description": profile.package_description,
        "lifecycle_status": defaults.lifecycle_status,
        "api_version": profile.api_version,
        "model_version": profile.model_version,
        "solution_ref": profile.solution_ref,
        "conceptual_entities": conceptual,
        "domain_contexts": [
            {
                "element_id": context_curie,
                "name": defaults.context_name,
                "title": defaults.context_title,
                "description": defaults.context_description,
                "lifecycle_status": defaults.lifecycle_status,
                "domain_ref": defaults.domain_ref,
                "solution_ref": profile.solution_ref,
                "namespace": defaults.namespace,
            }
        ],
        "logical_entities": logical,
        "relationships": relationships,
    }
    for key, items in collections.items():
        if items:
            package[key] = items
    if data_structures:
        package["data_structures"] = data_structures
    if mappings:
        package["mappings"] = mappings

    result = MapResult(package=package, errors=errors, warnings=warnings)
    if raise_on_error and errors:
        raise MappingFailed(errors)
    return result


def _slug_token(text: str) -> str:
    """Lowercase slug; alphabet [a-z0-9_.-]; other chars → _."""
    s = str(text or "").strip().lower()
    out: list[str] = []
    for ch in s:
        if ("a" <= ch <= "z") or ("0" <= ch <= "9") or ch in "_.-":
            out.append(ch)
        else:
            out.append("_")
    token = "".join(out)
    token = re.sub(r"_+", "_", token).strip("_.-")
    return token or "_"


def _path_segments(field: dict[str, Any]) -> list[str]:
    raw = field.get("schema_path")
    if raw is None or str(raw).strip() == "":
        raw = field.get("native_name") or field.get("name") or "field"
    # Prefer dotted paths; also split on /
    text = str(raw).strip().lstrip("/")
    parts = [p for p in re.split(r"[./]+", text) if p != ""]
    if not parts:
        parts = ["field"]
    return [_slug_token(p) for p in parts]


def _allocate_key(preferred: str, used: set[str]) -> str:
    key = preferred if _LOCAL_KEY_RE.match(preferred) else _slug_token(preferred)
    if key not in used:
        used.add(key)
        return key
    n = 2
    while f"{key}-{n}" in used:
        n += 1
    alt = f"{key}-{n}"
    used.add(alt)
    return alt


def _build_relational_nodes(
    fields: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """Build flat SchemaNode list; return (nodes, field_name→local_key)."""
    used: set[str] = {_ROOT_KEY}
    nodes: dict[str, dict[str, Any]] = {
        _ROOT_KEY: {
            "local_key": _ROOT_KEY,
            "node_kind": "object",
            "children": [],
        }
    }
    leaf_keys: dict[str, str] = {}

    for field in fields:
        segments = _path_segments(field)
        preferred_leaf = ".".join(segments)
        parent_key = _ROOT_KEY
        for i in range(len(segments) - 1):
            obj_key = ".".join(segments[: i + 1])
            if obj_key not in nodes:
                used.add(obj_key)
                nodes[obj_key] = {
                    "local_key": obj_key,
                    "node_kind": "object",
                    "children": [],
                }
                parent = nodes[parent_key]
                children = list(parent.get("children") or [])
                if obj_key not in children:
                    children.append(obj_key)
                    parent["children"] = children
            parent_key = obj_key

        leaf_key = _allocate_key(preferred_leaf, used)
        node: dict[str, Any] = {
            "local_key": leaf_key,
            "node_kind": "scalar",
            "native_name": field.get("native_name") or field.get("name"),
            "native_type": field.get("native_type"),
            "required": bool(field.get("required")),
        }
        if field.get("description"):
            node["description"] = field["description"]
        nodes[leaf_key] = node
        parent = nodes[parent_key]
        children = list(parent.get("children") or [])
        if leaf_key not in children:
            children.append(leaf_key)
            parent["children"] = children
        field_name = str(field.get("name") or leaf_key)
        leaf_keys[field_name] = leaf_key

    ordered = [nodes[_ROOT_KEY]] + [
        nodes[k] for k in sorted(nodes.keys()) if k != _ROOT_KEY
    ]
    return ordered, leaf_keys


def _resolve_mapping_refs(
    raw: str,
    sheet: str,
    row: int,
    field: str,
    errors: list[MapperError],
    *,
    entity_by_name: dict[str, str],
    attr_by_dotted: dict[str, str],
    phys_obj_by_name: dict[str, dict[str, Any]],
    field_by_dotted: dict[str, str],
) -> list[str]:
    refs: list[str] = []
    for token in _parse_pipe_list(raw):
        curie = _resolve_one_ref(
            token,
            entity_by_name=entity_by_name,
            attr_by_dotted=attr_by_dotted,
            phys_obj_by_name=phys_obj_by_name,
            field_by_dotted=field_by_dotted,
        )
        if curie is None:
            errors.append(
                MapperError(
                    sheet,
                    row,
                    f"unresolved {field} ref '{token}' "
                    f"(expected Entity, Entity.attr, Object, or Object.field)",
                )
            )
            continue
        refs.append(curie)
    return refs


def _resolve_one_ref(
    token: str,
    *,
    entity_by_name: dict[str, str],
    attr_by_dotted: dict[str, str],
    phys_obj_by_name: dict[str, dict[str, Any]],
    field_by_dotted: dict[str, str],
) -> str | None:
    if "." in token:
        if token in attr_by_dotted:
            return attr_by_dotted[token]
        if token in field_by_dotted:
            return field_by_dotted[token]
        return None
    if token in entity_by_name:
        return entity_by_name[token]
    obj = phys_obj_by_name.get(token)
    if obj is not None:
        return str(obj["element_id"])
    return None


def _parse_pipe_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split("|") if part.strip()]


def _req_str(
    value: Any,
    sheet: str,
    row: int,
    field: str,
    errors: list[MapperError],
) -> str | None:
    text = _opt_str(value)
    if text is None:
        errors.append(MapperError(sheet, row, f"missing required field '{field}'"))
        return None
    return text


def _opt_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _as_bool(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "y", "x", "pk"}


def _parse_cardinality(
    value: Any,
    sheet: str,
    row: int,
    field: str,
    errors: list[MapperError],
) -> tuple[int | None, int | None]:
    text = _opt_str(value)
    if text is None:
        return None, None
    match = _CARD_RE.match(text)
    if not match:
        errors.append(
            MapperError(
                sheet,
                row,
                f"invalid cardinality '{text}' in '{field}' "
                f"(expected N or N..M / N..*)",
            )
        )
        return None, None
    minimum = int(match.group(1))
    upper = match.group(2)
    if upper is None:
        return minimum, minimum
    if upper in {"*", "n", "N"}:
        return minimum, None
    return minimum, int(upper)
