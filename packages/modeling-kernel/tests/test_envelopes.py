"""Smoke tests for kernel envelopes."""

from __future__ import annotations

from moex_modeling import (
    ConformanceReport,
    ConformanceResult,
    Diagnostic,
    DiagnosticSeverity,
    ImplementationRef,
    LifecycleStatus,
    ModelingStandard,
    ReferenceSpecification,
    SpecificationImplementation,
    SpecificationKind,
    SpecificationRef,
    StandardFamily,
    StandardRef,
    SourceDescriptor,
    summarize_result,
)


def test_modeling_standard_frozen() -> None:
    std = ModelingStandard(
        id="moex:standard:linkml",
        name="linkml",
        version="1.8",
        revision="1.8.0",
        content_digest="sha256:abc",
        standard_family=StandardFamily.LINKML,
        specification_uri="https://w3id.org/linkml/",
    )
    assert std.standard_family is StandardFamily.LINKML


def test_implementation_envelope() -> None:
    impl = SpecificationImplementation(
        id="moex:implementation:mdm:0.1.0",
        name="mdm_solution_model",
        version="0.1.0",
        revision="deadbeef",
        content_digest="sha256:deadbeef",
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
        body_ref="mdm-solution-model.yaml",
    )
    assert impl.conforms_to.specification_id == "moex:spec:dams"


def test_summarize_result() -> None:
    assert summarize_result(()) is ConformanceResult.CONFORMANT
    warn = (
        Diagnostic(
            diagnostic_code="X",
            severity=DiagnosticSeverity.WARNING,
            diagnostic_message="warn",
        ),
    )
    assert summarize_result(warn) is ConformanceResult.CONFORMANT_WITH_WARNINGS
    err = (
        Diagnostic(
            diagnostic_code="Y",
            severity=DiagnosticSeverity.ERROR,
            diagnostic_message="err",
        ),
    )
    assert summarize_result(err) is ConformanceResult.NON_CONFORMANT


def test_reference_specification() -> None:
    spec = ReferenceSpecification(
        id="moex:spec:dams",
        name="moex-dams",
        version="0.1.0",
        revision="0.1.0",
        content_digest="sha256:dams",
        specification_kind=SpecificationKind.DATA_MODEL,
        expressed_in=StandardRef(
            standard_id="moex:standard:linkml",
            version_constraint=">=1.7,<2.0",
            standard_revision="1.8.0",
        ),
        root_type="MOEXModelRepository",
    )
    assert spec.root_type == "MOEXModelRepository"


def test_conformance_report_is_conformant() -> None:
    report = ConformanceReport(
        id="report:1",
        assessed_implementation=ImplementationRef(
            implementation_id="i",
            implementation_revision="r",
        ),
        assessed_specification=SpecificationRef(
            specification_id="s",
            specification_version="0.1",
            specification_revision="0.1",
        ),
        assessed_standard=StandardRef(
            standard_id="std",
            version_constraint="1.x",
        ),
        overall_result=ConformanceResult.CONFORMANT_WITH_WARNINGS,
    )
    assert report.is_conformant
