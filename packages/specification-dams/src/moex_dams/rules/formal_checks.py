"""Execute SpecificationRequirement formal_checks against a ModelPackage body."""

from __future__ import annotations

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

from moex_dams.mappings.iter_mappings import iter_mappings
from moex_dams.rules.assignment_resolver import resolve_governed
from moex_dams.rules.cascade import (
    DATA_OWNER_PLACEHOLDER,
    find_redundant_overrides,
)
from moex_dams.rules.conceptual_entity import check_conceptual_entities
from moex_dams.rules.definitions import (
    DefinitionIndex,
    DefinitionMode,
    ExternalDefinitionProvider,
    build_definition_index,
    find_redundant_definition_overrides,
    resolve_definition,
    validate_scoped_definition_systems,
)
from moex_dams.rules.references import check_references
from moex_dams.rules.relation_terms import check_relation_terms
from moex_dams.rules.semantic_layer import check_semantic_layer
from moex_dams.rules.technical_assets import (
    DATA_CARRIER_KINDS,
    check_technical_assets,
    iter_technical_assets,
)

# DataCarrier kinds (GEN-004 / PDM-003 allowlist).
DATA_CARRYING_KINDS = DATA_CARRIER_KINDS

_REQ_DIR = (
    Path(__file__).resolve().parents[5]
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "requirements"
)
_DEFAULT_CATALOG = _REQ_DIR / "it-solution-requirements.yaml"
_DEFAULT_CONCEPTUAL_CATALOG = _REQ_DIR / "conceptual-model-requirements.yaml"

# ADR-056: requirements in these lifecycle states are not enforced by assess.
# The catalog loader still returns them (viewer / export show deprecated rows).
_INACTIVE_REQUIREMENT_STATUSES = frozenset({"deprecated", "superseded", "rejected"})


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
        "conceptual_entities",
        "data_structures",
        "messages",
    ):
        for item in data.get(key) or []:
            if isinstance(item, dict) and item.get("element_id"):
                ids.add(str(item["element_id"]))
            if key == "logical_entities" and isinstance(item, dict):
                for attr in item.get("attributes") or []:
                    if isinstance(attr, dict) and attr.get("element_id"):
                        ids.add(str(attr["element_id"]))
            if key == "data_structures" and isinstance(item, dict):
                sid = str(item.get("element_id") or "")
                for node in item.get("nodes") or []:
                    if isinstance(node, dict) and node.get("local_key") and sid:
                        ids.add(f"{sid}#{node['local_key']}")
    for m in iter_mappings(data):
        if m.get("element_id"):
            ids.add(str(m["element_id"]))
    return ids


def _iter_targets(
    data: dict[str, Any],
    target_class: str,
) -> list[tuple[dict[str, Any], str | None]]:
    """Return (element_dict, subject_ref) for instances of target_class."""
    if target_class == "ModelPackage":
        return [(data, str(data.get("element_id") or "ModelPackage"))]
    if target_class == "ConceptualEntity":
        out = []
        for e in data.get("conceptual_entities") or []:
            if isinstance(e, dict):
                out.append((e, str(e.get("element_id") or e.get("name"))))
        return out
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
    if target_class == "DataStructure":
        out = []
        for ds in data.get("data_structures") or []:
            if isinstance(ds, dict):
                out.append((ds, str(ds.get("element_id") or ds.get("name"))))
        return out
    if target_class == "SchemaNode":
        out = []
        for s in data.get("data_structures") or []:
            if not isinstance(s, dict):
                continue
            sid = str(s.get("element_id") or "")
            for n in s.get("nodes") or []:
                if not isinstance(n, dict):
                    continue
                # Leaf field-like nodes (SchemaNode scalars); skip containers.
                if str(n.get("node_kind") or "") not in ("scalar", "enum"):
                    continue
                key = str(n.get("local_key") or "")
                subject = f"{sid}#{key}" if sid and key else (key or sid or None)
                out.append((n, subject))
        return out
    if target_class == "Message":
        out = []
        for msg in data.get("messages") or []:
            if isinstance(msg, dict):
                out.append((msg, str(msg.get("element_id") or msg.get("name"))))
        return out
    if target_class == "Mapping":
        out = []
        for m in iter_mappings(data):
            out.append((m, str(m.get("element_id") or m.get("name"))))
        return out
    return []


