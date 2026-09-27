from __future__ import annotations

from pathlib import Path

import pytest

from moex_standard_linkml.ingest.profile import load_profile
from moex_standard_linkml.ingest.workbook import (
    WorkbookError,
    load_workbook_tables,
    write_csv_dir_as_xlsx,
)


def test_load_csv_directory(fixture_dir: Path, fixture_profile_path: Path) -> None:
    profile = load_profile(fixture_profile_path)
    tables = load_workbook_tables(fixture_dir, profile)
    assert len(tables.entities.rows) == 2
    assert len(tables.attributes.rows) == 6
    assert tables.relationships is not None
    assert len(tables.relationships.rows) == 1
    assert tables.entities.rows[0]["name"] == "TradingClient"
    assert tables.conceptual is not None
    assert len(tables.conceptual.rows) == 2
    assert tables.physical_objects is not None
    assert len(tables.physical_objects.rows) == 1
    assert tables.physical_fields is not None
    assert len(tables.physical_fields.rows) == 1
    assert tables.mappings is not None
    assert len(tables.mappings.rows) == 1


def test_load_xlsx_roundtrip(
    fixture_dir: Path, fixture_profile_path: Path, tmp_path: Path
) -> None:
    profile = load_profile(fixture_profile_path)
    xlsx = tmp_path / "pilot.xlsx"
    write_csv_dir_as_xlsx(fixture_dir, xlsx)
    tables = load_workbook_tables(xlsx, profile)
    assert len(tables.entities.rows) == 2
    assert tables.attributes.rows[0]["entity"] == "TradingClient"
    assert tables.relationships is not None
    assert tables.relationships.rows[0]["name"] == "TradeClient"
    assert tables.conceptual is not None
    assert tables.conceptual.rows[0]["name"] == "Client"


def test_missing_required_sheet(
    fixture_dir: Path, fixture_profile_path: Path, tmp_path: Path
) -> None:
    profile = load_profile(fixture_profile_path)
    # Copy only Attributes — Entities missing
    dest = tmp_path / "partial"
    dest.mkdir()
    (dest / "Attributes.csv").write_text(
        (fixture_dir / "Attributes.csv").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    with pytest.raises(WorkbookError, match="Entities"):
        load_workbook_tables(dest, profile)
