"""Controlled YAML mutations for workspace drafts (ruamel)."""

from __future__ import annotations

from io import StringIO
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq


class MutationConflict(Exception):
    """Duplicate element_id or missing owner."""


class MutationError(Exception):
    """Invalid mutation payload or document shape."""


def _yaml() -> YAML:
    y = YAML()
    y.preserve_quotes = True
    y.default_flow_style = False
    y.width = 120
    return y


def load_yaml(text: str) -> CommentedMap:
    data = _yaml().load(StringIO(text))
    if not isinstance(data, CommentedMap):
        raise MutationError("root YAML must be a mapping")
    return data


def dump_yaml(data: CommentedMap) -> str:
    buf = StringIO()
    _yaml().dump(data, buf)
    return buf.getvalue()


def _ensure_seq(data: CommentedMap, key: str) -> CommentedSeq:
    if key not in data or data[key] is None:
        data[key] = CommentedSeq()
    seq = data[key]
    if not isinstance(seq, CommentedSeq) and not isinstance(seq, list):
        raise MutationError(f"{key} must be a sequence")
    if not isinstance(seq, CommentedSeq):
        data[key] = CommentedSeq(seq)
        seq = data[key]
    return seq


def _collect_ids(data: CommentedMap) -> set[str]:
    ids: set[str] = set()
    root = data.get("element_id")
    if root:
        ids.add(str(root))
    for key in (
        "logical_entities",
        "data_carriers",
        "access_points",
        "data_containers",
        "execution_assets",
        "mappings",
        "relationships",
        "conceptual_entities",
    ):
        items = data.get(key) or []
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            eid = item.get("element_id")
            if eid:
                ids.add(str(eid))
            for nested_key in ("attributes",):
                nested = item.get(nested_key) or []
                if not isinstance(nested, list):
                    continue
                for n in nested:
                    if isinstance(n, dict) and n.get("element_id"):
                        ids.add(str(n["element_id"]))
    for st in data.get("data_structures") or []:
        if isinstance(st, dict) and st.get("element_id"):
            ids.add(str(st["element_id"]))
    return ids


def add_logical_entity(data: CommentedMap, entity: dict[str, Any]) -> None:
    eid = str(entity.get("element_id") or "").strip()
    name = str(entity.get("name") or "").strip()
    if not eid or not name:
        raise MutationError("element_id and name are required")
    if eid in _collect_ids(data):
        raise MutationConflict(f"duplicate element_id: {eid}")

    row = CommentedMap()
    row["element_id"] = eid
    row["name"] = name
    row["title"] = str(entity.get("title") or name)
    row["description"] = str(
        entity.get("description") or f"Logical entity {name} (workbench draft)."
    )
    row["lifecycle_status"] = str(entity.get("lifecycle_status") or "draft")
    if entity.get("context_ref"):
        row["context_ref"] = str(entity["context_ref"])
    else:
        contexts = data.get("domain_contexts") or []
        if isinstance(contexts, list) and contexts:
            cref = (
                contexts[0].get("element_id")
                if isinstance(contexts[0], dict)
                else None
            )
            if cref:
                row["context_ref"] = str(cref)
            else:
                raise MutationError("context_ref is required")
        else:
            raise MutationError("context_ref is required (no domain_contexts)")
    row["solution_data_role"] = str(
        entity.get("solution_data_role") or "producer"
    )
    if entity.get("solution_ref"):
        row["solution_ref"] = str(entity["solution_ref"])
    elif data.get("solution_ref"):
        row["solution_ref"] = str(data["solution_ref"])
    row["attributes"] = CommentedSeq()

    seq = _ensure_seq(data, "logical_entities")
    seq.append(row)


