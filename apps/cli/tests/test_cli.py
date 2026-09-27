"""CLI adapter tests — handlers, not HTML."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from moex_model_cli.__main__ import main
from moex_model_cli.bootstrap import SlicePaths, find_repo_root


def test_find_repo_root(repo_root: Path) -> None:
    assert find_repo_root(repo_root) == repo_root
    nested = repo_root / "apps" / "cli"
    assert find_repo_root(nested) == repo_root


def test_validate_trading_solution(repo_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["validate", "--root", str(repo_root)])
    captured = capsys.readouterr()
    assert code == 0
    assert "overall=conformant" in captured.out
    assert "dams:model/trading/1.0.0" in captured.out


def test_validate_json(repo_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["validate", "--root", str(repo_root), "--json"])
    captured = capsys.readouterr()
    assert code == 0
    payload = json.loads(captured.out)
    assert payload["overall_result"] == "conformant"
    assert payload["assessed_specification"]["specification_id"] == "moex:spec:dams"


def test_publish_writes_json(
    repo_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    out = tmp_path / "slice.json"
    code = main(
        [
            "publish",
            "--root",
            str(repo_root),
            "--out",
            str(out),
            "--implementation-id",
            "moex:implementation:trading:1.0.0",
        ]
    )
    captured = capsys.readouterr()
    assert code == 0
    assert out.is_file()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["summary"]["is_conformant"] is True
    assert data["summary"]["package_id"] == "dams:model/trading/1.0.0"
    assert "wrote" in captured.out


def test_missing_schema_fails_fast(repo_root: Path) -> None:
    missing = repo_root / "no-such-schema.yaml"
    paths = SlicePaths.resolve(root=repo_root, schema=missing)
    assert not paths.schema.is_file()
    with pytest.raises(FileNotFoundError):
        main(["validate", "--root", str(repo_root), "--schema", str(missing)])
