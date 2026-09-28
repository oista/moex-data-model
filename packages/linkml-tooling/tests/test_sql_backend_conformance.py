"""SQL backend conformance vs ObjectTransformer (ADR-008)."""

from __future__ import annotations

from pathlib import Path

import pytest

from moex_linkml_tooling.map_provider import LinkmlMapProvider
from moex_modeling.shared.enums import DiagnosticSeverity

REPO = Path(__file__).resolve().parents[3]
TRANSFORMS = REPO / "model-assets" / "transformations"
FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize(
    "spec_name",
    ["person-identity.yaml", "person-rename-code.yaml"],
)
def test_sql_matches_object_transformer(spec_name: str) -> None:
    spec = TRANSFORMS / spec_name
    sample = FIXTURES / "person_sample.json"
    obj_provider = LinkmlMapProvider(backend="object")
    sql_provider = LinkmlMapProvider(backend="sql")
    obj_result = obj_provider.transform_sample(spec, sample)
    sql_result = sql_provider.transform_sample(spec, sample)
    assert not any(
        d.severity in {DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL}
        for d in obj_result.diagnostics + sql_result.diagnostics
    ), (obj_result.diagnostics, sql_result.diagnostics)
    # Compare as strings — SQL path stores TEXT
    assert {k: str(v) for k, v in sql_result.output.items()} == {
        k: str(v) for k, v in obj_result.output.items()
    }
    assert (
        sql_result.spec.source_schema_revision
        == obj_result.spec.source_schema_revision
    )
    assert (
        sql_result.spec.target_schema_revision
        == obj_result.spec.target_schema_revision
    )


def test_sql_rejects_expr(tmp_path: Path) -> None:
    spec = tmp_path / "expr.yaml"
    spec.write_text(
        """
moex:
  spec_id: bad-sql
  source_schema_revision: a
  target_schema_revision: b
id: bad-sql
class_derivations:
  Person:
    populated_from: Person
    slot_derivations:
      name:
        expr: "name.upper()"
""",
        encoding="utf-8",
    )
    sample = FIXTURES / "person_sample.json"
    provider = LinkmlMapProvider(backend="sql")
    diags = provider.validate_spec(spec)
    assert any(d.diagnostic_code == "MAP-SQL-001" for d in diags)
    result = provider.transform_sample(spec, sample)
    assert any(d.diagnostic_code == "MAP-SQL-001" for d in result.diagnostics)
    assert result.output == {}