def _is_data_carrying(obj: dict[str, Any]) -> bool:
    kind = str(obj.get("asset_kind") or "")
    if kind in DATA_CARRYING_KINDS:
        return True
    return bool(obj.get("structure_ref"))


def _has_entity_physical_mapping(data: dict[str, Any], physical_id: str) -> bool:
    logical_ids = {
        str(e.get("element_id"))
        for e in (data.get("logical_entities") or [])
        if isinstance(e, dict) and e.get("element_id")
    }
    for m in iter_mappings(data):
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
    schema_node_ref: str | None = None,
) -> bool:
    for m in iter_mappings(data):
        if str(m.get("mapping_type") or "") != "field_mapping":
            continue
        refs = {str(x) for x in (m.get("source_refs") or []) + (m.get("target_refs") or [])}
        if logical_attr_id and logical_attr_id in refs:
            return True
        if schema_node_ref and schema_node_ref in refs:
            return True
    return False




def _load_yaml_dict(path: Path) -> dict[str, Any] | None:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return raw if isinstance(raw, dict) else None


def _iter_implementation_envelopes(
    repo_root: Path,
) -> list[tuple[str, Path]]:
    """Return (implementation id, body path) for each implementation.yaml envelope."""
    impl_root = repo_root / "model-assets" / "implementations"
    if not impl_root.is_dir():
        return []
    out: list[tuple[str, Path]] = []
    for envelope in sorted(impl_root.rglob("implementation.yaml")):
        raw = _load_yaml_dict(envelope)
        if raw is None:
            continue
        body_ref = raw.get("body_ref") or raw.get("implementation_body")
        if not body_ref:
            continue
        body_path = (envelope.parent / str(body_ref)).resolve()
        if not body_path.is_file():
            continue
        impl_id = str(raw.get("id") or "").strip()
        if not impl_id:
            continue
        out.append((impl_id, body_path))
    return out


def _definition_bearing_ids(data: dict[str, Any]) -> set[str]:
    """Element ids indexed by DefinitionIndex.add_package."""
    ids: set[str] = set()
    for ent in data.get("conceptual_entities") or []:
        if isinstance(ent, dict) and ent.get("element_id"):
            ids.add(str(ent["element_id"]))
    for term in data.get("relation_terms") or []:
        if isinstance(term, dict) and term.get("element_id"):
            ids.add(str(term["element_id"]))
    for ent in data.get("logical_entities") or []:
        if not isinstance(ent, dict) or not ent.get("element_id"):
            continue
        ids.add(str(ent["element_id"]))
        for attr in ent.get("attributes") or []:
            if isinstance(attr, dict) and attr.get("element_id"):
                ids.add(str(attr["element_id"]))
    return ids


def _needed_cross_package_definition_refs(data: dict[str, Any]) -> set[str]:
    """dams: refs that definition cascade may need from another package."""
    local = _collect_ids(data)
    needed: set[str] = set()

    def consider(ref: Any) -> None:
        if not isinstance(ref, str):
            return
        key = ref.strip()
        if not key.startswith("dams:"):
            return
        if key in local:
            return
        needed.add(key)

    for key in ("conceptual_entities", "logical_entities", "relation_terms"):
        for el in data.get(key) or []:
            if not isinstance(el, dict):
                continue
            consider(el.get("definition_source_ref"))
            if key == "logical_entities":
                refs = el.get("conceptual_entity_refs") or []
                if isinstance(refs, list):
                    cleaned = [str(r) for r in refs if r]
                    if len(cleaned) == 1:
                        consider(cleaned[0])
                for attr in el.get("attributes") or []:
                    if isinstance(attr, dict):
                        consider(attr.get("definition_source_ref"))
    return needed


