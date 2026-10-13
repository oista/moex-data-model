"""Governance assignment override layer (ADR-049).

Preferred import path for assignment resolution. Containment cascade (ADR-023)
lives in ``cascade.py``; this module applies approved assignments over that
cascade and returns diagnostics.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from moex_dams.rules.cascade import (
    CLASSIFICATION_FAMILY,
    GOVERNED_SLOTS,
    OWNERSHIP_FAMILY,
    SlotProvenance,
    _cascade_only,
    _element_id,
    _parse_as_of,
    _slot_declared,
    iter_cascade_nodes,
)

_ASSIGNMENT_COLLECTIONS: tuple[tuple[str, str], ...] = (
    ("classification_assignments", "classification"),
    ("policy_bindings", "policies"),
    ("ownership_assignments", "ownership"),
)


@dataclass(frozen=True)
class GovernanceFinding:
    """Diagnostic from assignment resolution (ADR-049)."""

    code: str  # conflicting_assignments | dangling_target | shadowed_default
    severity: str  # error | warning
    message: str
    assignment_ids: tuple[str, ...] = ()
    element_id: str | None = None
    slot: str | None = None


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


__all__ = [
    "GovernanceFinding",
    "diagnose_governance",
    "resolve_governed",
]
