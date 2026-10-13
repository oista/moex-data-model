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
    seen: dict[str, str] = {}
    dups: list[str] = []

    def walk(obj: Any, path: str) -> None:
        if isinstance(obj, dict):
            eid = obj.get("element_id")
            if eid is not None and str(eid).strip():
                key = str(eid)
                if key in seen:
                    dups.append(key)
                else:
                    seen[key] = path
            for k, v in obj.items():
                if k == "element_id":
                    continue
                walk(v, f"{path}/{k}" if path else k)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                walk(item, f"{path}[{i}]")

    walk(data, "")
    out: list[Diagnostic] = []
    for eid in sorted(set(dups)):
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
    """INV-053: Relationship ends resolve to ConceptualEntity or LogicalEntity."""
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
    # Known non-entity ids in-package (attributes, tech, etc.)
    forbidden: set[str] = set()
    for ent in data.get("logical_entities") or []:
        if not isinstance(ent, dict):
            continue
        for a in ent.get("attributes") or []:
            if isinstance(a, dict) and a.get("element_id"):
                forbidden.add(str(a["element_id"]))
    for key in (
        "data_carriers",
        "access_points",
        "data_containers",
        "execution_assets",
    ):
        for el in data.get(key) or []:
            if isinstance(el, dict) and el.get("element_id"):
                forbidden.add(str(el["element_id"]))

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
            if ref_s in forbidden or ref_s:  # unresolved or wrong kind
                # External/cross-package refs: only fail when clearly wrong kind
                if ref_s in forbidden or (
                    ref_s.startswith("dams:") and ref_s not in allowed
                ):
                    out.append(
                        _diag(
                            code="DAMS-INV-053",
                            invariant_id="INV-053",
                            message=(
                                f'Relationship "{rid}" {slot}={ref_s!r} must resolve '
                                "to ConceptualEntity or LogicalEntity."
                            ),
                            subject=rid or None,
                            remediation=(
                                "Point relationship ends at conceptual or logical "
                                "entities. INV-053."
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
    return out