def load_related_definition_packages(
    data: dict[str, Any],
    repo_root: Path,
    *,
    source_path: Path | None = None,
) -> tuple[dict[str, Any], ...]:
    """Load sibling ModelPackage bodies needed for ADR-025 definition cascade.

    Declared ``conceptual_implementation_ref`` is loaded first. Remaining
    unresolved ``dams:`` definition refs are satisfied by scanning other
    implementation envelopes. Missing files do not raise.
    """
    if not isinstance(data, dict):
        return ()

    envelopes = _iter_implementation_envelopes(repo_root)
    if not envelopes:
        return ()

    source_resolved = source_path.resolve() if source_path is not None else None
    by_id: dict[str, Path] = {}
    for impl_id, body_path in envelopes:
        if source_resolved is not None and body_path == source_resolved:
            continue
        # First envelope wins for a given implementation id.
        by_id.setdefault(impl_id, body_path)

    loaded: list[dict[str, Any]] = []
    seen_paths: set[Path] = set()
    indexed_ids: set[str] = set(_definition_bearing_ids(data))

    def take(path: Path) -> dict[str, Any] | None:
        key = path.resolve()
        if key in seen_paths:
            return None
        if source_resolved is not None and key == source_resolved:
            return None
        pkg = _load_yaml_dict(key)
        if pkg is None:
            return None
        seen_paths.add(key)
        loaded.append(pkg)
        indexed_ids.update(_definition_bearing_ids(pkg))
        return pkg

    conceptual_ref = data.get("conceptual_implementation_ref")
    if isinstance(conceptual_ref, str) and conceptual_ref.strip():
        path = by_id.get(conceptual_ref.strip())
        if path is not None:
            take(path)

    needed = _needed_cross_package_definition_refs(data)
    open_refs = {ref for ref in needed if ref not in indexed_ids}
    if open_refs:
        for _impl_id, body_path in envelopes:
            if not open_refs:
                break
            if source_resolved is not None and body_path.resolve() == source_resolved:
                continue
            if body_path.resolve() in seen_paths:
                continue
            pkg = _load_yaml_dict(body_path)
            if pkg is None:
                continue
            pkg_ids = _definition_bearing_ids(pkg)
            closes = open_refs & pkg_ids
            if not closes:
                continue
            seen_paths.add(body_path.resolve())
            loaded.append(pkg)
            indexed_ids.update(pkg_ids)
            open_refs -= closes

    return tuple(loaded)


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
    for m in iter_mappings(data):
        if str(m.get("mapping_type") or "") != "realizes":
            continue
        sources = {str(x) for x in (m.get("source_refs") or [])}
        if logical_id not in sources:
            continue
        for t in m.get("target_refs") or []:
            if t:
                refs.add(str(t))
    return refs



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
    if scope == "enterprise":
        if data.get("implementation_scope") != "enterprise" or data.get("solution_ref"):
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


