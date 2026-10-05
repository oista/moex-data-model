"""Containment cascade of governed properties (ADR-023).

YAML stores declared values only (absent key = inherit). This module computes
effective values with provenance along ModelPackage containment trees.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class CascadeCardinality(str, Enum):
    SCALAR = "scalar"
    LIST_REPLACE = "list-replace"


@dataclass(frozen=True)
class CascadeFamily:
    name: str
    slots: tuple[str, ...]
    cardinality: CascadeCardinality


@dataclass(frozen=True)
class SlotProvenance:
    value: Any
    source_element_id: str | None
    level: str


OWNERSHIP_FAMILY = CascadeFamily(
    name="ownership",
    slots=("data_owner_ref", "data_steward_ref", "owning_unit_ref"),
    cardinality=CascadeCardinality.SCALAR,
)

CLASSIFICATION_FAMILY = CascadeFamily(
    name="classification",
    slots=("governance_classification",),
    cardinality=CascadeCardinality.SCALAR,
)

POLICIES_FAMILY = CascadeFamily(
    name="policies",
    slots=("policy_refs",),
    cardinality=CascadeCardinality.LIST_REPLACE,
)

GOVERNED_FAMILIES: tuple[CascadeFamily, ...] = (
    OWNERSHIP_FAMILY,
    CLASSIFICATION_FAMILY,
    POLICIES_FAMILY,
)

GOVERNED_SLOTS: frozenset[str] = frozenset(
    slot for family in GOVERNED_FAMILIES for slot in family.slots
)

# Containment edges from package root (DomainContext is intentionally excluded).
_CHILD_COLLECTIONS: tuple[tuple[str, str, str | None], ...] = (
    # (collection_key, level_name, nested_collection_key)
    ("logical_entities", "LogicalEntity", "attributes"),
    ("conceptual_entities", "ConceptualEntity", None),
    ("data_carriers", "DataCarrier", "physical_fields"),
    ("access_points", "AccessPoint", None),
    ("data_containers", "DataContainer", None),
    ("execution_assets", "ExecutionAsset", None),
)

_NESTED_LEVEL: dict[str, str] = {
    "attributes": "LogicalAttribute",
    "physical_fields": "PhysicalField",
}

DATA_OWNER_PLACEHOLDER = "org:role/DATA_OWNER_PENDING"


def _element_id(el: dict[str, Any], fallback: str) -> str:
    return str(el.get("element_id") or el.get("name") or fallback)


def _slot_declared(el: dict[str, Any], slot: str) -> bool:
    """True if the key is present (including empty list for list-replace)."""
    return slot in el


def _resolve_slot(
    *,
    el: dict[str, Any],
    slot: str,
    family: CascadeFamily,
    parent_eff: dict[str, SlotProvenance],
    element_id: str,
    level: str,
) -> SlotProvenance:
    if _slot_declared(el, slot):
        return SlotProvenance(
            value=el.get(slot),
            source_element_id=element_id,
            level=level,
        )
    if slot in parent_eff:
        return parent_eff[slot]
    # Scalar inherit of "nothing"; list inherit of empty.
    default: Any = [] if family.cardinality is CascadeCardinality.LIST_REPLACE else None
    return SlotProvenance(value=default, source_element_id=None, level=level)


def _resolve_element(
    el: dict[str, Any],
    *,
    level: str,
    parent_eff: dict[str, SlotProvenance],
    out: dict[str, dict[str, SlotProvenance]],
) -> dict[str, SlotProvenance]:
    eid = _element_id(el, level)
    effective: dict[str, SlotProvenance] = {}
    for family in GOVERNED_FAMILIES:
        for slot in family.slots:
            effective[slot] = _resolve_slot(
                el=el,
                slot=slot,
                family=family,
                parent_eff=parent_eff,
                element_id=eid,
                level=level,
            )
    out[eid] = effective
    return effective


def resolve_governed(body_data: dict[str, Any]) -> dict[str, dict[str, SlotProvenance]]:
    """Resolve effective governed slots for every cascade node in the package.

    Returns ``{element_id: {slot: SlotProvenance}}``.
    """
    out: dict[str, dict[str, SlotProvenance]] = {}
    root_eff = _resolve_element(
        body_data,
        level="ModelPackage",
        parent_eff={},
        out=out,
    )

    for collection, level, nested_key in _CHILD_COLLECTIONS:
        for child in body_data.get(collection) or []:
            if not isinstance(child, dict):
                continue
            child_eff = _resolve_element(
                child,
                level=level,
                parent_eff=root_eff,
                out=out,
            )
            if not nested_key:
                continue
            nested_level = _NESTED_LEVEL[nested_key]
            for nested in child.get(nested_key) or []:
                if not isinstance(nested, dict):
                    continue
                _resolve_element(
                    nested,
                    level=nested_level,
                    parent_eff=child_eff,
                    out=out,
                )
    return out


def effective_value(
    resolved: dict[str, dict[str, SlotProvenance]],
    element_id: str,
    slot: str,
) -> Any:
    prov = resolved.get(element_id, {}).get(slot)
    return None if prov is None else prov.value


def iter_cascade_nodes(
    body_data: dict[str, Any],
) -> list[tuple[dict[str, Any], str, dict[str, Any] | None, str | None]]:
    """Yield (element, level, parent_element_or_None, parent_level_or_None)."""
    nodes: list[tuple[dict[str, Any], str, dict[str, Any] | None, str | None]] = [
        (body_data, "ModelPackage", None, None)
    ]
    for collection, level, nested_key in _CHILD_COLLECTIONS:
        for child in body_data.get(collection) or []:
            if not isinstance(child, dict):
                continue
            nodes.append((child, level, body_data, "ModelPackage"))
            if not nested_key:
                continue
            nested_level = _NESTED_LEVEL[nested_key]
            for nested in child.get(nested_key) or []:
                if isinstance(nested, dict):
                    nodes.append((nested, nested_level, child, level))
    return nodes


def find_redundant_overrides(
    body_data: dict[str, Any],
) -> list[tuple[str, str, Any, str]]:
    """Return (element_id, slot, value, parent_element_id) for redundant overrides.

    A declared value equal to the parent's *effective* value is redundant.
    """
    resolved = resolve_governed(body_data)
    findings: list[tuple[str, str, Any, str]] = []
    for el, level, parent, _parent_level in iter_cascade_nodes(body_data):
        if parent is None:
            continue
        eid = _element_id(el, level)
        pid = _element_id(parent, "ModelPackage")
        parent_eff = resolved.get(pid, {})
        for slot in GOVERNED_SLOTS:
            if not _slot_declared(el, slot):
                continue
            declared = el.get(slot)
            parent_prov = parent_eff.get(slot)
            if parent_prov is None:
                continue
            if declared == parent_prov.value:
                findings.append((eid, slot, declared, pid))
    return findings
