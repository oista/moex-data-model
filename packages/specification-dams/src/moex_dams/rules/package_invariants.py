"""Wave C package-level L2 invariants (INV-042..053) for audit gap closure."""

from __future__ import annotations

from typing import Any

from moex_modeling import (
    ConformancePhase,
    Diagnostic,
    DiagnosticDetail,
    DiagnosticSeverity,
)

from moex_dams.mappings.iter_mappings import iter_mappings
from moex_dams.rules.repository_invariants import collect_element_ids


def _diag(
    *,
    code: str,
    invariant_id: str,
    message: str,
    subject: str | None,
    remediation: str | None = None,
    severity: DiagnosticSeverity = DiagnosticSeverity.ERROR,
) -> Diagnostic:
    details: list[DiagnosticDetail] = [
        DiagnosticDetail(detail_key="finding", detail_value=message),
        DiagnosticDetail(detail_key="invariant_id", detail_value=invariant_id),
    ]
    parts = [message]
    if remediation:
        parts.append(f"Remediation: {remediation}")
        details.append(
            DiagnosticDetail(detail_key="remediation", detail_value=remediation)
        )
    return Diagnostic(
        diagnostic_code=code,
        severity=severity,
        diagnostic_message=" ".join(parts),
        conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
        subject_ref=subject,
        diagnostic_details=tuple(details),
    )


def check_solution_scope_refs(data: dict[str, Any]) -> list[Diagnostic]:
    """INV-042: implementation_scope=solution requires solution_ref + conceptual impl."""
    if str(data.get("implementation_scope") or "") != "solution":
        return []
    subject = str(data.get("element_id") or data.get("name") or "")
    out: list[Diagnostic] = []
    if not data.get("solution_ref"):
        out.append(
            _diag(
                code="DAMS-INV-042",
                invariant_id="INV-042",
                message="solution scope requires solution_ref",
                subject=subject or None,
                remediation="Set solution_ref on the ModelPackage. INV-042.",
            )
        )
    if not data.get("conceptual_implementation_ref"):
        out.append(
            _diag(
                code="DAMS-INV-042",
                invariant_id="INV-042",
                message="solution scope requires conceptual_implementation_ref",
                subject=subject or None,
                remediation="Set conceptual_implementation_ref. INV-042.",
            )
        )
    return out


def check_attribute_cardinality_bounds(data: dict[str, Any]) -> list[Diagnostic]:
    """INV-045: LogicalAttribute maximum_cardinality >= minimum_cardinality."""
    out: list[Diagnostic] = []
    for ent in data.get("logical_entities") or []:
        if not isinstance(ent, dict):
            continue
        for attr in ent.get("attributes") or []:
            if not isinstance(attr, dict):
                continue
            mn, mx = attr.get("minimum_cardinality"), attr.get("maximum_cardinality")
            if mn is None or mx is None:
                continue
            try:
                mn_i, mx_i = int(mn), int(mx)
            except (TypeError, ValueError):
                continue
            if mx_i < mn_i:
                aid = str(attr.get("element_id") or "")
                out.append(
                    _diag(
                        code="DAMS-INV-045",
                        invariant_id="INV-045",
                        message=(
                            f'LogicalAttribute "{aid}" has maximum_cardinality={mx_i} '
                            f"< minimum_cardinality={mn_i}."
                        ),
                        subject=aid or None,
                        remediation="Ensure maximum_cardinality >= minimum_cardinality. INV-045.",
                    )
                )
    return out


