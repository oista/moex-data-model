"""Semantic layer checks: ConceptualProperty, domains, DataType (ADR-034..036)."""

from __future__ import annotations

from typing import Any

from moex_modeling import (
    ConformancePhase,
    Diagnostic,
    DiagnosticDetail,
    DiagnosticSeverity,
)


def _diag(
    code: str,
    severity: DiagnosticSeverity,
    message: str,
    subject: str | None,
    *,
    remediation: str | None = None,
    invariant_id: str | None = None,
) -> Diagnostic:
    details: list[DiagnosticDetail] = [
        DiagnosticDetail(detail_key="finding", detail_value=message)
    ]
    if invariant_id:
        details.append(
            DiagnosticDetail(detail_key="invariant_id", detail_value=str(invariant_id))
        )
    parts = [message]
    if remediation and str(remediation).strip():
        parts.append(f"Remediation: {remediation}")
        details.append(
            DiagnosticDetail(
                detail_key="remediation",
                detail_value=str(remediation).strip(),
            )
        )
    return Diagnostic(
        diagnostic_code=code,
        severity=severity,
        diagnostic_message=" ".join(parts),
        conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
        subject_ref=subject,
        diagnostic_details=tuple(details),
    )


def _scope(data: dict[str, Any]) -> str:
    return str(data.get("implementation_scope") or "").strip()


def _index_by_id(items: list[Any] | None) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for el in items or []:
        if not isinstance(el, dict):
            continue
        eid = str(el.get("element_id") or el.get("binding_id") or "")
        if eid:
            out[eid] = el
    return out


def _iter_attributes(data: dict[str, Any]) -> list[dict[str, Any]]:
    attrs: list[dict[str, Any]] = []
    for ent in data.get("logical_entities") or []:
        if not isinstance(ent, dict):
            continue
        for attr in ent.get("attributes") or []:
            if isinstance(attr, dict):
                attrs.append(attr)
    return attrs


def check_identifying_requires_is_identifying(
    prop: dict[str, Any],
) -> Diagnostic | None:
    """INV-001: property_kind=identifying требует is_identifying=true.

    L1 rule exists but JSON Schema ``equals_string`` on boolean is defective
    (``l1_positive=not_satisfiable``); L2 enforces the same statement.

    Example error::

        ConceptualProperty \"dams:concept/C/p\": property_kind=identifying,
        но is_identifying не true.
        Remediation: Установите is_identifying: true … См. INV-001 / ADR-034.
    """
    eid = str(prop.get("element_id") or "")
    if str(prop.get("property_kind") or "") != "identifying":
        return None
    if prop.get("is_identifying") is True:
        return None
    return _diag(
        "DAMS-INV-001",
        DiagnosticSeverity.ERROR,
        (
            f'ConceptualProperty "{eid}": property_kind=identifying, '
            "но is_identifying не true."
        ),
        eid or None,
        invariant_id="INV-001",
        remediation=(
            "Установите is_identifying: true для identifying-свойства "
            "или смените property_kind. См. INV-001 / ADR-034."
        ),
    )