def add_logical_attribute(
    data: CommentedMap,
    owner_element_id: str,
    attr: dict[str, Any],
) -> None:
    owner = str(owner_element_id or "").strip()
    eid = str(attr.get("element_id") or "").strip()
    name = str(attr.get("name") or "").strip()
    data_type_ref = str(attr.get("data_type_ref") or "").strip()
    value_domain_ref = str(attr.get("value_domain_ref") or "").strip()
    if not owner or not eid or not name:
        raise MutationError(
            "owner_element_id, element_id, and name are required"
        )
    if not (data_type_ref or value_domain_ref):
        raise MutationError(
            "data_type_ref or value_domain_ref is required"
        )
    if eid in _collect_ids(data):
        raise MutationConflict(f"duplicate element_id: {eid}")

    entities = data.get("logical_entities") or []
    if not isinstance(entities, list):
        raise MutationError("logical_entities missing")
    target = None
    for item in entities:
        if isinstance(item, dict) and str(item.get("element_id")) == owner:
            target = item
            break
    if target is None:
        raise MutationError(f"owner entity not found: {owner}")

    if "attributes" not in target or target["attributes"] is None:
        target["attributes"] = CommentedSeq()
    attrs = target["attributes"]
    if not isinstance(attrs, CommentedSeq):
        target["attributes"] = CommentedSeq(list(attrs) if attrs else [])
        attrs = target["attributes"]

    row = CommentedMap()
    row["element_id"] = eid
    row["name"] = name
    row["title"] = str(attr.get("title") or name)
    row["description"] = str(
        attr.get("description") or f"Logical attribute {name} (workbench draft)."
    )
    row["lifecycle_status"] = str(attr.get("lifecycle_status") or "draft")
    row["owner_entity_ref"] = str(attr.get("owner_entity_ref") or owner)
    if data_type_ref:
        row["data_type_ref"] = data_type_ref
    if value_domain_ref:
        row["value_domain_ref"] = value_domain_ref
    if attr.get("concept_ref"):
        row["concept_ref"] = str(attr["concept_ref"])
    if "critical_data_element" in attr:
        row["critical_data_element"] = bool(attr.get("critical_data_element"))
    row["required"] = bool(attr.get("required", False))
    row["multivalued"] = bool(attr.get("multivalued", False))
    attrs.append(row)


_ENTITY_PATCH_KEYS = frozenset(
    {
        "name",
        "title",
        "description",
        "lifecycle_status",
        "context_ref",
        "solution_data_role",
    }
)
_ATTR_PATCH_KEYS = frozenset(
    {
        "name",
        "title",
        "description",
        "data_type_ref",
        "value_domain_ref",
        "concept_ref",
        "critical_data_element",
        "required",
        "multivalued",
        "lifecycle_status",
    }
)


def _find_logical_entity(
    data: CommentedMap, element_id: str
) -> tuple[int, CommentedMap | dict[str, Any]]:
    eid = str(element_id or "").strip()
    if not eid:
        raise MutationError("element_id is required")
    entities = data.get("logical_entities") or []
    if not isinstance(entities, list):
        raise MutationError("logical_entities missing")
    for idx, item in enumerate(entities):
        if isinstance(item, dict) and str(item.get("element_id")) == eid:
            return idx, item
    raise MutationError(f"logical entity not found: {eid}")


def _find_logical_attribute(
    data: CommentedMap, element_id: str
) -> tuple[CommentedMap | dict[str, Any], int, CommentedMap | dict[str, Any]]:
    eid = str(element_id or "").strip()
    if not eid:
        raise MutationError("element_id is required")
    entities = data.get("logical_entities") or []
    if not isinstance(entities, list):
        raise MutationError("logical_entities missing")
    for entity in entities:
        if not isinstance(entity, dict):
            continue
        attrs = entity.get("attributes") or []
        if not isinstance(attrs, list):
            continue
        for idx, attr in enumerate(attrs):
            if isinstance(attr, dict) and str(attr.get("element_id")) == eid:
                return entity, idx, attr
    raise MutationError(f"logical attribute not found: {eid}")


