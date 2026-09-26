"""Tests for validation helpers and export / CLI behaviour."""

import json
from pathlib import Path

import pytest

from ontology.fibo.cli import main
from ontology.validation import (
    ValidationError,
    parse_csv_list,
    validate_entity_types,
    validate_formats,
)


FIXTURES = Path(__file__).parent / "fixtures" / "mini_fibo"


def test_validate_entity_types_rejects_unknown():
    with pytest.raises(ValidationError):
        validate_entity_types(["class", "foo"])


def test_validate_formats_ok():
    assert validate_formats(["csv", "xlsx"]) == ["csv", "xlsx"]


def test_parse_csv_list_default():
    assert parse_csv_list(None, default=("a", "b")) == ["a", "b"]
    assert parse_csv_list("x, y", default=("a",)) == ["x", "y"]


def test_cli_export_mini_fibo(tmp_path: Path):
    out = tmp_path / "output"
    code = main(
        [
            "--source",
            str(FIXTURES),
            "--output",
            str(out),
            "--release",
            "master_2026Q2",
            "--domains",
            "FND,BE",
            "--format",
            "csv,xlsx,json",
        ]
    )
    assert code == 0

    all_csv = out / "fibo_definitions_all.csv"
    glossary_csv = out / "fibo_glossary.csv"
    active_csv = out / "fibo_definitions_active.csv"
    deprecated_csv = out / "fibo_definitions_deprecated.csv"
    no_def_csv = out / "fibo_definitions_no_definition.csv"
    errors_csv = out / "fibo_parse_errors.csv"
    xlsx = out / "fibo_definitions.xlsx"
    manifest = out / "fibo_export_manifest.json"
    json_file = out / "fibo_definitions_all.json"

    assert all_csv.exists()
    assert glossary_csv.exists()
    assert active_csv.exists()
    assert deprecated_csv.exists()
    assert no_def_csv.exists()
    assert errors_csv.exists()
    assert xlsx.exists()
    assert manifest.exists()
    assert json_file.exists()

    all_text = all_csv.read_text(encoding="utf-8")
    assert "BusinessDay" in all_text
    assert "OldBusinessDay" not in all_text  # deprecated excluded from all by default
    assert "Monday" not in all_text  # individuals excluded from main CSV
    assert "ExampleOnlyClass" not in all_text

    glossary_text = glossary_csv.read_text(encoding="utf-8")
    assert "BusinessDay" in glossary_text
    assert "local_name" in glossary_text
    assert "hasBusinessDayAdjustment" not in glossary_text  # properties not in glossary
    assert "OldBusinessDay" not in glossary_text

    dep_text = deprecated_csv.read_text(encoding="utf-8")
    assert "OldBusinessDay" in dep_text

    err_text = errors_csv.read_text(encoding="utf-8")
    assert "Broken.rdf" in err_text

    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data["source_release"] == "master_2026Q2"
    assert data["failed_files"] >= 1
    assert data["entities_total"] >= 1
    assert "fibo_definitions_all.csv" in data["output_files"]
    assert "fibo_glossary.csv" in data["output_files"]


def test_cli_fail_on_parse_error(tmp_path: Path):
    out = tmp_path / "output"
    code = main(
        [
            "--source",
            str(FIXTURES),
            "--output",
            str(out),
            "--domains",
            "FND",
            "--fail-on-parse-error",
            "--format",
            "csv",
        ]
    )
    assert code == 1
    assert (out / "fibo_parse_errors.csv").exists()


def test_cli_include_examples(tmp_path: Path):
    out = tmp_path / "output"
    code = main(
        [
            "--source",
            str(FIXTURES),
            "--output",
            str(out),
            "--domains",
            "FND",
            "--include-examples",
            "--format",
            "csv",
        ]
    )
    assert code == 0
    text = (out / "fibo_definitions_all.csv").read_text(encoding="utf-8")
    assert "ExampleOnlyClass" in text


def test_cli_include_deprecated_and_individuals(tmp_path: Path):
    out = tmp_path / "output"
    code = main(
        [
            "--source",
            str(FIXTURES),
            "--output",
            str(out),
            "--domains",
            "FND",
            "--include-deprecated",
            "--include-individuals",
            "--format",
            "csv",
        ]
    )
    assert code == 0
    text = (out / "fibo_definitions_all.csv").read_text(encoding="utf-8")
    assert "OldBusinessDay" in text
    assert "Monday" in text
