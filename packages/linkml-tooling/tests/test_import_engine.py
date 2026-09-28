"""Tests for SchemaAutomatorImportEngine."""

from __future__ import annotations

from pathlib import Path

import pytest

from moex_linkml_tooling.import_engine import SchemaAutomatorImportEngine
from moex_modeling.import_draft.public import GENERATED_DRAFT_STATUS, ImportSourceType

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def engine() -> SchemaAutomatorImportEngine:
    return SchemaAutomatorImportEngine()


def test_json_schema_import_draft(engine: SchemaAutomatorImportEngine, tmp_path: Path) -> None:
    out = tmp_path / "imports"
    manifest = engine.run_import(
        FIXTURES / "mini.schema.json",
        ImportSourceType.JSON_SCHEMA,
        out,
        options={"job_id": "js-1", "name": "MiniPerson"},
    )
    job_dir = out / "js-1"
    assert manifest.status == GENERATED_DRAFT_STATUS
    assert (job_dir / "job.json").is_file()
    assert (job_dir / "source.json").is_file() or list(job_dir.glob("source*"))
    assert (job_dir / "inferred-schema.yaml").is_file()
    assert (job_dir / "diagnostics.json").is_file()
    text = (job_dir / "inferred-schema.yaml").read_text(encoding="utf-8")
    assert "MiniPerson" in text or "name" in text


def test_sql_import_draft(engine: SchemaAutomatorImportEngine, tmp_path: Path) -> None:
    out = tmp_path / "imports"
    manifest = engine.run_import(
        FIXTURES / "mini.sql",
        ImportSourceType.SQL,
        out,
        options={"job_id": "sql-1", "name": "MiniSql"},
    )
    assert manifest.status == GENERATED_DRAFT_STATUS
    inferred = out / "sql-1" / "inferred-schema.yaml"
    assert inferred.is_file()
    assert "person" in inferred.read_text(encoding="utf-8").lower()


def test_reimport_same_source_digest(
    engine: SchemaAutomatorImportEngine, tmp_path: Path
) -> None:
    out = tmp_path / "imports"
    m1 = engine.run_import(
        FIXTURES / "mini.schema.json",
        ImportSourceType.JSON_SCHEMA,
        out,
        options={"job_id": "a", "name": "Mini"},
    )
    m2 = engine.run_import(
        FIXTURES / "mini.schema.json",
        ImportSourceType.JSON_SCHEMA,
        out,
        options={"job_id": "b", "name": "Mini"},
    )
    assert m1.source_digest == m2.source_digest
    t1 = (out / "a" / "inferred-schema.yaml").read_text(encoding="utf-8").replace(
        "\r\n", "\n"
    )
    t2 = (out / "b" / "inferred-schema.yaml").read_text(encoding="utf-8").replace(
        "\r\n", "\n"
    )
    assert t1 == t2