_RELATIONSHIP_PATCH_KEYS = frozenset(
    {
        "name",
        "title",
        "description",
        "lifecycle_status",
        "source_entity_ref",
        "target_entity_ref",
        "source_role",
        "target_role",
        "source_min_cardinality",
        "source_max_cardinality",
        "target_min_cardinality",
        "target_max_cardinality",
        "identifying",
        "associative",
    }
)
_MAPPING_PATCH_KEYS = frozenset(
    {
        "name",
        "title",
        "description",
        "lifecycle_status",
        "source_refs",
        "target_refs",
        "mapping_type",
        "mapping_cardinality",
        "transformation_expression",
    }
)
_CARDINALITY_KEYS = frozenset(
    {
        "source_min_cardinality",
        "source_max_cardinality",
        "target_min_cardinality",
        "target_max_cardinality",
    }
)
_BOOL_PATCH_KEYS = frozenset(
    {"required", "multivalued", "identifying", "associative", "nullable"}
)


def _apply_patch(
    target: CommentedMap | dict[str, Any],
    patch: dict[str, Any],
    allowed: frozenset[str],
) -> None:
    if not patch:
        raise MutationError("patch must be a non-empty object")
    if "element_id" in patch:
        raise MutationError("element_id cannot be changed via patch")
    applied = False
    for key, value in patch.items():
        if key not in allowed:
            raise MutationError(f"unsupported patch key: {key}")
        if key in _BOOL_PATCH_KEYS:
            target[key] = bool(value)
        elif key in _CARDINALITY_KEYS:
            target[key] = int(value) if value is not None else None
        elif key in {"source_refs", "target_refs"}:
            if not isinstance(value, list) or not value:
                raise MutationError(f"{key} must be a non-empty list")
            target[key] = list(value)
        else:
            target[key] = value
        applied = True
    if not applied:
        raise MutationError("patch must be a non-empty object")


def update_logical_entity(
    data: CommentedMap, element_id: str, patch: dict[str, Any]
) -> None:
    _, entity = _find_logical_entity(data, element_id)
    _apply_patch(entity, patch or {}, _ENTITY_PATCH_KEYS)


def delete_logical_entity(data: CommentedMap, element_id: str) -> None:
    idx, _ = _find_logical_entity(data, element_id)
    entities = data["logical_entities"]
    del entities[idx]


def update_logical_attribute(
    data: CommentedMap, element_id: str, patch: dict[str, Any]
) -> None:
    _, _, attr = _find_logical_attribute(data, element_id)
    _apply_patch(attr, patch or {}, _ATTR_PATCH_KEYS)


def delete_logical_attribute(data: CommentedMap, element_id: str) -> None:
    entity, idx, _ = _find_logical_attribute(data, element_id)
    attrs = entity["attributes"]
    del attrs[idx]


def _find_top_level_item(
    data: CommentedMap, collection: str, element_id: str, label: str
) -> tuple[int, CommentedMap | dict[str, Any]]:
    eid = str(element_id or "").strip()
    if not eid:
        raise MutationError("element_id is required")
    items = data.get(collection) or []
    if not isinstance(items, list):
        raise MutationError(f"{collection} missing")
    for idx, item in enumerate(items):
        if isinstance(item, dict) and str(item.get("element_id")) == eid:
            return idx, item
    raise MutationError(f"{label} not found: {eid}")


def add_relationship(data: CommentedMap, relationship: dict[str, Any]) -> None:
    eid = str(relationship.get("element_id") or "").strip()
    name = str(relationship.get("name") or "").strip()
    description = str(relationship.get("description") or "").strip()
    source = str(relationship.get("source_entity_ref") or "").strip()
    target = str(relationship.get("target_entity_ref") or "").strip()
    if not eid or not name or not description or not source or not target:
        raise MutationError(
            "element_id, name, description, source_entity_ref, "
            "and target_entity_ref are required"
        )
    if eid in _collect_ids(data):
        raise MutationConflict(f"duplicate element_id: {eid}")

    row = CommentedMap()
    row["element_id"] = eid
    row["name"] = name
    row["title"] = str(relationship.get("title") or name)
    row["description"] = description
    row["lifecycle_status"] = str(relationship.get("lifecycle_status") or "draft")
    row["source_entity_ref"] = source
    row["target_entity_ref"] = target
    for key in (
        "source_role",
        "target_role",
        "source_min_cardinality",
        "source_max_cardinality",
        "target_min_cardinality",
        "target_max_cardinality",
        "identifying",
        "associative",
    ):
        if key in relationship and relationship[key] is not None:
            if key in _BOOL_PATCH_KEYS:
                row[key] = bool(relationship[key])
            elif key in _CARDINALITY_KEYS:
                row[key] = int(relationship[key])
            else:
                row[key] = relationship[key]

    seq = _ensure_seq(data, "relationships")
    seq.append(row)


