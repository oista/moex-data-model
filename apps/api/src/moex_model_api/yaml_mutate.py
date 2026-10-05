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
            for nested_key in ("attributes", "physical_fields", "fields"):
                nested = item.get(nested_key) or []
                if not isinstance(nested, list):
                    continue
                for n in nested:
                    if isinstance(n, dict) and n.get("element_id"):
                        ids.add(str(n["element_id"]))
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
    "message_type": "data_carriers",
    "in_memory": "data_carriers",
    "api_resource": "data_carriers",
    "other": "data_carriers",
    "table": "data_carriers",
    "view": "data_carriers",
    "topic": "data_carriers",
    "queue": "data_carriers",
    "message": "data_carriers",
    "payload": "data_carriers",
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
    "message": "message_type",
    "payload": "message_type",
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
_PHYSICAL_FIELD_PATCH_KEYS = frozenset(
    {
        "name",
        "title",
        "description",
        "lifecycle_status",
        "native_name",
        "native_type",
        "required",
        "nullable",
        "logical_attribute_ref",
        "schema_path",
    }
)


def _normalize_asset_kind(raw: str | None) -> str:
    kind = str(raw or "relational_table").strip() or "relational_table"
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


def _find_physical_field(
    data: CommentedMap, element_id: str
) -> tuple[CommentedMap | dict[str, Any], int, CommentedMap | dict[str, Any]]:
    eid = str(element_id or "").strip()
    if not eid:
        raise MutationError("element_id is required")
    for key in _TECHNICAL_COLLECTIONS:
        objects = data.get(key) or []
        if not isinstance(objects, list):
            continue
        for obj in objects:
            if not isinstance(obj, dict):
                continue
            fields = obj.get("physical_fields") or []
            if not isinstance(fields, list):
                continue
            for idx, field in enumerate(fields):
                if isinstance(field, dict) and str(field.get("element_id")) == eid:
                    return obj, idx, field
    raise MutationError(f"physical field not found: {eid}")


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
            # native_schema_ref → structure_ref for carriers
            if key == "native_schema_ref":
                row["structure_ref"] = str(obj[key])
            else:
                row[key] = str(obj[key])
    if collection == "data_carriers":
        row["physical_fields"] = CommentedSeq()
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


def add_physical_field(
    data: CommentedMap,
    owner_element_id: str,
    field: dict[str, Any],
) -> None:
    owner = str(owner_element_id or "").strip()
    eid = str(field.get("element_id") or "").strip()
    name = str(field.get("name") or "").strip()
    native_type = str(field.get("native_type") or "").strip()
    if not owner or not eid or not name or not native_type:
        raise MutationError(
            "owner_element_id, element_id, name, and native_type are required"
        )
    if eid in _collect_ids(data):
        raise MutationConflict(f"duplicate element_id: {eid}")

    _, target = _find_physical_object(data, owner)
    if "physical_fields" not in target or target["physical_fields"] is None:
        target["physical_fields"] = CommentedSeq()
    fields = target["physical_fields"]
    if not isinstance(fields, CommentedSeq):
        target["physical_fields"] = CommentedSeq(list(fields) if fields else [])
        fields = target["physical_fields"]

    row = CommentedMap()
    row["element_id"] = eid
    row["name"] = name
    row["description"] = str(
        field.get("description") or f"Physical field {name} (workbench draft)."
    )
    row["lifecycle_status"] = str(field.get("lifecycle_status") or "draft")
    row["carrier_ref"] = str(
        field.get("carrier_ref") or field.get("physical_object_ref") or owner
    )
    row["native_name"] = str(field.get("native_name") or name)
    row["native_type"] = native_type
    row["required"] = bool(field.get("required", False))
    if "nullable" in field and field["nullable"] is not None:
        row["nullable"] = bool(field["nullable"])
    if field.get("logical_attribute_ref"):
        row["logical_attribute_ref"] = str(field["logical_attribute_ref"])
    if field.get("schema_path"):
        row["schema_path"] = str(field["schema_path"])
    fields.append(row)


def update_physical_field(
    data: CommentedMap, element_id: str, patch: dict[str, Any]
) -> None:
    _, _, field = _find_physical_field(data, element_id)
    _apply_patch(field, patch or {}, _PHYSICAL_FIELD_PATCH_KEYS)

def delete_physical_field(data: CommentedMap, element_id: str) -> None:
    obj, idx, _ = _find_physical_field(data, element_id)
    fields = obj["physical_fields"]
    del fields[idx]


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
    elif op == "add_physical_field":
        add_physical_field(
            data,
            str(payload.get("owner_element_id") or ""),
            payload.get("physical_field") or {},
        )
    elif op == "update_physical_field":
        update_physical_field(
            data,
            str(payload.get("element_id") or ""),
            payload.get("patch") or {},
        )
    elif op == "delete_physical_field":
        delete_physical_field(data, str(payload.get("element_id") or ""))
    else:
        raise MutationError(f"unsupported op: {op!r}")
    return dump_yaml(data)
