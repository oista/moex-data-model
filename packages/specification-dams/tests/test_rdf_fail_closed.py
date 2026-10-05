"""Fail-closed Turtle parse in generate_artifacts (Stage 8)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from generate_artifacts import main, rdf_ground_digest, write_rdf_artifact  # noqa: E402


def test_rdf_ground_digest_rejects_bad_turtle() -> None:
    with pytest.raises(Exception):
        rdf_ground_digest("@prefix broken ttl !!!")


def test_write_rdf_artifact_rejects_bad_turtle(tmp_path: Path) -> None:
    out = tmp_path / "bad.ttl"
    with pytest.raises(Exception):
        write_rdf_artifact(out, "@prefix broken !!!")


def test_generate_artifacts_main_returns_1_on_bad_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force generate_owl to raise; main must return 1."""
    import generate_artifacts as ga

    def boom(**_kwargs):
        raise ValueError("forced owl failure")

    monkeypatch.setattr(ga, "generate_owl", boom)
    assert main(["--only", "owl"]) == 1