def update_relationship(
    data: CommentedMap, element_id: str, patch: dict[str, Any]
) -> None:
    _, item = _find_top_level_item(
        data, "relationships", element_id, "relationship"
    )
    _apply_patch(item, patch or {}, _RELATIONSHIP_PATCH_KEYS)


def delete_relationship(data: CommentedMap, element_id: str) -> None:
    idx, _ = _find_top_level_item(
        data, "relationships", element_id, "relationship"
    )
    seq = data["relationships"]
    del seq[idx]


def add_mapping(data: CommentedMap, mapping: dict[str, Any]) -> None:
    eid = str(mapping.get("element_id") or "").strip()
    name = str(mapping.get("name") or "").strip()
    description = str(mapping.get("description") or "").strip()
    mapping_type = str(mapping.get("mapping_type") or "").strip()
    mapping_cardinality = str(mapping.get("mapping_cardinality") or "").strip()
    source_refs = mapping.get("source_refs")
    target_refs = mapping.get("target_refs")
    if (
        not eid
        or not name
        or not description
        or not mapping_type
        or not mapping_cardinality
        or not isinstance(source_refs, list)
        or not source_refs
        or not isinstance(target_refs, list)
        or not target_refs
    ):
        raise MutationError(
            "element_id, name, description, source_refs, target_refs, "
            "mapping_type, and mapping_cardinality are required"
        )
    if eid in _collect_ids(data):
        raise MutationConflict(f"duplicate element_id: {eid}")

    row = CommentedMap()
    row["element_id"] = eid
    row["name"] = name
    row["title"] = str(mapping.get("title") or name)
    row["description"] = description
    row["lifecycle_status"] = str(mapping.get("lifecycle_status") or "draft")
    row["source_refs"] = list(source_refs)
    row["target_refs"] = list(target_refs)
    row["mapping_type"] = mapping_type
    row["mapping_cardinality"] = mapping_cardinality
    if mapping.get("transformation_expression") is not None:
        row["transformation_expression"] = str(mapping["transformation_expression"])

    seq = _ensure_seq(data, "mappings")
    seq.append(row)


def update_mapping(
    data: CommentedMap, element_id: str, patch: dict[str, Any]
) -> None:
    _, item = _find_top_level_item(data, "mappings", element_id, "mapping")
    _apply_patch(item, patch or {}, _MAPPING_PATCH_KEYS)


def delete_mapping(data: CommentedMap, element_id: str) -> None:
    idx, _ = _find_top_level_item(data, "mappings", element_id, "mapping")
    seq = data["mappings"]
    del seq[idx]


_TECHNICAL_COLLECTIONS = (
    "data_carriers",
    "access_points",
    "data_containers",
    "execution_assets",
)

_ASSET_KIND_TO_COLLECTION: dict[str, str] = {
    "relational_table": "data_carriers",
    "relational_view": "data_carriers",
    "file": "data_carriers",
    "dataset": "data_carriers",
    "stream_topic": "data_carriers",
    "stream_queue": "data_carriers",
    "in_memory": "data_carriers",
    "api_resource": "data_carriers",
    "other": "data_carriers",
    "table": "data_carriers",
    "view": "data_carriers",
    "topic": "data_carriers",
    "queue": "data_carriers",
    "interface": "access_points",
    "operation": "access_points",
    "channel": "access_points",
    "api": "access_points",
    "endpoint": "access_points",
    "database": "data_containers",
    "schema": "data_containers",
    "bucket": "data_containers",
    "broker": "data_containers",
    "directory": "data_containers",
    "cluster": "data_containers",
    "pipeline": "execution_assets",
    "job": "execution_assets",
}

_LEGACY_KIND_MAP: dict[str, str] = {
    "table": "relational_table",
    "view": "relational_view",
    "topic": "stream_topic",
    "queue": "stream_queue",
    "api": "interface",
    "endpoint": "operation",
}

