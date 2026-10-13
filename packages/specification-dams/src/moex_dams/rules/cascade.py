"""Containment cascade of governed properties (ADR-023 / ADR-049).

YAML stores declared values only (absent key = inherit). This module computes
effective values with provenance along ModelPackage containment trees.

ADR-049 assignment overrides are implemented here (shared helpers) and exposed
via ``moex_dams.rules.assignment_resolver`` as the preferred import path
(Wave D4). Effective values are never written back into authored YAML.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
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
    layer: str = "inline"  # assignment | inline | none
    assignment_id: str | None = None


@dataclass(frozen=True)
class GovernanceFinding:
    """Diagnostic from assignment resolution (ADR-049)."""

    code: str  # conflicting_assignments | dangling_target | shadowed_default
    severity: str  # error | warning
    message: str
    assignment_ids: tuple[str, ...] = ()
    element_id: str | None = None
    slot: str | None = None


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
    ("data_carriers", "DataCarrier", None),
    ("access_points", "AccessPoint", None),
    ("data_containers", "DataContainer", None),
    ("execution_assets", "ExecutionAsset", None),
    ("data_structures", "DataStructure", "nodes"),
    ("messages", "Message", None),
)

_NESTED_LEVEL: dict[str, str] = {
    "attributes": "LogicalAttribute",
    "nodes": "SchemaNode",
}

_ASSIGNMENT_COLLECTIONS: tuple[tuple[str, str], ...] = (
    ("classification_assignments", "classification"),
    ("policy_bindings", "policies"),
    ("ownership_assignments", "ownership"),
)

DATA_OWNER_PLACEHOLDER = "org:role/DATA_OWNER_PENDING"


def _element_id(
    el: dict[str, Any],
    fallback: str,
    *,
    parent_id: str | None = None,
) -> str:
    if el.get("element_id"):
        return str(el["element_id"])
    if parent_id and el.get("local_key"):
        return f"{parent_id}#{el['local_key']}"
    if el.get("name"):
        return str(el["name"])
    if el.get("local_key"):
        return str(el["local_key"])
    return fallback


def _slot_declared(el: dict[str, Any], slot: str) -> bool:
    """True if the key is present (including empty list for list-replace)."""
    return slot in el


def _parse_as_of(as_of: date | datetime | str | None) -> date | None:
    if as_of is None:
        return None
    if isinstance(as_of, datetime):
        return as_of.date()
    if isinstance(as_of, date):
        return as_of
    text = str(as_of).strip()
    if not text:
        return None
    if "T" in text:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    return date.fromisoformat(text[:10])


def _parse_bound(raw: Any) -> date | None:
    if raw is None or raw == "":
        return None
    return _parse_as_of(raw)


def _in_force(asg: dict[str, Any], as_of: date | None) -> bool:
    if str(asg.get("approval_status") or "") != "approved":
        return False
    if as_of is None:
        return True
    start = _parse_bound(asg.get("valid_from"))
    end = _parse_bound(asg.get("valid_to"))
    if start is not None and as_of < start:
        return False
    if end is not None and as_of > end:
        return False
    return True


def _assignment_id(asg: dict[str, Any]) -> str:
    return str(asg.get("assignment_id") or asg.get("policy_binding_id") or "")


def _assignment_target(asg: dict[str, Any]) -> str:
    return str(
        asg.get("target_element_ref")
        or asg.get("classified_element_ref")
        or asg.get("policy_target_ref")
        or ""
    )


def _assignment_scope(asg: dict[str, Any]) -> str:
    scope = asg.get("assignment_scope")
    if scope in ("element", "subtree"):
        return str(scope)
    return "element"


def _collect_assignments(
    body_data: dict[str, Any],
    assignments: dict[str, list[Any]] | None,
) -> list[tuple[str, dict[str, Any]]]:
    """Return (family_name, assignment_dict) pairs."""
    source = assignments if assignments is not None else body_data
    out: list[tuple[str, dict[str, Any]]] = []
    for key, family in _ASSIGNMENT_COLLECTIONS:
        for item in source.get(key) or []:
            if isinstance(item, dict):
                out.append((family, item))
    return out


def _build_parent_map(
    body_data: dict[str, Any],
) -> tuple[dict[str, str | None], set[str]]:
    """Map element_id -> parent element_id; set of all cascade element ids."""
    parent_of: dict[str, str | None] = {}
    ids: set[str] = set()
    for el, level, parent, parent_level in iter_cascade_nodes(body_data):
        eid = _element_id(el, level)
        ids.add(eid)
        if parent is None:
            parent_of[eid] = None
        else:
            parent_of[eid] = _element_id(parent, parent_level or "ModelPackage")
    return parent_of, ids


def _ancestor_chain(element_id: str, parent_of: dict[str, str | None]) -> list[str]:
    """Self first, then ancestors toward package root."""
    chain: list[str] = []
    cur: str | None = element_id
    seen: set[str] = set()
    while cur is not None and cur not in seen:
        seen.add(cur)
        chain.append(cur)
        cur = parent_of.get(cur)
    return chain


def _covers(
    asg: dict[str, Any],
    element_id: str,
    parent_of: dict[str, str | None],
) -> int | None:
    """Return distance (0 = self) if assignment covers element, else None."""
    target = _assignment_target(asg)
    if not target:
        return None
    scope = _assignment_scope(asg)
    chain = _ancestor_chain(element_id, parent_of)
    if target not in chain:
        return None
    distance = chain.index(target)
    if scope == "element" and distance != 0:
        return None
    return distance


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
            layer="inline",
        )
    if slot in parent_eff:
        return parent_eff[slot]
    # Scalar inherit of "nothing"; list inherit of empty.
    default: Any = [] if family.cardinality is CascadeCardinality.LIST_REPLACE else None
    return SlotProvenance(
        value=default,
        source_element_id=None,
        level=level,
        layer="none",
    )


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


def _cascade_only(body_data: dict[str, Any]) -> dict[str, dict[str, SlotProvenance]]:
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
            parent_id = str(child.get("element_id") or child.get("name") or "")
            for nested in child.get(nested_key) or []:
                if not isinstance(nested, dict):
                    continue
                if nested_key == "nodes":
                    lk = str(nested.get("local_key") or "")
                    node_for_resolve = dict(nested)
                    if parent_id and lk:
                        node_for_resolve["element_id"] = f"{parent_id}#{lk}"
                    _resolve_element(
                        node_for_resolve,
                        level=nested_level,
                        parent_eff=child_eff,
                        out=out,
                    )
                else:
                    _resolve_element(
                        nested,
                        level=nested_level,
                        parent_eff=child_eff,
                        out=out,
                    )
    return out


def _scalar_value(asg: dict[str, Any], slot: str) -> Any:
    return asg.get(slot)


def _apply_assignments(
    cascade: dict[str, dict[str, SlotProvenance]],
    *,
    body_data: dict[str, Any],
    as_of: date | None,
    raw_assignments: list[tuple[str, dict[str, Any]]],
    parent_of: dict[str, str | None],
    element_ids: set[str],
) -> tuple[dict[str, dict[str, SlotProvenance]], list[GovernanceFinding]]:
    findings: list[GovernanceFinding] = []
    in_force: list[tuple[str, dict[str, Any]]] = []
    for family, asg in raw_assignments:
        aid = _assignment_id(asg)
        target = _assignment_target(asg)
        if target and target not in element_ids:
            findings.append(
                GovernanceFinding(
                    code="dangling_target",
                    severity="error",
                    message=f"assignment {aid or '?'} target {target} not in package",
                    assignment_ids=(aid,) if aid else (),
                    element_id=target,
                )
            )
        if _in_force(asg, as_of):
            in_force.append((family, asg))

    result: dict[str, dict[str, SlotProvenance]] = {
        eid: dict(slots) for eid, slots in cascade.items()
    }
    levels = {
        _element_id(el, level): level for el, level, _p, _pl in iter_cascade_nodes(body_data)
    }

    for eid, slots in list(result.items()):
        level = levels.get(eid, "ModelPackage")

        # --- scalar families: ownership + classification ---
        for family in (OWNERSHIP_FAMILY, CLASSIFICATION_FAMILY):
            for slot in family.slots:
                candidates: list[tuple[int, dict[str, Any], Any]] = []
                for fam_name, asg in in_force:
                    if fam_name != family.name:
                        continue
                    if slot not in asg:
                        continue
                    dist = _covers(asg, eid, parent_of)
                    if dist is None:
                        continue
                    candidates.append((dist, asg, asg.get(slot)))
                if not candidates:
                    continue
                min_dist = min(c[0] for c in candidates)
                nearest = [c for c in candidates if c[0] == min_dist]
                values = {c[2] for c in nearest}
                if len(values) > 1:
                    ids = tuple(_assignment_id(c[1]) for c in nearest if _assignment_id(c[1]))
                    findings.append(
                        GovernanceFinding(
                            code="conflicting_assignments",
                            severity="error",
                            message=(
                                f"conflicting {family.name}.{slot} assignments "
                                f"on nearest target for {eid}"
                            ),
                            assignment_ids=ids,
                            element_id=eid,
                            slot=slot,
                        )
                    )
                    continue
                _dist, winner, value = nearest[0]
                result[eid][slot] = SlotProvenance(
                    value=value,
                    source_element_id=_assignment_target(winner),
                    level=level,
                    layer="assignment",
                    assignment_id=_assignment_id(winner) or None,
                )

        # --- policies ---
        policy_candidates: list[tuple[int, dict[str, Any]]] = []
        for fam_name, asg in in_force:
            if fam_name != "policies":
                continue
            dist = _covers(asg, eid, parent_of)
            if dist is None:
                continue
            policy_candidates.append((dist, asg))
        if policy_candidates:
            min_dist = min(c[0] for c in policy_candidates)
            nearest_bindings = [c[1] for c in policy_candidates if c[0] == min_dist]
            replaces = [
                b
                for b in nearest_bindings
                if str(b.get("binding_effect") or "replace") == "replace"
            ]
            adds = [
                b
                for b in nearest_bindings
                if str(b.get("binding_effect") or "replace") == "add"
            ]
            # ADR-049 D2 / Wave D4: multiple replace bindings at same nearest
            # target with different policy_ref sets -> conflicting_assignments.
            if len(replaces) > 1:
                replace_sets = {
                    frozenset(filter(None, [b.get("policy_ref")]))
                    for b in replaces
                }
                if len(replace_sets) > 1:
                    ids = tuple(
                        _assignment_id(b) for b in replaces if _assignment_id(b)
                    )
                    findings.append(
                        GovernanceFinding(
                            code="conflicting_assignments",
                            severity="error",
                            message=(
                                f"conflicting policy replace bindings "
                                f"on nearest target for {eid}"
                            ),
                            assignment_ids=ids,
                            element_id=eid,
                            slot="policy_refs",
                        )
                    )
                    continue
            if replaces:
                base: list[Any] = []
                for b in replaces:
                    ref = b.get("policy_ref")
                    if ref is not None and ref not in base:
                        base.append(ref)
            else:
                cascade_val = cascade[eid]["policy_refs"].value
                base = list(cascade_val) if isinstance(cascade_val, list) else []
            for b in adds:
                ref = b.get("policy_ref")
                if ref is not None and ref not in base:
                    base.append(ref)
            primary = (replaces or adds or nearest_bindings)[0]
            result[eid]["policy_refs"] = SlotProvenance(
                value=base,
                source_element_id=_assignment_target(primary),
                level=level,
                layer="assignment",
                assignment_id=_assignment_id(primary) or None,
            )

    return result, findings


def resolve_governed(
    body_data: dict[str, Any],
    *,
    as_of: date | datetime | str | None = None,
    assignments: dict[str, list[Any]] | None = None,
) -> dict[str, dict[str, SlotProvenance]]:
    """Resolve effective governed slots for every cascade node in the package.

    When no assignments apply, behaviour matches ADR-023 (inline cascade only).
    Approved assignments override per ADR-049. Returns
    ``{element_id: {slot: SlotProvenance}}``.
    """
    cascade = _cascade_only(body_data)
    raw = _collect_assignments(body_data, assignments)
    if not raw:
        return cascade
    parent_of, element_ids = _build_parent_map(body_data)
    merged, _findings = _apply_assignments(
        cascade,
        body_data=body_data,
        as_of=_parse_as_of(as_of),
        raw_assignments=raw,
        parent_of=parent_of,
        element_ids=element_ids,
    )
    return merged


def diagnose_governance(
    body_data: dict[str, Any],
    *,
    as_of: date | datetime | str | None = None,
    assignments: dict[str, list[Any]] | None = None,
) -> list[GovernanceFinding]:
    """Return assignment diagnostics (conflicts, dangling targets, shadowed defaults)."""
    cascade = _cascade_only(body_data)
    raw = _collect_assignments(body_data, assignments)
    parent_of, element_ids = _build_parent_map(body_data)
    merged, findings = _apply_assignments(
        cascade,
        body_data=body_data,
        as_of=_parse_as_of(as_of),
        raw_assignments=raw,
        parent_of=parent_of,
        element_ids=element_ids,
    )

    for el, level, _parent, _pl in iter_cascade_nodes(body_data):
        eid = _element_id(el, level)
        for slot in GOVERNED_SLOTS:
            if not _slot_declared(el, slot):
                continue
            prov = merged.get(eid, {}).get(slot)
            if prov is None or prov.layer != "assignment":
                continue
            if el.get(slot) != prov.value:
                findings.append(
                    GovernanceFinding(
                        code="shadowed_default",
                        severity="warning",
                        message=(
                            f"inline {slot} on {eid} shadowed by assignment "
                            f"{prov.assignment_id or '?'}"
                        ),
                        assignment_ids=(prov.assignment_id,) if prov.assignment_id else (),
                        element_id=eid,
                        slot=slot,
                    )
                )
    return findings


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
            parent_id = str(child.get("element_id") or child.get("name") or "")
            for nested in child.get(nested_key) or []:
                if not isinstance(nested, dict):
                    continue
                if nested_key == "nodes":
                    lk = str(nested.get("local_key") or "")
                    node_view = dict(nested)
                    if parent_id and lk:
                        node_view["element_id"] = f"{parent_id}#{lk}"
                    nodes.append((node_view, nested_level, child, level))
                else:
                    nodes.append((nested, nested_level, child, level))
    return nodes


def find_redundant_overrides(
    body_data: dict[str, Any],
    *,
    as_of: date | datetime | str | None = None,
    assignments: dict[str, list[Any]] | None = None,
) -> list[tuple[str, str, Any, str]]:
    """Return (element_id, slot, value, parent_element_id) for redundant overrides.

    A declared value equal to the parent's *effective* value is redundant.
    Uses merged resolution (assignments over cascade) when assignments exist.
    """
    resolved = resolve_governed(body_data, as_of=as_of, assignments=assignments)
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
