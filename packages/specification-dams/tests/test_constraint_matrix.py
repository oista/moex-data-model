"""Constraint matrix structural checks (ADR-045 / PR-C1)."""

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


def test_matrix_file_exists() -> None:
    assert MATRIX.is_file()
    assert MATRIX.with_name("constraint-matrix.schema.yaml").is_file()


def test_baseline_has_seventeen_rules() -> None:
    data = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    assert len(data["baseline"]["rules"]) == 17
    assert len(data["invariants"]) == 27
    statuses = {inv["id"]: inv["status"] for inv in data["invariants"]}
    for i in range(1, 18):
        assert statuses[f"INV-{i:03d}"] == "implemented-untested"
    for i in range(18, 28):
        assert statuses[f"INV-{i:03d}"] == "planned"


def test_check_constraint_matrix_script_ok() -> None:
    proc = subprocess.run(
        [sys.executable, str(CHECK), "--no-write-doc"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_extra_schema_rule_would_fail(tmp_path: Path, monkeypatch) -> None:
    """Sanity: baseline digest is pinned; mutating matrix digest fails the check."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("check_constraint_matrix", CHECK)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    data = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    data["baseline"]["rules_sha256"] = "0" * 64
    errors = mod.validate_matrix(data)
    assert any("rules_sha256 mismatch" in e for e in errors)
