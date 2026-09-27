"""Conformance diagnostics, assessments, and reports."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from moex_modeling.shared.enums import (
    ConformancePhase,
    ConformanceResult,
    DiagnosticSeverity,
)
from moex_modeling.shared.types import (
    AnnotationPair,
    DiagnosticDetail,
    ImplementationRef,
    SourceLocation,
    SpecificationRef,
    StandardRef,
)


class Diagnostic(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    diagnostic_code: str
    severity: DiagnosticSeverity
    diagnostic_message: str
    conformance_phase: ConformancePhase | None = None
    subject_ref: str | None = None
    source_location: SourceLocation | None = None
    diagnostic_details: tuple[DiagnosticDetail, ...] = ()


class ConformanceAssessment(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    id: str
    description: str | None = None
    annotations: tuple[AnnotationPair, ...] = ()
    assessed_implementation: ImplementationRef
    assessed_specification: SpecificationRef
    assessed_standard: StandardRef
    conformance_result: ConformanceResult
    diagnostics: tuple[Diagnostic, ...] = ()
    assessed_at: str | None = None


class ConformanceReport(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    id: str
    description: str | None = None
    assessed_implementation: ImplementationRef
    assessed_specification: SpecificationRef
    assessed_standard: StandardRef
    overall_result: ConformanceResult
    assessments: tuple[ConformanceAssessment, ...] = ()
    reported_at: str | None = None

    @property
    def is_conformant(self) -> bool:
        return self.overall_result in {
            ConformanceResult.CONFORMANT,
            ConformanceResult.CONFORMANT_WITH_WARNINGS,
        }


def summarize_result(diagnostics: tuple[Diagnostic, ...]) -> ConformanceResult:
    """Derive overall result from diagnostic severities."""
    if not diagnostics:
        return ConformanceResult.CONFORMANT
    has_error = any(
        d.severity in {DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL}
        for d in diagnostics
    )
    if has_error:
        return ConformanceResult.NON_CONFORMANT
    has_warning = any(d.severity == DiagnosticSeverity.WARNING for d in diagnostics)
    if has_warning:
        return ConformanceResult.CONFORMANT_WITH_WARNINGS
    return ConformanceResult.CONFORMANT
