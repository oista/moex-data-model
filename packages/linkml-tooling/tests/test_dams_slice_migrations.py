"""DAMS slice identity + LogicalAttribute rename (Stage 7 fixtures)."""

from __future__ import annotations

from pathlib import Path

from moex_linkml_tooling.map_provider import LinkmlMapProvider
from moex_modeling.shared.enums import DiagnosticSeverity

REPO = Path(__file__).resolve().parents[3]
TRANSFORMS = REPO / "model-assets" / "transformations"
ENTITY_IDENTITY = TRANSFORMS / "dams-logical-entity-identity.yaml"
ENTITY_SAMPLE = TRANSFORMS / "samples" / "dams_logical_entity_sample.json"
ATTR_RENAME = TRANSFORMS / "dams-logical-attribute-rename-type.yaml"
ATTR_SAMPLE = TRANSFORMS / "samples" / "dams_logical_attribute_sample.json"


def test_dams_logical_entity_identity_meta() -> None:
    provider = LinkmlMapProvider(backend="object")
    meta = provider.load_spec_meta(ENTITY_IDENTITY)
    assert meta.source_schema_revision == "dams-0.1-slice"
    assert meta.target_schema_revision == "dams-0.1-slice"
    diags = provider.validate_spec(ENTITY_IDENTITY)
    assert not any(
        d.severity in {DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL}
        for d in diags
    ), diags


def test_dams_logical_entity_identity_transform() -> None:
    provider = LinkmlMapProvider(backend="object")
    result = provider.transform_sample(ENTITY_IDENTITY, ENTITY_SAMPLE)
    assert not any(
        d.severity in {DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL}
        for d in result.diagnostics
    ), result.diagnostics
    assert result.output.get("name") == "TradeOrder"
    assert result.output.get("description") == "Client trade order"
    assert result.output.get("entity_type") == "core"
    assert "LogicalEntity.name" in result.preserved_semantics
    assert result.lost_semantics == ()


def test_dams_logical_entity_identity_sql_matches_object() -> None:
    obj = LinkmlMapProvider(backend="object").transform_sample(
        ENTITY_IDENTITY, ENTITY_SAMPLE
    )
    sql = LinkmlMapProvider(backend="sql").transform_sample(
        ENTITY_IDENTITY, ENTITY_SAMPLE
    )
    assert not any(
        d.severity in {DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL}
        for d in obj.diagnostics + sql.diagnostics
    ), (obj.diagnostics, sql.diagnostics)
    assert {k: str(v) for k, v in sql.output.items()} == {
        k: str(v) for k, v in obj.output.items()
    }


def test_dams_logical_attribute_rename_meta() -> None:
    provider = LinkmlMapProvider(backend="object")
    meta = provider.load_spec_meta(ATTR_RENAME)
    assert meta.source_schema_revision == "dams-0.1-slice"
    assert meta.target_schema_revision == "dams-0.1-next-slice"
    diags = provider.validate_spec(ATTR_RENAME)
    assert not any(
        d.severity in {DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL}
        for d in diags
    ), diags


def test_dams_logical_attribute_rename_transform() -> None:
    provider = LinkmlMapProvider(backend="object")
    preview = provider.preview(ATTR_RENAME, ATTR_SAMPLE)
    assert not any(
        d.severity in {DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL}
        for d in preview.diagnostics
    ), preview.diagnostics
    assert preview.preview_payload.get("name") == "orderId"
    assert preview.preview_payload.get("description") == "Client order identifier"
    assert preview.preview_payload.get("attribute_type") == "string"
    assert "logical_type" not in preview.preview_payload
    assert "LogicalAttribute.name" in preview.preserved_semantics
    assert "LogicalAttribute.logical_type" in preview.lost_semantics

    result = provider.transform_sample(ATTR_RENAME, ATTR_SAMPLE)
    assert result.output.get("attribute_type") == "string"
    assert result.output.get("name") == "orderId"


def test_dams_logical_attribute_sql_matches_object() -> None:
    obj = LinkmlMapProvider(backend="object").transform_sample(ATTR_RENAME, ATTR_SAMPLE)
    sql = LinkmlMapProvider(backend="sql").transform_sample(ATTR_RENAME, ATTR_SAMPLE)
    assert not any(
        d.severity in {DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL}
        for d in obj.diagnostics + sql.diagnostics
    ), (obj.diagnostics, sql.diagnostics)
    assert {k: str(v) for k, v in sql.output.items()} == {
        k: str(v) for k, v in obj.output.items()
    }