def check_parent_concept_cycles(data: dict[str, Any]) -> list[Diagnostic]:
    """INV-046: ConceptualEntity.parent_concept_ref must not form a cycle."""
    concepts: dict[str, dict[str, Any]] = {}
    for el in data.get("conceptual_entities") or []:
        if isinstance(el, dict) and el.get("element_id"):
            concepts[str(el["element_id"])] = el
    out: list[Diagnostic] = []
    for eid, el in concepts.items():
        parent = el.get("parent_concept_ref")
        if not parent:
            continue
        parent_s = str(parent)
        if parent_s == eid:
            out.append(
                _diag(
                    code="DAMS-INV-046",
                    invariant_id="INV-046",
                    message=f'ConceptualEntity "{eid}" parent_concept_ref is a self-reference.',
                    subject=eid,
                    remediation="Point parent_concept_ref to a distinct ancestor. INV-046.",
                )
            )
            continue
        seen: set[str] = {eid}
        cur = parent_s
        while cur:
            if cur in seen:
                out.append(
                    _diag(
                        code="DAMS-INV-046",
                        invariant_id="INV-046",
                        message=(
                            f'ConceptualEntity "{eid}" participates in a '
                            f"parent_concept_ref cycle (reached {cur!r})."
                        ),
                        subject=eid,
                        remediation="Break the parent_concept_ref cycle. INV-046.",
                    )
                )
                break
            seen.add(cur)
            nxt = concepts.get(cur)
            if not nxt:
                break
            pref = nxt.get("parent_concept_ref")
            cur = str(pref) if pref else ""
    return out


def check_selection_attribute_closure(data: dict[str, Any]) -> list[Diagnostic]:
    """INV-048: selected_attributes must belong to the selected logical entity."""
    attr_by_entity: dict[str, set[str]] = {}
    for ent in data.get("logical_entities") or []:
        if not isinstance(ent, dict) or not ent.get("element_id"):
            continue
        eid = str(ent["element_id"])
        attr_by_entity[eid] = {
            str(a["element_id"])
            for a in (ent.get("attributes") or [])
            if isinstance(a, dict) and a.get("element_id")
        }

    out: list[Diagnostic] = []
    selections: list[dict[str, Any]] = []
    for binding in data.get("data_model_bindings") or []:
        if isinstance(binding, dict):
            for sel in binding.get("selections") or []:
                if isinstance(sel, dict):
                    selections.append(sel)
    for sel in data.get("selections") or []:
        if isinstance(sel, dict):
            selections.append(sel)

    for sel in selections:
        for sent in sel.get("selected_entities") or []:
            if not isinstance(sent, dict):
                continue
            lref = str(sent.get("logical_entity_ref") or "")
            allowed = attr_by_entity.get(lref, set())
            for sattr in sent.get("selected_attributes") or []:
                if not isinstance(sattr, dict):
                    continue
                aref = str(sattr.get("logical_attribute_ref") or "")
                if not aref:
                    continue
                if lref and aref not in allowed:
                    sid = str(sattr.get("element_id") or aref)
                    out.append(
                        _diag(
                            code="DAMS-INV-048",
                            invariant_id="INV-048",
                            message=(
                                f'SelectedAttribute "{sid}" logical_attribute_ref '
                                f"{aref!r} is not among attributes of selected "
                                f"logical entity {lref!r}."
                            ),
                            subject=sid,
                            remediation=(
                                "Select only attributes of the SelectedEntity's "
                                "logical_entity_ref. INV-048."
                            ),
                        )
                    )
    return out


def check_binding_compatibility(data: dict[str, Any]) -> list[Diagnostic]:
    """INV-049: non-none compatibility_mode requires compatibility_baseline_ref."""
    out: list[Diagnostic] = []
    bindings = list(data.get("data_model_bindings") or [])
    # Single binding document shape
    if data.get("compatibility_mode") is not None and "data_model_bindings" not in data:
        bindings.append(data)
    for binding in bindings:
        if not isinstance(binding, dict):
            continue
        mode = str(binding.get("compatibility_mode") or "").strip()
        if not mode or mode == "none":
            continue
        baseline = str(binding.get("compatibility_baseline_ref") or "").strip()
        if not baseline:
            bid = str(binding.get("element_id") or binding.get("name") or "")
            out.append(
                _diag(
                    code="DAMS-INV-049",
                    invariant_id="INV-049",
                    message=(
                        f'DataModelBinding "{bid}" has compatibility_mode={mode!r} '
                        "but no compatibility_baseline_ref."
                    ),
                    subject=bid or None,
                    remediation=(
                        "Set compatibility_baseline_ref or use compatibility_mode=none. "
                        "INV-049."
                    ),
                )
            )
    return out


