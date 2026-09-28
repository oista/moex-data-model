"""DAMS LogicalEntity slice migration (Stage 7 fixture)."""

from __future__ import annotations

from pathlib import Path

from moex_linkml_tooling.map_provider import LinkmlMapProvider
from moex_modeling.shared.enums import DiagnosticSeverity

REPO = Path(__file__).resolve().parents[3]
TRANSFORMS = REPO / "model-assets" / "transformations"
SPEC = TRANSFORMS / "dams-logical-entity-rename-kind.yaml"
SAMPLE = TRANSFORMS / "samples" / "dams_logical_entity_sample.json"


def test_dams_logical_entity_rename_meta() -> None:
    provider = LinkmlMapProvider(backend="object")
    meta = provider.load_spec_meta(SPEC)
    assert meta.source_schema_revision == "dams-0.1-slice"
    assert meta.target_schema_revision == "dams-0.1-next-slice"
    assert meta.source_schema_revision != meta.target_schema_revision


def test_dams_logical_entity_rename_transform() -> None:
    provider = LinkmlMapProvider(backend="object")
    preview = provider.preview(SPEC, SAMPLE)
    assert not any(
        d.severity in {DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL}
        for d in preview.diagnostics
    ), preview.diagnostics
    assert preview.preview_payload.get("name") == "TradeOrder"
    assert preview.preview_payload.get("description") == "Client trade order"
    assert preview.preview_payload.get("logical_entity_kind") == "core"
    assert "entity_type" not in preview.preview_payload
    assert "LogicalEntity.name" in preview.preserved_semantics
    assert "LogicalEntity.entity_type" in preview.lost_semantics

    result = provider.transform_sample(SPEC, SAMPLE)
    assert result.output.get("logical_entity_kind") == "core"
    assert result.output.get("name") == "TradeOrder"


def test_dams_logical_entity_sql_matches_object() -> None:
    obj = LinkmlMapProvider(backend="object").transform_sample(SPEC, SAMPLE)
    sql = LinkmlMapProvider(backend="sql").transform_sample(SPEC, SAMPLE)
    assert not any(
        d.severity in {DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL}
        for d in obj.diagnostics + sql.diagnostics
    ), (obj.diagnostics, sql.diagnostics)
    assert {k: str(v) for k, v in sql.output.items()} == {
        k: str(v) for k, v in obj.output.items()
    }
