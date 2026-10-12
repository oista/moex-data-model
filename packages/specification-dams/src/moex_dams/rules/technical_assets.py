"""TechnicalAsset semantic checks (Variant B collections, ADR-031/032/033)."""

from __future__ import annotations

import re
from typing import Any

from moex_modeling import (
    ConformancePhase,
    Diagnostic,
    DiagnosticDetail,
    DiagnosticSeverity,
)

from moex_dams.mappings.iter_mappings import iter_mappings
from moex_dams.rules.data_structure import check_data_structures

TECHNICAL_COLLECTIONS: tuple[tuple[str, str], ...] = (
    ("data_carriers", "DataCarrier"),
    ("access_points", "AccessPoint"),
    ("data_containers", "DataContainer"),
    ("execution_assets", "ExecutionAsset"),
)

DATA_CARRIER_KINDS = frozenset(
    {
        "relational_table",
        "relational_view",
        "file",
        "dataset",
        "stream_topic",
        "stream_queue",
        "in_memory",
        "api_resource",
        "other",
    }
)

ACCESS_POINT_KINDS = frozenset({"interface", "operation", "channel"})

DATA_CONTAINER_KINDS = frozenset(
    {"database", "schema", "bucket", "broker", "directory", "cluster"}
)

EXECUTION_ASSET_KINDS = frozenset({"pipeline", "job"})

KIND_ALLOWLIST_BY_CLASS: dict[str, frozenset[str]] = {
    "DataCarrier": DATA_CARRIER_KINDS,
    "AccessPoint": ACCESS_POINT_KINDS,
    "DataContainer": DATA_CONTAINER_KINDS,
    "ExecutionAsset": EXECUTION_ASSET_KINDS,
}

DIRECTION_FORBIDDEN_CLASSES = frozenset({"DataContainer", "ExecutionAsset"})


def iter_technical_assets(
    data: dict[str, Any],
) -> list[tuple[dict[str, Any], str, str]]:
    """Yield (element, subject_ref, class_name) for all four collections."""
    out: list[tuple[dict[str, Any], str, str]] = []
    for key, class_name in TECHNICAL_COLLECTIONS:
        for item in data.get(key) or []:
            if isinstance(item, dict):
                sid = str(item.get("element_id") or item.get("name") or "")
                out.append((item, sid, class_name))
    return out


def technical_asset_ids_by_class(data: dict[str, Any]) -> dict[str, set[str]]:
    """Map class name → set of element_ids present in that collection."""
    out: dict[str, set[str]] = {c: set() for _, c in TECHNICAL_COLLECTIONS}
    for el, sid, class_name in iter_technical_assets(data):
        eid = str(el.get("element_id") or "")
        if eid:
            out[class_name].add(eid)
        elif sid:
            out[class_name].add(sid)
    return out


def _diag(
    *,
    code: str,
    message: str,
    subject: str | None,
    remediation: str | None = None,
    requirement_code: str | None = None,
    invariant_id: str | None = None,
    severity: DiagnosticSeverity = DiagnosticSeverity.ERROR,
) -> Diagnostic:
    details: list[DiagnosticDetail] = [
        DiagnosticDetail(detail_key="finding", detail_value=message)
    ]
    if invariant_id:
        details.append(
            DiagnosticDetail(detail_key="invariant_id", detail_value=str(invariant_id))
        )
    if requirement_code:
        details.append(
            DiagnosticDetail(
                detail_key="requirement_code",
                detail_value=str(requirement_code),
            )
        )
    if remediation:
        details.append(
            DiagnosticDetail(
                detail_key="remediation",
                detail_value=str(remediation),
            )
        )
    parts = [message]
    if remediation:
        parts.append(f"Remediation: {remediation}")
    return Diagnostic(
        diagnostic_code=code,
        severity=severity,
        diagnostic_message=" ".join(parts),
        conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
        subject_ref=subject,
        diagnostic_details=tuple(details),
    )


