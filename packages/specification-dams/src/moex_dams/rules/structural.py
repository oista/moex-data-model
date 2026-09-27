"""Structural DAMS invariants on ModelPackage instances."""

from __future__ import annotations

from moex_modeling import ConformancePhase, Diagnostic, DiagnosticSeverity
from moex_standard_linkml.domain.body import LinkMLImplementationBody


def check_structural(body: LinkMLImplementationBody) -> tuple[Diagnostic, ...]:
    data = body.data
    diagnostics: list[Diagnostic] = []

    if not data.get("element_id"):
        diagnostics.append(
            Diagnostic(
                diagnostic_code="DAMS-STRUCT-001",
                severity=DiagnosticSeverity.ERROR,
                diagnostic_message="ModelPackage requires element_id",
                conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
                subject_ref=body.source_path,
            )
        )
    if not data.get("name"):
        diagnostics.append(
            Diagnostic(
                diagnostic_code="DAMS-STRUCT-002",
                severity=DiagnosticSeverity.ERROR,
                diagnostic_message="ModelPackage requires name",
                conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
                subject_ref=body.element_id,
            )
        )
    if not data.get("model_version"):
        diagnostics.append(
            Diagnostic(
                diagnostic_code="DAMS-STRUCT-003",
                severity=DiagnosticSeverity.WARNING,
                diagnostic_message="ModelPackage missing model_version",
                conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
                subject_ref=body.element_id,
            )
        )

    logical = data.get("logical_entities") or []
    for entity in logical:
        if not isinstance(entity, dict):
            continue
        eid = entity.get("element_id")
        attrs = entity.get("attributes") or []
        key_refs = entity.get("key_attribute_refs") or []
        attr_ids = {
            str(a.get("element_id"))
            for a in attrs
            if isinstance(a, dict) and a.get("element_id")
        }
        for key_ref in key_refs:
            if str(key_ref) not in attr_ids:
                diagnostics.append(
                    Diagnostic(
                        diagnostic_code="DAMS-STRUCT-004",
                        severity=DiagnosticSeverity.ERROR,
                        diagnostic_message=(
                            f"key_attribute_refs entry {key_ref!r} is not among "
                            f"attributes of {eid}"
                        ),
                        conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
                        subject_ref=str(eid) if eid else None,
                    )
                )

        for attr in attrs:
            if not isinstance(attr, dict):
                continue
            owner = attr.get("owner_entity_ref")
            if owner and eid and str(owner) != str(eid):
                diagnostics.append(
                    Diagnostic(
                        diagnostic_code="DAMS-STRUCT-005",
                        severity=DiagnosticSeverity.WARNING,
                        diagnostic_message=(
                            f"attribute {attr.get('element_id')} owner_entity_ref "
                            f"{owner!r} differs from parent entity {eid}"
                        ),
                        conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
                        subject_ref=str(attr.get("element_id")),
                    )
                )

    return tuple(diagnostics)
