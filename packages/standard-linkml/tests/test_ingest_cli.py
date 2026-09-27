from __future__ import annotations

from pathlib import Path

import yaml

from moex_standard_linkml.ingest.cli import main
from moex_standard_linkml.ingest.envelope import GENERATOR_ID
from moex_standard_linkml.ingest.workbook import write_csv_dir_as_xlsx


def test_cli_ingest_csv_validates(
    fixture_dir: Path,
    fixture_profile_path: Path,
    dams_schema: Path,
    tmp_path: Path,
) -> None:
    out = tmp_path / "out"
    rc = main(
        [
            "ingest",
            "--workbook",
            str(fixture_dir),
            "--profile",
            str(fixture_profile_path),
            "--schema",
            str(dams_schema),
            "--out",
            str(out),
        ]
    )
    assert rc == 0, (out / "pilot_solution_model.validation.txt").read_text(
        encoding="utf-8"
    )

    package_path = out / "pilot_solution_model.package.yaml"
    envelope_path = out / "pilot_solution_model.envelope.yaml"
    assert package_path.is_file()
    assert envelope_path.is_file()

    package = yaml.safe_load(package_path.read_text(encoding="utf-8"))
    assert package["element_id"] == "dams:model/pilot/0.1.0"
    assert len(package["logical_entities"]) == 2

    envelope = yaml.safe_load(envelope_path.read_text(encoding="utf-8"))
    assert envelope["conforms_to"]["specification_id"] == "moex-dams"
    assert envelope["implementation_kind"] == "linkml"
    assert envelope["body_ref"] == "pilot_solution_model.package.yaml"
    assert envelope["content_digest"].startswith("sha256:")
    assert envelope["provenance"]["generator_id"] == GENERATOR_ID


def test_cli_ingest_xlsx_validates(
    fixture_dir: Path,
    fixture_profile_path: Path,
    dams_schema: Path,
    tmp_path: Path,
) -> None:
    xlsx = tmp_path / "pilot.xlsx"
    write_csv_dir_as_xlsx(fixture_dir, xlsx)
    out = tmp_path / "out-xlsx"
    rc = main(
        [
            "ingest",
            "--workbook",
            str(xlsx),
            "--profile",
            str(fixture_profile_path),
            "--schema",
            str(dams_schema),
            "--out",
            str(out),
            "--name",
            "from_xlsx",
        ]
    )
    assert rc == 0, (out / "from_xlsx.validation.txt").read_text(encoding="utf-8")
    envelope = yaml.safe_load(
        (out / "from_xlsx.envelope.yaml").read_text(encoding="utf-8")
    )
    assert envelope["body_ref"] == "from_xlsx.package.yaml"
    assert "spreadsheetml" in envelope["source"]["media_type"]


def test_no_schema_automator_dependency() -> None:
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    text = pyproject.read_text(encoding="utf-8")
    assert "schema-automator" not in text
    assert "schemasheets" not in text