_PHYSICAL_OBJECT_PATCH_KEYS = frozenset(
    {
        "name",
        "title",
        "description",
        "lifecycle_status",
        "asset_kind",
        "object_kind",  # legacy alias → remapped in update
        "logical_entity_ref",
        "qualified_name",
        "technology",
        "system_ref",
        "direction",
        "asset_namespace",
        "structure_ref",
        "parent_ref",
    }
)
_SCHEMA_NODE_PATCH_KEYS = frozenset(
    {
        "native_name",
        "native_type",
        "required",
        "description",
        "nullable",
        "column_position",
        "ordinal_position",
        "is_primary_key",
        "is_unique",
    }
)


def _normalize_asset_kind(raw: str | None) -> str:
    kind = str(raw or "relational_table").strip() or "relational_table"
    removed = {"message", "payload", "message" + "_type"}
    if kind in removed:
        raise MutationError(
            f"asset_kind {kind!r} removed; use Message + DataStructure (ADR-040)"
        )
    return _LEGACY_KIND_MAP.get(kind, kind)


def _collection_for_kind(asset_kind: str) -> str:
    return _ASSET_KIND_TO_COLLECTION.get(asset_kind, "data_carriers")


def _find_technical_asset(
    data: CommentedMap, element_id: str
) -> tuple[str, int, CommentedMap | dict[str, Any]]:
    eid = str(element_id or "").strip()
    if not eid:
        raise MutationError("element_id is required")
    for key in _TECHNICAL_COLLECTIONS:
        items = data.get(key) or []
        if not isinstance(items, list):
            continue
        for idx, item in enumerate(items):
            if isinstance(item, dict) and str(item.get("element_id")) == eid:
                return key, idx, item
    raise MutationError(f"technical asset not found: {eid}")


def _find_physical_object(
    data: CommentedMap, element_id: str
) -> tuple[int, CommentedMap | dict[str, Any]]:
    _key, idx, item = _find_technical_asset(data, element_id)
    return idx, item


def _slug_local_key(text: str) -> str:
    s = str(text or "").strip().lower()
    out: list[str] = []
    for ch in s:
        if ("a" <= ch <= "z") or ("0" <= ch <= "9") or ch in "_.-":
            out.append(ch)
        else:
            out.append("_")
    token = "".join(out).strip("_.-") or "_"
    return token


def _ensure_structure_for_carrier(
    data: CommentedMap, carrier: CommentedMap | dict[str, Any]
) -> CommentedMap | dict[str, Any]:
    sid = str(carrier.get("structure_ref") or "").strip()
    structures = _ensure_seq(data, "data_structures")
    if sid:
        for st in structures:
            if isinstance(st, dict) and str(st.get("element_id")) == sid:
                if "nodes" not in st or st["nodes"] is None:
                    st["nodes"] = CommentedSeq()
                return st
    # Create a new relational DataStructure
    name = str(carrier.get("name") or "structure")
    eid = str(carrier.get("element_id") or "")
    slug = "unknown"
    parts = eid.split("/")
    if len(parts) >= 3:
        slug = parts[1]
    structure_id = f"dams:structure/{slug}/{name}"
    row = CommentedMap()
    row["element_id"] = structure_id
    row["name"] = name
    row["title"] = str(carrier.get("title") or name)
    row["description"] = f"Structure for {name}"
    row["lifecycle_status"] = str(carrier.get("lifecycle_status") or "draft")
    row["schema_format"] = "relational"
    row["structure_version"] = "1.0.0"
    row["root_local_key"] = "root"
    root = CommentedMap()
    root["local_key"] = "root"
    root["node_kind"] = "object"
    root["children"] = CommentedSeq()
    row["nodes"] = CommentedSeq([root])
    structures.append(row)
    carrier["structure_ref"] = structure_id
    return row


def _parse_node_ref(ref: str) -> tuple[str, str]:
    text = str(ref or "").strip()
    if "#" not in text:
        raise MutationError(
            f"schema node ref must be structure_id#local_key, got: {ref!r}"
        )
    sid, key = text.split("#", 1)
    if not sid or not key:
        raise MutationError(f"invalid schema node ref: {ref!r}")
    return sid, key