def check_package_element_id_uniqueness(data: dict[str, Any]) -> list[Diagnostic]:
    """INV-050: element_id values must be unique within a ModelPackage document."""
    locations = collect_element_ids(data)
    out: list[Diagnostic] = []
    for eid in sorted(eid for eid, paths in locations.items() if len(paths) > 1):
        out.append(
            _diag(
                code="DAMS-INV-050",
                invariant_id="INV-050",
                message=f"Duplicate element_id {eid!r} within package document.",
                subject=eid,
                remediation="Make every element_id unique in the package. INV-050.",
            )
        )
    return out


_KNOWN_MAPPING_CARDINALITIES = frozenset(
    {"one_to_one", "one_to_many", "many_to_one", "many_to_many"}
)


def check_mapping_cardinality_consistency(data: dict[str, Any]) -> list[Diagnostic]:
    """INV-051: mapping_cardinality agrees with source/target multiset sizes."""
    out: list[Diagnostic] = []
    for m in iter_mappings(data):
        card = str(m.get("mapping_cardinality") or "")
        if not card:
            continue
        n_src = len(m.get("source_refs") or [])
        n_tgt = len(m.get("target_refs") or [])
        mid = str(m.get("element_id") or "")
        if card not in _KNOWN_MAPPING_CARDINALITIES:
            out.append(
                _diag(
                    code="DAMS-INV-051",
                    invariant_id="INV-051",
                    message=(
                        f'Mapping "{mid}" has unknown mapping_cardinality={card!r} '
                        f"(expected one of {sorted(_KNOWN_MAPPING_CARDINALITIES)})."
                    ),
                    subject=mid or None,
                    remediation=(
                        "Use MappingCardinalityEnum: one_to_one, one_to_many, "
                        "many_to_one, or many_to_many. INV-051."
                    ),
                )
            )
            continue
        ok = True
        if card == "one_to_one" and not (n_src == 1 and n_tgt == 1):
            ok = False
        elif card == "one_to_many" and not (n_src == 1 and n_tgt >= 1):
            ok = False
        elif card == "many_to_one" and not (n_src >= 1 and n_tgt == 1):
            ok = False
        elif card == "many_to_many" and not (n_src >= 1 and n_tgt >= 1):
            ok = False
        if not ok:
            out.append(
                _diag(
                    code="DAMS-INV-051",
                    invariant_id="INV-051",
                    message=(
                        f'Mapping "{mid}" mapping_cardinality={card!r} inconsistent '
                        f"with |source_refs|={n_src}, |target_refs|={n_tgt}."
                    ),
                    subject=mid or None,
                    remediation=(
                        "Align mapping_cardinality with endpoint counts, or adjust "
                        "refs. INV-051."
                    ),
                )
            )
    return out


def check_relationship_endpoint_kinds(data: dict[str, Any]) -> list[Diagnostic]:
    """INV-053: Relationship ends resolve to in-package Conceptual/Logical entity.

    Ends must be ConceptualEntity or LogicalEntity **in the same package
    document**. Wrong kinds (attributes, technical assets), unresolved
    ``dams:`` ids, cross-package entity ids, and non-``dams:`` refs that are
    not local entities all fail.
    """
    conceptual = {
        str(e["element_id"])
        for e in (data.get("conceptual_entities") or [])
        if isinstance(e, dict) and e.get("element_id")
    }
    logical = {
        str(e["element_id"])
        for e in (data.get("logical_entities") or [])
        if isinstance(e, dict) and e.get("element_id")
    }
    allowed = conceptual | logical

    out: list[Diagnostic] = []
    for rel in data.get("relationships") or []:
        if not isinstance(rel, dict):
            continue
        rid = str(rel.get("element_id") or "")
        for slot in ("source_entity_ref", "target_entity_ref"):
            ref = rel.get(slot)
            if not ref:
                continue
            ref_s = str(ref)
            if ref_s in allowed:
                continue
            out.append(
                _diag(
                    code="DAMS-INV-053",
                    invariant_id="INV-053",
                    message=(
                        f'Relationship "{rid}" {slot}={ref_s!r} must resolve '
                        "to a ConceptualEntity or LogicalEntity in this package "
                        "(not attributes, technical assets, cross-package, or "
                        "non-entity refs)."
                    ),
                    subject=rid or None,
                    remediation=(
                        "Point relationship ends at conceptual or logical "
                        "entities authored in the same package document. INV-053."
                    ),
                )
            )
    return out


