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
    src = tmp_path / "src.yaml"
    tgt = tmp_path / "tgt.yaml"
    src.write_text("id: http://example.org/src\nname: src\n", encoding="utf-8")
    tgt.write_text("id: http://example.org/tgt\nname: tgt\n", encoding="utf-8")
    spec = tmp_path / "bad.yaml"
    spec.write_text(
        """
moex:
  spec_id: bad
  source_schema_revision: a
  target_schema_revision: b
  source_schema: src.yaml
  target_schema: tgt.yaml
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


def test_migration_requires_both_schema_paths(
    provider: LinkmlMapProvider, tmp_path: Path
) -> None:
    spec = tmp_path / "mig.yaml"
    spec.write_text(
        """
moex:
  spec_id: mig
  source_schema_revision: dams-0.1-slice
  target_schema_revision: dams-0.1-next-slice
id: mig
class_derivations:
  LogicalEntity:
    populated_from: LogicalEntity
    slot_derivations:
      name:
        populated_from: name
""",
        encoding="utf-8",
    )
    diags = provider.validate_spec(spec)
    codes = [d.diagnostic_code for d in diags]
    assert codes.count("MAP-SPEC-003") == 2


def test_migration_missing_target_schema_only(
    provider: LinkmlMapProvider, tmp_path: Path
) -> None:
    src = tmp_path / "src.yaml"
    src.write_text("id: http://example.org/src\nname: src\n", encoding="utf-8")
    spec = tmp_path / "mig.yaml"
    spec.write_text(
        """
moex:
  spec_id: mig
  source_schema_revision: a
  target_schema_revision: b
  source_schema: src.yaml
id: mig
class_derivations:
  Person:
    populated_from: Person
""",
        encoding="utf-8",
    )
    diags = provider.validate_spec(spec)
    assert any(d.diagnostic_code == "MAP-SPEC-003" for d in diags)
    assert any("target_schema" in d.diagnostic_message for d in diags)


def test_schema_path_not_found(
    provider: LinkmlMapProvider, tmp_path: Path
) -> None:
    spec = tmp_path / "mig.yaml"
    spec.write_text(
        """
moex:
  spec_id: mig
  source_schema_revision: a
  target_schema_revision: b
  source_schema: missing_src.yaml
  target_schema: missing_tgt.yaml
id: mig
class_derivations:
  Person:
    populated_from: Person
""",
        encoding="utf-8",
    )
    diags = provider.validate_spec(spec)
    assert sum(1 for d in diags if d.diagnostic_code == "MAP-SPEC-004") == 2


def test_identity_equal_revisions_need_not_declare_target(
    provider: LinkmlMapProvider,
) -> None:
    """Equal revisions: source_schema optional for path rule; person-identity OK."""
    diags = provider.validate_spec(TRANSFORMS / "person-identity.yaml")
    assert not any(
        d.diagnostic_code in {"MAP-SPEC-003", "MAP-SPEC-004"} for d in diags
    )
    assert not any(
        d.severity in {DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL}
        for d in diags
    )
