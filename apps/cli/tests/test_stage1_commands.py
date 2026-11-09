"""Tests for Stage 1 CLI: semantic-diff fail-on, fmt, matrix-check, pubs."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from moex_model_cli.__main__ import main
from moex_model_cli.bootstrap import SlicePaths
from moex_model_cli.commands.matrix_check import check_waiver_expiry
from moex_model_cli.commands.fmt_cmd import canonical_bytes
from moex_model_cli.commands.publish import (
    resolve_implementation_body,
    run_publish,
)


def test_semantic_diff_fail_on_never(repo_root: Path, capsys) -> None:
    left = repo_root / "model-assets/implementations/solutions/mdm/mdm-solution-model.yaml"
    code = main(
        [
            "semantic-diff",
            "--root",
            str(repo_root),
            "--left",
            str(left),
            "--right",
            str(left),
            "--fail-on",
            "never",
        ]
    )
    assert code == 0
    assert "semantic-diff" in capsys.readouterr().out


def test_publications_fresh_ok(repo_root: Path, capsys) -> None:
    code = main(["publications-fresh", "--root", str(repo_root)])
    captured = capsys.readouterr()
    assert code == 0, captured.out
    assert "publications-fresh OK" in captured.out


def test_publish_resolves_body_from_implementation_id(
    repo_root: Path, tmp_path: Path
) -> None:
    """--implementation-id must select that impl's body, not the MDM default."""
    paths = SlicePaths.resolve(root=repo_root)
    crm_id = "moex:implementation:crm:0.1.0"
    crm_body = resolve_implementation_body(repo_root, crm_id)
    assert crm_body != paths.implementation
    out = tmp_path / "crm_slice.json"
    code, text = run_publish(
        paths,
        out=out,
        implementation_id=crm_id,
        skip_gate=True,
    )
    assert code == 0, text
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["summary"]["implementation_id"] == crm_id


def test_fmt_canonical_roundtrip() -> None:
    pytest.importorskip("ruamel.yaml")
    src = "a: 1\nb:\n  - x\n"
    out = canonical_bytes(src)
    assert out.endswith(b"\n")
    assert b"\r" not in out


def test_fmt_check_on_known_file(repo_root: Path, tmp_path: Path, capsys) -> None:
    pytest.importorskip("ruamel.yaml")
    dirty = tmp_path / "dirty.yaml"
    dirty.write_text("a: 1\nb:  2\n", encoding="utf-8")
    code = main(["fmt", "--root", str(repo_root), "--check", str(dirty)])
    assert code == 1
    assert "need format" in capsys.readouterr().out


def test_waiver_expiry_requires_date() -> None:
    data = {
        "invariants": [
            {
                "id": "INV-999",
                "status": "waived",
                "level_status": {"L1": "waived", "L2": "not-applicable", "L3": "not-applicable"},
                "waiver_reason": "test",
                "adr_ref": "ADR-045",
            }
        ]
    }
    errors, _warnings = check_waiver_expiry(data, today=date(2026, 11, 9), require_expires=True)
    assert any("waiver_expires" in e for e in errors)


def test_waiver_expiry_past_fails() -> None:
    data = {
        "invariants": [
            {
                "id": "INV-999",
                "status": "waived",
                "level_status": {"L1": "waived", "L2": "not-applicable", "L3": "not-applicable"},
                "waiver_reason": "test",
                "adr_ref": "ADR-045",
                "waiver_expires": "2020-01-01",
            }
        ]
    }
    errors, _ = check_waiver_expiry(data, today=date(2026, 11, 9), require_expires=True)
    assert any("is past" in e for e in errors)


def test_waiver_expiry_soon_warns() -> None:
    soon = (date(2026, 11, 9) + timedelta(days=7)).isoformat()
    data = {
        "invariants": [
            {
                "id": "INV-999",
                "status": "waived",
                "level_status": {"L1": "waived", "L2": "not-applicable", "L3": "not-applicable"},
                "waiver_reason": "test",
                "adr_ref": "ADR-045",
                "waiver_expires": soon,
            }
        ]
    }
    errors, warnings = check_waiver_expiry(
        data, today=date(2026, 11, 9), require_expires=True, warn_days=14
    )
    assert errors == []
    assert warnings


def test_matrix_check_ok(repo_root: Path, capsys) -> None:
    code = main(
        [
            "matrix-check",
            "--root",
            str(repo_root),
        ]
    )
    captured = capsys.readouterr()
    assert code == 0, captured.out
    assert "matrix-check OK" in captured.out