def check_parent_ref_cycles(data: dict[str, Any]) -> list[Diagnostic]:
    """Detect self-references and cycles in TechnicalAsset.parent_ref."""
    assets = {
        sid: el
        for el, sid, _ in iter_technical_assets(data)
        if sid
    }
    out: list[Diagnostic] = []
    for sid, el in assets.items():
        parent = el.get("parent_ref")
        if not parent:
            continue
        parent_s = str(parent)
        if parent_s == sid:
            out.append(
                _diag(
                    code="DAMS-REQ-PDM-006.c1",
                    message=f'TechnicalAsset "{sid}" parent_ref is a self-reference.',
                    subject=sid,
                    remediation="Remove parent_ref or point it to a distinct ancestor.",
                    requirement_code="PDM-006",
                )
            )
            continue
        seen: set[str] = {sid}
        cur = parent_s
        while cur:
            if cur in seen:
                out.append(
                    _diag(
                        code="DAMS-REQ-PDM-006.c2",
                        message=(
                            f'TechnicalAsset "{sid}" participates in a parent_ref cycle '
                            f"(reached {cur!r})."
                        ),
                        subject=sid,
                        remediation="Break the parent_ref cycle in the containment hierarchy.",
                        requirement_code="PDM-006",
                    )
                )
                break
            seen.add(cur)
            nxt = assets.get(cur)
            if not nxt:
                break
            pref = nxt.get("parent_ref")
            cur = str(pref) if pref else ""
    return out


def check_unique_asset_keys(data: dict[str, Any]) -> list[Diagnostic]:
    """PRIMARY unique_keys: (asset_namespace, qualified_name) across all collections."""
    seen: dict[tuple[str, str], str] = {}
    out: list[Diagnostic] = []
    for el, sid, _class_name in iter_technical_assets(data):
        ns = str(el.get("asset_namespace") or "").strip()
        qn = str(el.get("qualified_name") or "").strip()
        if not ns or not qn:
            continue
        key = (ns, qn)
        if key in seen:
            out.append(
                _diag(
                    code="DAMS-REQ-PDM-005.c1",
                    message=(
                        f'TechnicalAsset "{sid}" duplicates (asset_namespace, '
                        f'qualified_name)=({ns!r}, {qn!r}) already used by "{seen[key]}".'
                    ),
                    subject=sid,
                    remediation=(
                        "Ensure asset_namespace + qualified_name is unique across "
                        "data_carriers, access_points, data_containers, and execution_assets."
                    ),
                    requirement_code="PDM-005",
                )
            )
        else:
            seen[key] = sid
    return out


def check_asset_kind_allowlists(data: dict[str, Any]) -> list[Diagnostic]:
    """asset_kind must belong to the enum of the concrete subclass collection."""
    out: list[Diagnostic] = []
    for el, sid, class_name in iter_technical_assets(data):
        kind = str(el.get("asset_kind") or "")
        allow = KIND_ALLOWLIST_BY_CLASS[class_name]
        if not kind:
            continue
        if kind not in allow:
            out.append(
                _diag(
                    code="DAMS-REQ-PDM-007.c1",
                    message=(
                        f'{class_name} "{sid}" has asset_kind {kind!r} not allowed '
                        f"for this subclass."
                    ),
                    subject=sid,
                    remediation=f"Use one of: {', '.join(sorted(allow))}.",
                    requirement_code="PDM-007",
                )
            )
    return out


def check_direction_forbidden(data: dict[str, Any]) -> list[Diagnostic]:
    """INV-018: direction is forbidden on DataContainer and ExecutionAsset (PDM-008).

    Example error::

        DataContainer \"dams:container/x/db\" must not declare direction (got 'inbound').
        Remediation: Remove direction; it is only for DataCarrier/AccessPoint. INV-018.
    """
    out: list[Diagnostic] = []
    for el, sid, class_name in iter_technical_assets(data):
        if class_name not in DIRECTION_FORBIDDEN_CLASSES:
            continue
        if el.get("direction") is not None and str(el.get("direction") or "").strip():
            out.append(
                _diag(
                    code="DAMS-REQ-PDM-008.c1",
                    invariant_id="INV-018",
                    message=(
                        f'{class_name} "{sid}" must not declare direction '
                        f"(got {el.get('direction')!r})."
                    ),
                    subject=sid,
                    remediation=(
                        "Remove direction; it is only for DataCarrier/AccessPoint. INV-018."
                    ),
                    requirement_code="PDM-008",
                )
            )
    return out


