from pathlib import Path

import pytest

from moex_standard_linkml.solution_xlsx.convert import convert_solution
from moex_standard_linkml.solution_xlsx.diagnostics import Severity
from moex_standard_linkml.solution_xlsx.writer import write_yaml_safe

FIXTURE = Path(__file__).parent / "fixtures" / "solution-xlsx"
REPO = Path(__file__).resolve().parents[3]
SCHEMA = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "schemas"
    / "moex-dams.yaml"
)


def test_convert_crm_builds_package(tmp_path):
    # CRM fixture has no hard errors (case warning only + FK ok)
    result = convert_solution(
        xlsx=FIXTURE / "fixture.xlsx",
        profile=FIXTURE / "profile.yaml",
        src_system="CRM",
        out_dir=tmp_path / "crm",
        report_dir=tmp_path / "crm-report",
        force=True,
        schema=SCHEMA if SCHEMA.is_file() else None,
        skip_validate=not SCHEMA.is_file(),
    )
    assert result.package is not None
    names = {e["name"] for e in result.package["logical_entities"]}
    assert "CUSTOMER" in names
    assert "CONTACT" in names
    assert result.package_path is not None
    assert result.package_path.is_file()
    assert (tmp_path / "crm" / "publish.yaml").is_file()
    # field mappings present
    assert any(
        m.get("mapping_type") == "field_mapping"
        for m in result.package.get("mappings") or []
    )
    assert any(
        m.get("mapping_type") == "entity_physical"
        for m in result.package.get("mappings") or []
    )


def test_writer_no_overwrite(tmp_path):
    target = tmp_path / "out.yaml"
    report = tmp_path / "report"
    write_yaml_safe({"a": 1}, target, force=True, report_dir=report)
    path2, diag = write_yaml_safe({"a": 2}, target, force=False, report_dir=report)
    assert diag is not None
    assert diag.code == "SXI-IO-001"
    assert path2 != target
    assert path2.is_file()


@pytest.mark.skipif(not SCHEMA.is_file(), reason="DAMS schema missing")
def test_convert_esed_validates(tmp_path):
    result = convert_solution(
        xlsx=FIXTURE / "fixture.xlsx",
        profile=FIXTURE / "profile.yaml",
        src_system="ЕСЭД",
        out_dir=tmp_path / "esed",
        force=True,
        schema=SCHEMA,
    )
    assert result.package is not None
    # FK errors none for esed fixture (instance exists)
    assert not any(
        d.code.startswith("SXI-FK") and d.severity is Severity.ERROR
        for d in result.diagnostics
    )
    assert result.validation is not None
    assert result.validation.ok, result.validation.report
