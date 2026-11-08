"""Air-gap overlay pack helpers: deps fingerprint, stage zip context, apply script.

See docs/adr/ADR-058-airgap-image-deploy.md. The operation follows the
moex-prodata-platform air-gap pack; this repository does not import that code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

IMAGE_API = "moex-data-model-api"
IMAGE_WEB = "moex-data-model-web"
ARCHIVE_PREFIX = "moex-model"

# Paths hashed for the Full vs Overlay gate (a change forces Full).
# pyproject.toml is hashed via the dependency slice only (not version).
_FINGERPRINT_DOCKERFILES = (
    "docker/api.Dockerfile",
    "docker/web.Dockerfile",
)
_FINGERPRINT_LOCK = "apps/web/package-lock.json"

# Trees the API image installs editable. Overlay replaces these and does not pip install.
OVERLAY_TREES = (
    "apps/api",
    "apps/cli",
    "apps/viewer",
    "packages/modeling-kernel",
    "packages/standard-linkml",
    "packages/specification-dams",
    "packages/semantic-mappings",
    "packages/linkml-tooling",
    "packages/external-sources",
    "packages/publication",
    "packages/repository-loader",
    "packages/git-adapter",
    "packages/drawdb-adapter",
    "generated/contracts",
    "generated/manifests",
)
OVERLAY_FILES = (
    "docker/models-sync.sh",
    "docker/nginx.conf",
)
WEB_DIST = "apps/web/dist"

_SKIP_DIR_NAMES = frozenset(
    {
        "node_modules",
        "__pycache__",
        ".git",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        ".venv",
        "venv",
    }
)

# release-bundle paths (must match pack-docker-images.ps1 Invoke-ConfigBundle).
RELEASE_BUNDLE_PATHS = (
    "docker-compose.yml",
    "docker/docker-compose.prod.yml",
    ".env.example",
)

_FORBIDDEN_DROP_SUBSTRINGS = (
    "grafana/grafana",
    "prom/prometheus",
    "nginx:alpine",
)

_VERSION_RE = re.compile(r'(?m)^(version\s*=\s*")(\d+)\.(\d+)\.(\d+)("\s*)$')


class OverlayError(Exception):
    """Raised when overlay pack/apply is not allowed."""


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _pyproject_files(root: Path) -> list[Path]:
    found: list[Path] = []
    for path in root.rglob("pyproject.toml"):
        if not path.is_file():
            continue
        if any(part in _SKIP_DIR_NAMES for part in path.parts):
            continue
        found.append(path)
    return sorted(found, key=lambda item: item.relative_to(root).as_posix())


def _pyproject_deps_slice(text: str) -> str:
    """Extract dependency-relevant pyproject sections; ignore project version."""
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    in_deps_array = False
    in_optional = False
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("requires-python"):
            out.append(line)
            continue
        if re.match(r"^\[project\.optional-dependencies\]", line):
            in_optional = True
            in_deps_array = False
            out.append(line)
            continue
        if in_optional:
            if stripped.startswith("[") and not stripped.startswith(
                "[project.optional-dependencies]"
            ):
                in_optional = False
            else:
                out.append(line)
                continue
        if re.match(r"^dependencies\s*=", line):
            in_deps_array = True
            out.append(line)
            continue
        if in_deps_array:
            out.append(line)
            if "]" in stripped and not stripped.strip().startswith("#"):
                in_deps_array = False
            continue
    return "".join(out)


def read_pyproject_version(repo_root: Path) -> str:
    text = (repo_root / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"', text)
    if not match:
        raise OverlayError("Cannot parse version from pyproject.toml")
    return match.group(1)


def bump_patch(version: str) -> str:
    """Increment patch: 0.1.0 -> 0.1.1; 0.1.9 -> 0.1.10."""
    parts = version.strip().split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise OverlayError(f"expected X.Y.Z semver, got {version!r}")
    major, minor, patch = (int(part) for part in parts)
    return f"{major}.{minor}.{patch + 1}"


def write_pyproject_version(repo_root: Path, new_version: str) -> str:
    """Set the first project version in the root pyproject.toml; return the previous one."""
    path = repo_root / "pyproject.toml"
    text = path.read_text(encoding="utf-8")
    match = _VERSION_RE.search(text)
    if not match:
        raise OverlayError('Cannot bump version: no version = "X.Y.Z" in pyproject.toml')
    old = f"{match.group(2)}.{match.group(3)}.{match.group(4)}"
    new_text = _VERSION_RE.sub(rf"\g<1>{new_version}\g<5>", text, count=1)
    path.write_text(new_text, encoding="utf-8")
    return old


def bump_pyproject_patch(repo_root: Path) -> tuple[str, str]:
    """Bump patch in the root pyproject.toml. Returns (old_version, new_version)."""
    old = read_pyproject_version(repo_root)
    new = bump_patch(old)
    write_pyproject_version(repo_root, new)
    return old, new


def deps_fingerprint(repo_root: Path) -> str:
    """SHA256 over Dockerfiles, every pyproject dependency slice, and the web lockfile.

    Project ``version`` is excluded so a Contour patch bump stays Overlay-eligible.
    """
    root = repo_root.resolve()
    digest = hashlib.sha256()
    for rel in _FINGERPRINT_DOCKERFILES:
        path = root / rel
        if not path.is_file():
            raise OverlayError(f"fingerprint input missing: {rel}")
        digest.update(rel.encode())
        digest.update(b"\0")
        digest.update(_sha256_file(path).encode())
        digest.update(b"\0")
    pyprojects = _pyproject_files(root)
    if not pyprojects:
        raise OverlayError("fingerprint input missing: pyproject.toml")
    for path in pyprojects:
        rel = path.relative_to(root).as_posix()
        deps_slice = _pyproject_deps_slice(path.read_text(encoding="utf-8"))
        digest.update(rel.encode())
        digest.update(b"\0")
        digest.update(hashlib.sha256(deps_slice.encode()).hexdigest().encode())
        digest.update(b"\0")
    lock = root / _FINGERPRINT_LOCK
    if not lock.is_file():
        raise OverlayError(f"fingerprint input missing: {_FINGERPRINT_LOCK}")
    digest.update(_FINGERPRINT_LOCK.encode())
    digest.update(b"\0")
    digest.update(_sha256_file(lock).encode())
    digest.update(b"\0")
    return digest.hexdigest()


def assert_overlay_allowed(parent_fingerprint: str, current: str) -> None:
    if parent_fingerprint != current:
        raise OverlayError(
            "deps_fingerprint mismatch: Overlay not allowed; run Full pack. "
            f"parent={parent_fingerprint[:12]}… current={current[:12]}…"
        )


def assert_git_clean_for_contour(
    repo_root: Path, *, allow_pyproject_version_only: bool = False
) -> None:
    """Abort Contour pack on a dirty tree (optionally allow only the version bump)."""
    root = repo_root.resolve()
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise OverlayError(f"git status failed: {exc}") from exc
    if proc.returncode != 0:
        raise OverlayError(f"git status failed: {proc.stderr.strip()}")
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    if not lines:
        return
    if allow_pyproject_version_only and _only_pyproject_version_dirty(root, lines):
        return
    shown = ", ".join(line[3:] for line in lines[:8])
    suffix = " …" if len(lines) > 8 else ""
    raise OverlayError(
        "Contour pack requires a clean git tree (commit or stash first). "
        f"Dirty: {shown}{suffix}"
    )


def _only_pyproject_version_dirty(repo_root: Path, porcelain: list[str]) -> bool:
    """True if the only change is the Contour bump: pyproject.toml and/or uv.lock versions."""
    paths: set[str] = set()
    for line in porcelain:
        body = line[3:] if len(line) > 3 else line
        if " -> " in body:
            body = body.split(" -> ", 1)[1]
        paths.add(body.strip().strip('"'))
    allowed = {"pyproject.toml", "uv.lock"}
    if not paths or not paths.issubset(allowed):
        return False
    if "pyproject.toml" not in paths:
        return False
    return all(_diff_only_version_lines(repo_root, rel) for rel in paths)


def _diff_only_version_lines(repo_root: Path, rel_path: str) -> bool:
    """True if the HEAD diff for rel_path only touches version = \"X.Y.Z\" lines."""
    try:
        diff = subprocess.run(
            ["git", "-C", str(repo_root), "diff", "HEAD", "--", rel_path],
            check=False,
            capture_output=True,
            text=True,
        )
        diff_cached = subprocess.run(
            ["git", "-C", str(repo_root), "diff", "--cached", "--", rel_path],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return False
    if diff.returncode != 0 or diff_cached.returncode != 0:
        return False
    combined = (diff.stdout or "") + (diff_cached.stdout or "")
    if not combined.strip():
        return False
    for line in combined.splitlines():
        if not (line.startswith("+") or line.startswith("-")):
            continue
        if line.startswith("+++") or line.startswith("---"):
            continue
        content = line[1:].strip()
        if re.match(r'^version\s*=\s*"\d+\.\d+\.\d+"\s*$', content):
            continue
        return False
    return True


def assert_version_not_reused(out_dir: Path, version: str, git_sha: str) -> None:
    """Fail if a manifest already recorded this version with another git_sha."""
    short = git_sha.strip()[:7]
    for path in out_dir.glob(f"{ARCHIVE_PREFIX}-{version}*.manifest.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        existing = str(data.get("git_sha") or "")[:7]
        if existing and existing != short:
            raise OverlayError(
                f"version {version} already packed with git_sha={existing} "
                f"({path.name}); refuse reuse with {short}"
            )


def new_overlay_tag(version: str, git_sha: str) -> str:
    sha = git_sha.strip()
    if not sha or sha == "unknown":
        raise OverlayError("git_sha required for overlay tag")
    short = sha[:7] if len(sha) >= 7 else sha
    return f"{version}-{short}"


def git_sha_short(repo_root: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--short", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()
    except OSError:
        pass
    return "unknown"


def git_commit_unix(repo_root: Path) -> int:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "log", "-1", "--format=%ct"],
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0 and proc.stdout.strip().isdigit():
            return int(proc.stdout.strip())
    except OSError:
        pass
    return 0


def apply_md_text(*, mode: str, tag: str, parent_tag: str | None = None) -> str:
    """Operator instructions packed inside the contour zip."""
    lines = [
        "# Применение пакета для контура",
        "",
        "Этот файл — **zip**. Распаковывать командой `unzip`, не `gunzip` и не `gzip -d`.",
        "",
        "## Одной командой",
        "",
        "Если сценарий скопирован с Windows и bash пишет `set: pipefail`",
        "или `invalid option name`, сначала уберите CR:",
        "`sed -i 's/\\r$//' apply-contour.sh`",
        "",
        "```bash",
        "bash apply-contour.sh /path/to/moex-model-contour.zip",
        "# DEPLOY_DIR=/opt/moex-data-model bash apply-contour.sh /tmp/moex-model-contour.zip",
        "```",
        "",
        f"Сценарий ставит `MODEL_TAG={tag}`, распаковывает файлы запуска в",
        "`DEPLOY_DIR` (по умолчанию `/opt/moex-data-model`) и выполняет",
        "`docker compose up -d`.",
        "",
        "Переменные: `DEPLOY_DIR`, `SKIP_COMPOSE=1`, `APPLY_ALLOW_DOWNGRADE=1` (только поставка поверх).",
        "",
    ]
    if mode == "overlay":
        lines += [
            "## Вручную, поставка поверх",
            "",
            f"Основа — полная поставка `{parent_tag}`. Её образы уже должны быть загружены.",
            "",
            "```bash",
            "unzip -o moex-model-*-contour.zip -d /tmp/moex-contour",
            "cd /tmp/moex-contour",
            "unzip -o moex-model-*-overlay.zip -d overlay-stage",
            "cd overlay-stage && bash apply-overlay.sh",
            f"export MODEL_TAG={tag}",
            "```",
            "",
        ]
    else:
        lines += [
            "## Вручную, полная поставка",
            "",
            "```bash",
            "unzip -o moex-model-*-contour.zip -d /tmp/moex-contour",
            "cd /tmp/moex-contour",
            f"sha256sum -c {ARCHIVE_PREFIX}-{tag}.tar.gz.sha256",
            f"gunzip -c {ARCHIVE_PREFIX}-{tag}.tar.gz | docker load",
            f"export MODEL_TAG={tag}",
            "```",
            "",
        ]
    lines += [
        "## Файлы запуска",
        "",
        "```bash",
        "unzip -o release-bundle-*.zip -d /opt/moex-data-model",
        "cd /opt/moex-data-model",
        "# первый раз: cp .env.example .env  и заполнить секреты",
        "```",
        "",
        "Секреты из `.env` в пакет не входят.",
        "",
        "## Запуск",
        "",
        "Первый файл compose — `docker-compose.yml`.",
        "",
        "```bash",
        f"export MODEL_TAG={tag}",
        "docker compose -f docker-compose.yml -f docker/docker-compose.prod.yml up -d",
        "curl -s http://127.0.0.1:8080/api/health",
        "```",
        "",
    ]
    return "\n".join(lines)


def contour_drop_required_names(*, mode: str, tag: str) -> list[str]:
    common = ["APPLY.md", "apply-contour.sh"]
    if mode == "overlay":
        return [
            *common,
            f"{ARCHIVE_PREFIX}-{tag}-overlay.zip",
            f"release-bundle-{tag}.zip",
        ]
    if mode == "full":
        return [
            *common,
            f"{ARCHIVE_PREFIX}-{tag}.tar.gz",
            f"release-bundle-{tag}.zip",
        ]
    raise OverlayError(f"unknown contour mode {mode!r}")


def assert_contour_drop_inventory(names: list[str], *, mode: str) -> None:
    """Validate a contour drop file-name list: required present, forbidden absent."""
    joined = "\n".join(names)
    for bad in _FORBIDDEN_DROP_SUBSTRINGS:
        if bad in joined:
            raise OverlayError(f"contour drop must not include {bad!r}")
    basenames = {Path(name).name for name in names}
    if "apply-contour.sh" not in basenames:
        raise OverlayError("contour drop missing apply-contour.sh")
    if mode == "overlay":
        if not any(name.endswith("-overlay.zip") for name in names):
            raise OverlayError("overlay contour drop missing *-overlay.zip")
        if not any("release-bundle" in name for name in names):
            raise OverlayError("contour drop missing release-bundle")
        if not any(name == "APPLY.md" or name.endswith("/APPLY.md") for name in names):
            raise OverlayError("contour drop missing APPLY.md")
    elif mode == "full":
        if not any(name.endswith(".tar.gz") and ARCHIVE_PREFIX in name for name in names):
            raise OverlayError("full contour drop missing moex-model-*.tar.gz")
        if not any("release-bundle" in name for name in names):
            raise OverlayError("contour drop missing release-bundle")
    else:
        raise OverlayError(f"unknown contour mode {mode!r}")


def assemble_contour_zip(dest_zip: Path, *, members: list[Path], apply_md: str) -> None:
    """Write a contour zip with APPLY.md and the given files at the archive root."""
    if dest_zip.exists():
        dest_zip.unlink()
    dest_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("APPLY.md", apply_md)
        for path in members:
            if not path.is_file():
                raise OverlayError(f"contour member missing: {path}")
            if path.suffix == ".sh" or path.name.endswith(".sh"):
                text = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
                archive.writestr(path.name, text)
            else:
                archive.write(path, arcname=path.name)


def zip_tree_posix(src_dir: Path, dest_zip: Path) -> None:
    """Zip a directory with POSIX archive paths.

    Windows ``Compress-Archive`` embeds backslashes; ``unzip`` on Linux then
    warns and exits 1, which aborts ``set -e`` apply scripts.
    """
    src_dir = src_dir.resolve()
    if not src_dir.is_dir():
        raise OverlayError(f"zip source is not a directory: {src_dir}")
    if dest_zip.exists():
        dest_zip.unlink()
    dest_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(src_dir.rglob("*")):
            if not path.is_file():
                continue
            if any(part in _SKIP_DIR_NAMES for part in path.parts):
                continue
            arc = path.relative_to(src_dir).as_posix()
            if "\\" in arc:
                raise OverlayError(f"refusing backslash in zip arcname: {arc!r}")
            archive.write(path, arcname=arc)
    with zipfile.ZipFile(dest_zip, "r") as archive:
        for name in archive.namelist():
            if "\\" in name:
                raise OverlayError(f"zip contains backslash path: {name!r}")


def _copy_tree(src: Path, dest: Path) -> None:
    if not src.exists():
        raise OverlayError(f"missing path for overlay stage: {src}")
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    def _ignore(directory: str, names: list[str]) -> set[str]:
        del directory
        return {name for name in names if name in _SKIP_DIR_NAMES}

    shutil.copytree(src, dest, ignore=_ignore)


def _copy_file(src: Path, dest: Path) -> None:
    if not src.is_file():
        raise OverlayError(f"missing file for overlay stage: {src}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def dockerfile_overlay_api() -> str:
    return f"""\
ARG PARENT_TAG
FROM {IMAGE_API}:${{PARENT_TAG}}
USER root
RUN rm -rf /app/apps/api /app/apps/cli /app/apps/viewer \\
    /app/packages /app/generated/contracts /app/generated/manifests
COPY apps/api /app/apps/api
COPY apps/cli /app/apps/cli
COPY apps/viewer /app/apps/viewer
COPY packages /app/packages
COPY generated/contracts /app/generated/contracts
COPY generated/manifests /app/generated/manifests
COPY docker/models-sync.sh /app/docker/models-sync.sh
ARG MOEX_GIT_SHA=
ARG MOEX_PARENT_TAG=
LABEL moexmodel.git_sha="${{MOEX_GIT_SHA}}" \\
      moexmodel.parent_tag="${{MOEX_PARENT_TAG}}"
RUN sed -i 's/\\r$//' /app/docker/models-sync.sh \\
    && chmod 755 /app/docker/models-sync.sh \\
    && chown -R moex:moex /app/apps /app/packages /app/generated /app/docker
USER moex
"""


def dockerfile_overlay_web() -> str:
    return f"""\
ARG PARENT_TAG
FROM {IMAGE_WEB}:${{PARENT_TAG}}
USER root
RUN rm -rf /usr/share/nginx/html
COPY apps/web/dist /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
ARG MOEX_GIT_SHA=
ARG MOEX_PARENT_TAG=
LABEL moexmodel.git_sha="${{MOEX_GIT_SHA}}" \\
      moexmodel.parent_tag="${{MOEX_PARENT_TAG}}"
"""


def apply_overlay_sh(
    *,
    parent_tag: str,
    new_tag: str,
    git_sha: str,
    git_commit_unix_ts: int,
    deps_fp: str,
) -> str:
    """Bash apply script for the closed host. No pip, npm, or host Python."""
    return f"""\
#!/usr/bin/env bash
# Apply an air-gap overlay (ADR-058). Builds FROM local Full images only.
set -euo pipefail

PARENT_TAG="{parent_tag}"
NEW_TAG="{new_tag}"
GIT_SHA="{git_sha}"
GIT_COMMIT_UNIX="{git_commit_unix_ts}"
DEPS_FINGERPRINT="{deps_fp}"
IMAGE_API="{IMAGE_API}"
IMAGE_WEB="{IMAGE_WEB}"
STATE_FILE="${{AIRGAP_STATE_FILE:-./airgap-state.json}}"
ALLOW_DOWNGRADE="${{APPLY_ALLOW_DOWNGRADE:-0}}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

json_field() {{
  awk -v key="$1" '
    $0 ~ "\\"" key "\\"" {{
      line = $0
      sub(/^[^:]*:[[:space:]]*/, "", line)
      gsub(/[",[:space:]]/, "", line)
      print line
      exit
    }}
  ' "$2"
}}

require_image() {{
  local ref="$1"
  if ! docker image inspect "$ref" >/dev/null 2>&1; then
    echo "ERROR: image not found locally: $ref" >&2
    echo "Load the Full pack first (docker load), then retry." >&2
    exit 1
  fi
}}

require_image "${{IMAGE_API}}:${{PARENT_TAG}}"
require_image "${{IMAGE_WEB}}:${{PARENT_TAG}}"

if [[ -f "$STATE_FILE" ]]; then
  state_full="$(json_field full_tag "$STATE_FILE")"
  state_fp="$(json_field deps_fingerprint "$STATE_FILE")"
  state_ts="$(json_field git_commit_unix "$STATE_FILE")"
  state_ts="${{state_ts:-0}}"
  if [[ -n "$state_full" && "$state_full" != "$PARENT_TAG" ]]; then
    echo "ERROR: overlay parent_tag=$PARENT_TAG but airgap-state full_tag=$state_full" >&2
    exit 1
  fi
  if [[ -n "$state_fp" && "$state_fp" != "$DEPS_FINGERPRINT" ]]; then
    echo "ERROR: deps_fingerprint mismatch vs airgap-state.json — need a Full pack" >&2
    exit 1
  fi
  if [[ "$ALLOW_DOWNGRADE" != "1" && "$GIT_COMMIT_UNIX" -lt "$state_ts" ]]; then
    echo "ERROR: overlay is older than applied state. Set APPLY_ALLOW_DOWNGRADE=1 to force." >&2
    exit 1
  fi
fi

export DOCKER_BUILDKIT=1
docker build --network=none \\
  --build-arg "PARENT_TAG=${{PARENT_TAG}}" \\
  --build-arg "MOEX_GIT_SHA=${{GIT_SHA}}" \\
  --build-arg "MOEX_PARENT_TAG=${{PARENT_TAG}}" \\
  -f Dockerfile.overlay.api \\
  -t "${{IMAGE_API}}:${{NEW_TAG}}" \\
  .

docker build --network=none \\
  --build-arg "PARENT_TAG=${{PARENT_TAG}}" \\
  --build-arg "MOEX_GIT_SHA=${{GIT_SHA}}" \\
  --build-arg "MOEX_PARENT_TAG=${{PARENT_TAG}}" \\
  -f Dockerfile.overlay.web \\
  -t "${{IMAGE_WEB}}:${{NEW_TAG}}" \\
  .

applied_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat > "$STATE_FILE" <<EOF
{{
  "full_tag": "${{PARENT_TAG}}",
  "app_tag": "${{NEW_TAG}}",
  "git_sha": "${{GIT_SHA}}",
  "git_commit_unix": ${{GIT_COMMIT_UNIX}},
  "deps_fingerprint": "${{DEPS_FINGERPRINT}}",
  "applied_at": "${{applied_at}}"
}}
EOF

echo "Wrote $STATE_FILE"
echo ""
echo "Overlay applied."
echo "  export MODEL_TAG=${{NEW_TAG}}"
echo "  docker compose -f docker-compose.yml -f docker/docker-compose.prod.yml up -d"
"""


def write_manifest(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def stage_overlay(
    repo_root: Path,
    dest: Path,
    *,
    parent_tag: str,
    new_tag: str,
    git_sha: str | None = None,
    git_commit_unix_ts: int | None = None,
    fingerprint: str | None = None,
) -> dict[str, Any]:
    """Stage the overlay build context under dest. Returns the manifest dict."""
    root = repo_root.resolve()
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    sha = git_sha or git_sha_short(root)
    ts = git_commit_unix_ts if git_commit_unix_ts is not None else git_commit_unix(root)
    fp = fingerprint or deps_fingerprint(root)

    for rel in OVERLAY_TREES:
        _copy_tree(root / rel, dest / rel)
    for rel in OVERLAY_FILES:
        _copy_file(root / rel, dest / rel)
    dist_src = root / WEB_DIST
    if not dist_src.is_dir() or not any(dist_src.iterdir()):
        raise OverlayError(
            "apps/web/dist missing or empty — build the web app before stage_overlay"
        )
    _copy_tree(dist_src, dest / WEB_DIST)

    (dest / "Dockerfile.overlay.api").write_text(dockerfile_overlay_api(), encoding="utf-8")
    (dest / "Dockerfile.overlay.web").write_text(dockerfile_overlay_web(), encoding="utf-8")

    apply_path = dest / "apply-overlay.sh"
    apply_path.write_text(
        apply_overlay_sh(
            parent_tag=parent_tag,
            new_tag=new_tag,
            git_sha=sha,
            git_commit_unix_ts=ts,
            deps_fp=fp,
        ),
        encoding="utf-8",
        newline="\n",
    )

    if any(path.name == "node_modules" for path in dest.rglob("node_modules")):
        raise OverlayError("stage contains node_modules — copy filter failed")

    manifest: dict[str, Any] = {
        "mode": "overlay",
        "parent_tag": parent_tag,
        "new_tag": new_tag,
        "git_sha": sha,
        "git_commit_unix": ts,
        "deps_fingerprint": fp,
        "images": [
            f"{IMAGE_API}:{new_tag}",
            f"{IMAGE_WEB}:{new_tag}",
        ],
        "created_utc": datetime.now(UTC).isoformat(),
    }
    write_manifest(dest / "overlay.manifest.json", manifest)
    return manifest


def _cmd_fingerprint(args: argparse.Namespace) -> int:
    print(deps_fingerprint(Path(args.repo_root).resolve()))
    return 0


def _cmd_stage(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).resolve()
    current = deps_fingerprint(root)
    if args.parent_fingerprint:
        assert_overlay_allowed(args.parent_fingerprint, current)
    sha = args.git_sha or git_sha_short(root)
    new_tag = args.new_tag or new_overlay_tag(args.version, sha)
    manifest = stage_overlay(
        root,
        Path(args.dest).resolve(),
        parent_tag=args.parent_tag,
        new_tag=new_tag,
        git_sha=sha,
        fingerprint=current,
    )
    print(json.dumps(manifest, indent=2))
    return 0


def _cmd_bump(args: argparse.Namespace) -> int:
    old, new = bump_pyproject_patch(Path(args.repo_root).resolve())
    print(json.dumps({"old": old, "new": new}))
    return 0


def _cmd_gate_clean(args: argparse.Namespace) -> int:
    assert_git_clean_for_contour(
        Path(args.repo_root).resolve(),
        allow_pyproject_version_only=bool(args.allow_pyproject_version),
    )
    print("ok")
    return 0


def _cmd_gate_version(args: argparse.Namespace) -> int:
    assert_version_not_reused(Path(args.out_dir), args.version, args.git_sha)
    print("ok")
    return 0


def _cmd_write_apply(args: argparse.Namespace) -> int:
    text = apply_md_text(mode=args.mode, tag=args.tag, parent_tag=args.parent_tag or None)
    Path(args.out).write_text(text, encoding="utf-8")
    print(args.out)
    return 0


def _cmd_assemble_contour(args: argparse.Namespace) -> int:
    members = [Path(path) for path in args.member]
    apply = Path(args.apply_md).read_text(encoding="utf-8")
    names = ["APPLY.md"] + [path.name for path in members]
    assert_contour_drop_inventory(names, mode=args.mode)
    dest = Path(args.dest)
    assemble_contour_zip(dest, members=members, apply_md=apply)
    print(dest)
    return 0


def _cmd_zip_tree(args: argparse.Namespace) -> int:
    zip_tree_posix(Path(args.src), Path(args.dest))
    print(args.dest)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Air-gap overlay helper (ADR-058)")
    parser.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parent.parent),
        help="Repository root (default: parent of scripts/)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    fingerprint = sub.add_parser("fingerprint", help="Print deps_fingerprint")
    fingerprint.set_defaults(func=_cmd_fingerprint)

    stage = sub.add_parser("stage", help="Stage overlay build context")
    stage.add_argument("--dest", required=True)
    stage.add_argument("--parent-tag", required=True)
    stage.add_argument("--version", required=True)
    stage.add_argument("--new-tag", default="")
    stage.add_argument("--git-sha", default="")
    stage.add_argument("--parent-fingerprint", default="")
    stage.set_defaults(func=_cmd_stage)

    bump = sub.add_parser("bump-patch", help="Bump patch in pyproject.toml")
    bump.set_defaults(func=_cmd_bump)

    gate = sub.add_parser("gate-clean", help="Require a clean git tree for Contour")
    gate.add_argument("--allow-pyproject-version", action="store_true")
    gate.set_defaults(func=_cmd_gate_clean)

    version_gate = sub.add_parser("gate-version", help="Refuse version reuse with another git_sha")
    version_gate.add_argument("--out-dir", required=True)
    version_gate.add_argument("--version", required=True)
    version_gate.add_argument("--git-sha", required=True)
    version_gate.set_defaults(func=_cmd_gate_version)

    apply = sub.add_parser("write-apply-md", help="Write APPLY.md for a contour drop")
    apply.add_argument("--mode", required=True, choices=("overlay", "full"))
    apply.add_argument("--tag", required=True)
    apply.add_argument("--parent-tag", default="")
    apply.add_argument("--out", required=True)
    apply.set_defaults(func=_cmd_write_apply)

    assemble = sub.add_parser("assemble-contour", help="Zip contour drop members plus APPLY.md")
    assemble.add_argument("--mode", required=True, choices=("overlay", "full"))
    assemble.add_argument("--dest", required=True)
    assemble.add_argument("--apply-md", required=True)
    assemble.add_argument("--member", action="append", default=[])
    assemble.set_defaults(func=_cmd_assemble_contour)

    zip_tree = sub.add_parser("zip-tree", help="Zip a directory with POSIX path separators")
    zip_tree.add_argument("--src", required=True)
    zip_tree.add_argument("--dest", required=True)
    zip_tree.set_defaults(func=_cmd_zip_tree)

    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except OverlayError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
