"""L2 governance assignment invariants (ADR-049)."""

from __future__ import annotations

from typing import Any

from moex_modeling import (
    ConformancePhase,
    Diagnostic,
    DiagnosticDetail,
    DiagnosticSeverity,
)

from moex_dams.rules.assignment_resolver import diagnose_governance

_CODE_TO_INV = {
    "conflicting_assignments": ("INV-054", "DAMS-INV-054", DiagnosticSeverity.ERROR),
    "dangling_target": ("INV-055", "DAMS-INV-055", DiagnosticSeverity.ERROR),
    "shadowed_default": ("INV-056", "DAMS-INV-056", DiagnosticSeverity.WARNING),
}


def _diag(
    *,
    code: str,
    message: str,
    subject: str | None,
    invariant_id: str,
    severity: DiagnosticSeverity,
) -> Diagnostic:
    return Diagnostic(
        diagnostic_code=code,
        severity=severity,
        diagnostic_message=message,
        conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
        subject_ref=subject,
        diagnostic_details=(
            DiagnosticDetail(detail_key="finding", detail_value=message),
            DiagnosticDetail(detail_key="invariant_id", detail_value=invariant_id),
        ),
    )


def check_governance_assignments(
    data: dict[str, Any],
    *,
    as_of: str | None = None,
) -> list[Diagnostic]:
    """Emit INV-054…INV-056 from diagnose_governance findings."""
    if not isinstance(data, dict):
        return []
    # Skip when no assignment collections are present (inline-only packages).
    has_asg = any(
        data.get(key)
        for key in (
            "classification_assignments",
            "policy_bindings",
            "ownership_assignments",
        )
    )
    if not has_asg:
        return []

    out: list[Diagnostic] = []
    for finding in diagnose_governance(data, as_of=as_of):
        mapped = _CODE_TO_INV.get(finding.code)
        if mapped is None:
            continue
        iid, dcode, severity = mapped
        out.append(
            _diag(
                code=dcode,
                message=finding.message,
                subject=finding.element_id,
                invariant_id=iid,
                severity=severity,
            )
        )
    return out
