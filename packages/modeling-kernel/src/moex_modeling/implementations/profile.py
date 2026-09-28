"""Implementation profile / DAMS model level envelope invariants (ADR-021)."""

from __future__ import annotations

from moex_modeling.conformance.domain import Diagnostic
from moex_modeling.implementations.domain import SpecificationImplementation
from moex_modeling.shared.enums import (
    ConformancePhase,
    DAMSModelLevel,
    DiagnosticSeverity,
    ImplementationProfile,
)


def validate_implementation_profile(
    impl: SpecificationImplementation,
) -> tuple[Diagnostic, ...]:
    """Validate envelope profile/level pairing.

    Legacy envelopes without ``implementation_profile`` are allowed (soft warning).
    Hard errors only when a profile is declared and rules are violated.
    """
    diags: list[Diagnostic] = []
    profile = impl.implementation_profile
    level = impl.dams_model_level
    phase = ConformancePhase.SPECIFICATION

    if profile is None:
        if level is not None:
            diags.append(
                Diagnostic(
                    diagnostic_code="IMPL-PROFILE-001",
                    severity=DiagnosticSeverity.ERROR,
                    diagnostic_message=(
                        "dams_model_level is set but implementation_profile is absent; "
                        "dams_model_level is only valid for dams-data-model"
                    ),
                    conformance_phase=phase,
                    subject_ref=impl.id,
                )
            )
        else:
            diags.append(
                Diagnostic(
                    diagnostic_code="IMPL-PROFILE-000",
                    severity=DiagnosticSeverity.WARNING,
                    diagnostic_message=(
                        "implementation_profile not set (legacy envelope); "
                        "DAMS profile/level rules are not enforced"
                    ),
                    conformance_phase=phase,
                    subject_ref=impl.id,
                )
            )
        return tuple(diags)

    if profile is ImplementationProfile.DAMS_DATA_MODEL:
        if level is None:
            diags.append(
                Diagnostic(
                    diagnostic_code="IMPL-PROFILE-002",
                    severity=DiagnosticSeverity.ERROR,
                    diagnostic_message=(
                        "implementation_profile dams-data-model requires "
                        "dams_model_level (enterprise-conceptual | solution)"
                    ),
                    conformance_phase=phase,
                    subject_ref=impl.id,
                )
            )
    elif level is not None:
        diags.append(
            Diagnostic(
                diagnostic_code="IMPL-PROFILE-003",
                severity=DiagnosticSeverity.ERROR,
                diagnostic_message=(
                    f"dams_model_level is forbidden for implementation_profile "
                    f"{profile.value!r}"
                ),
                conformance_phase=phase,
                subject_ref=impl.id,
            )
        )

    if level is not None and level not in (
        DAMSModelLevel.ENTERPRISE_CONCEPTUAL,
        DAMSModelLevel.SOLUTION,
    ):
        diags.append(
            Diagnostic(
                diagnostic_code="IMPL-PROFILE-004",
                severity=DiagnosticSeverity.ERROR,
                diagnostic_message=f"unsupported dams_model_level {level!r}",
                conformance_phase=phase,
                subject_ref=impl.id,
            )
        )

    return tuple(diags)


def profile_validation_has_errors(diags: tuple[Diagnostic, ...]) -> bool:
    return any(d.severity is DiagnosticSeverity.ERROR for d in diags)