_APPROVED_STATUSES = frozenset({"approved"})
_REJECTED_STATUSES = frozenset({"rejected"})


def _norm_iri(value: object) -> str:
    return str(value or "").strip().rstrip("/")


def check_alignment_dual_path_consistency(data: dict[str, Any]) -> list[Diagnostic]:
    """INV-057: ExternalClassRef ↔ AlignsWithMapping must not contradict (ADR-053)."""
    ecr_by_pair: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for ent in data.get("conceptual_entities") or []:
        if not isinstance(ent, dict):
            continue
        concept_id = _norm_iri(ent.get("element_id"))
        if not concept_id:
            continue
        for ecr in ent.get("external_class_refs") or []:
            if not isinstance(ecr, dict):
                continue
            target = _norm_iri(ecr.get("target_ref"))
            if not target:
                continue
            ecr_by_pair.setdefault((concept_id, target), []).append(ecr)

    out: list[Diagnostic] = []
    for mapping in iter_mappings(data):
        if str(mapping.get("mapping_type") or "") != "aligns_with":
            continue
        sources = [
            _norm_iri(s) for s in (mapping.get("source_refs") or []) if _norm_iri(s)
        ]
        targets = [
            _norm_iri(t) for t in (mapping.get("target_refs") or []) if _norm_iri(t)
        ]
        mid = str(mapping.get("element_id") or "")
        map_conf = mapping.get("confidence")
        map_approval = str(mapping.get("approval_status") or "").strip().lower()
        for concept_id in sources:
            for target in targets:
                peers = ecr_by_pair.get((concept_id, target)) or []
                if not peers:
                    continue
                for ecr in peers:
                    ecr_conf = ecr.get("confidence")
                    if map_conf is not None and ecr_conf is not None:
                        try:
                            if abs(float(map_conf) - float(ecr_conf)) > 1e-9:
                                out.append(
                                    _diag(
                                        code="DAMS-INV-057",
                                        invariant_id="INV-057",
                                        message=(
                                            f'AlignsWithMapping "{mid}" and ExternalClassRef '
                                            f"for {concept_id} → {target} disagree on confidence "
                                            f"({map_conf} vs {ecr_conf})."
                                        ),
                                        subject=mid or concept_id,
                                        remediation=(
                                            "Align confidence on both paths or drop one. "
                                            "INV-057 / ADR-053."
                                        ),
                                    )
                                )
                        except (TypeError, ValueError):
                            pass
                    ecr_approval = str(ecr.get("approval_status") or "").strip().lower()
                    if (
                        map_approval in _APPROVED_STATUSES
                        and ecr_approval in _REJECTED_STATUSES
                    ) or (
                        map_approval in _REJECTED_STATUSES
                        and ecr_approval in _APPROVED_STATUSES
                    ):
                        out.append(
                            _diag(
                                code="DAMS-INV-057",
                                invariant_id="INV-057",
                                message=(
                                    f'AlignsWithMapping "{mid}" and ExternalClassRef '
                                    f"for {concept_id} → {target} disagree on approval_status "
                                    f"({map_approval!r} vs {ecr_approval!r})."
                                ),
                                subject=mid or concept_id,
                                remediation=(
                                    "Align approval_status on both paths or drop one. "
                                    "INV-057 / ADR-053."
                                ),
                            )
                        )
    return out


def check_package_invariants(data: dict[str, Any]) -> list[Diagnostic]:
    """Run Wave C package invariants that live in this module."""
    out: list[Diagnostic] = []
    out.extend(check_solution_scope_refs(data))
    out.extend(check_attribute_cardinality_bounds(data))
    out.extend(check_parent_concept_cycles(data))
    out.extend(check_selection_attribute_closure(data))
    out.extend(check_binding_compatibility(data))
    out.extend(check_package_element_id_uniqueness(data))
    out.extend(check_mapping_cardinality_consistency(data))
    out.extend(check_relationship_endpoint_kinds(data))
    out.extend(check_alignment_dual_path_consistency(data))
    return out