def _find_schema_node(
    data: CommentedMap, node_ref: str
) -> tuple[CommentedMap | dict[str, Any], int, CommentedMap | dict[str, Any]]:
    sid, local_key = _parse_node_ref(node_ref)
    structures = data.get("data_structures") or []
    if not isinstance(structures, list):
        raise MutationError("data_structures missing")
    for st in structures:
        if not isinstance(st, dict) or str(st.get("element_id")) != sid:
            continue
        nodes = st.get("nodes") or []
        if not isinstance(nodes, list):
            continue
        for idx, node in enumerate(nodes):
            if isinstance(node, dict) and str(node.get("local_key")) == local_key:
                return st, idx, node
    raise MutationError(f"schema node not found: {node_ref}")


def add_physical_object(data: CommentedMap, obj: dict[str, Any]) -> None:
    eid = str(obj.get("element_id") or "").strip()
    name = str(obj.get("name") or "").strip()
    if not eid or not name:
        raise MutationError("element_id and name are required")
    if eid in _collect_ids(data):
        raise MutationConflict(f"duplicate element_id: {eid}")

    asset_kind = _normalize_asset_kind(
        obj.get("asset_kind") or obj.get("object_kind")
    )
    collection = str(obj.get("collection") or _collection_for_kind(asset_kind))
    if collection not in _TECHNICAL_COLLECTIONS:
        collection = "data_carriers"

    row = CommentedMap()
    row["element_id"] = eid
    row["name"] = name
    row["title"] = str(obj.get("title") or name)
    row["description"] = str(
        obj.get("description") or f"Technical asset {name} (workbench draft)."
    )
    row["lifecycle_status"] = str(obj.get("lifecycle_status") or "draft")
    row["asset_kind"] = asset_kind
    for key in (
        "logical_entity_ref",
        "qualified_name",
        "technology",
        "system_ref",
        "direction",
        "solution_ref",
        "asset_namespace",
        "structure_ref",
        "parent_ref",
        "native_schema_ref",
    ):
        if obj.get(key) is not None:
            if key == "native_schema_ref":
                row["structure_ref"] = str(obj[key])
            else:
                row[key] = str(obj[key])
    seq = _ensure_seq(data, collection)
    seq.append(row)


def update_physical_object(
    data: CommentedMap, element_id: str, patch: dict[str, Any]
) -> None:
    _, item = _find_physical_object(data, element_id)
    patch = dict(patch or {})
    if "object_kind" in patch and "asset_kind" not in patch:
        patch["asset_kind"] = _normalize_asset_kind(str(patch.pop("object_kind")))
    elif "asset_kind" in patch:
        patch["asset_kind"] = _normalize_asset_kind(str(patch["asset_kind"]))
        patch.pop("object_kind", None)
    _apply_patch(item, patch, _PHYSICAL_OBJECT_PATCH_KEYS)


def delete_physical_object(data: CommentedMap, element_id: str) -> None:
    key, idx, _ = _find_technical_asset(data, element_id)
    seq = data[key]
    del seq[idx]


def add_schema_node(
    data: CommentedMap,
    owner_element_id: str,
    node: dict[str, Any],
) -> None:
    owner = str(owner_element_id or "").strip()
    name = str(node.get("name") or node.get("native_name") or node.get("local_key") or "").strip()
    native_type = str(node.get("native_type") or "").strip()
    if not owner or not name or not native_type:
        raise MutationError(
            "owner_element_id, name (or local_key), and native_type are required"
        )
    _, carrier = _find_physical_object(data, owner)
    structure = _ensure_structure_for_carrier(data, carrier)
    nodes = structure["nodes"]
    if not isinstance(nodes, CommentedSeq):
        structure["nodes"] = CommentedSeq(list(nodes) if nodes else [])
        nodes = structure["nodes"]

    local_key = str(node.get("local_key") or _slug_local_key(name)).strip()
    used = {
        str(n.get("local_key"))
        for n in nodes
        if isinstance(n, dict) and n.get("local_key")
    }
    if local_key in used:
        base = local_key
        n = 2
        while f"{base}-{n}" in used:
            n += 1
        local_key = f"{base}-{n}"

    row = CommentedMap()
    row["local_key"] = local_key
    row["node_kind"] = "scalar"
    row["native_name"] = str(node.get("native_name") or name)
    row["native_type"] = native_type
    row["required"] = bool(node.get("required", False))
    if node.get("description"):
        row["description"] = str(node["description"])
    nodes.append(row)

    # Attach under root children
    root_key = str(structure.get("root_local_key") or "root")
    for n in nodes:
        if isinstance(n, dict) and str(n.get("local_key")) == root_key:
            children = n.get("children")
            if not isinstance(children, list):
                n["children"] = CommentedSeq()
                children = n["children"]
            if local_key not in children:
                children.append(local_key)
            break