def _load_catalog_file(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return []
    reqs = raw.get("requirements") or []
    return [r for r in reqs if isinstance(r, dict)]


def load_it_solution_catalog(catalog_path: Path | None = None) -> list[dict[str, Any]]:
    path = catalog_path or _DEFAULT_CATALOG
    if not path.is_file():
        alt = (
            Path("model-assets/specifications/moex-dams/0.1/requirements/"
                 "it-solution-requirements.yaml")
        )
        path = alt if alt.is_file() else path
    return _load_catalog_file(path)


def load_conceptual_catalog(catalog_path: Path | None = None) -> list[dict[str, Any]]:
    path = catalog_path or _DEFAULT_CONCEPTUAL_CATALOG
    if not path.is_file():
        alt = (
            Path("model-assets/specifications/moex-dams/0.1/requirements/"
                 "conceptual-model-requirements.yaml")
        )
        path = alt if alt.is_file() else path
    return _load_catalog_file(path)


def _is_enterprise_package(data: dict[str, Any]) -> bool:
    return (
        data.get("implementation_scope") == "enterprise"
        and not data.get("solution_ref")
    )


def _conceptual_catalog_path(it_solution_path: Path | None) -> Path:
    if it_solution_path is not None:
        sibling = it_solution_path.parent / "conceptual-model-requirements.yaml"
        if sibling.is_file():
            return sibling
    return _DEFAULT_CONCEPTUAL_CATALOG


def _effective_slot(
    resolved: dict[str, Any],
    element_id: str | None,
    slot: str,
) -> Any:
    if not element_id:
        return None
    prov = (resolved.get(element_id) or {}).get(slot)
    return None if prov is None else prov.value


def _entity_or_all_attrs_effective(
    *,
    el: dict[str, Any],
    subject: str | None,
    resolved: dict[str, Any],
    slot: str,
) -> tuple[bool, list[str]]:
    """True if entity effective slot is filled, or every attribute has it filled.

    Returns (ok, missing_attribute_ids). missing is empty when ok or entity has
    no attributes (entity-level miss with empty attrs → ok=False, missing=[]).
    """
    entity_val = _effective_slot(resolved, subject, slot)
    if _filled(entity_val):
        return True, []
    attrs = [a for a in (el.get("attributes") or []) if isinstance(a, dict)]
    if not attrs:
        return False, []
    missing: list[str] = []
    for attr in attrs:
        aid = str(attr.get("element_id") or attr.get("name") or "")
        if not _filled(_effective_slot(resolved, aid or None, slot)):
            missing.append(aid or "(anonymous attribute)")
    return (not missing), missing


def _run_conditional(
    *,
    template: str,
    el: dict[str, Any],
    subject: str | None,
    data: dict[str, Any],
    check: dict[str, Any],
    statement: str | None,
    requirement_code: str | None = None,
    resolved: dict[str, Any] | None = None,
) -> list[Diagnostic]:
    code = str(check.get("diagnostic_code") or check.get("check_id") or "DAMS-REQ")
    sev = _severity(check.get("severity"))
    rem = check.get("remediation")
    out: list[Diagnostic] = []
    req_kw = {"requirement_code": requirement_code}
    resolved = resolved or {}

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

    if template == "pdm003_entity_physical":
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
        # Mapping coverage applies to leaf scalar/enum nodes (SchemaNode).
        if str(el.get("node_kind") or "") not in ("scalar", "enum"):
            return out
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
                            f'SchemaNode "{subject}" status {status} '
                            "requires mapping_rationale."
                        ),
                        subject=subject,
                        remediation=rem,
                        statement=statement,
                        requirement_code=requirement_code,
                    )
                )
            return out
        node_ref = str(subject or "")
        has_map = _has_field_mapping(data, schema_node_ref=node_ref)
        if has_map:
            return out
        out.append(
            _diag(
                code=code,
                severity=sev,
                message=(
                    f'SchemaNode "{subject}" needs field_mapping or '
                    "mapping_coverage_status exception."
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

    if template == "ref003_kind_soft":
        # Severity comes from the FormalCheck (soft warning on legacy REF-003;
        # error when handed to ADR-056 backbone LDM-07).
        if str(el.get("lifecycle_status") or "active") == "active" and not _filled(
            el.get("relationship_kind")
        ):
            out.append(
                _diag(
                    code=code,
                    severity=sev,
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

    if template == "ldm09_data_class":
        ok, missing = _entity_or_all_attrs_effective(
            el=el, subject=subject, resolved=resolved, slot="data_class"
        )
        if not ok:
            if missing:
                detail = " missing on attributes: " + ", ".join(missing)
            else:
                detail = " (entity has no attributes to carry mixed classification)"
            out.append(
                _diag(
                    code=code,
                    severity=sev,
                    message=(
                        f'LogicalEntity "{subject}" must have effective data_class '
                        f"on the entity or on every attribute{detail}."
                    ),
                    subject=subject,
                    remediation=rem,
                    statement=statement,
                    requirement_code=requirement_code,
                )
            )
        return out

    if template == "ldm12_source_system":
        ok, missing = _entity_or_all_attrs_effective(
            el=el,
            subject=subject,
            resolved=resolved,
            slot="source_system_refs",
        )
        if not ok:
            if missing:
                detail = " missing on attributes: " + ", ".join(missing)
            else:
                detail = " (entity has no attributes to carry mixed sources)"
            out.append(
                _diag(
                    code=code,
                    severity=sev,
                    message=(
                        f'LogicalEntity "{subject}" must have effective '
                        f"source_system_refs on the entity or on every attribute"
                        f"{detail}."
                    ),
                    subject=subject,
                    remediation=rem,
                    statement=statement,
                    requirement_code=requirement_code,
                )
            )
        return out

    if template == "ldm01_has_logical_entity":
        if not data.get("logical_entities"):
            out.append(
                _diag(
                    code=code,
                    severity=sev,
                    message="Model package has no logical entities.",
                    subject=subject,
                    remediation=rem,
                    statement=statement,
                    **req_kw,
                )
            )
        return out

    if template == "ldm06_identifier":
        if str(el.get("entity_type") or "") == "technical":
            return out
        keys = el.get("key_attribute_refs") or []
        kind = el.get("business_key_kind")
        if not _filled(keys):
            out.append(
                _diag(
                    code=code,
                    severity=sev,
                    message=(
                        f'LogicalEntity "{subject}" has no key_attribute_refs '
                        "(unique identifier attributes)."
                    ),
                    subject=subject,
                    remediation=rem,
                    statement=statement,
                    **req_kw,
                )
            )
        if kind == "surrogate" and not _filled(el.get("identity_rule")):
            out.append(
                _diag(
                    code=code,
                    severity=sev,
                    message=(
                        f'LogicalEntity "{subject}" uses a surrogate key without '
                        "identity_rule explaining why a business/natural key is absent."
                    ),
                    subject=subject,
                    remediation=rem,
                    statement=statement,
                    **req_kw,
                )
            )
        return out

    if template == "cdm02_relation_typed":
        if str(el.get("lifecycle_status") or "active") != "active":
            return out
        missing: list[str] = []
        if not _filled(el.get("relationship_kind")):
            missing.append("relationship_kind")
        if not _filled(el.get("relation_term_ref")):
            missing.append("relation_term_ref")
        if missing:
            out.append(
                _diag(
                    code=code,
                    severity=sev,
                    message=(
                        f'Relationship "{subject}" is active without '
                        + " and ".join(missing)
                        + "."
                    ),
                    subject=subject,
                    remediation=rem,
                    statement=statement,
                    **req_kw,
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
    as_of: str | None = None,
    assignments: dict[str, list[Any]] | None = None,
    repo_root: Path | None = None,
) -> tuple[Diagnostic, ...]:
    """Run it-solution catalog formal_checks against implementation body."""
    data = body.data
    if not isinstance(data, dict):
        return ()

    if _is_enterprise_package(data):
        reqs = load_conceptual_catalog(_conceptual_catalog_path(catalog_path))
    else:
        reqs = load_it_solution_catalog(catalog_path)
    if not reqs:
        return ()

    id_set = _collect_ids(data)
    effective_as_of = as_of
    if effective_as_of is None and repo_root is not None:
        try:
            from moex_dams.governance.materialize import load_as_of

            effective_as_of = load_as_of(repo_root)
        except Exception:
            effective_as_of = None
    resolved = resolve_governed(
        data, as_of=effective_as_of, assignments=assignments
    )
    related: tuple[dict[str, Any], ...] = ()
    if (
        repo_root is not None
        and not extra_definition_packages
        and definition_index is None
    ):
        src = (
            Path(body.source_path)
            if getattr(body, "source_path", None)
            else None
        )
        related = load_related_definition_packages(
            data, repo_root, source_path=src
        )
    def_index = definition_index or build_definition_index(
        data,
        *extra_definition_packages,
        providers=definition_providers,
    )
    if definition_index is not None:
        def_index.add_package(data)
        for pkg in extra_definition_packages:
            def_index.add_package(pkg)
    elif related:
        for pkg in related:
            def_index.add_package(pkg, overwrite=False)
    diagnostics: list[Diagnostic] = []

    for req in reqs:
        if str(req.get("lifecycle_status") or "") in _INACTIVE_REQUIREMENT_STATUSES:
            continue
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
                            resolved=resolved,
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
    # REF ends resolve here too: REF-001 catalog row is deprecated (ADR-056 PR-9),
    # but DAMS-REF-005/006 must keep firing via references.py.
    diagnostics.extend(check_references(body))
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
                requirement_code="LDM-11",
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
    repo_root: Path | None = None
    # Walk from body source path toward repo requirements catalog
    src = Path(body.source_path) if getattr(body, "source_path", None) else None
    if src is not None:
        for parent in [src.parent, *src.parents]:
            if (
                repo_root is None
                and (parent / "model-assets").is_dir()
                and (parent / "packages").is_dir()
            ):
                repo_root = parent
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
    return check_formal_requirements(
        body, catalog_path=catalog, repo_root=repo_root
    )