_SCHEMA_NODE_REF_RE = re.compile(r"^dams:structure/.+#.+$")
_HTTP_IRI_RE = re.compile(r"^https?://", re.IGNORECASE)


def check_mapping_endpoint_types(data: dict[str, Any]) -> list[Diagnostic]:
    """Direction-aware Mapping endpoint kinds (INV-033..036 / PDM-009).

    - entity_physical: source ⊆ DataCarrier (exactly 1), target ⊆ LogicalEntity (exactly 1)
    - field_mapping: source ⊆ LogicalAttribute, target SchemaNodeRef pattern + resolve
    - realizes: source ⊆ LogicalEntity|ConceptualEntity, target ⊆ ConceptualEntity (local)
      or not a known non-concept local id (external conceptual ok)
    - aligns_with: exactly one ConceptualEntity source; target http(s) IRIs
    """
    logical_ids = {
        str(e.get("element_id"))
        for e in (data.get("logical_entities") or [])
        if isinstance(e, dict) and e.get("element_id")
    }
    conceptual_ids = {
        str(e.get("element_id"))
        for e in (data.get("conceptual_entities") or [])
        if isinstance(e, dict) and e.get("element_id")
    }
    attr_ids: set[str] = set()
    for e in data.get("logical_entities") or []:
        if not isinstance(e, dict):
            continue
        for a in e.get("attributes") or []:
            if isinstance(a, dict) and a.get("element_id"):
                attr_ids.add(str(a["element_id"]))
    by_class = technical_asset_ids_by_class(data)
    carrier_ids = by_class["DataCarrier"]
    all_tech_ids = set().union(*by_class.values()) if by_class else set()
    node_ids: set[str] = set()
    for s in data.get("data_structures") or []:
        if not isinstance(s, dict):
            continue
        sid = str(s.get("element_id") or "")
        for n in s.get("nodes") or []:
            if isinstance(n, dict) and n.get("local_key"):
                node_ids.add(f"{sid}#{n['local_key']}")

    known_non_concept = logical_ids | attr_ids | all_tech_ids | node_ids
    known_non_logical_source = attr_ids | all_tech_ids | node_ids

    out: list[Diagnostic] = []
    for m in iter_mappings(data):
        mtype = str(m.get("mapping_type") or "")
        mid = str(m.get("element_id") or m.get("name") or "")
        sources = [str(x) for x in (m.get("source_refs") or [])]
        targets = [str(x) for x in (m.get("target_refs") or [])]

        if mtype == "entity_physical":
            src_ok = len(sources) == 1 and sources[0] in carrier_ids
            tgt_ok = len(targets) == 1 and targets[0] in logical_ids
            if not (src_ok and tgt_ok):
                out.append(
                    _diag(
                        code="DAMS-REQ-PDM-009.c1",
                        invariant_id="INV-033",
                        message=(
                            f'Mapping "{mid}" entity_physical requires source_refs ⊆ '
                            "DataCarrier (exactly 1) and target_refs ⊆ LogicalEntity "
                            "(exactly 1)."
                        ),
                        subject=mid or None,
                        remediation=(
                            "Set source_refs to one DataCarrier id and target_refs to "
                            "one LogicalEntity id. INV-033."
                        ),
                        requirement_code="PDM-009",
                    )
                )
        elif mtype == "field_mapping":
            src_ok = bool(sources) and all(r in attr_ids for r in sources)
            tgt_pattern_ok = bool(targets) and all(
                _SCHEMA_NODE_REF_RE.match(r) for r in targets
            )
            tgt_resolved = bool(targets) and all(r in node_ids for r in targets)
            if not (src_ok and tgt_pattern_ok and tgt_resolved):
                out.append(
                    _diag(
                        code="DAMS-REQ-PDM-009.c2",
                        invariant_id="INV-034",
                        message=(
                            f'Mapping "{mid}" field_mapping requires source_refs ⊆ '
                            "LogicalAttribute and target_refs matching "
                            "dams:structure/…#… that resolve in data_structures.nodes."
                        ),
                        subject=mid or None,
                        remediation=(
                            "Use LogicalAttribute ids in source_refs and resolvable "
                            "SchemaNodeRef targets. INV-034."
                        ),
                        requirement_code="PDM-009",
                    )
                )
        elif mtype == "realizes":
            src_ok = bool(sources) and all(
                r in logical_ids or r in conceptual_ids for r in sources
            )
            # External conceptual targets allowed when not a known local non-concept.
            tgt_ok = bool(targets) and all(
                r in conceptual_ids or r not in known_non_concept for r in targets
            )
            if sources and any(r in known_non_logical_source for r in sources):
                src_ok = False
            if not (src_ok and tgt_ok):
                out.append(
                    _diag(
                        code="DAMS-INV-035",
                        invariant_id="INV-035",
                        message=(
                            f'Mapping "{mid}" realizes requires source_refs ⊆ '
                            "LogicalEntity|ConceptualEntity (min 1) and target_refs ⊆ "
                            "ConceptualEntity (min 1; external conceptual ids allowed)."
                        ),
                        subject=mid or None,
                        remediation=(
                            "Point source_refs at logical/conceptual entities and "
                            "target_refs at conceptual entities. INV-035."
                        ),
                        requirement_code="PDM-009",
                    )
                )
        elif mtype == "aligns_with":
            src_ok = len(sources) == 1 and sources[0] in conceptual_ids
            tgt_ok = bool(targets) and all(_HTTP_IRI_RE.match(r) for r in targets)
            if not (src_ok and tgt_ok):
                out.append(
                    _diag(
                        code="DAMS-INV-036",
                        invariant_id="INV-036",
                        message=(
                            f'Mapping "{mid}" aligns_with requires exactly one '
                            "ConceptualEntity in source_refs and http(s) IRI "
                            "target_refs."
                        ),
                        subject=mid or None,
                        remediation=(
                            "Use one ConceptualEntity source and absolute http(s) "
                            "IRI targets. INV-036."
                        ),
                        requirement_code="PDM-009",
                    )
                )
    return out


