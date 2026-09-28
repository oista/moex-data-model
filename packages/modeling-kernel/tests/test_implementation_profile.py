"""Tests for implementation_profile / dams_model_level envelope rules (ADR-021)."""

from __future__ import annotations

from moex_modeling import (
    DAMSModelLevel,
    DiagnosticSeverity,
    ImplementationProfile,
    LifecycleStatus,
    SpecificationImplementation,
    SpecificationRef,
    StandardFamily,
    SourceDescriptor,
    profile_validation_has_errors,
    validate_implementation_profile,
)


def _impl(**kwargs) -> SpecificationImplementation:
    base = dict(
        id="moex:implementation:test:0.1",
        name="test",
        version="0.1.0",
        revision="0.1.0",
        content_digest="sha256:test",
        conforms_to=SpecificationRef(
            specification_id="moex:spec:dams",
            specification_version="0.1.0",
            specification_revision="0.1.0",
        ),
        implementation_kind=StandardFamily.LINKML,
        lifecycle_status=LifecycleStatus.DRAFT,
        source=SourceDescriptor(
            source_uri="file:///tmp/model.yaml",
            source_root_type="ModelPackage",
        ),
    )
    base.update(kwargs)
    return SpecificationImplementation(**base)


def test_legacy_envelope_warns_without_profile() -> None:
    diags = validate_implementation_profile(_impl())
    assert not profile_validation_has_errors(diags)
    assert any(d.diagnostic_code == "IMPL-PROFILE-000" for d in diags)


def test_dams_data_model_requires_level() -> None:
    diags = validate_implementation_profile(
        _impl(implementation_profile=ImplementationProfile.DAMS_DATA_MODEL)
    )
    assert profile_validation_has_errors(diags)
    assert any(d.diagnostic_code == "IMPL-PROFILE-002" for d in diags)


def test_dams_data_model_with_level_ok() -> None:
    diags = validate_implementation_profile(
        _impl(
            implementation_profile=ImplementationProfile.DAMS_DATA_MODEL,
            dams_model_level=DAMSModelLevel.ENTERPRISE_CONCEPTUAL,
        )
    )
    assert not profile_validation_has_errors(diags)


def test_ontology_application_forbids_dams_level() -> None:
    diags = validate_implementation_profile(
        _impl(
            implementation_profile=ImplementationProfile.ONTOLOGY_APPLICATION,
            dams_model_level=DAMSModelLevel.SOLUTION,
            implementation_kind=StandardFamily.OWL,
        )
    )
    assert profile_validation_has_errors(diags)
    assert any(d.diagnostic_code == "IMPL-PROFILE-003" for d in diags)


def test_level_without_profile_is_error() -> None:
    diags = validate_implementation_profile(
        _impl(dams_model_level=DAMSModelLevel.SOLUTION)
    )
    assert profile_validation_has_errors(diags)
    assert any(d.diagnostic_code == "IMPL-PROFILE-001" for d in diags)
    assert all(
        d.severity is DiagnosticSeverity.ERROR
        for d in diags
        if d.diagnostic_code == "IMPL-PROFILE-001"
    )
