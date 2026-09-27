"""Extract searchable elements from a DAMS ModelPackage dict."""

from __future__ import annotations

from typing import Any

from moex_model_api.ports import IndexElement

_LIST_KINDS: tuple[tuple[str, str, str], ...] = (
    ("conceptual_entities", "ConceptualEntity", "conceptual"),
    ("logical_entities", "LogicalEntity", "logical"),
    ("physical_objects", "PhysicalObject", "physical"),
    ("mappings", "Mapping", "mapping"),
)


def elements_from_package(data: dict[str, Any]) -> list[IndexElement]:
    out: list[IndexElement] = []
    root_id = str(data.get("element_id") or "")
    if root_id:
        out.append(
            IndexElement(
                element_id=root_id,
                element_kind="ModelPackage",
                name=str(data.get("name") or ""),
                layer="package",
            )
        )
    for key, kind, layer in _LIST_KINDS:
        items = data.get(key) or []
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            eid = item.get("element_id")
            if not eid:
                continue
            out.append(
                IndexElement(
                    element_id=str(eid),
                    element_kind=kind,
                    name=str(item.get("name") or ""),
                    layer=layer,
                )
            )
            nested_lists = (
                ("attributes", "LogicalAttribute"),
                ("physical_fields", "PhysicalField"),
                ("fields", "PhysicalField"),
            )
            for nested_key, nested_kind in nested_lists:
                attrs = item.get(nested_key) or []
                if not isinstance(attrs, list):
                    continue
                for nested in attrs:
                    if isinstance(nested, dict) and nested.get("element_id"):
                        out.append(
                            IndexElement(
                                element_id=str(nested["element_id"]),
                                element_kind=nested_kind,
                                name=str(nested.get("name") or ""),
                                layer=layer,
                            )
                        )
    return out
