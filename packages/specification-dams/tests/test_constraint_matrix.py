"""Constraint matrix structural checks (ADR-045 / PR-C1…C5; audit A2)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
MATRIX = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "constraints"
    / "constraint-matrix.yaml"
)
CHECK = REPO / "scripts" / "check_constraint_matrix.py"


def _load_matrix() -> dict:
    return yaml.safe_load(MATRIX.read_text(encoding="utf-8"))


def test_matrix_file_exists() -> None:
    assert MATRIX.is_file()
    assert MATRIX.with_name("constraint-matrix.schema.yaml").is_file()


def test_registry_matches_invariants() -> None:
    data = _load_matrix()
    assert "baseline" not in data or not data.get("baseline")
    registry = list(data["invariant_id_registry"])
    invs = list(data["invariants"])
    inv_ids = [inv["id"] for inv in invs]
    assert len(registry) == len(invs)
    assert registry == inv_ids
    assert len(invs) >= 58
    assert inv_ids[0] == "INV-001"
    assert inv_ids[-1] == "INV-058"
    assert inv_ids == sorted(inv_ids)


def test_known_waivers_and_level_status() -> None:
    data = _load_matrix()
    statuses = {inv["id"]: inv["status"] for inv in data["invariants"]}
    level_status = {inv["id"]: inv["level_status"] for inv in data["invariants"]}
    assert level_status["INV-001"]["L1"] == "waived"
    assert level_status["INV-002"]["L3"] == "implemented"
    for inv_id in (
        "INV-018",
        "INV-019",
        "INV-020",
        "INV-021",
        "INV-022",
        "INV-026",
        "INV-028",
        "INV-029",
        "INV-030",
        "INV-031",
        "INV-032",
        "INV-033",
        "INV-034",
        "INV-035",
        "INV-036",
        "INV-037",
        "INV-038",
        "INV-039",
        "INV-040",
        "INV-041",
        "INV-042",
        "INV-043",
        "INV-044",
        "INV-045",
        "INV-046",
        "INV-047",
        "INV-048",
        "INV-049",
        "INV-050",
        "INV-051",
        "INV-052",
        "INV-053",
        "INV-054",
        "INV-055",
        "INV-056",
        "INV-057",
    ):
        assert statuses[inv_id] == "implemented"
    assert level_status["INV-020"]["L3"] == "waived"
    for inv_id in ("INV-023", "INV-024", "INV-025", "INV-027"):
        assert statuses[inv_id] == "waived"
        row = next(i for i in data["invariants"] if i["id"] == inv_id)
        assert row.get("adr_ref")


def test_check_constraint_matrix_script_ok() -> None:
    proc = subprocess.run(
        [sys.executable, str(CHECK), "--no-write-doc", "--gate-strict"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_extra_schema_rule_would_fail() -> None:
    """Sanity: registry must list every invariant id."""
    from moex_dams.rules.constraint_matrix import validate_matrix

    data = _load_matrix()
    data["invariant_id_registry"] = [
        x for x in data["invariant_id_registry"] if x != "INV-001"
    ]
    errors = validate_matrix(data, run_fixtures=False)
    assert any("INV-001" in e and "registry" in e for e in errors)


def test_package_validate_matrix_ok() -> None:
    from moex_dams.rules.constraint_matrix import validate_matrix

    data = _load_matrix()
    assert validate_matrix(data, run_fixtures=False, gate_strict=True) == []
