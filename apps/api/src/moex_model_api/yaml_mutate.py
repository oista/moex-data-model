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
    for key in ("logical_entities", "physical_objects", "mappings", "conceptual_entities"):
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
    logical_type = str(attr.get("logical_type") or "").strip()
    if not owner or not eid or not name or not logical_type:
        raise MutationError(
            "owner_element_id, element_id, name, and logical_type are required"
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
    row["logical_type"] = logical_type
    row["required"] = bool(attr.get("required", False))
    row["multivalued"] = bool(attr.get("multivalued", False))
    attrs.append(row)


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
    else:
        raise MutationError(f"unsupported op: {op!r}")
    return dump_yaml(data)
