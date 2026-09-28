"""CLI adapter tests — handlers, not HTML."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from moex_model_cli.__main__ import main
from moex_model_cli.bootstrap import (
    DEFAULT_IMPLEMENTATION_ENVELOPE,
    DEFAULT_SPECIFICATION_ENVELOPE,
    SlicePaths,
    find_repo_root,
    resolve_body_from_implementation_envelope,
    resolve_schema_from_specification_envelope,
)


def test_find_repo_root(repo_root: Path) -> None:
    assert find_repo_root(repo_root) == repo_root
    nested = repo_root / "apps" / "cli"
    assert find_repo_root(nested) == repo_root


def test_envelopes_resolve_schema_and_body(repo_root: Path) -> None:
    spec_env = repo_root / DEFAULT_SPECIFICATION_ENVELOPE
    impl_env = repo_root / DEFAULT_IMPLEMENTATION_ENVELOPE
    assert spec_env.is_file()
    assert impl_env.is_file()
    schema = resolve_schema_from_specification_envelope(spec_env)
    body = resolve_body_from_implementation_envelope(impl_env)
    assert schema.name == "moex-dams.yaml"
    assert body.name == "trading-solution-model.yaml"
    paths = SlicePaths.resolve(root=repo_root)
    assert paths.schema == schema
    assert paths.implementation == body


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


def test_lint_and_compile(repo_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["lint", "--root", str(repo_root)]) == 0
    assert "lint diagnostics=" in capsys.readouterr().out
    assert main(["compile", "--root", str(repo_root)]) == 0
    assert "contracts OK" in capsys.readouterr().out


def test_diagram_projects_logical(
    repo_root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "out.dbml"
    assert main(
        [
            "diagram",
            "--root",
            str(repo_root),
            "--profile",
            "logical",
            "--out",
            str(out),
        ]
    ) == 0
    text = out.read_text(encoding="utf-8")
    assert "Table TradingClient" in text
    assert "clientId" in text
    assert (tmp_path / "out.dbml.manifest.json").is_file()
    assert "digest=sha256:" in capsys.readouterr().out


def test_import_er_dictionary_fixture(
    repo_root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    workbook = (
        repo_root / "packages" / "standard-linkml" / "tests" / "fixtures" / "er-dictionary"
    )
    profile = workbook / "profile.yaml"
    out = tmp_path / "ingest-out"
    code = main(
        [
            "import",
            "--root",
            str(repo_root),
            "--workbook",
            str(workbook),
            "--profile",
            str(profile),
            "--out",
            str(out),
            "--skip-validate",
        ]
    )
    captured = capsys.readouterr()
    assert code == 0, captured.out + captured.err
    assert (out / "pilot_solution_model.package.yaml").is_file()
    assert "import OK" in captured.out


def test_map_sssom_and_extract(
    repo_root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sssom = (
        repo_root
        / "model-assets"
        / "transformations"
        / "mappings"
        / "dams-fibo.sssom.yaml"
    )
    assert main(["map", "--root", str(repo_root), "--sssom", str(sssom)]) == 0
    out = capsys.readouterr().out
    assert "moex:mappings:dams-fibo" in out
    assert "bindings=1" in out

    assert main(["map", "--root", str(repo_root)]) == 2
    assert "requires --sssom" in capsys.readouterr().out

    fixture = (
        repo_root
        / "packages"
        / "semantic-mappings"
        / "tests"
        / "fixtures"
        / "mapped_schema.yaml"
    )
    assert (
        main(
            [
                "map",
                "--root",
                str(repo_root),
                "--extract-schema",
                str(fixture),
            ]
        )
        == 0
    )
    assert "bindings=" in capsys.readouterr().out


def test_missing_schema_fails_fast(repo_root: Path) -> None:
    missing = repo_root / "no-such-schema.yaml"
    paths = SlicePaths.resolve(root=repo_root, schema=missing)
    assert not paths.schema.is_file()
    with pytest.raises(FileNotFoundError):
        main(["validate", "--root", str(repo_root), "--schema", str(missing)])


def test_semantic_diff_identical_exit_0(
    repo_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    trading = (
        repo_root
        / "model-assets"
        / "implementations"
        / "solutions"
        / "trading-platform"
        / "trading-solution-model.yaml"
    )
    left = tmp_path / "left.yaml"
    right = tmp_path / "right.yaml"
    text = trading.read_text(encoding="utf-8")
    left.write_text(text, encoding="utf-8")
    right.write_text(text, encoding="utf-8")
    code = main(
        [
            "semantic-diff",
            "--root",
            str(repo_root),
            "--left",
            str(left),
            "--right",
            str(right),
            "--json",
        ]
    )
    captured = capsys.readouterr()
    assert code == 0
    payload = json.loads(captured.out)
    assert payload["changes"] == []


def test_semantic_diff_breaking_exit_1(
    repo_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    import yaml

    trading = (
        repo_root
        / "model-assets"
        / "implementations"
        / "solutions"
        / "trading-platform"
        / "trading-solution-model.yaml"
    )
    left = tmp_path / "left.yaml"
    right = tmp_path / "right.yaml"
    left.write_text(trading.read_text(encoding="utf-8"), encoding="utf-8")
    data = yaml.safe_load(trading.read_text(encoding="utf-8"))
    for entity in data["logical_entities"]:
        if entity.get("element_id") == "dams:logical/trading/Client":
            entity["attributes"] = [
                a
                for a in entity["attributes"]
                if a.get("element_id") != "dams:logical/trading/Client/fullName"
            ]
    right.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    code = main(
        [
            "semantic-diff",
            "--root",
            str(repo_root),
            "--left",
            str(left),
            "--right",
            str(right),
            "--json",
        ]
    )
    captured = capsys.readouterr()
    assert code == 1
    payload = json.loads(captured.out)
    categories = {c["category"] for c in payload["changes"]}
    assert "breaking" in categories
