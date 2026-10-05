"""DAMS package-level profile/level body rules (ADR-021)."""

from __future__ import annotations

from moex_modeling import ConformancePhase, Diagnostic, DiagnosticSeverity
from moex_standard_linkml.domain.body import LinkMLImplementationBody

ENTERPRISE_CONCEPTUAL_REF = "moex:implementation:moex-enterprise-conceptual-model:0.1"


def check_dams_model_level(body: LinkMLImplementationBody) -> tuple[Diagnostic, ...]:
    """Enforce enterprise-conceptual vs solution body constraints when declared.

    Packages without ``implementation_scope`` are legacy — soft warning only.
    """
    data = body.data
    diagnostics: list[Diagnostic] = []
    scope = data.get("implementation_scope")
    subject = str(data.get("element_id") or body.element_id or body.source_path)

    if not scope:
        diagnostics.append(
            Diagnostic(
                diagnostic_code="DAMS-LEVEL-000",
                severity=DiagnosticSeverity.WARNING,
                diagnostic_message=(
                    "ModelPackage missing implementation_scope "
                    "(legacy); enterprise/solution rules not enforced"
                ),
                conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
                subject_ref=subject,
            )
        )
        return tuple(diagnostics)

    conceptual = data.get("conceptual_entities") or []
    technical = (
        (data.get("data_carriers") or [])
        or (data.get("access_points") or [])
        or (data.get("data_containers") or [])
        or (data.get("execution_assets") or [])
    )
    logical = data.get("logical_entities") or []
    mappings = data.get("mappings") or []
    solution_ref = data.get("solution_ref")
    conceptual_ref = data.get("conceptual_implementation_ref")

    if scope == "enterprise":
        if solution_ref:
            diagnostics.append(
                Diagnostic(
                    diagnostic_code="DAMS-LEVEL-001",
                    severity=DiagnosticSeverity.ERROR,
                    diagnostic_message=(
                        "enterprise implementation_scope forbids solution_ref"
                    ),
                    conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
                    subject_ref=subject,
                )
            )
        if not conceptual:
            diagnostics.append(
                Diagnostic(
                    diagnostic_code="DAMS-LEVEL-002",
                    severity=DiagnosticSeverity.ERROR,
                    diagnostic_message=(
                        "enterprise-conceptual package requires conceptual_entities"
                    ),
                    conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
                    subject_ref=subject,
                )
            )
        if technical:
            diagnostics.append(
                Diagnostic(
                    diagnostic_code="DAMS-LEVEL-003",
                    severity=DiagnosticSeverity.ERROR,
                    diagnostic_message=(
                        "enterprise-conceptual package forbids technical assets "
                        "(data_carriers / access_points / data_containers / "
                        "execution_assets)"
                    ),
                    conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
                    subject_ref=subject,
                )
            )

    elif scope == "solution":
        if not solution_ref:
            diagnostics.append(
                Diagnostic(
                    diagnostic_code="DAMS-LEVEL-004",
                    severity=DiagnosticSeverity.ERROR,
                    diagnostic_message="solution scope requires solution_ref",
                    conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
                    subject_ref=subject,
                )
            )
        if not conceptual_ref:
            diagnostics.append(
                Diagnostic(
                    diagnostic_code="DAMS-LEVEL-005",
                    severity=DiagnosticSeverity.ERROR,
                    diagnostic_message=(
                        "solution scope requires conceptual_implementation_ref"
                    ),
                    conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
                    subject_ref=subject,
                )
            )
        if not logical and not technical:
            diagnostics.append(
                Diagnostic(
                    diagnostic_code="DAMS-LEVEL-006",
                    severity=DiagnosticSeverity.ERROR,
                    diagnostic_message=(
                        "solution package requires at least one logical_entities "
                        "or technical-asset facet (data_carriers / access_points / "
                        "data_containers / execution_assets)"
                    ),
                    conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
                    subject_ref=subject,
                )
            )
        realizes = [
            m
            for m in mappings
            if isinstance(m, dict) and m.get("mapping_type") == "realizes"
        ]
        na = data.get("realizes_not_applicable")
        if not realizes and not na:
            diagnostics.append(
                Diagnostic(
                    diagnostic_code="DAMS-LEVEL-007",
                    severity=DiagnosticSeverity.ERROR,
                    diagnostic_message=(
                        "solution package requires at least one mapping_type: realizes "
                        "or realizes_not_applicable with rationale"
                    ),
                    conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
                    subject_ref=subject,
                )
            )

    return tuple(diagnostics)
