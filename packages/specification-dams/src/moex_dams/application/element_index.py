"""Unified searchable element index for DAMS ModelPackage instances."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ElementIndexEntry:
    element_id: str
    element_kind: str
    name: str
    layer: str


_LIST_KINDS: tuple[tuple[str, str, str], ...] = (
    ("conceptual_entities", "ConceptualEntity", "conceptual"),
    ("logical_entities", "LogicalEntity", "logical"),
    ("data_carriers", "DataCarrier", "physical"),
    ("access_points", "AccessPoint", "physical"),
    ("data_containers", "DataContainer", "physical"),
    ("execution_assets", "ExecutionAsset", "physical"),
    ("data_structures", "DataStructure", "physical"),
    ("messages", "Message", "physical"),
    ("mappings", "Mapping", "mapping"),
    ("relationships", "Relationship", "logical"),
)


def build_element_index(data: dict[str, Any]) -> list[ElementIndexEntry]:
    """Build a stable element_id index from a ModelPackage dict."""
    out: list[ElementIndexEntry] = []
    root_id = str(data.get("element_id") or "")
    if root_id:
        out.append(
            ElementIndexEntry(
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
                ElementIndexEntry(
                    element_id=str(eid),
                    element_kind=kind,
                    name=str(item.get("name") or ""),
                    layer=layer,
                )
            )
            if key == "logical_entities":
                for nested in item.get("attributes") or []:
                    if isinstance(nested, dict) and nested.get("element_id"):
                        out.append(
                            ElementIndexEntry(
                                element_id=str(nested["element_id"]),
                                element_kind="LogicalAttribute",
                                name=str(nested.get("name") or ""),
                                layer=layer,
                            )
                        )
            if key == "data_structures":
                sid = str(eid)
                for nested in item.get("nodes") or []:
                    if not isinstance(nested, dict):
                        continue
                    local_key = nested.get("local_key")
                    if not local_key:
                        continue
                    out.append(
                        ElementIndexEntry(
                            element_id=f"{sid}#{local_key}",
                            element_kind="SchemaNode",
                            name=str(
                                nested.get("native_name")
                                or nested.get("local_key")
                                or ""
                            ),
                            layer=layer,
                        )
                    )
    return out