def update_schema_node(
    data: CommentedMap, node_ref: str, patch: dict[str, Any]
) -> None:
    _, _, node = _find_schema_node(data, node_ref)
    _apply_patch(node, patch or {}, _SCHEMA_NODE_PATCH_KEYS)


def delete_schema_node(data: CommentedMap, node_ref: str) -> None:
    st, idx, node = _find_schema_node(data, node_ref)
    local_key = str(node.get("local_key"))
    nodes = st["nodes"]
    del nodes[idx]
    # Drop from parent children lists
    for n in nodes:
        if not isinstance(n, dict):
            continue
        children = n.get("children")
        if isinstance(children, list) and local_key in children:
            while local_key in children:
                children.remove(local_key)


def apply_mutation(text: str, payload: dict[str, Any]) -> str:
    data = load_yaml(text)
    op = payload.get("op")
    if op == "add_logical_entity":
        add_logical_entity(data, payload.get("entity") or {})
    elif op == "add_logical_attribute":
        add_logical_attribute(
            data,
            str(payload.get("owner_element_id") or ""),
            payload.get("attribute") or {},
        )
    elif op == "update_logical_entity":
        update_logical_entity(
            data,
            str(payload.get("element_id") or ""),
            payload.get("patch") or {},
        )
    elif op == "delete_logical_entity":
        delete_logical_entity(data, str(payload.get("element_id") or ""))
    elif op == "update_logical_attribute":
        update_logical_attribute(
            data,
            str(payload.get("element_id") or ""),
            payload.get("patch") or {},
        )
    elif op == "delete_logical_attribute":
        delete_logical_attribute(data, str(payload.get("element_id") or ""))
    elif op == "add_relationship":
        add_relationship(data, payload.get("relationship") or {})
    elif op == "update_relationship":
        update_relationship(
            data,
            str(payload.get("element_id") or ""),
            payload.get("patch") or {},
        )
    elif op == "delete_relationship":
        delete_relationship(data, str(payload.get("element_id") or ""))
    elif op == "add_mapping":
        add_mapping(data, payload.get("mapping") or {})
    elif op == "update_mapping":
        update_mapping(
            data,
            str(payload.get("element_id") or ""),
            payload.get("patch") or {},
        )
    elif op == "delete_mapping":
        delete_mapping(data, str(payload.get("element_id") or ""))
    elif op == "add_physical_object":
        add_physical_object(data, payload.get("physical_object") or {})
    elif op == "update_physical_object":
        update_physical_object(
            data,
            str(payload.get("element_id") or ""),
            payload.get("patch") or {},
        )
    elif op == "delete_physical_object":
        delete_physical_object(data, str(payload.get("element_id") or ""))
    elif op == "add_schema_node":
        add_schema_node(
            data,
            str(payload.get("owner_element_id") or ""),
            payload.get("schema_node") or payload.get("node") or {},
        )
    elif op == "update_schema_node":
        update_schema_node(
            data,
            str(payload.get("element_id") or payload.get("node_ref") or ""),
            payload.get("patch") or {},
        )
    elif op == "delete_schema_node":
        delete_schema_node(
            data,
            str(payload.get("element_id") or payload.get("node_ref") or ""),
        )
    else:
        raise MutationError(f"unsupported op: {op!r}")
    return dump_yaml(data)