def check_carrier_refs_are_data_carriers(data: dict[str, Any]) -> list[Diagnostic]:
    """DataFlowEntityBinding / SelectedEntity carrier_refs must be DataCarrier ids."""
    carrier_ids = technical_asset_ids_by_class(data)["DataCarrier"]
    non_carrier_tech: set[str] = set()
    for class_name, ids in technical_asset_ids_by_class(data).items():
        if class_name != "DataCarrier":
            non_carrier_tech |= ids

    out: list[Diagnostic] = []

    def _check_binding(owner_id: str, refs: list[Any], *, context: str) -> None:
        for ref in refs:
            if ref is None:
                continue
            rid = str(ref)
            if rid in carrier_ids:
                continue
            if rid in non_carrier_tech:
                out.append(
                    _diag(
                        code="DAMS-REQ-PDM-010.c1",
                        message=(
                            f'{context} "{owner_id}" carrier_refs includes {rid!r} '
                            "which is not a DataCarrier."
                        ),
                        subject=owner_id,
                        remediation="Point carrier_refs only at data_carriers element_ids.",
                        requirement_code="PDM-010",
                    )
                )

    for flow in data.get("data_flows") or []:
        if not isinstance(flow, dict):
            continue
        for binding in flow.get("entity_bindings") or []:
            if not isinstance(binding, dict):
                continue
            bid = str(binding.get("element_id") or binding.get("name") or flow.get("element_id") or "")
            _check_binding(
                bid,
                list(binding.get("carrier_refs") or []),
                context="DataFlowEntityBinding",
            )

    for model in data.get("data_model_bindings") or []:
        if not isinstance(model, dict):
            continue
        for sel in model.get("selected_entities") or []:
            if not isinstance(sel, dict):
                continue
            sid = str(sel.get("element_id") or sel.get("name") or "")
            _check_binding(
                sid,
                list(sel.get("carrier_refs") or []),
                context="SelectedEntity",
            )

    # Also scan contract-style selections if present under model_selections
    for sel_root in data.get("model_selections") or []:
        if not isinstance(sel_root, dict):
            continue
        for sel in sel_root.get("selected_entities") or []:
            if not isinstance(sel, dict):
                continue
            sid = str(sel.get("element_id") or sel.get("name") or "")
            _check_binding(
                sid,
                list(sel.get("carrier_refs") or []),
                context="SelectedEntity",
            )

    return out


