"""Tests for LinkmlMapProvider."""

from __future__ import annotations

from pathlib import Path

import pytest

from moex_linkml_tooling.map_provider import LinkmlMapProvider
from moex_modeling.shared.enums import DiagnosticSeverity

REPO = Path(__file__).resolve().parents[3]
TRANSFORMS = REPO / "model-assets" / "transformations"
FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def provider() -> LinkmlMapProvider:
    return LinkmlMapProvider()


def test_identity_meta_and_preview(provider: LinkmlMapProvider) -> None:
    spec = TRANSFORMS / "person-identity.yaml"
    sample = FIXTURES / "person_sample.json"
    meta = provider.load_spec_meta(spec)
    assert meta.source_schema_revision == "fixture-person-src-0.1"
    assert meta.target_schema_revision == "fixture-person-src-0.1"
    preview = provider.preview(spec, sample)
    assert not any(
        d.severity in {DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL}
        for d in preview.diagnostics
    )
    assert preview.preview_payload.get("name") == "Ada"
    assert preview.preview_payload.get("legacy_code") == "L1"
    assert "Person.name" in preview.preserved_semantics


def test_rename_transform_revisions(provider: LinkmlMapProvider) -> None:
    spec = TRANSFORMS / "person-rename-code.yaml"
    sample = FIXTURES / "person_sample.json"
    meta = provider.load_spec_meta(spec)
    assert meta.source_schema_revision != meta.target_schema_revision
    result = provider.transform_sample(spec, sample)
    assert result.output.get("name") == "Ada"
    assert result.output.get("code") == "L1"
    assert "legacy_code" not in result.output
    assert "Person.legacy_code" in result.lost_semantics


def test_expr_rejected_by_default(provider: LinkmlMapProvider, tmp_path: Path) -> None:
    spec = tmp_path / "bad.yaml"
    spec.write_text(
        """
moex:
  spec_id: bad
  source_schema_revision: a
  target_schema_revision: b
id: bad
class_derivations:
  Person:
    populated_from: Person
    slot_derivations:
      name:
        expr: "name.upper()"
""",
        encoding="utf-8",
    )
    diags = provider.validate_spec(spec)
    assert any(d.diagnostic_code == "MAP-EXPR-001" for d in diags)
