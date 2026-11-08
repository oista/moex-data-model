"""Export the models repository described in ADR-058 D7.

Subcommands:
  verify     archive the owned paths and run the model checks on that tree
  seed       fresh clone plus git filter-repo, then root files, ready to push
  spec-sync  copy code-owned paths into a models clone and optionally push a MR

The path list lives in deploy/models-repo/paths.yaml. Push is never the default.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PATHS_FILE = REPO_ROOT / "deploy" / "models-repo" / "paths.yaml"
TEMPLATE_DIR = REPO_ROOT / "deploy" / "models-repo"
IMAGE_MANIFEST = (
    REPO_ROOT / "generated" / "manifests" / "moex-dams-contracts.json"
)


class ExportError(Exception):
    """The models export cannot proceed."""


def load_paths(path: Path | None = None) -> dict[str, list[str]]:
    raw = yaml.safe_load((path or PATHS_FILE).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ExportError(f"{PATHS_FILE} must be a mapping")
    out: dict[str, list[str]] = {}
    for key in ("gitlab_owned", "code_owned", "root_files", "exclude"):
        value = raw.get(key) or []
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise ExportError(f"{key} must be a list of strings")
        out[key] = list(value)
    return out


def export_paths(spec: dict[str, list[str]]) -> list[str]:
    return [*spec["gitlab_owned"], *spec["code_owned"]]


def _run(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    print("+", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=cwd, env=env)
    if proc.returncode != 0:
        raise ExportError(f"command failed ({proc.returncode}): {' '.join(cmd)}")


def _git_sha(repo: Path) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        raise ExportError("cannot read git HEAD")
    return proc.stdout.strip()


def materialize(dest: Path, spec: dict[str, list[str]], *, revision: str = "HEAD") -> None:
    """Extract the owned paths at revision into dest."""
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    archive = dest.parent / f"{dest.name}.tar"
    _run(
        [
            "git",
            "-C",
            str(REPO_ROOT),
            "archive",
            "--format=tar",
            "-o",
            str(archive),
            revision,
            *export_paths(spec),
        ]
    )
    with tarfile.open(archive) as tar:
        try:
            tar.extractall(dest, filter="data")
        except TypeError:
            tar.extractall(dest)
    archive.unlink()


def _python() -> str:
    override = os.environ.get("MOEX_PYTHON")
    if override:
        return override
    for candidate in (
        REPO_ROOT / "apps" / "cli" / ".venv" / "Scripts" / "python.exe",
        REPO_ROOT / "apps" / "cli" / ".venv" / "bin" / "python",
    ):
        if candidate.is_file():
            return str(candidate)
    return sys.executable


def verify_tree(dest: Path) -> None:
    """Run the model checks against an extracted tree. Fail closed."""
    py = _python()
    env = os.environ.copy()
    env["MOEX_MODELS_ROOT"] = str(dest)
    env["MOEX_IMAGE_CONTRACTS_MANIFEST"] = str(IMAGE_MANIFEST)
    # preflight lives in apps/api, which is not part of the CLI virtualenv.
    api_src = str(REPO_ROOT / "apps" / "api" / "src")
    env["PYTHONPATH"] = api_src + os.pathsep + env.get("PYTHONPATH", "")
    steps = [
        [py, "-m", "moex_model_cli", "check-manifest", "--root", str(dest)],
        [py, "-m", "moex_model_cli", "lock", "verify", "--root", str(dest)],
        [py, "-m", "moex_dams.catalog.cli", "check", "--root", str(dest)],
        [py, "-m", "moex_dams.governance.cli", "check", "--root", str(dest)],
        [
            py,
            "-m",
            "moex_publication_viewer.cli",
            "build",
            "--root",
            str(dest),
            "--dist",
            str(dest / ".viewer-dist"),
        ],
        [py, "-m", "moex_model_api.preflight"],
        [py, "-m", "moex_model_cli.gates.publish_gate"],
    ]
    for cmd in steps:
        _run(cmd, cwd=dest, env=env)


def _copy_tree(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dest)
    elif src.is_file():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    else:
        raise ExportError(f"missing path to copy: {src}")


def _copy_root_files(dest: Path, spec: dict[str, list[str]]) -> None:
    for name in spec["root_files"]:
        src = TEMPLATE_DIR / name
        if not src.is_file():
            raise ExportError(f"root template missing: {src}")
        shutil.copy2(src, dest / name)


def _owned_dirty(repo: Path, prefixes: list[str]) -> list[str]:
    proc = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain"],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise ExportError(proc.stderr.strip() or "git status failed")
    dirty: list[str] = []
    for line in proc.stdout.splitlines():
        path = line[3:].strip().strip('"').replace("\\", "/")
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if any(path == prefix or path.startswith(prefix + "/") for prefix in prefixes):
            dirty.append(path)
    return dirty


def _commit(repo: Path, message: str) -> None:
    _run(["git", "-C", str(repo), "add", "-A"])
    status = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain"],
        check=False,
        capture_output=True,
        text=True,
    )
    if not status.stdout.strip():
        print("nothing to commit")
        return
    _run(["git", "-C", str(repo), "commit", "-m", message])


def cmd_verify(_args: argparse.Namespace) -> int:
    spec = load_paths()
    for rel in export_paths(spec):
        if not (REPO_ROOT / rel).exists():
            raise ExportError(f"export path missing in monorepo: {rel}")
    with tempfile.TemporaryDirectory(prefix="moex-models-") as tmp:
        dest = Path(tmp) / "tree"
        materialize(dest, spec)
        verify_tree(dest)
    print("verify OK")
    return 0


def _filter_repo_bin() -> str:
    found = shutil.which("git-filter-repo")
    if found:
        return found
    sibling = Path(_python()).parent
    for name in ("git-filter-repo.exe", "git-filter-repo"):
        candidate = sibling / name
        if candidate.is_file():
            return str(candidate)
    raise ExportError(
        "git-filter-repo is not installed. "
        "Install it (pip install git-filter-repo) and rerun seed."
    )


def cmd_seed(args: argparse.Namespace) -> int:
    spec = load_paths()
    dest = Path(args.dest).resolve()
    if dest.exists() and any(dest.iterdir()):
        raise ExportError(f"dest is not empty: {dest}")
    filt = _filter_repo_bin()
    dest.parent.mkdir(parents=True, exist_ok=True)
    _run(["git", "clone", "--no-local", str(REPO_ROOT), str(dest)])
    cmd = [filt, "--force"]
    for rel in export_paths(spec):
        cmd.extend(["--path", rel])
    _run(cmd, cwd=dest)
    _copy_root_files(dest, spec)
    sha = _git_sha(REPO_ROOT)
    _commit(dest, f"Add models repository root files.\n\nExported from {sha}.")
    print(dest)
    print("Push when ready: git -C", dest, "remote add origin <gitlab-url>")
    print("  git -C", dest, "push -u origin HEAD")
    return 0


def cmd_spec_sync(args: argparse.Namespace) -> int:
    spec = load_paths()
    clone = Path(args.models_clone).resolve()
    if not (clone / ".git").exists():
        raise ExportError(f"not a git clone: {clone}")
    dirty = _owned_dirty(clone, spec["gitlab_owned"])
    if dirty:
        raise ExportError(
            "models clone already has gitlab-owned changes: " + ", ".join(dirty[:8])
        )
    sha = _git_sha(REPO_ROOT)
    branch = args.branch or f"spec-sync/{sha}"
    _run(["git", "-C", str(clone), "checkout", "-B", branch])
    with tempfile.TemporaryDirectory(prefix="moex-spec-sync-") as tmp:
        staged = Path(tmp) / "code"
        code_only = {
            "gitlab_owned": [],
            "code_owned": spec["code_owned"],
            "root_files": [],
            "exclude": [],
        }
        materialize(staged, code_only)
        for rel in spec["code_owned"]:
            _copy_tree(staged / rel, clone / rel)
    _copy_root_files(clone, spec)
    leaked = _owned_dirty(clone, spec["gitlab_owned"])
    if leaked:
        _run(["git", "-C", str(clone), "reset", "--hard"])
        _run(["git", "-C", str(clone), "clean", "-fd"])
        raise ExportError("spec-sync touched gitlab-owned paths: " + ", ".join(leaked))
    _commit(clone, f"spec-sync from {sha}\n\nSchemas and generated files only.")
    if args.push:
        _run(
            [
                "git",
                "-C",
                str(clone),
                "push",
                "-u",
                "origin",
                "HEAD",
                "-o",
                "merge_request.create",
                "-o",
                "merge_request.target=main",
                "-o",
                f"merge_request.title=spec-sync {sha}",
            ]
        )
    else:
        print(f"branch {branch} committed locally. Re-run with --push to open a merge request.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export the models repository (ADR-058 D7)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_verify = sub.add_parser("verify", help="Check that the owned paths form a working tree")
    p_verify.set_defaults(func=cmd_verify)

    p_seed = sub.add_parser("seed", help="History-preserving export ready to push")
    p_seed.add_argument("--dest", required=True, help="Empty destination directory")
    p_seed.set_defaults(func=cmd_seed)

    p_sync = sub.add_parser("spec-sync", help="Copy code-owned paths into a models clone")
    p_sync.add_argument("--models-clone", required=True)
    p_sync.add_argument("--branch", default="", help="Default spec-sync/<git_sha>")
    p_sync.add_argument(
        "--push",
        action="store_true",
        help="Push and ask GitLab to open a merge request",
    )
    p_sync.set_defaults(func=cmd_spec_sync)

    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except ExportError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