def check_operation_interface_ref(data: dict[str, Any]) -> list[Diagnostic]:
    """INV-016: AccessPoint with asset_kind=operation requires interface_ref (PDM-011).

    Example error::

        AccessPoint \"dams:ap/x/op\" with asset_kind=operation requires interface_ref.
        Remediation: Set interface_ref to the parent AccessPoint (interface). INV-016.
    """
    out: list[Diagnostic] = []
    for el in data.get("access_points") or []:
        if not isinstance(el, dict):
            continue
        if str(el.get("asset_kind") or "") != "operation":
            continue
        sid = str(el.get("element_id") or el.get("name") or "")
        if not (el.get("interface_ref") and str(el.get("interface_ref")).strip()):
            out.append(
                _diag(
                    code="DAMS-REQ-PDM-011.c1",
                    invariant_id="INV-016",
                    message=(
                        f'AccessPoint "{sid}" with asset_kind=operation requires interface_ref.'
                    ),
                    subject=sid or None,
                    remediation=(
                        "Set interface_ref to the parent AccessPoint (interface). INV-016."
                    ),
                    requirement_code="PDM-011",
                )
            )
    return out


def check_in_memory_location(data: dict[str, Any]) -> list[Diagnostic]:
    """INV-015: in_memory DataCarrier must not have location_uri or region (PDM-012).

    Example error::

        DataCarrier \"dams:carrier/x\" with asset_kind=in_memory must not set location_uri.
        Remediation: Remove location_uri and region for in_memory carriers. INV-015.
    """
    out: list[Diagnostic] = []
    for el in data.get("data_carriers") or []:
        if not isinstance(el, dict):
            continue
        if str(el.get("asset_kind") or "") != "in_memory":
            continue
        sid = str(el.get("element_id") or el.get("name") or "")
        bad: list[str] = []
        if el.get("location_uri"):
            bad.append("location_uri")
        if el.get("region"):
            bad.append("region")
        if bad:
            out.append(
                _diag(
                    code="DAMS-REQ-PDM-012.c1",
                    invariant_id="INV-015",
                    message=(
                        f'DataCarrier "{sid}" with asset_kind=in_memory must not set '
                        f"{', '.join(bad)}."
                    ),
                    subject=sid or None,
                    remediation=(
                        "Remove location_uri and region for in_memory carriers. INV-015."
                    ),
                    requirement_code="PDM-012",
                )
            )
    return out


def check_technical_assets(data: dict[str, Any]) -> tuple[Diagnostic, ...]:
    """Run all TechnicalAsset semantic checks."""
    diags: list[Diagnostic] = []
    diags.extend(check_unique_asset_keys(data))
    diags.extend(check_parent_ref_cycles(data))
    diags.extend(check_asset_kind_allowlists(data))
    diags.extend(check_direction_forbidden(data))
    diags.extend(check_mapping_endpoint_types(data))
    diags.extend(check_carrier_refs_are_data_carriers(data))
    diags.extend(check_operation_interface_ref(data))
    diags.extend(check_in_memory_location(data))
    diags.extend(check_data_structures(data))
    return tuple(diags)
