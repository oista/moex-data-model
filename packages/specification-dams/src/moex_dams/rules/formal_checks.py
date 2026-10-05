"""Execute SpecificationRequirement formal_checks against a ModelPackage body."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from moex_modeling import (
    ConformancePhase,
    Diagnostic,
    DiagnosticDetail,
    DiagnosticSeverity,
)
from moex_standard_linkml.domain.body import LinkMLImplementationBody

from moex_dams.rules.cascade import (
    DATA_OWNER_PLACEHOLDER,
    find_redundant_overrides,
    resolve_governed,
)
from moex_dams.rules.conceptual_entity import check_conceptual_entities
from moex_dams.rules.dams_levels import ENTERPRISE_CONCEPTUAL_REF
from moex_dams.rules.definitions import (
    DefinitionIndex,
    DefinitionMode,
    ExternalDefinitionProvider,
    build_definition_index,
    find_redundant_definition_overrides,
    resolve_definition,
    validate_scoped_definition_systems,
)
from moex_dams.rules.relation_terms import check_relation_terms
from moex_dams.rules.semantic_layer import check_semantic_layer
from moex_dams.rules.technical_assets import (
    DATA_CARRIER_KINDS,
    check_technical_assets,
    iter_technical_assets,
)

# DataCarrier kinds (GEN-004 / PDM-003 allowlist).
DATA_CARRYING_KINDS = DATA_CARRIER_KINDS

_DEFAULT_CATALOG = (
    Path(__file__).resolve().parents[5]
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "requirements"
    / "it-solution-requirements.yaml"
)


def _severity(raw: str | None) -> DiagnosticSeverity:
    if raw == "info":
        return DiagnosticSeverity.INFO
    if raw == "warning":
        return DiagnosticSeverity.WARNING
    return DiagnosticSeverity.ERROR


def _filled(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return len(value) > 0
    return True


def _slot_value(
    el: dict[str, Any],
    slot: str,
    *,
    subject: str | None,
    effective: bool,
    resolved: dict[str, Any],
) -> Any:
    """Return declared or effective slot value for formal_checks."""
    if not effective:
        return el.get(slot)
    if subject and subject in resolved:
        prov = resolved[subject].get(slot)
        return None if prov is None else prov.value
    # Fallback: package root may use element_id as subject
    eid = str(el.get("element_id") or "")
    if eid and eid in resolved:
        prov = resolved[eid].get(slot)
        return None if prov is None else prov.value
    return el.get(slot)


def _diag(
    *,
    code: str,
    severity: DiagnosticSeverity,
    message: str,
    subject: str | None,
    remediation: str | None = None,
    statement: str | None = None,
    requirement_code: str | None = None,
) -> Diagnostic:
    parts = [message]
    if statement:
        short = statement.strip().split(".")[0].strip()
        if short:
            parts.append(f"Required by: {short}.")
    if remediation:
        parts.append(f"Remediation: {remediation}")
    details: list[DiagnosticDetail] = []
    if requirement_code:
        details.append(
            DiagnosticDetail(
                detail_key="requirement_code",
                detail_value=str(requirement_code),
            )
        )
    if statement and str(statement).strip():
        details.append(
            DiagnosticDetail(
                detail_key="statement",
                detail_value=str(statement).strip(),
            )
        )
    if remediation and str(remediation).strip():
        details.append(
            DiagnosticDetail(
                detail_key="remediation",
                detail_value=str(remediation).strip(),
            )
        )
    details.append(
        DiagnosticDetail(detail_key="finding", detail_value=message)
    )
    return Diagnostic(
        diagnostic_code=code,
        severity=severity,
        diagnostic_message=" ".join(parts),
        conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
        subject_ref=subject,
        diagnostic_details=tuple(details),
    )


def _collect_ids(data: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    if data.get("element_id"):
        ids.add(str(data["element_id"]))
    for key in (
        "domain_contexts",
        "logical_entities",
        "relationships",
        "data_carriers",
        "access_points",
        "data_containers",
        "execution_assets",
        "mappings",
        "conceptual_entities",
    ):
        for item in data.get(key) or []:
            if isinstance(item, dict) and item.get("element_id"):
                ids.add(str(item["element_id"]))
            if key == "logical_entities" and isinstance(item, dict):
                for attr in item.get("attributes") or []:
                    if isinstance(attr, dict) and attr.get("element_id"):
                        ids.add(str(attr["element_id"]))
            if key == "data_carriers" and isinstance(item, dict):
                for field in item.get("physical_fields") or []:
                    if isinstance(field, dict) and field.get("element_id"):
                        ids.add(str(field["element_id"]))
    return ids


def _iter_targets(
    data: dict[str, Any],
    target_class: str,
) -> list[tuple[dict[str, Any], str | None]]:
    """Return (element_dict, subject_ref) for instances of target_class."""
    if target_class == "ModelPackage":
        return [(data, str(data.get("element_id") or "ModelPackage"))]
    if target_class == "LogicalEntity":
        out = []
        for e in data.get("logical_entities") or []:
            if isinstance(e, dict):
                out.append((e, str(e.get("element_id") or e.get("name"))))
        return out
    if target_class == "LogicalAttribute":
        out = []
        for e in data.get("logical_entities") or []:
            if not isinstance(e, dict):
                continue
            for a in e.get("attributes") or []:
                if isinstance(a, dict):
                    out.append((a, str(a.get("element_id") or a.get("name"))))
        return out
    if target_class == "Relationship":
        out = []
        for r in data.get("relationships") or []:
            if isinstance(r, dict):
                out.append((r, str(r.get("element_id") or r.get("name"))))
        return out
    if target_class == "TechnicalAsset":
        return [(el, sid) for el, sid, _ in iter_technical_assets(data)]
    if target_class == "DataCarrier":
        out = []
        for p in data.get("data_carriers") or []:
            if isinstance(p, dict):
                out.append((p, str(p.get("element_id") or p.get("name"))))
        return out
    if target_class == "AccessPoint":
        out = []
        for p in data.get("access_points") or []:
            if isinstance(p, dict):
                out.append((p, str(p.get("element_id") or p.get("name"))))
        return out
    if target_class == "DataContainer":
        out = []
        for p in data.get("data_containers") or []:
            if isinstance(p, dict):
                out.append((p, str(p.get("element_id") or p.get("name"))))
        return out
    if target_class == "ExecutionAsset":
        out = []
        for p in data.get("execution_assets") or []:
            if isinstance(p, dict):
                out.append((p, str(p.get("element_id") or p.get("name"))))
        return out
    if target_class == "PhysicalField":
        out = []
        for p in data.get("data_carriers") or []:
            if not isinstance(p, dict):
                continue
            for f in p.get("physical_fields") or []:
                if isinstance(f, dict):
                    out.append((f, str(f.get("element_id") or f.get("name"))))
        return out
    return []


def _is_data_carrying(obj: dict[str, Any]) -> bool:
    kind = str(obj.get("asset_kind") or "")
    if kind in DATA_CARRYING_KINDS:
        return True
    fields = obj.get("physical_fields") or []
    return bool(fields)


def _has_entity_physical_mapping(data: dict[str, Any], physical_id: str) -> bool:
    logical_ids = {
        str(e.get("element_id"))
        for e in (data.get("logical_entities") or [])
        if isinstance(e, dict) and e.get("element_id")
    }
    for m in data.get("mappings") or []:
        if not isinstance(m, dict):
            continue
        if str(m.get("mapping_type") or "") != "entity_physical":
            continue
        refs = {str(x) for x in (m.get("source_refs") or []) + (m.get("target_refs") or [])}
        if physical_id not in refs:
            continue
        if refs & logical_ids:
            return True
    return False


def _has_field_mapping(
    data: dict[str, Any],
    *,
    logical_attr_id: str | None = None,
    physical_field_id: str | None = None,
) -> bool:
    for m in data.get("mappings") or []:
        if not isinstance(m, dict):
            continue
        if str(m.get("mapping_type") or "") != "field_mapping":
            continue
        refs = {str(x) for x in (m.get("source_refs") or []) + (m.get("target_refs") or [])}
        if logical_attr_id and logical_attr_id in refs:
            return True
        if physical_field_id and physical_field_id in refs:
            return True
    return False


def _entity_in_relationship(data: dict[str, Any], entity_id: str) -> bool:
    for r in data.get("relationships") or []:
        if not isinstance(r, dict):
            continue
        if str(r.get("source_entity_ref")) == entity_id or str(
            r.get("target_entity_ref")
        ) == entity_id:
            return True
    return False


def _has_realizes(data: dict[str, Any], entity_id: str) -> bool:
    for m in data.get("mappings") or []:
        if not isinstance(m, dict):
            continue
        if str(m.get("mapping_type") or "") != "realizes":
            continue
        refs = {str(x) for x in (m.get("source_refs") or []) + (m.get("target_refs") or [])}
        if entity_id in refs:
            return True
    return False


_ENTERPRISE_BODY_CACHE: dict[str, dict[str, Any] | None] = {}


def _enterprise_body_path(conceptual_ref: str) -> Path | None:
    """Resolve enterprise ModelPackage body for a conceptual_implementation_ref."""
    if conceptual_ref != ENTERPRISE_CONCEPTUAL_REF:
        return None
    # packages/specification-dams/src/moex_dams/rules → repo root = parents[5]
    root = Path(__file__).resolve().parents[5]
    path = (
        root
        / "model-assets"
        / "implementations"
        / "enterprise"
        / "moex-enterprise-conceptual-model"
        / "0.1"
        / "enterprise-conceptual-model.yaml"
    )
    return path if path.is_file() else None


def _load_enterprise_concepts(
    conceptual_ref: str | None,
) -> dict[str, dict[str, Any]]:
    """Map conceptual element_id → entity dict from the enterprise package."""
    if not conceptual_ref:
        return {}
    if conceptual_ref in _ENTERPRISE_BODY_CACHE:
        body = _ENTERPRISE_BODY_CACHE[conceptual_ref]
    else:
        path = _enterprise_body_path(str(conceptual_ref))
        body = None
        if path is not None:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            body = raw if isinstance(raw, dict) else None
        _ENTERPRISE_BODY_CACHE[conceptual_ref] = body
    if not body:
        return {}
    out: dict[str, dict[str, Any]] = {}
    for el in body.get("conceptual_entities") or []:
        if isinstance(el, dict) and el.get("element_id"):
            out[str(el["element_id"])] = el
    return out


def _concepts_realized_by_logical(
    data: dict[str, Any], logical_id: str
) -> set[str]:
    """Concepts referenced via conceptual_entity_refs or Mapping(realizes)."""
    refs: set[str] = set()
    for el in data.get("logical_entities") or []:
        if not isinstance(el, dict):
            continue
        if str(el.get("element_id") or "") != logical_id:
            continue
        for r in el.get("conceptual_entity_refs") or []:
            if r:
                refs.add(str(r))
    for m in data.get("mappings") or []:
        if not isinstance(m, dict):
            continue
        if str(m.get("mapping_type") or "") != "realizes":
            continue
        sources = {str(x) for x in (m.get("source_refs") or [])}
        if logical_id not in sources:
            continue
        for t in m.get("target_refs") or []:
            if t:
                refs.add(str(t))
    return refs


def _logical_linked_to_owner_realizer(
    data: dict[str, Any],
    logical_id: str,
    owner_concept: str,
) -> bool:
    """True if a Relationship links logical_id to a peer realizing owner_concept."""
    for rel in data.get("relationships") or []:
        if not isinstance(rel, dict):
            continue
        src = str(rel.get("source_entity_ref") or "")
        tgt = str(rel.get("target_entity_ref") or "")
        if src == logical_id:
            peer = tgt
        elif tgt == logical_id:
            peer = src
        else:
            continue
        if owner_concept in _concepts_realized_by_logical(data, peer):
            return True
    return False


def _applies(req: dict[str, Any], data: dict[str, Any]) -> bool:
    applies = req.get("applies_to") or {}
    if not isinstance(applies, dict):
        return True
    scope = applies.get("applies_implementation_scope")
    if scope == "solution":
        impl_scope = data.get("implementation_scope")
        # Treat missing scope + solution_ref as solution packages.
        if impl_scope and impl_scope != "solution":
            return False
        if impl_scope is None and not data.get("solution_ref"):
            return False
    level = applies.get("applies_dams_model_level")
    if level == "solution" and data.get("implementation_scope") == "enterprise":
        return False
    return True


def _filter_by_kinds(
    elements: list[tuple[dict[str, Any], str | None]],
    applies: dict[str, Any],
) -> list[tuple[dict[str, Any], str | None]]:
    kinds = applies.get("applies_target_kinds") or []
    if not kinds:
        return elements
    allow = {str(k) for k in kinds}
    return [
        (el, sid)
        for el, sid in elements
        if str(el.get("asset_kind") or "") in allow
    ]


def load_it_solution_catalog(catalog_path: Path | None = None) -> list[dict[str, Any]]:
    path = catalog_path or _DEFAULT_CATALOG
    if not path.is_file():
        # Repo-relative fallback from CWD
        alt = (
            Path("model-assets/specifications/moex-dams/0.1/requirements/"
                 "it-solution-requirements.yaml")
        )
        path = alt if alt.is_file() else path
    if not path.is_file():
        return []
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return []
    reqs = raw.get("requirements") or []
    return [r for r in reqs if isinstance(r, dict)]


def _run_conditional(
    *,
    template: str,
    el: dict[str, Any],
    subject: str | None,
    data: dict[str, Any],
    check: dict[str, Any],
    statement: str | None,
    requirement_code: str | None = None,
) -> list[Diagnostic]:
    code = str(check.get("diagnostic_code") or check.get("check_id") or "DAMS-REQ")
    sev = _severity(check.get("severity"))
    rem = check.get("remediation")
    out: list[Diagnostic] = []
    req_kw = {"requirement_code": requirement_code}

    if template == "implementation_scope_solution":
        if data.get("implementation_scope") != "solution":
            out.append(
                _diag(
                    code=code,
                    severity=sev,
                    message='ModelPackage must have implementation_scope "solution".',
                    subject=subject,
                    remediation=rem,
                    statement=statement,
                    **req_kw,
                )
            )
        return out

    if template == "non_empty_logical_or_physical":
        has_tech = any(
            data.get(k)
            for k in (
                "data_carriers",
                "access_points",
                "data_containers",
                "execution_assets",
            )
        )
        if not (data.get("logical_entities") or has_tech):
            out.append(
                _diag(
                    code=code,
                    severity=sev,
                    message=(
                        "Model package has neither logical entities nor "
                        "technical assets (data_carriers / access_points / "
                        "data_containers / execution_assets)."
                    ),
                    subject=subject,
                    remediation=rem,
                    statement=statement,
                    **req_kw,
                )
            )
        return out

    if template in (
        "data_carrying_entity_mapping_or_technical",
        "pdm003_entity_physical",
    ):
        if not _is_data_carrying(el):
            return out
        status = str(el.get("mapping_coverage_status") or "")
        if status == "technical-only":
            if not _filled(el.get("mapping_rationale")):
                out.append(
                    _diag(
                        code=code,
                        severity=sev,
                        message=(
                            f'DataCarrier "{subject}" is technical-only but '
                            "mapping_rationale is empty."
                        ),
                        subject=subject,
                        remediation=rem,
                        statement=statement,
                        requirement_code=requirement_code,
                    )
                )
            return out
        pid = str(el.get("element_id") or "")
        if not _has_entity_physical_mapping(data, pid):
            out.append(
                _diag(
                    code=code,
                    severity=sev,
                    message=(
                        f'DataCarrier "{subject}" lacks entity_physical Mapping '
                        "to a logical entity."
                    ),
                    subject=subject,
                    remediation=rem,
                    statement=statement,
                    requirement_code=requirement_code,
                )
            )
        return out

    if template == "pdm001_structure_ref":
        kind = str(el.get("asset_kind") or "")
        if kind == "in_memory":
            return out
        if not _filled(el.get("structure_ref")):
            out.append(
                _diag(
                    code=code,
                    severity=sev,
                    message=(
                        f'DataCarrier "{subject}" missing required structure_ref '
                        "(not required for in_memory)."
                    ),
                    subject=subject,
                    remediation=rem,
                    statement=statement,
                    requirement_code=requirement_code,
                )
            )
        return out

    if template == "ldm004_identity":
        entity_type = str(el.get("entity_type") or "")
        if entity_type == "technical":
            return out
        if not _filled(el.get("identity_rule")):
            out.append(
                _diag(
                    code=code,
                    severity=sev,
                    message=f'LogicalEntity "{subject}" does not define identity_rule.',
                    subject=subject,
                    remediation=rem,
                    statement=statement,
                    requirement_code=requirement_code,
                )
            )
        kind = el.get("business_key_kind")
        keys = el.get("key_attribute_refs") or []
        if not _filled(kind) and not _filled(keys):
            out.append(
                _diag(
                    code=code,
                    severity=sev,
                    message=(
                        f'LogicalEntity "{subject}" needs business_key_kind '
                        "and/or key_attribute_refs."
                    ),
                    subject=subject,
                    remediation=rem,
                    statement=statement,
                    requirement_code=requirement_code,
                )
            )
        elif kind == "surrogate" and not _filled(el.get("identity_rule")):
            out.append(
                _diag(
                    code=code,
                    severity=sev,
                    message=(
                        f'LogicalEntity "{subject}": surrogate alone does not '
                        "satisfy identity for a non-technical entity."
                    ),
                    subject=subject,
                    remediation=rem,
                    statement=statement,
                    requirement_code=requirement_code,
                )
            )
        elif kind == "surrogate" and not _filled(keys) and _filled(el.get("identity_rule")):
            # surrogate + identity_rule without key refs: still warn via surrogate-alone spirit
            # Plan: surrogate alone insufficient — require identity_rule (already) AND
            # not treat surrogate as sole proof. If only surrogate kind with identity_rule, OK.
            pass
        return out

    if template == "ldm005_attributes":
        attrs = el.get("attributes") or []
        if attrs:
            return out
        if str(el.get("entity_type") or "") == "technical" and (
            _filled(el.get("isolation_rationale")) or _filled(el.get("alignment_rationale"))
        ):
            return out
        out.append(
            _diag(
                code=code,
                severity=sev,
                message=f'LogicalEntity "{subject}" has no attributes.',
                subject=subject,
                remediation=rem,
                statement=statement,
                requirement_code=requirement_code,
            )
        )
        return out

    if template == "ldm006_alignment":
        status = str(el.get("conceptual_alignment_status") or "")
        refs = el.get("conceptual_entity_refs") or []
        rationale = el.get("alignment_rationale")
        entity_type = str(el.get("entity_type") or "")
        if status == "aligned" or (not status and refs):
            if not refs:
                out.append(
                    _diag(
                        code=code,
                        severity=sev,
                        message=(
                            f'LogicalEntity "{subject}" status aligned requires '
                            "conceptual_entity_refs."
                        ),
                        subject=subject,
                        remediation=rem,
                        statement=statement,
                        requirement_code=requirement_code,
                    )
                )
            return out
        if status in ("pending", "local-only"):
            if not _filled(rationale):
                out.append(
                    _diag(
                        code=code,
                        severity=sev,
                        message=(
                            f'LogicalEntity "{subject}" with status {status} '
                            "requires alignment_rationale."
                        ),
                        subject=subject,
                        remediation=rem,
                        statement=statement,
                        requirement_code=requirement_code,
                    )
                )
            return out
        if status == "not-applicable":
            if entity_type != "technical":
                out.append(
                    _diag(
                        code=code,
                        severity=sev,
                        message=(
                            f'LogicalEntity "{subject}": not-applicable only allowed '
                            "for technical entities."
                        ),
                        subject=subject,
                        remediation=rem,
                        statement=statement,
                        requirement_code=requirement_code,
                    )
                )
            elif not _filled(rationale):
                out.append(
                    _diag(
                        code=code,
                        severity=sev,
                        message=(
                            f'LogicalEntity "{subject}" not-applicable requires '
                            "alignment_rationale."
                        ),
                        subject=subject,
                        remediation=rem,
                        statement=statement,
                        requirement_code=requirement_code,
                    )
                )
            return out
        # No status and no refs
        if not refs:
            out.append(
                _diag(
                    code=code,
                    severity=sev,
                    message=(
                        f'LogicalEntity "{subject}" needs conceptual_entity_refs '
                        "or conceptual_alignment_status with rationale."
                    ),
                    subject=subject,
                    remediation=rem,
                    statement=statement,
                    requirement_code=requirement_code,
                )
            )
        return out

    if template == "ldm007_semantic_inclusion":
        if str(el.get("entity_type") or "") == "technical":
            return out
        eid = str(el.get("element_id") or "")
        alignedish = str(el.get("conceptual_alignment_status") or "") in (
            "aligned",
            "pending",
            "local-only",
        ) and (
            _filled(el.get("conceptual_entity_refs"))
            or _filled(el.get("alignment_rationale"))
        )
        ok = (
            _entity_in_relationship(data, eid)
            or _filled(el.get("conceptual_entity_refs"))
            or _has_realizes(data, eid)
            or alignedish
            or _filled(el.get("isolation_rationale"))
        )
        if not ok:
            out.append(
                _diag(
                    code=code,
                    severity=sev,
                    message=(
                        f'LogicalEntity "{subject}" is semantically isolated '
                        "(no relationship, conceptual alignment, or isolation rationale)."
                    ),
                    subject=subject,
                    remediation=rem,
                    statement=statement,
                    requirement_code=requirement_code,
                )
            )
        return out

    if template == "ldm008_realization_completeness":
        status = str(el.get("conceptual_alignment_status") or "")
        refs = [str(r) for r in (el.get("conceptual_entity_refs") or []) if r]
        aligned = status == "aligned" or (not status and refs)
        if not aligned or not refs:
            return out
        enterprise = _load_enterprise_concepts(
            str(data.get("conceptual_implementation_ref") or "") or None
        )
        if not enterprise:
            return out
        eid = str(el.get("element_id") or "")
        for cref in refs:
            concept = enterprise.get(cref)
            if not concept or str(concept.get("entity_tier") or "") != "dependent":
                continue
            owners = [str(o) for o in (concept.get("depends_on_refs") or []) if o]
            for owner in owners:
                if _logical_linked_to_owner_realizer(data, eid, owner):
                    continue
                out.append(
                    _diag(
                        code=code,
                        severity=sev,
                        message=(
                            f'LogicalEntity "{subject}" realizes dependent concept '
                            f'"{cref}" but has no Relationship to a logical entity '
                            f'that realizes owner "{owner}".'
                        ),
                        subject=subject,
                        remediation=rem,
                        statement=statement,
                        requirement_code=requirement_code,
                    )
                )
        return out

    if template == "atr005_mapping_coverage":
        status = str(el.get("mapping_coverage_status") or "")
        if status in (
            "planned",
            "derived",
            "inherited",
            "technical-only",
            "not-applicable",
        ):
            if status in ("planned", "technical-only", "not-applicable", "inherited") and not _filled(
                el.get("mapping_rationale")
            ):
                # derived may use derived_expression instead
                if status == "derived" and _filled(el.get("derived_expression")):
                    return out
                if status != "derived":
                    out.append(
                        _diag(
                            code=code,
                            severity=sev,
                            message=(
                                f'LogicalAttribute "{subject}" status {status} '
                                "requires mapping_rationale."
                            ),
                            subject=subject,
                            remediation=rem,
                            statement=statement,
                            requirement_code=requirement_code,
                        )
                    )
            elif status == "derived" and not (
                _filled(el.get("derived_expression")) or _filled(el.get("mapping_rationale"))
            ):
                out.append(
                    _diag(
                        code=code,
                        severity=sev,
                        message=(
                            f'LogicalAttribute "{subject}" derived requires '
                            "derived_expression or mapping_rationale."
                        ),
                        subject=subject,
                        remediation=rem,
                        statement=statement,
                        requirement_code=requirement_code,
                    )
                )
            return out
        aid = str(el.get("element_id") or "")
        if status == "mapped" or not status:
            if _has_field_mapping(data, logical_attr_id=aid) or _filled(
                el.get("derived_expression")
            ):
                return out
            out.append(
                _diag(
                    code=code,
                    severity=sev,
                    message=(
                        f'LogicalAttribute "{subject}" needs field_mapping, '
                        "derived_expression, or mapping_coverage_status exception."
                    ),
                    subject=subject,
                    remediation=rem,
                    statement=statement,
                    requirement_code=requirement_code,
                )
            )
        return out

    if template == "planned_on_active_warning":
        if (
            str(el.get("mapping_coverage_status") or "") == "planned"
            and str(el.get("lifecycle_status") or "") == "active"
        ):
            out.append(
                _diag(
                    code=code,
                    severity=DiagnosticSeverity.WARNING,
                    message=(
                        f'"{subject}" uses mapping_coverage_status planned while '
                        "lifecycle_status is active; planned is not a permanent bypass."
                    ),
                    subject=subject,
                    remediation=rem,
                    statement=statement,
                    requirement_code=requirement_code,
                )
            )
        return out

    if template == "ref002_cardinality":
        status = str(el.get("lifecycle_status") or "active")
        slots = (
            "source_min_cardinality",
            "source_max_cardinality",
            "target_min_cardinality",
            "target_max_cardinality",
        )
        missing = [s for s in slots if el.get(s) is None]
        if not missing:
            return out
        if status == "draft" and _filled(el.get("cardinality_rationale")):
            return out
        out.append(
            _diag(
                code=code,
                severity=sev,
                message=(
                    f'Relationship "{subject}" missing cardinality: {", ".join(missing)}.'
                ),
                subject=subject,
                remediation=rem,
                statement=statement,
                requirement_code=requirement_code,
            )
        )
        return out

    if template == "pdm004_field_mapping":
        status = str(el.get("mapping_coverage_status") or "")
        if status in (
            "planned",
            "derived",
            "inherited",
            "technical-only",
            "not-applicable",
        ):
            if status in ("planned", "technical-only", "not-applicable", "inherited") and not _filled(
                el.get("mapping_rationale")
            ):
                out.append(
                    _diag(
                        code=code,
                        severity=sev,
                        message=(
                            f'PhysicalField "{subject}" status {status} '
                            "requires mapping_rationale."
                        ),
                        subject=subject,
                        remediation=rem,
                        statement=statement,
                        requirement_code=requirement_code,
                    )
                )
            return out
        fid = str(el.get("element_id") or "")
        # Also accept mapping with transformation_expression mentioning field
        has_map = _has_field_mapping(data, physical_field_id=fid)
        if has_map:
            return out
        out.append(
            _diag(
                code=code,
                severity=sev,
                message=(
                    f'PhysicalField "{subject}" needs field_mapping or '
                    "mapping_coverage_status exception."
                ),
                subject=subject,
                remediation=rem,
                statement=statement,
                requirement_code=requirement_code,
            )
        )
        return out

    if template == "atr002_snake_case":
        name = str(el.get("name") or "")
        if not name:
            return out
        if not re.fullmatch(r"[a-z][a-z0-9]*(_[a-z0-9]+)*", name):
            out.append(
                _diag(
                    code=code,
                    severity=DiagnosticSeverity.WARNING,
                    message=(
                        f'LogicalAttribute "{subject}" name "{name}" should be '
                        "lower_snake_case."
                    ),
                    subject=subject,
                    remediation=rem,
                    statement=statement,
                    requirement_code=requirement_code,
                )
            )
        return out

    if template == "cls001_axes_present":
        if not el.get("entity_type") or not el.get("data_class"):
            out.append(
                _diag(
                    code=code,
                    severity=DiagnosticSeverity.WARNING,
                    message=(
                        f'LogicalEntity "{subject}" should set both entity_type '
                        "and data_class independently."
                    ),
                    subject=subject,
                    remediation=rem,
                    statement=statement,
                    requirement_code=requirement_code,
                )
            )
        return out

    if template == "flw001_soft_presence":
        # Soft: warn if package has outbound/inbound data_carriers and no data_flows
        carriers = data.get("data_carriers") or []
        directions = {
            str(p.get("direction"))
            for p in carriers
            if isinstance(p, dict) and p.get("direction")
        }
        if directions & {"outbound", "inbound", "bidirectional"}:
            if not data.get("data_flows"):
                out.append(
                    _diag(
                        code=code,
                        severity=DiagnosticSeverity.WARNING,
                        message=(
                            "Package exposes integration-facing data carriers but "
                            "has no data_flows section yet."
                        ),
                        subject=subject,
                        remediation=rem,
                        statement=statement,
                        requirement_code=requirement_code,
                    )
                )
        return out

    if template == "cls002_security_soft":
        gov = str(el.get("governance_classification") or "")
        if gov in ("confidential", "restricted") and not _filled(
            el.get("security_classification")
        ):
            out.append(
                _diag(
                    code=code,
                    severity=DiagnosticSeverity.WARNING,
                    message=(
                        f'LogicalEntity "{subject}" has governance {gov} but no '
                        "security_classification."
                    ),
                    subject=subject,
                    remediation=rem,
                    statement=statement,
                    requirement_code=requirement_code,
                )
            )
        return out

    if template == "ref003_kind_soft":
        if str(el.get("lifecycle_status") or "active") == "active" and not _filled(
            el.get("relationship_kind")
        ):
            out.append(
                _diag(
                    code=code,
                    severity=DiagnosticSeverity.WARNING,
                    message=(
                        f'Relationship "{subject}" is active without relationship_kind.'
                    ),
                    subject=subject,
                    remediation=rem,
                    statement=statement,
                    requirement_code=requirement_code,
                )
            )
        return out

    if template == "atr004_type_specific_soft":
        ltype = str(el.get("logical_type") or "")
        if ltype == "decimal" and not (
            _filled(el.get("unit_code")) or _filled(el.get("currency_attribute_ref"))
        ):
            # Soft hint only when name suggests money/amount/quantity
            name = str(el.get("name") or "").lower()
            if any(t in name for t in ("amount", "rate", "quantity", "price", "sum")):
                out.append(
                    _diag(
                        code=code,
                        severity=DiagnosticSeverity.WARNING,
                        message=(
                            f'LogicalAttribute "{subject}" looks quantitative; '
                            "consider unit_code or currency_attribute_ref."
                        ),
                        subject=subject,
                        remediation=rem,
                        statement=statement,
                        requirement_code=requirement_code,
                    )
                )
        if ltype == "datetime" and not _filled(el.get("timezone_policy")):
            out.append(
                _diag(
                    code=code,
                    severity=DiagnosticSeverity.WARNING,
                    message=(
                        f'LogicalAttribute "{subject}" is datetime without timezone_policy.'
                    ),
                    subject=subject,
                    remediation=rem,
                    statement=statement,
                    requirement_code=requirement_code,
                )
            )
        return out

    # Unknown template — surface as warning so authors notice
    out.append(
        _diag(
            code=code,
            severity=DiagnosticSeverity.WARNING,
            message=f"Unknown conditional_branch template: {template!r}.",
            subject=subject,
            remediation="Fix formal_checks expression to a supported template.",
            statement=statement,
            requirement_code=requirement_code,
        )
    )
    return out


def check_formal_requirements(
    body: LinkMLImplementationBody,
    *,
    catalog_path: Path | None = None,
    definition_index: DefinitionIndex | None = None,
    definition_providers: tuple[ExternalDefinitionProvider, ...] = (),
    extra_definition_packages: tuple[dict[str, Any], ...] = (),
) -> tuple[Diagnostic, ...]:
    """Run it-solution catalog formal_checks against implementation body."""
    data = body.data
    if not isinstance(data, dict):
        return ()

    # Skip enterprise conceptual packages
    if data.get("implementation_scope") == "enterprise" and not data.get("solution_ref"):
        return ()

    reqs = load_it_solution_catalog(catalog_path)
    if not reqs:
        return ()

    id_set = _collect_ids(data)
    resolved = resolve_governed(data)
    def_index = definition_index or build_definition_index(
        data,
        *extra_definition_packages,
        providers=definition_providers,
    )
    if definition_index is not None:
        def_index.add_package(data)
        for pkg in extra_definition_packages:
            def_index.add_package(pkg)
    diagnostics: list[Diagnostic] = []

    for req in reqs:
        if not _applies(req, data):
            continue
        statement = req.get("statement")
        requirement_code = req.get("code")
        if requirement_code is not None:
            requirement_code = str(requirement_code)
        applies = req.get("applies_to") if isinstance(req.get("applies_to"), dict) else {}
        target_class = str(
            (applies or {}).get("applies_target_class")
            or ""
        )

        for check in req.get("formal_checks") or []:
            if not isinstance(check, dict):
                continue
            kind = str(check.get("kind") or "")
            tclass = str(check.get("target_class") or target_class or "")
            if not tclass:
                continue
            elements = _iter_targets(data, tclass)
            if tclass in (
                "DataCarrier",
                "TechnicalAsset",
                "AccessPoint",
                "DataContainer",
                "ExecutionAsset",
            ) and (applies or {}).get("applies_target_kinds"):
                elements = _filter_by_kinds(elements, applies or {})

            sev = _severity(check.get("severity"))
            code = str(check.get("diagnostic_code") or check.get("check_id") or "DAMS-REQ")
            rem = check.get("remediation")
            slot = check.get("target_slot")
            use_effective = bool(check.get("effective"))

            for el, subject in elements:
                if kind == "slot_required":
                    val = _slot_value(
                        el,
                        str(slot),
                        subject=subject,
                        effective=use_effective,
                        resolved=resolved,
                    )
                    if slot and not _filled(val):
                        diagnostics.append(
                            _diag(
                                code=code,
                                severity=sev,
                                message=f'{tclass} "{subject}" missing required {slot}.',
                                subject=subject,
                                remediation=rem,
                                statement=statement,
                                requirement_code=requirement_code,
                            )
                        )
                elif kind == "at_least_one_slots":
                    slots = check.get("target_slots") or []
                    if slots and not any(
                        _filled(
                            _slot_value(
                                el,
                                str(s),
                                subject=subject,
                                effective=use_effective,
                                resolved=resolved,
                            )
                        )
                        for s in slots
                    ):
                        diagnostics.append(
                            _diag(
                                code=code,
                                severity=sev,
                                message=(
                                    f'{tclass} "{subject}" needs at least one of: '
                                    + ", ".join(str(s) for s in slots)
                                    + "."
                                ),
                                subject=subject,
                                remediation=rem,
                                statement=statement,
                                requirement_code=requirement_code,
                            )
                        )
                elif kind == "definition_resolvable":
                    prov = resolve_definition(el, def_index, level=tclass)
                    if prov.mode is DefinitionMode.UNRESOLVED or not _filled(
                        prov.text
                    ):
                        detail = prov.diagnostic or "effective definition unresolved"
                        diagnostics.append(
                            _diag(
                                code=code,
                                severity=sev,
                                message=(
                                    f'{tclass} "{subject}" has no resolvable '
                                    f"definition ({detail})."
                                ),
                                subject=subject,
                                remediation=rem,
                                statement=statement,
                                requirement_code=requirement_code,
                            )
                        )
                elif kind == "ref_resolves":
                    if not slot:
                        continue
                    val = el.get(slot)
                    refs = val if isinstance(val, list) else ([val] if val else [])
                    for ref in refs:
                        if ref is None:
                            continue
                        if str(ref) not in id_set:
                            diagnostics.append(
                                _diag(
                                    code=code,
                                    severity=sev,
                                    message=(
                                        f'{tclass} "{subject}" {slot}={ref!r} '
                                        "does not resolve in package."
                                    ),
                                    subject=subject,
                                    remediation=rem,
                                    statement=statement,
                                    requirement_code=requirement_code,
                                )
                            )
                elif kind == "slot_min_cardinality":
                    if not slot:
                        continue
                    val = el.get(slot) or []
                    if not isinstance(val, list) or len(val) < 1:
                        diagnostics.append(
                            _diag(
                                code=code,
                                severity=sev,
                                message=(
                                    f'{tclass} "{subject}" {slot} must have '
                                    "min cardinality 1."
                                ),
                                subject=subject,
                                remediation=rem,
                                statement=statement,
                                requirement_code=requirement_code,
                            )
                        )
                elif kind == "conditional_branch":
                    template = str(check.get("expression") or "")
                    diagnostics.extend(
                        _run_conditional(
                            template=template,
                            el=el if tclass != "ModelPackage" else data,
                            subject=subject,
                            data=data,
                            check=check,
                            statement=statement,
                            requirement_code=requirement_code,
                        )
                    )
                elif kind == "custom":
                    continue

    diagnostics.extend(_cascade_governance_lints(data, resolved))
    diagnostics.extend(_definition_lints(data, def_index))
    diagnostics.extend(check_conceptual_entities(data))
    diagnostics.extend(check_relation_terms(data))
    diagnostics.extend(check_technical_assets(data))
    diagnostics.extend(check_semantic_layer(data))
    return tuple(diagnostics)


def _cascade_governance_lints(
    data: dict[str, Any],
    resolved: dict[str, Any],
) -> list[Diagnostic]:
    """Placeholder owner warning and redundant-override info (ADR-023)."""
    out: list[Diagnostic] = []
    reported_sources: set[str] = set()
    for eid, slots in resolved.items():
        owner = slots.get("data_owner_ref")
        if owner is None or not _filled(owner.value):
            continue
        if str(owner.value) != DATA_OWNER_PLACEHOLDER:
            continue
        source = owner.source_element_id or eid
        if source in reported_sources:
            continue
        reported_sources.add(source)
        out.append(
            _diag(
                code="DAMS-REQ-GEN-001.placeholder",
                severity=DiagnosticSeverity.WARNING,
                message=(
                    f'Effective data_owner_ref on "{source}" is placeholder '
                    f"{DATA_OWNER_PLACEHOLDER!r}."
                ),
                subject=source,
                remediation=(
                    "Replace the package-level data_owner_ref with a real "
                    "org:role/... once ownership is assigned."
                ),
                requirement_code="GEN-001",
            )
        )

    for eid, slot, _value, parent_id in find_redundant_overrides(data):
        out.append(
            _diag(
                code="DAMS-CASCADE-redundant-override",
                severity=DiagnosticSeverity.INFO,
                message=(
                    f'Element "{eid}" declares {slot} equal to effective value '
                    f'inherited from "{parent_id}" (redundant override).'
                ),
                subject=eid,
                remediation=(
                    "Remove the declared slot to inherit from the parent "
                    "(ADR-023 containment cascade)."
                ),
            )
        )
    return out


def _definition_lints(
    data: dict[str, Any],
    def_index: DefinitionIndex,
) -> list[Diagnostic]:
    """ADR-025 definition diagnostics beyond catalog formal_checks."""
    out: list[Diagnostic] = []
    solution_ref = str(data.get("solution_ref") or "") or None

    for tclass in ("LogicalEntity", "LogicalAttribute", "ConceptualEntity"):
        if tclass == "ConceptualEntity":
            elements = []
            for e in data.get("conceptual_entities") or []:
                if isinstance(e, dict):
                    elements.append((e, str(e.get("element_id") or e.get("name"))))
        else:
            elements = _iter_targets(data, tclass)

        for el, subject in elements:
            if not subject:
                continue
            desc = el.get("description")
            title = el.get("title")
            if (
                isinstance(desc, str)
                and isinstance(title, str)
                and desc.strip()
                and desc.strip() == title.strip()
            ):
                out.append(
                    _diag(
                        code="DAMS-DEF-description-eq-title",
                        severity=DiagnosticSeverity.INFO,
                        message=(
                            f'{tclass} "{subject}" description equals title '
                            "(likely not a real definition)."
                        ),
                        subject=subject,
                        remediation=(
                            "Replace description with an unambiguous definition "
                            "or inherit via definition_source_ref (ADR-025)."
                        ),
                    )
                )

            # Own override with source but without rationale
            if (
                isinstance(desc, str)
                and desc.strip()
                and el.get("definition_source_ref")
                and not (
                    isinstance(el.get("definition_rationale"), str)
                    and el["definition_rationale"].strip()
                )
            ):
                out.append(
                    _diag(
                        code="DAMS-DEF-override-without-rationale",
                        severity=DiagnosticSeverity.WARNING,
                        message=(
                            f'{tclass} "{subject}" declares own description with '
                            "definition_source_ref but no definition_rationale."
                        ),
                        subject=subject,
                        remediation=(
                            "Add definition_rationale explaining the adaptation "
                            "or override (ADR-025)."
                        ),
                    )
                )

            for msg in validate_scoped_definition_systems(
                el, solution_ref=solution_ref, index=def_index
            ):
                out.append(
                    _diag(
                        code="DAMS-DEF-scope-ref-invalid",
                        severity=DiagnosticSeverity.ERROR,
                        message=f'{tclass} "{subject}": {msg}',
                        subject=subject,
                        remediation=(
                            "Set scope_ref to an ITSystem in the solution's "
                            "member_system_refs (ADR-025)."
                        ),
                    )
                )

    for eid, parent_id in find_redundant_definition_overrides(data, def_index):
        out.append(
            _diag(
                code="DAMS-DEF-redundant-override",
                severity=DiagnosticSeverity.INFO,
                message=(
                    f'Element "{eid}" declares description equal to inherited '
                    f'definition from "{parent_id}" (redundant override).'
                ),
                subject=eid,
                remediation=(
                    "Remove description to inherit the reference definition "
                    "(ADR-025)."
                ),
            )
        )
    return out


def check_formal_requirements_for_repo(
    body: LinkMLImplementationBody,
) -> tuple[Diagnostic, ...]:
    """Entry used by rules_runner; resolves catalog relative to schema if possible."""
    catalog: Path | None = None
    # Walk from body source path toward repo requirements catalog
    src = Path(body.source_path) if getattr(body, "source_path", None) else None
    if src is not None:
        for parent in [src.parent, *src.parents]:
            candidate = (
                parent
                / "model-assets"
                / "specifications"
                / "moex-dams"
                / "0.1"
                / "requirements"
                / "it-solution-requirements.yaml"
            )
            if candidate.is_file():
                catalog = candidate
                break
            candidate2 = (
                parent
                / "requirements"
                / "it-solution-requirements.yaml"
            )
            if candidate2.is_file():
                catalog = candidate2
                break
    return check_formal_requirements(body, catalog_path=catalog)
