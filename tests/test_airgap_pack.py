"""Tests for contour-drop helpers (ADR-058)."""

from __future__ import annotations

import importlib.util
import json
import sys
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "airgap_overlay.py"


def _load_mod():
    spec = importlib.util.spec_from_file_location("airgap_overlay_pack", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["airgap_overlay_pack"] = mod
    spec.loader.exec_module(mod)
    return mod


ao = _load_mod()


def test_bump_patch() -> None:
    assert ao.bump_patch("0.1.0") == "0.1.1"
    assert ao.bump_patch("0.1.9") == "0.1.10"
    with pytest.raises(ao.OverlayError, match="semver"):
        ao.bump_patch("0.1")
    with pytest.raises(ao.OverlayError, match="semver"):
        ao.bump_patch("v0.1.0")


def test_write_pyproject_version(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('name = "x"\nversion = "0.1.0"\n', encoding="utf-8")
    old = ao.write_pyproject_version(tmp_path, "0.1.1")
    assert old == "0.1.0"
    assert 'version = "0.1.1"' in pyproject.read_text(encoding="utf-8")


def test_assert_version_not_reused(tmp_path: Path) -> None:
    manifest = tmp_path / "moex-model-0.1.1.manifest.json"
    manifest.write_text(json.dumps({"git_sha": "aaaaaaa", "mode": "full"}), encoding="utf-8")
    ao.assert_version_not_reused(tmp_path, "0.1.1", "aaaaaaa")
    with pytest.raises(ao.OverlayError, match="already packed"):
        ao.assert_version_not_reused(tmp_path, "0.1.1", "bbbbbbb")


def test_drop_inventory_overlay_ok() -> None:
    ao.assert_contour_drop_inventory(
        [
            "APPLY.md",
            "apply-contour.sh",
            "moex-model-0.1.1-9eaa59b-overlay.zip",
            "release-bundle-0.1.1-9eaa59b.zip",
        ],
        mode="overlay",
    )


def test_drop_inventory_forbids_base_images() -> None:
    with pytest.raises(ao.OverlayError, match="grafana"):
        ao.assert_contour_drop_inventory(
            [
                "APPLY.md",
                "apply-contour.sh",
                "grafana/grafana:11.tar",
                "release-bundle-x.zip",
            ],
            mode="full",
        )
    with pytest.raises(ao.OverlayError, match="nginx:alpine"):
        ao.assert_contour_drop_inventory(
            [
                "APPLY.md",
                "apply-contour.sh",
                "moex-model-0.1.1.tar.gz",
                "nginx:alpine.tar",
                "release-bundle-0.1.1.zip",
            ],
            mode="full",
        )


def test_drop_inventory_full_requires_tar() -> None:
    with pytest.raises(ao.OverlayError, match="tar.gz"):
        ao.assert_contour_drop_inventory(
            ["APPLY.md", "apply-contour.sh", "release-bundle-0.1.1.zip"],
            mode="full",
        )
    ao.assert_contour_drop_inventory(
        [
            "APPLY.md",
            "apply-contour.sh",
            "moex-model-0.1.1.tar.gz",
            "release-bundle-0.1.1.zip",
        ],
        mode="full",
    )


def test_drop_inventory_requires_apply_script() -> None:
    with pytest.raises(ao.OverlayError, match="apply-contour"):
        ao.assert_contour_drop_inventory(
            ["APPLY.md", "moex-model-0.1.1.tar.gz", "release-bundle-0.1.1.zip"],
            mode="full",
        )


def test_assemble_contour_zip(tmp_path: Path) -> None:
    overlay = tmp_path / "moex-model-0.1.1-abc1234-overlay.zip"
    overlay.write_bytes(b"PK\x03\x04fake")
    bundle = tmp_path / "release-bundle-0.1.1-abc1234.zip"
    bundle.write_bytes(b"PK\x03\x04bundle")
    apply_sh = tmp_path / "apply-contour.sh"
    apply_sh.write_bytes(b"#!/usr/bin/env bash\necho ok\r\n")
    dest = tmp_path / "out" / "moex-model-0.1.1-abc1234-contour.zip"
    apply = ao.apply_md_text(mode="overlay", tag="0.1.1-abc1234", parent_tag="0.1.0")
    ao.assemble_contour_zip(dest, members=[overlay, bundle, apply_sh], apply_md=apply)
    with zipfile.ZipFile(dest) as archive:
        names = set(archive.namelist())
        assert "APPLY.md" in names
        assert overlay.name in names
        assert bundle.name in names
        assert "apply-contour.sh" in names
        assert b"\r" not in archive.read("apply-contour.sh")
        text = archive.read("APPLY.md").decode()
        assert "apply-contour.sh" in text
        assert "gunzip" in text
        assert "MODEL_TAG" in text


def test_zip_tree_posix_no_backslashes(tmp_path: Path) -> None:
    src = tmp_path / "tree"
    (src / "docker").mkdir(parents=True)
    (src / "docker" / "docker-compose.prod.yml").write_text("x: 1\n", encoding="utf-8")
    (src / "docker-compose.yml").write_text("y: 2\n", encoding="utf-8")
    dest = tmp_path / "out" / "bundle.zip"
    ao.zip_tree_posix(src, dest)
    with zipfile.ZipFile(dest) as archive:
        names = archive.namelist()
    assert "docker/docker-compose.prod.yml" in names
    assert "docker-compose.yml" in names
    assert all("\\" not in name for name in names)


def test_full_dockerfiles_have_git_sha_label() -> None:
    api = (REPO_ROOT / "docker" / "api.Dockerfile").read_text(encoding="utf-8")
    web = (REPO_ROOT / "docker" / "web.Dockerfile").read_text(encoding="utf-8")
    assert "ARG GIT_SHA=" in api
    assert 'moexmodel.git_sha="${GIT_SHA}"' in api
    assert "ARG GIT_SHA=" in web
    assert 'moexmodel.git_sha="${GIT_SHA}"' in web


def test_compose_passes_git_sha_build_arg() -> None:
    compose = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert compose.count("GIT_SHA: ${GIT_SHA:-unknown}") >= 2


def test_assert_git_clean_non_repo(tmp_path: Path) -> None:
    with pytest.raises(ao.OverlayError):
        ao.assert_git_clean_for_contour(tmp_path)


def test_release_bundle_paths_exist() -> None:
    for rel in ao.RELEASE_BUNDLE_PATHS:
        assert (REPO_ROOT / rel).is_file(), rel
