from pathlib import Path

from moex_standard_linkml.solution_xlsx.profile import load_solution_profile
from moex_standard_linkml.solution_xlsx.rules import run_rules
from moex_standard_linkml.solution_xlsx.source import load_solution_ir

FIXTURE = Path(__file__).parent / "fixtures" / "solution-xlsx"


def _codes(diags):
    return {d.code for d in diags}


def test_mdm_rules_cover_defects():
    profile = load_solution_profile(FIXTURE / "profile.yaml")
    system = profile.system_for("MDM")
    assert system is not None
    ir = load_solution_ir(FIXTURE / "fixture.xlsx", profile, src_system="MDM")
    diags = run_rules(ir, profile, system)
    codes = _codes(diags)
    assert "SXI-SRC-010" in codes  # src-only
    assert "SXI-SRC-011" in codes  # ignored sheets
    assert "SXI-ATTR-001" in codes  # nbsp
    assert "SXI-ATTR-002" in codes  # duplicate INN
    assert "SXI-ATTR-004" in codes  # FOOBAR99
    assert "SXI-FK-002" in codes  # MISSING.ID
    assert "SXI-OBJ-001" in codes  # PERSON_CEO synthesized
    assert "SXI-PHY-001" in codes


def test_esed_synthesizes_objects():
    profile = load_solution_profile(FIXTURE / "profile.yaml")
    system = profile.system_for("ЕСЭД")
    assert system is not None
    ir = load_solution_ir(FIXTURE / "fixture.xlsx", profile, src_system="ЕСЭД")
    run_rules(ir, profile, system)
    assert "document" in {o.object_code for o in ir.objects.values()}
    assert "instance" in {o.object_code for o in ir.objects.values()}
