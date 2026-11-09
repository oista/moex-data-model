"""models-sync builds only when the commit or image changes and swaps current."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "docker" / "models-sync.sh"
NGINX_CONF = REPO_ROOT / "docker" / "nginx.conf"
COMPOSE = REPO_ROOT / "docker-compose.yml"
ENV_EXAMPLE = REPO_ROOT / ".env.example"
MARKER = Path("model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml")


def test_published_paths_and_interval_defaults() -> None:
    script = SCRIPT.read_text(encoding="utf-8")
    assert "reset --hard" not in script
    assert "clean -fd" not in script
    assert "MOEX_SYNC_ONCE" in script
    assert "ln -sfn" in script
    assert "mv -T" in script
    assert "${MOEX_MODELS_SYNC_INTERVAL:-60}" in script
    assert "alias /usr/share/nginx/viewer/current/;" in NGINX_CONF.read_text(encoding="utf-8")
    compose = COMPOSE.read_text(encoding="utf-8")
    assert "MOEX_MODELS_SYNC_INTERVAL: ${MOEX_MODELS_SYNC_INTERVAL:-60}" in compose
    assert "MOEX_SYNC_ONCE:" in compose
    example = ENV_EXAMPLE.read_text(encoding="utf-8")
    assert "MOEX_MODELS_SYNC_INTERVAL=60" in example
    assert "MOEX_SYNC_ONCE=1" in example


def test_script_syntax() -> None:
    bash = _git_bash()
    if bash is None:
        pytest.skip("Git bash is required to syntax-check docker/models-sync.sh")
    proc = subprocess.run(
        [bash, "-n", SCRIPT.as_posix()],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr


def test_skips_build_when_commit_and_image_match(tmp_path: Path) -> None:
    bare, seed = _bare_repo(tmp_path)
    _commit(seed, "schema: first\n")
    _push(seed)
    log = tmp_path / "build-log"
    dist = tmp_path / "viewer"
    env = _env(tmp_path, bare, dist, log, _ok_builder(tmp_path))
    first = _run(env)
    assert first.returncode == 0, first.stderr
    assert log.read_text(encoding="utf-8").count("\n") == 1
    current = _read_info(dist)["commit"]
    second = _run(env)
    assert second.returncode == 0, second.stderr
    assert "already built" in second.stdout
    assert log.read_text(encoding="utf-8").count("\n") == 1
    assert _read_info(dist)["commit"] == current
    assert not (tmp_path / "models" / "from-build").exists()
    link = dist / "current"
    if link.is_symlink():
        assert not os.readlink(link).startswith("/")


def test_rebuilds_and_keeps_two_releases(tmp_path: Path) -> None:
    bare, seed = _bare_repo(tmp_path)
    _commit(seed, "schema: first\n")
    _push(seed)
    log = tmp_path / "build-log"
    dist = tmp_path / "viewer"
    env = _env(tmp_path, bare, dist, log, _ok_builder(tmp_path))
    assert _run(env).returncode == 0
    first_commit = _read_info(dist)["commit"]

    _commit(seed, "schema: second\n")
    _push(seed)
    second_run = _run(env)
    assert second_run.returncode == 0, second_run.stderr
    info = _read_info(dist)
    assert info["commit"] != first_commit
    assert info["ok"] is True
    assert info["commit"] != first_commit
    assert info["image_sha"] == "image-sha-1"
    assert isinstance(info["duration_ms"], int)
    assert info["built_at"]
    models_head = _git(tmp_path / "models", "rev-parse", "HEAD").stdout.strip()
    assert info["commit"] == models_head
    assert (dist / ".built-for").read_text(encoding="utf-8").strip() == f"{models_head} image-sha-1"

    _commit(seed, "schema: third\n")
    _push(seed)
    assert _run(env).returncode == 0
    releases = [p for p in (dist / "releases").iterdir() if p.is_dir()]
    assert len(releases) == 2
    assert _read_info(dist)["commit"] == _git(tmp_path / "models", "rev-parse", "HEAD").stdout.strip()
    assert not (tmp_path / "models" / "from-build").exists()
    status = _git(tmp_path / "models", "status", "--porcelain")
    assert status.stdout.strip() == ""


def test_failed_build_keeps_previous_current(tmp_path: Path) -> None:
    bare, seed = _bare_repo(tmp_path)
    _commit(seed, "schema: first\n")
    _push(seed)
    log = tmp_path / "build-log"
    dist = tmp_path / "viewer"
    env = _env(tmp_path, bare, dist, log, _ok_builder(tmp_path))
    assert _run(env).returncode == 0, "seed build failed"
    previous = _read_info(dist)["commit"]
    stamp = (dist / ".built-for").read_text(encoding="utf-8")

    env["MOEX_VIEWER_BUILD"] = _fail_builder(tmp_path)
    _commit(seed, "schema: broken\n")
    _push(seed)
    failed = _run(env)
    assert failed.returncode == 0, failed.stderr
    assert "viewer build failed" in failed.stderr
    assert _read_info(dist)["commit"] == previous
    assert (dist / ".built-for").read_text(encoding="utf-8") == stamp
    assert not (tmp_path / "models" / "from-build").exists()


def test_failed_fetch_keeps_the_published_viewer(tmp_path: Path) -> None:
    bare, seed = _bare_repo(tmp_path)
    _commit(seed, "schema: first\n")
    _push(seed)
    log = tmp_path / "build-log"
    dist = tmp_path / "viewer"
    env = _env(tmp_path, bare, dist, log, _ok_builder(tmp_path))
    assert _run(env).returncode == 0
    previous = _read_info(dist)["commit"]
    env["MOEX_MODELS_GIT_URL"] = (tmp_path / "missing.git").as_posix()
    failed = _run(env)
    assert failed.returncode == 0, failed.stderr
    assert "git sync failed" in failed.stderr
    assert _read_info(dist)["commit"] == previous
    assert log.read_text(encoding="utf-8").count("\n") == 1


def test_bind_mount_builds_in_the_models_tree(tmp_path: Path) -> None:
    models = tmp_path / "models"
    _git_init(models)
    marker = models / MARKER
    marker.parent.mkdir(parents=True)
    marker.write_text("schema: local\n", encoding="utf-8", newline="\n")
    _git(models, "add", "-A")
    _git(models, "commit", "-m", "local")
    log = tmp_path / "build-log"
    dist = tmp_path / "viewer"
    env = _env(tmp_path, None, dist, log, _ok_builder(tmp_path))
    env["MOEX_MODELS_GIT_URL"] = ""
    proc = _run(env)
    assert proc.returncode == 0, proc.stderr
    assert "skip fetch" in proc.stdout
    built_root = log.read_text(encoding="utf-8").strip()
    assert Path(built_root) == models
    assert (models / "from-build").is_file()
    assert (dist / "current").is_symlink() or (dist / "current").is_dir()


def test_image_sha_falls_back_to_manifest_hash(tmp_path: Path) -> None:
    bare, seed = _bare_repo(tmp_path)
    _commit(seed, "schema: first\n")
    _push(seed)
    manifest = tmp_path / "contracts.json"
    manifest.write_text('{"contracts":"v"}\n', encoding="utf-8", newline="\n")
    log = tmp_path / "build-log"
    dist = tmp_path / "viewer"
    env = _env(tmp_path, bare, dist, log, _ok_builder(tmp_path))
    env.pop("MOEX_IMAGE_GIT_SHA", None)
    env["MOEX_IMAGE_CONTRACTS_MANIFEST"] = manifest.as_posix()
    proc = _run(env)
    assert proc.returncode == 0, proc.stderr
    info = _read_info(dist)
    assert info["image_sha"] != "unknown"
    assert len(info["image_sha"]) == 64


def _ok_builder(tmp_path: Path) -> str:
    path = tmp_path / "build-ok.sh"
    path.write_text(
        "#!/bin/sh\n"
        'mkdir -p "$MOEX_BUILD_DIST"\n'
        "printf '%s\\n' ok > \"$MOEX_BUILD_DIST/index.html\"\n"
        "printf '%s\\n' \"$MOEX_BUILD_ROOT\" >> \"$MOEX_BUILD_LOG\"\n"
        "printf '%s\\n' snap > \"$MOEX_BUILD_ROOT/from-build\"\n",
        encoding="utf-8",
        newline="\n",
    )
    return path.as_posix()


def _fail_builder(tmp_path: Path) -> str:
    path = tmp_path / "build-fail.sh"
    path.write_text(
        "#!/bin/sh\nprintf '%s\\n' fail >> \"$MOEX_BUILD_LOG\"\nexit 1\n",
        encoding="utf-8",
        newline="\n",
    )
    return path.as_posix()


def _bare_repo(tmp_path: Path) -> tuple[Path, Path]:
    bare = tmp_path / "bare.git"
    seed = tmp_path / "seed"
    _git(tmp_path, "init", "--bare", "-b", "main", str(bare))
    _git_init(seed)
    _git(seed, "remote", "add", "origin", bare.as_posix())
    return bare, seed


def _git_init(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    _git(path, "init", "-b", "main")
    _git(path, "config", "user.email", "models-sync@example.com")
    _git(path, "config", "user.name", "models-sync")


def _commit(repo: Path, schema: str) -> None:
    marker = repo / MARKER
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(schema, encoding="utf-8", newline="\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "schema")


def _push(repo: Path) -> None:
    proc = _git(repo, "push", "origin", "main")
    assert proc.returncode == 0, proc.stderr


def _env(
    tmp_path: Path,
    bare: Path | None,
    dist: Path,
    log: Path,
    build: str,
) -> dict[str, str]:
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    env = os.environ.copy()
    env.update(
        {
            "HOME": home.as_posix(),
            "USERPROFILE": str(home),
            "GIT_CONFIG_GLOBAL": (home / ".gitconfig").as_posix(),
            "GIT_CONFIG_NOSYSTEM": "1",
            "MOEX_MODELS_ROOT": (tmp_path / "models").as_posix(),
            "MOEX_MODELS_GIT_URL": "" if bare is None else bare.as_posix(),
            "MOEX_MODELS_GIT_REF": "main",
            "MOEX_VIEWER_DIST": dist.as_posix(),
            "MOEX_SYNC_ONCE": "1",
            "MOEX_MODELS_SYNC_INTERVAL": "60",
            "MOEX_IMAGE_GIT_SHA": "image-sha-1",
            "MOEX_VIEWER_BUILD": build,
            "MOEX_BUILD_LOG": log.as_posix(),
            "MOEX_MODELS_DEPLOY_TOKEN": "",
            "MOEX_MODELS_DEPLOY_USER": "",
            "MOEX_GITLAB_CA_BUNDLE": "",
        }
    )
    return env


def _run(env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    bash = _git_bash()
    if bash is None:
        pytest.skip("Git bash is required to run docker/models-sync.sh")
    return subprocess.run(
        [bash, SCRIPT.as_posix()],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def _read_info(dist: Path) -> dict:
    return json.loads((dist / "current" / "build-info.json").read_text(encoding="utf-8"))


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def _git_bash() -> str | None:
    git = shutil.which("git")
    if git is None:
        return None
    git_path = Path(git).resolve()
    for candidate in (
        git_path.parent / "bash.exe",
        git_path.parent.parent / "bin" / "bash.exe",
    ):
        if candidate.is_file():
            return str(candidate)
    return None
