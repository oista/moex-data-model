"""Tests for scripts/airgap_overlay.py (ADR-058 overlay pack)."""

from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "airgap_overlay.py"


def _load_mod():
    spec = importlib.util.spec_from_file_location("airgap_overlay", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["airgap_overlay"] = mod
    spec.loader.exec_module(mod)
    return mod


ao = _load_mod()


def _touch(path: Path, text: str = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _minimal_repo(tmp: Path) -> Path:
    tmp.mkdir(parents=True, exist_ok=True)
    _touch(tmp / "docker" / "api.Dockerfile", "FROM python:3.11-slim\n")
    _touch(tmp / "docker" / "web.Dockerfile", "FROM nginx:1.27-alpine\n")
    _touch(tmp / "docker" / "models-sync.sh", "#!/bin/sh\n")
    _touch(tmp / "docker" / "nginx.conf", "server { listen 80; }\n")
    _touch(tmp / "pyproject.toml", 'version = "0.1.0"\n')
    _touch(tmp / "apps" / "web" / "package-lock.json", "{}\n")
    _touch(tmp / "apps" / "web" / "dist" / "index.html", "<html></html>\n")
    for rel in ao.OVERLAY_TREES:
        _touch(tmp / rel / "marker.txt")
    return tmp


def test_fingerprint_stable_on_version_only(tmp_path: Path) -> None:
    repo = _minimal_repo(tmp_path / "repo")
    (repo / "pyproject.toml").write_text(
        'version = "0.1.0"\nrequires-python = ">=3.11"\ndependencies = [\n    "a>=1",\n]\n',
        encoding="utf-8",
    )
    before = ao.deps_fingerprint(repo)
    (repo / "pyproject.toml").write_text(
        'version = "0.1.1"\nrequires-python = ">=3.11"\ndependencies = [\n    "a>=1",\n]\n',
        encoding="utf-8",
    )
    assert ao.deps_fingerprint(repo) == before


def test_fingerprint_changes_on_dependencies(tmp_path: Path) -> None:
    repo = _minimal_repo(tmp_path / "repo")
    (repo / "pyproject.toml").write_text(
        'version = "0.1.0"\nrequires-python = ">=3.11"\ndependencies = [\n    "a>=1",\n]\n',
        encoding="utf-8",
    )
    before = ao.deps_fingerprint(repo)
    (repo / "pyproject.toml").write_text(
        'version = "0.1.0"\nrequires-python = ">=3.11"\ndependencies = [\n    "a>=1",\n    "b>=2",\n]\n',
        encoding="utf-8",
    )
    assert ao.deps_fingerprint(repo) != before


def test_fingerprint_changes_on_lockfile(tmp_path: Path) -> None:
    repo = _minimal_repo(tmp_path / "repo")
    before = ao.deps_fingerprint(repo)
    (repo / "apps" / "web" / "package-lock.json").write_text('{"lock": 2}\n', encoding="utf-8")
    assert ao.deps_fingerprint(repo) != before


def test_fingerprint_stable_on_src_only(tmp_path: Path) -> None:
    repo = _minimal_repo(tmp_path / "repo")
    before = ao.deps_fingerprint(repo)
    (repo / "apps" / "api" / "marker.txt").write_text("changed\n", encoding="utf-8")
    assert ao.deps_fingerprint(repo) == before


def test_fingerprint_includes_nested_pyproject(tmp_path: Path) -> None:
    repo = _minimal_repo(tmp_path / "repo")
    before = ao.deps_fingerprint(repo)
    _touch(
        repo / "apps" / "api" / "pyproject.toml",
        'version = "0.1.0"\ndependencies = [\n    "fastapi",\n]\n',
    )
    assert ao.deps_fingerprint(repo) != before


def test_assert_overlay_allowed() -> None:
    ao.assert_overlay_allowed("abc", "abc")
    with pytest.raises(ao.OverlayError, match="fingerprint mismatch"):
        ao.assert_overlay_allowed("abc", "def")


def test_new_overlay_tag() -> None:
    assert ao.new_overlay_tag("0.1.0", "a1b2c3d") == "0.1.0-a1b2c3d"
    assert ao.new_overlay_tag("0.1.0", "a1b2c3def012") == "0.1.0-a1b2c3d"
    with pytest.raises(ao.OverlayError):
        ao.new_overlay_tag("0.1.0", "unknown")


def test_dockerfiles_replace_code_without_install() -> None:
    api = ao.dockerfile_overlay_api()
    web = ao.dockerfile_overlay_web()
    assert "rm -rf" in api
    assert "pip " not in api
    assert "COPY packages" in api
    assert "models-sync.sh" in api
    assert "rm -rf" in web
    assert "npm " not in web
    assert "apps/web/dist" in web
    assert "nginx.conf" in web


def test_stage_copies_dist_and_skips_node_modules(tmp_path: Path) -> None:
    repo = _minimal_repo(tmp_path / "repo")
    leftover = repo / "apps" / "api" / "node_modules" / "left"
    _touch(leftover / "pkg.js", "1\n")

    dest = tmp_path / "stage"
    manifest = ao.stage_overlay(
        repo,
        dest,
        parent_tag="0.1.0",
        new_tag="0.1.1-abc1234",
        git_sha="abc1234",
        git_commit_unix_ts=1_700_000_000,
        fingerprint="abc",
    )
    assert manifest["mode"] == "overlay"
    assert manifest["parent_tag"] == "0.1.0"
    assert manifest["images"] == [
        "moex-data-model-api:0.1.1-abc1234",
        "moex-data-model-web:0.1.1-abc1234",
    ]
    assert (dest / "apps" / "web" / "dist" / "index.html").is_file()
    assert (dest / "docker" / "nginx.conf").is_file()
    assert not any(dest.rglob("node_modules"))
    apply = (dest / "apply-overlay.sh").read_text(encoding="utf-8")
    assert "APPLY_ALLOW_DOWNGRADE" in apply
    assert "MODEL_TAG" in apply
    assert "--network=none" in apply
    assert "python3" not in apply
    assert "moex-data-model-api" in apply
    assert "\r" not in apply


def test_stage_fails_without_dist(tmp_path: Path) -> None:
    repo = _minimal_repo(tmp_path / "repo")
    shutil.rmtree(repo / "apps" / "web" / "dist")
    with pytest.raises(ao.OverlayError, match="apps/web/dist"):
        ao.stage_overlay(
            repo,
            tmp_path / "stage",
            parent_tag="0.1.0",
            new_tag="0.1.1-abc1234",
            git_sha="abc1234",
            fingerprint="abc",
        )


def test_overlay_covers_api_image_copies() -> None:
    text = (REPO_ROOT / "docker" / "api.Dockerfile").read_text(encoding="utf-8")
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("COPY "):
            continue
        src = stripped.split()[1]
        covered = src in ao.OVERLAY_FILES or any(
            src == tree or src.startswith(tree + "/") for tree in ao.OVERLAY_TREES
        )
        assert covered, src
