from pathlib import Path

import pytest

from moex_standard_linkml.solution_xlsx.normalize import match_key
from moex_standard_linkml.solution_xlsx.profile import load_solution_profile
from moex_standard_linkml.solution_xlsx.source import load_solution_ir

FIXTURE = Path(__file__).parent / "fixtures" / "solution-xlsx"
PROFILE = FIXTURE / "profile.yaml"
XLSX = FIXTURE / "fixture.xlsx"


@pytest.fixture(scope="module")
def profile():
    return load_solution_profile(PROFILE)


def test_load_mdm_target_and_src_only(profile):
    ir = load_solution_ir(XLSX, profile, src_system="MDM")
    assert match_key("ENTERPRISE") in ir.objects
    assert match_key("PERSON") in ir.objects
    assert len(ir.src_only) >= 1
    codes = {(a.object_code, a.attribute_code) for a in ir.attributes}
    assert ("PERSON", "LAST_NAME") in codes  # nbsp stripped


def test_crm_case_match_diagnostic(profile):
    ir = load_solution_ir(XLSX, profile, src_system="CRM")
    assert any(d.code == "SXI-OBJ-003" for d in ir.diagnostics)
    # Canonical from Object sheet
    cust = ir.object_by_code("Customer")
    assert cust is not None
    assert cust.object_code == "CUSTOMER"


def test_esed_blank_object_row(profile):
    ir = load_solution_ir(XLSX, profile, src_system="ЕСЭД")
    assert any(d.code == "SXI-OBJ-002" for d in ir.diagnostics)
    # attributes present; objects synthesized later by rules
    assert any(a.object_code == "document" for a in ir.attributes)
