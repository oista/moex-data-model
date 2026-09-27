"""Reference integrity rules for DAMS ModelPackage."""

from __future__ import annotations

from moex_modeling import ConformancePhase, Diagnostic, DiagnosticSeverity
from moex_standard_linkml.domain.body import LinkMLImplementationBody

from moex_dams.mappings.dams_to_graph import package_index


def check_references(body: LinkMLImplementationBody) -> tuple[Diagnostic, ...]:
    data = body.data
    index = package_index(data)
    diagnostics: list[Diagnostic] = []

    def require(ref: str | None, *, subject: str | None, code: str, label: str) -> None:
        if not ref:
            return
        if str(ref) not in index:
            diagnostics.append(
                Diagnostic(
                    diagnostic_code=code,
                    severity=DiagnosticSeverity.ERROR,
                    diagnostic_message=f"Unresolved {label}: {ref}",
                    conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
                    subject_ref=subject,
                )
            )

    for entity in data.get("logical_entities") or []:
        if not isinstance(entity, dict):
            continue
        eid = str(entity.get("element_id") or "")
        for cref in entity.get("conceptual_entity_refs") or []:
            require(
                str(cref),
                subject=eid,
                code="DAMS-REF-001",
                label="conceptual_entity_ref",
            )
        require(
            entity.get("context_ref"),
            subject=eid,
            code="DAMS-REF-002",
            label="context_ref",
        )

    for mapping in data.get("mappings") or []:
        if not isinstance(mapping, dict):
            continue
        mid = str(mapping.get("element_id") or "")
        sources = mapping.get("source_refs") or []
        targets = mapping.get("target_refs") or []
        if not sources or not targets:
            diagnostics.append(
                Diagnostic(
                    diagnostic_code="DAMS-REF-003",
                    severity=DiagnosticSeverity.ERROR,
                    diagnostic_message=(
                        "Mapping must have at least one source_refs and target_refs"
                    ),
                    conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
                    subject_ref=mid or None,
                )
            )
        for ref in list(sources) + list(targets):
            require(
                str(ref),
                subject=mid,
                code="DAMS-REF-004",
                label="mapping endpoint",
            )

    return tuple(diagnostics)
