"""Structural DAMS invariants on ModelPackage instances."""

from __future__ import annotations

from typing import Any

from moex_modeling import (
    ConformancePhase,
    Diagnostic,
    DiagnosticDetail,
    DiagnosticSeverity,
)
from moex_standard_linkml.domain.body import LinkMLImplementationBody


def _struct_diag(
    *,
    code: str,
    message: str,
    subject: str | None,
    severity: DiagnosticSeverity = DiagnosticSeverity.ERROR,
    invariant_id: str | None = None,
) -> Diagnostic:
    details: list[DiagnosticDetail] = [
        DiagnosticDetail(detail_key="finding", detail_value=message)
    ]
    if invariant_id:
        details.append(
            DiagnosticDetail(detail_key="invariant_id", detail_value=invariant_id)
        )
    return Diagnostic(
        diagnostic_code=code,
        severity=severity,
        diagnostic_message=message,
        conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
        subject_ref=subject,
        diagnostic_details=tuple(details),
    )


def check_structural_data(data: dict[str, Any]) -> list[Diagnostic]:
    """Structural checks on a ModelPackage-shaped mapping (INV-052 owner equality)."""
    diagnostics: list[Diagnostic] = []

    if not data.get("element_id"):
        diagnostics.append(
            _struct_diag(
                code="DAMS-STRUCT-001",
                message="ModelPackage requires element_id",
                subject=None,
            )
        )
    if not data.get("name"):
        diagnostics.append(
            _struct_diag(
                code="DAMS-STRUCT-002",
                message="ModelPackage requires name",
                subject=str(data.get("element_id") or "") or None,
            )
        )
    if not data.get("model_version"):
        diagnostics.append(
            _struct_diag(
                code="DAMS-STRUCT-003",
                message="ModelPackage missing model_version",
                subject=str(data.get("element_id") or "") or None,
                severity=DiagnosticSeverity.WARNING,
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
                    _struct_diag(
                        code="DAMS-STRUCT-004",
                        message=(
                            f"key_attribute_refs entry {key_ref!r} is not among "
                            f"attributes of {eid}"
                        ),
                        subject=str(eid) if eid else None,
                    )
                )

        for attr in attrs:
            if not isinstance(attr, dict):
                continue
            owner = attr.get("owner_entity_ref")
            if owner and eid and str(owner) != str(eid):
                diagnostics.append(
                    _struct_diag(
                        code="DAMS-INV-052",
                        message=(
                            f"attribute {attr.get('element_id')} owner_entity_ref "
                            f"{owner!r} differs from parent entity {eid}"
                        ),
                        subject=str(attr.get("element_id")),
                        invariant_id="INV-052",
                    )
                )

    return diagnostics


def check_structural(body: LinkMLImplementationBody) -> tuple[Diagnostic, ...]:
    return tuple(check_structural_data(body.data))
