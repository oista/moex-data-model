"""Bridge LinkML Validator results to kernel Diagnostic."""

from __future__ import annotations

from pathlib import Path

import yaml
from moex_modeling import (
    ConformancePhase,
    Diagnostic,
    DiagnosticSeverity,
    SourceLocation,
)

from moex_standard_linkml.domain.body import LinkMLImplementationBody


def validate_instance(
    body: LinkMLImplementationBody,
    schema_path: Path | str,
) -> tuple[Diagnostic, ...]:
    """Validate implementation instance against a LinkML schema path."""
    schema_path = Path(schema_path)
    try:
        from moex_standard_linkml.validation import make_linkml_validator
    except ImportError as exc:
        return (
            Diagnostic(
                diagnostic_code="LINKML-VALIDATOR-UNAVAILABLE",
                severity=DiagnosticSeverity.FATAL,
                diagnostic_message=str(exc),
                conformance_phase=ConformancePhase.STANDARD_SYNTAX,
            ),
        )

    try:
        instance = body.data
        if not instance:
            instance = yaml.safe_load(body.path.read_text(encoding="utf-8"))
        validator = make_linkml_validator(schema_path)
        report = validator.validate(instance, body.target_class)
    except Exception as exc:  # noqa: BLE001
        return (
            Diagnostic(
                diagnostic_code="LINKML-VALIDATE-ERROR",
                severity=DiagnosticSeverity.ERROR,
                diagnostic_message=f"{type(exc).__name__}: {exc}",
                conformance_phase=ConformancePhase.STANDARD_SYNTAX,
                source_location=SourceLocation(source_uri=body.source_path),
            ),
        )

    results = list(getattr(report, "results", []) or [])
    diagnostics: list[Diagnostic] = []
    for item in results:
        severity_raw = str(getattr(item, "severity", None) or "ERROR").lower()
        severity = {
            "info": DiagnosticSeverity.INFO,
            "warning": DiagnosticSeverity.WARNING,
            "error": DiagnosticSeverity.ERROR,
            "fatal": DiagnosticSeverity.FATAL,
        }.get(severity_raw, DiagnosticSeverity.ERROR)
        message = getattr(item, "message", None) or str(item)
        diagnostics.append(
            Diagnostic(
                diagnostic_code="LINKML-VALIDATE",
                severity=severity,
                diagnostic_message=str(message),
                conformance_phase=ConformancePhase.STANDARD_SYNTAX,
                subject_ref=body.element_id,
                source_location=SourceLocation(source_uri=body.source_path),
            )
        )
    return tuple(diagnostics)
