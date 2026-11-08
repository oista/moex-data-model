"""Nginx asks for a password and does not forward a client actor header."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
NGINX_CONF = REPO_ROOT / "docker" / "nginx.conf"
AUTH_SCRIPT = REPO_ROOT / "docker" / "40-moex-auth.sh"


def test_nginx_sets_actor_from_basic_auth() -> None:
    text = NGINX_CONF.read_text(encoding="utf-8")
    assert "include /etc/nginx/conf.d/auth.inc;" in text
    assert "proxy_set_header X-Remote-User $remote_user;" in text
    assert "proxy_set_header X-Moex-Actor $remote_user;" in text
    assert "$http_x_moex_actor" not in text.lower()


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


def _run_auth(tmp_path: Path, mode: str, *, with_file: bool) -> subprocess.CompletedProcess[str]:
    bash = _git_bash()
    if bash is None:
        pytest.skip("Git bash is required to run docker/40-moex-auth.sh")
    htpasswd = tmp_path / "htpasswd"
    auth_inc = tmp_path / "conf" / "auth.inc"
    if with_file:
        htpasswd.write_text("user:hash\n", encoding="utf-8")
    env = os.environ.copy()
    env["MOEX_AUTH_MODE"] = mode
    env["MOEX_AUTH_HTPASSWD"] = htpasswd.as_posix()
    env["MOEX_AUTH_INC"] = auth_inc.as_posix()
    env["MSYS_NO_PATHCONV"] = "1"
    return subprocess.run(
        [bash, AUTH_SCRIPT.as_posix()],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def test_auth_script_writes_basic_when_file_exists(tmp_path: Path) -> None:
    proc = _run_auth(tmp_path, "dev", with_file=True)
    assert proc.returncode == 0, proc.stderr
    text = (tmp_path / "conf" / "auth.inc").read_text(encoding="utf-8")
    assert 'auth_basic "MOEX";' in text
    assert "auth_basic_user_file" in text
    assert (tmp_path / "htpasswd").as_posix() in text


def test_auth_script_warns_without_file_in_dev(tmp_path: Path) -> None:
    proc = _run_auth(tmp_path, "dev", with_file=False)
    assert proc.returncode == 0, proc.stderr
    assert "WARNING" in proc.stderr
    assert (tmp_path / "conf" / "auth.inc").read_text(encoding="utf-8") == ""


def test_auth_script_refuses_trusted_header_without_file(tmp_path: Path) -> None:
    proc = _run_auth(tmp_path, "trusted-header", with_file=False)
    assert proc.returncode == 1
    assert "trusted-header" in proc.stderr
    assert not (tmp_path / "conf" / "auth.inc").exists()