def check_semantic_layer(data: dict[str, Any]) -> list[Diagnostic]:
    """Validate ConceptualProperty / domains / types against слой rules."""
    out: list[Diagnostic] = []
    scope = _scope(data)
    is_enterprise = scope == "enterprise"

    props = list(data.get("conceptual_properties") or [])
    domains = list(data.get("conceptual_domains") or [])
    value_domains = list(data.get("value_domains") or [])
    data_types = list(data.get("data_types") or [])
    bindings = list(data.get("native_type_bindings") or [])

    prop_index = _index_by_id(props)
    cd_index = _index_by_id(domains)
    vd_index = _index_by_id(value_domains)
    dt_index = _index_by_id(data_types)
    concept_index = _index_by_id(list(data.get("conceptual_entities") or []))

    # --- package scope gates ---
    if not is_enterprise:
        for el in props:
            if isinstance(el, dict):
                out.append(
                    _diag(
                        "DAMS-SEM-PROP-SCOPE",
                        DiagnosticSeverity.ERROR,
                        "ConceptualProperty допустим только в enterprise-пакетах.",
                        str(el.get("element_id") or ""),
                        remediation="Перенесите свойство в enterprise-модель КМД.",
                    )
                )
        for el in domains:
            if isinstance(el, dict):
                out.append(
                    _diag(
                        "DAMS-SEM-CD-SCOPE",
                        DiagnosticSeverity.ERROR,
                        "ConceptualDomain допустим только в enterprise-пакетах.",
                        str(el.get("element_id") or ""),
                    )
                )
        for el in data_types:
            if isinstance(el, dict):
                out.append(
                    _diag(
                        "DAMS-SEM-DT-SCOPE",
                        DiagnosticSeverity.ERROR,
                        "DataType допустим только в корпоративном реестре (enterprise).",
                        str(el.get("element_id") or ""),
                    )
                )
        for el in bindings:
            if isinstance(el, dict):
                out.append(
                    _diag(
                        "DAMS-SEM-NTB-SCOPE",
                        DiagnosticSeverity.ERROR,
                        "NativeTypeBinding допустим только в корпоративном реестре.",
                        str(el.get("binding_id") or el.get("element_id") or ""),
                    )
                )

    # --- ConceptualProperty rules ---
    seen_keys: set[tuple[str, str]] = set()
    for prop in props:
        if not isinstance(prop, dict):
            continue
        eid = str(prop.get("element_id") or "")
        owner = str(prop.get("property_owner_entity_ref") or "")
        name = str(prop.get("name") or "")
        basis = prop.get("significance_basis") or []
        if isinstance(basis, str):
            basis = [basis]
        basis_set = {str(b) for b in basis if b}

        if not basis_set:
            out.append(
                _diag(
                    "DAMS-SEM-PROP-BASIS",
                    DiagnosticSeverity.ERROR,
                    "significance_basis не должен быть пуст.",
                    eid,
                )
            )
        if prop.get("is_identifying") is True and "identifying" not in basis_set:
            out.append(
                _diag(
                    "DAMS-SEM-PROP-IDENT",
                    DiagnosticSeverity.ERROR,
                    "is_identifying=true требует significance_basis containing identifying.",
                    eid,
                )
            )
        inv001 = check_identifying_requires_is_identifying(prop)
        if inv001 is not None:
            out.append(inv001)
        if "explicit_decision" in basis_set and not str(
            prop.get("significance_rationale") or ""
        ).strip():
            out.append(
                _diag(
                    "DAMS-SEM-PROP-RATIONALE",
                    DiagnosticSeverity.ERROR,
                    "explicit_decision требует significance_rationale.",
                    eid,
                )
            )
        if owner and owner not in concept_index and is_enterprise:
            out.append(
                _diag(
                    "DAMS-SEM-PROP-OWNER",
                    DiagnosticSeverity.ERROR,
                    f"property_owner_entity_ref {owner!r} не резолвится.",
                    eid,
                )
            )
        key = (owner, name)
        if owner and name:
            if key in seen_keys:
                out.append(
                    _diag(
                        "DAMS-SEM-PROP-DUP",
                        DiagnosticSeverity.ERROR,
                        f"Дубликат ConceptualProperty ({owner}, {name}).",
                        eid,
                    )
                )
            seen_keys.add(key)

        cd_ref = str(prop.get("conceptual_domain_ref") or "")
        if cd_ref and cd_ref not in cd_index and is_enterprise:
            out.append(
                _diag(
                    "DAMS-SEM-PROP-CD",
                    DiagnosticSeverity.ERROR,
                    f"conceptual_domain_ref {cd_ref!r} не резолвится.",
                    eid,
                )
            )

    # --- ConceptualDomain ---
    for cd in domains:
        if not isinstance(cd, dict):
            continue
        eid = str(cd.get("element_id") or "")
        kind = str(cd.get("conceptual_domain_kind") or "")
        meanings = cd.get("value_meanings") or []
        scheme = str(cd.get("concept_scheme_uri") or "").strip()
        if kind == "enumerated" and not meanings and not scheme:
            out.append(
                _diag(
                    "DAMS-SEM-CD-ENUM",
                    DiagnosticSeverity.ERROR,
                    "enumerated ConceptualDomain требует value_meanings или concept_scheme_uri.",
                    eid,
                )
            )
        if kind == "described":
            if meanings:
                out.append(
                    _diag(
                        "DAMS-SEM-CD-DESC",
                        DiagnosticSeverity.ERROR,
                        "described ConceptualDomain не должен содержать value_meanings.",
                        eid,
                    )
                )
            if not str(cd.get("description") or "").strip():
                out.append(
                    _diag(
                        "DAMS-SEM-CD-DESC-REQ",
                        DiagnosticSeverity.ERROR,
                        "described ConceptualDomain требует description.",
                        eid,
                    )
                )
        keys: set[str] = set()
        for vm in meanings:
            if not isinstance(vm, dict):
                continue
            mk = str(vm.get("meaning_key") or "")
            if not mk:
                continue
            if mk in keys:
                out.append(
                    _diag(
                        "DAMS-SEM-VM-DUP",
                        DiagnosticSeverity.ERROR,
                        f"Дубликат meaning_key {mk!r}.",
                        eid,
                    )
                )
            keys.add(mk)

    # --- ValueDomain / PermissibleValue ---
    for vd in value_domains:
        if not isinstance(vd, dict):
            continue
        eid = str(vd.get("element_id") or "")
        kind = str(vd.get("value_domain_kind") or "")
        pvs = vd.get("permissible_values") or []
        dt_ref = str(vd.get("data_type_ref") or "")
        if not dt_ref:
            out.append(
                _diag(
                    "DAMS-SEM-VD-TYPE",
                    DiagnosticSeverity.ERROR,
                    "ValueDomain требует data_type_ref.",
                    eid,
                )
            )
        elif dt_ref not in dt_index and is_enterprise:
            # solution packages may reference enterprise types via imports; warn only
            if is_enterprise:
                out.append(
                    _diag(
                        "DAMS-SEM-VD-TYPE-RESOLVE",
                        DiagnosticSeverity.ERROR,
                        f"data_type_ref {dt_ref!r} не резолвится в пакете.",
                        eid,
                    )
                )
        if kind == "enumerated" and not pvs:
            out.append(
                _diag(
                    "DAMS-SEM-VD-ENUM",
                    DiagnosticSeverity.ERROR,
                    "enumerated ValueDomain требует permissible_values.",
                    eid,
                )
            )
        if kind in {"described", "reference_set"} and pvs:
            out.append(
                _diag(
                    "DAMS-SEM-VD-NO-PV",
                    DiagnosticSeverity.ERROR,
                    f"{kind} ValueDomain не должен содержать permissible_values.",
                    eid,
                )
            )
        if kind == "reference_set":
            src = str(vd.get("value_set_source") or "").strip()
            dq = vd.get("dynamic_query")
            if not src and not dq:
                out.append(
                    _diag(
                        "DAMS-SEM-VD-REF",
                        DiagnosticSeverity.ERROR,
                        "reference_set требует value_set_source или dynamic_query.",
                        eid,
                    )
                )
        codes: set[str] = set()
        cd_ref = str(vd.get("conceptual_domain_ref") or "")
        meaning_keys: set[str] = set()
        if cd_ref and cd_ref in cd_index:
            for vm in cd_index[cd_ref].get("value_meanings") or []:
                if isinstance(vm, dict) and vm.get("meaning_key"):
                    meaning_keys.add(str(vm["meaning_key"]))
        for pv in pvs:
            if not isinstance(pv, dict):
                continue
            code = str(pv.get("value_code") or "")
            if code in codes:
                out.append(
                    _diag(
                        "DAMS-SEM-PV-DUP",
                        DiagnosticSeverity.ERROR,
                        f"Дубликат value_code {code!r}.",
                        eid,
                    )
                )
            if code:
                codes.add(code)
            vmk = str(pv.get("value_meaning_key") or "")
            if vmk and cd_ref and meaning_keys and vmk not in meaning_keys:
                out.append(
                    _diag(
                        "DAMS-SEM-PV-MEANING",
                        DiagnosticSeverity.ERROR,
                        f"value_meaning_key {vmk!r} отсутствует в ConceptualDomain.",
                        eid,
                    )
                )

    # --- DataType parameter rules ---
    for dt in data_types:
        if not isinstance(dt, dict):
            continue
        eid = str(dt.get("element_id") or "")
        family = str(dt.get("type_family") or "")
        precision = dt.get("precision")
        scale = dt.get("scale")
        if precision is not None and family != "decimal":
            out.append(
                _diag(
                    "DAMS-SEM-DT-PREC",
                    DiagnosticSeverity.ERROR,
                    "precision допустим только для type_family=decimal.",
                    eid,
                )
            )
        if scale is not None and family != "decimal":
            out.append(
                _diag(
                    "DAMS-SEM-DT-SCALE",
                    DiagnosticSeverity.ERROR,
                    "scale допустим только для type_family=decimal.",
                    eid,
                )
            )
        if (
            precision is not None
            and scale is not None
            and isinstance(precision, int)
            and isinstance(scale, int)
            and scale > precision
        ):
            out.append(
                _diag(
                    "DAMS-SEM-DT-SCALE-LE",
                    DiagnosticSeverity.ERROR,
                    "scale не должен превышать precision.",
                    eid,
                )
            )
        for length_slot in ("max_length", "min_length"):
            if dt.get(length_slot) is not None and family not in {"string", "binary"}:
                out.append(
                    _diag(
                        f"DAMS-SEM-DT-{length_slot.upper()}",
                        DiagnosticSeverity.ERROR,
                        f"{length_slot} допустим только для string/binary.",
                        eid,
                    )
                )

    # --- LogicalAttribute representation & concept_ref ---
    # Build realizes map: logical_entity -> set of conceptual_entity ids
    realizes: dict[str, set[str]] = {}
    for m in data.get("mappings") or []:
        if not isinstance(m, dict):
            continue
        if str(m.get("mapping_type") or "") != "realizes":
            continue
        sources = m.get("source_refs") or []
        targets = m.get("target_refs") or []
        if isinstance(sources, str):
            sources = [sources]
        if isinstance(targets, str):
            targets = [targets]
        for s in sources:
            realizes.setdefault(str(s), set()).update(str(t) for t in targets)

    def _ancestors(cid: str) -> set[str]:
        seen: set[str] = set()
        cur = cid
        while cur and cur not in seen:
            seen.add(cur)
            parent = concept_index.get(cur, {}).get("parent_concept_ref")
            cur = str(parent) if parent else ""
        return seen

    for attr in _iter_attributes(data):
        aid = str(attr.get("element_id") or "")
        has_vd = bool(str(attr.get("value_domain_ref") or "").strip())
        has_dt = bool(str(attr.get("data_type_ref") or "").strip())
        if not (has_vd or has_dt):
            out.append(
                _diag(
                    "DAMS-SEM-ATTR-TYPE",
                    DiagnosticSeverity.ERROR,
                    "Атрибут должен иметь value_domain_ref и/или data_type_ref.",
                    aid,
                )
            )
        vd_ref = str(attr.get("value_domain_ref") or "")
        dt_ref = str(attr.get("data_type_ref") or "")
        if has_vd and vd_ref in vd_index and has_dt:
            vd_dt = str(vd_index[vd_ref].get("data_type_ref") or "")
            if vd_dt and dt_ref and vd_dt != dt_ref:
                out.append(
                    _diag(
                        "DAMS-SEM-ATTR-TYPE-MISMATCH",
                        DiagnosticSeverity.ERROR,
                        "data_type_ref атрибута должен совпадать с типом ValueDomain.",
                        aid,
                    )
                )

        concept_ref = str(attr.get("concept_ref") or "").strip()
        if not concept_ref:
            # absence is never an error or warning (вариант B)
            continue
        if concept_ref not in prop_index:
            # may live in imported enterprise package — warn only if enterprise has props empty
            continue
        prop = prop_index[concept_ref]
        prop_owner = str(prop.get("property_owner_entity_ref") or "")
        owner_entity = str(attr.get("owner_entity_ref") or "")
        allowed = realizes.get(owner_entity, set())
        ok = False
        for cid in allowed:
            if prop_owner == cid or prop_owner in _ancestors(cid):
                ok = True
                break
        # also allow if prop_owner is in allowed ancestors of realized concepts
        if not ok and allowed:
            for cid in allowed:
                if cid in _ancestors(prop_owner) or prop_owner in _ancestors(cid):
                    ok = True
                    break
        if not ok and allowed:
            out.append(
                _diag(
                    "DAMS-SEM-ATTR-CONCEPT",
                    DiagnosticSeverity.ERROR,
                    "concept_ref указывает на свойство чужой ConceptualEntity "
                    "(нет realizes / parent_concept_ref согласования).",
                    aid,
                    remediation="Исправьте concept_ref или Mapping realizes.",
                )
            )

    return out
