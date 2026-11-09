"""Tests for moex-model ci-validate and warning baseline."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from moex_model_cli.__main__ import main
from moex_model_cli.commands.ci_validate import (
    SoftFingerprint,
    baseline_from_soft,
    baseline_grew,
    compare_to_baseline,
    write_baseline,
)
from moex_model_cli.commands.breaking_gate import (
    evaluate_breaking_gate,
    latest_approved_breaking,
    report_has_breaking,
)
from moex_model_cli.commands.mr_summary import build_summary_markdown


def test_compare_blocks_new_soft_fingerprint() -> None:
    baseline = baseline_from_soft(
        [
            SoftFingerprint(
                "moex:implementation:mdm:0.1.0",
                "DAMS-REQ-GEN-001.placeholder",
                "subj-a",
            )
        ]
    )
    from moex_model_cli.commands.ci_validate import ImplResult

    result = ImplResult(
        implementation_id="moex:implementation:mdm:0.1.0",
        path="solutions/mdm/implementation.yaml",
        overall="conformant_with_warnings",
        is_conformant=True,
        soft_fps=[
            SoftFingerprint(
                "moex:implementation:mdm:0.1.0",
                "DAMS-REQ-GEN-001.placeholder",
                "subj-a",
            ),
            SoftFingerprint(
                "moex:implementation:mdm:0.1.0",
                "DAMS-REQ-GEN-001.placeholder",
                "subj-NEW",
            ),
        ],
    )
    problems = compare_to_baseline([result], baseline)
    assert any("new soft diagnostic" in p for p in problems)


def test_compare_allows_budgeted_soft() -> None:
    fp = SoftFingerprint(
        "moex:implementation:mdm:0.1.0",
        "DAMS-REQ-GEN-001.placeholder",
        "subj-a",
    )
    baseline = baseline_from_soft([fp])
    from moex_model_cli.commands.ci_validate import ImplResult

    result = ImplResult(
        implementation_id="moex:implementation:mdm:0.1.0",
        path="solutions/mdm/implementation.yaml",
        overall="conformant_with_warnings",
        is_conformant=True,
        soft_fps=[fp],
    )
    assert compare_to_baseline([result], baseline) == []


def test_baseline_growth_detected() -> None:
    old = baseline_from_soft(
        [SoftFingerprint("moex:implementation:mdm:0.1.0", "CODE", "a")]
    )
    new = baseline_from_soft(
        [
            SoftFingerprint("moex:implementation:mdm:0.1.0", "CODE", "a"),
            SoftFingerprint("moex:implementation:mdm:0.1.0", "CODE", "b"),
        ]
    )
    problems = baseline_grew(old, new)
    assert problems


def test_breaking_gate_requires_maintainer_label() -> None:
    events = [
        {
            "action": "add",
            "created_at": "2026-01-02T00:00:00Z",
            "label": {"name": "approved-breaking"},
            "user": {"id": 7, "username": "dev"},
        }
    ]
    versions = [
        {"head_commit_sha": "abc123", "created_at": "2026-01-01T00:00:00Z"},
    ]

    code, text = evaluate_breaking_gate(
        has_breaking=True,
        api_base="http://example/api/v4",
        project_id="12",
        mr_iid="1",
        token="x",
        head_sha="abc123",
        fetch_events=lambda **_: events,
        fetch_versions=lambda **_: versions,
        fetch_access=lambda **_: 30,
    )
    assert code == 1
    assert "access_level=30" in text


def test_breaking_gate_accepts_maintainer() -> None:
    events = [
        {
            "action": "add",
            "created_at": "2026-01-02T00:00:00Z",
            "label": {"name": "approved-breaking"},
            "user": {"id": 1, "username": "maint"},
        }
    ]
    versions = [
        {"head_commit_sha": "abc123", "created_at": "2026-01-01T00:00:00Z"},
    ]
    code, text = evaluate_breaking_gate(
        has_breaking=True,
        api_base="http://example/api/v4",
        project_id="12",
        mr_iid="1",
        token="x",
        head_sha="abc123",
        fetch_events=lambda **_: events,
        fetch_versions=lambda **_: versions,
        fetch_access=lambda **_: 40,
    )
    assert code == 0
    assert "breaking-gate OK" in text


def test_breaking_gate_rejects_label_before_push() -> None:
    events = [
        {
            "action": "add",
            "created_at": "2026-01-01T00:00:00Z",
            "label": {"name": "approved-breaking"},
            "user": {"id": 1, "username": "maint"},
        }
    ]
    versions = [
        {"head_commit_sha": "abc123", "created_at": "2026-01-02T00:00:00Z"},
    ]
    code, text = evaluate_breaking_gate(
        has_breaking=True,
        api_base="http://example/api/v4",
        project_id="12",
        mr_iid="1",
        token="x",
        head_sha="abc123",
        fetch_events=lambda **_: events,
        fetch_versions=lambda **_: versions,
        fetch_access=lambda **_: 40,
    )
    assert code == 1
    assert "re-add the label" in text


def test_latest_approved_breaking_cleared_on_remove() -> None:
    events = [
        {
            "action": "add",
            "created_at": "2026-01-01T00:00:00Z",
            "label": {"name": "approved-breaking"},
            "user": {"id": 1, "username": "maint"},
        },
        {
            "action": "remove",
            "created_at": "2026-01-02T00:00:00Z",
            "label": {"name": "approved-breaking"},
            "user": {"id": 1, "username": "maint"},
        },
    ]
    assert latest_approved_breaking(events) is None


def test_mr_summary_markdown_contains_marker() -> None:
    text = build_summary_markdown(
        ci_validate={"implementations": [], "problems": []},
        semantic_diff_text="breaking=0",
        matrix_check={"ok": True},
    )
    assert "<!-- moex-ci-summary -->" in text
    assert "Semantic diff" in text


def _deploy_baseline(repo_root: Path) -> Path:
    return repo_root / "deploy" / "models-repo" / ".moex" / "warning-baseline.yaml"


def test_ci_validate_cli_ok_on_repo(repo_root: Path, capsys) -> None:
    code = main(
        [
            "ci-validate",
            "--root",
            str(repo_root),
            "--baseline",
            str(_deploy_baseline(repo_root)),
        ]
    )
    captured = capsys.readouterr()
    assert code == 0, captured.out
    assert "ci-validate OK" in captured.out


def test_ci_validate_json_and_reports(repo_root: Path, tmp_path: Path, capsys) -> None:
    junit = tmp_path / "junit.xml"
    cq = tmp_path / "cq.json"
    code = main(
        [
            "ci-validate",
            "--root",
            str(repo_root),
            "--baseline",
            str(_deploy_baseline(repo_root)),
            "--json",
            "--junit",
            str(junit),
            "--codequality",
            str(cq),
        ]
    )
    captured = capsys.readouterr()
    assert code == 0, captured.out
    payload = json.loads(captured.out)
    assert payload["ok"] is True
    assert junit.is_file()
    assert cq.is_file()
    assert json.loads(cq.read_text(encoding="utf-8")) == []


def test_report_has_breaking_from_changes_when_flag_omitted() -> None:
    assert report_has_breaking({"changes": [{"category": "breaking"}]}) is True
    assert report_has_breaking({"has_breaking": False, "changes": []}) is False
    assert report_has_breaking({"has_breaking": True, "changes": []}) is True


def test_semantic_diff_json_includes_has_breaking(repo_root: Path, capsys) -> None:
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
            "--json",
            "--fail-on",
            "never",
        ]
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["has_breaking"] is False


def test_gated_hard_error_blocks() -> None:
    from moex_model_cli.commands.ci_validate import ImplResult

    baseline = baseline_from_soft([])
    result = ImplResult(
        implementation_id="moex:implementation:mdm:0.1.0",
        path="solutions/mdm/implementation.yaml",
        overall="nonconformant",
        is_conformant=False,
        hard=[{"code": "LINKML-VALIDATE", "message": "required slot missing"}],
    )
    problems = compare_to_baseline([result], baseline)
    assert any("LINKML-VALIDATE" in p for p in problems)


def test_write_baseline_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "baseline.yaml"
    baseline = baseline_from_soft(
        [SoftFingerprint("moex:implementation:mdm:0.1.0", "CODE", "s")]
    )
    write_baseline(path, baseline)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert raw["gate_implementations"]
    assert raw["counts_by_code"]["moex:implementation:mdm:0.1.0"]["CODE"] == 1
