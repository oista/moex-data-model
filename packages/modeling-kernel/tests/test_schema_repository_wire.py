"""Tests for SchemaRepository port and diagnostic wire mapping."""

from __future__ import annotations

from pathlib import Path

from moex_modeling import (
    Diagnostic,
    DiagnosticDetail,
    DiagnosticSeverity,
    SchemaRepository,
    SourceLocation,
    SpecificationRef,
    diagnostic_to_wire,
)


def test_schema_repository_protocol_is_runtime_checkable() -> None:
    class _Stub:
        def resolve_specification_path(self, specification: SpecificationRef) -> Path:
            return Path("x.yaml")

        def load_specification(self, specification: SpecificationRef) -> object:
            return object()

        def load_implementation(self, implementation, *, path):  # noqa: ANN001
            return object()

    assert isinstance(_Stub(), SchemaRepository)


def test_diagnostic_to_wire_maps_fields() -> None:
    d = Diagnostic(
        diagnostic_code="MOEX-MAPPING-001",
        severity=DiagnosticSeverity.ERROR,
        diagnostic_message="Mapping must have at least one source and target",
        subject_ref="moex:mapping:123",
        source_location=SourceLocation(
            source_uri="model.yaml",
            line=241,
            json_pointer="mappings[3]",
        ),
        diagnostic_details=(
            DiagnosticDetail(
                detail_key="suggestion",
                detail_value="Add source_element_refs and target_element_refs",
            ),
        ),
    )
    wire = diagnostic_to_wire(d)
    assert wire == {
        "code": "MOEX-MAPPING-001",
        "severity": "error",
        "message": "Mapping must have at least one source and target",
        "path": "mappings[3]",
        "element_id": "moex:mapping:123",
        "source": "model.yaml",
        "line": 241,
        "suggestion": "Add source_element_refs and target_element_refs",
    }


def test_diagnostic_to_wire_defaults_optional() -> None:
    d = Diagnostic(
        diagnostic_code="X",
        severity=DiagnosticSeverity.WARNING,
        diagnostic_message="warn",
    )
    wire = diagnostic_to_wire(d)
    assert wire["code"] == "X"
    assert wire["path"] is None
    assert wire["element_id"] is None
    assert wire["suggestion"] is None
