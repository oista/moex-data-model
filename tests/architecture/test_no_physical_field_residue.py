"""Acceptance: PhysicalField-era tokens only in allowlisted migration/history paths."""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Assemble tokens so this file does not itself contain contiguous banned literals.
_CLS = "Physical" + "Field"
_COLL = "physical" + "_fields"
_KIND = "message" + "_type"
RESIDUE_RE = re.compile(
    rf"{re.escape(_CLS)}|\b{re.escape(_COLL)}\b|\b{re.escape(_KIND)}\b"
)

# Path prefixes (posix, relative to repo root) where residue is allowed.
ALLOW_PREFIXES = (
    "scripts/migrate_physical_field_to_schema_node.py",
    "scripts/spike_schema_node_generators.py",
    "scripts/migrate_physical_to_technical_asset.py",
    "tests/migration/",
    "tests/architecture/test_no_physical_field_residue.py",
    "docs/",
    "tmp/",
    ".cursor/",
    "generated/",
    "apps/viewer/static/",
    "model-assets/implementations/enterprise/",
    "packages/standard-linkml/README.md",
    "packages/standard-linkml/templates/",
)

SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".tox",
}

SKIP_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".gz",
    ".whl",
    ".so",
    ".dll",
    ".exe",
    ".bin",
}

TEXT_SUFFIXES = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".md",
    ".mdc",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".txt",
    ".csv",
    ".ps1",
    ".sh",
    ".puml",
    ".plantuml",
    ".html",
    ".css",
    ".rst",
    ".ini",
    ".cfg",
    ".makefile",
}


def _rel_posix(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def _is_allowlisted(rel: str) -> bool:
    for prefix in ALLOW_PREFIXES:
        if rel == prefix.rstrip("/") or rel.startswith(prefix):
            return True
    name = Path(rel).name.lower()
    if "changelog" in name:
        return True
    return False


def _should_scan(path: Path) -> bool:
    if path.suffix.lower() in SKIP_SUFFIXES:
        return False
    if path.suffix.lower() in TEXT_SUFFIXES:
        return True
    name = path.name.lower()
    return name in {"makefile", "dockerfile", "changelog"} or name.startswith(
        "makefile"
    )


def _iter_files() -> list[Path]:
    files: list[Path] = []
    for path in REPO.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        rel = _rel_posix(path)
        if _is_allowlisted(rel):
            continue
        if not _should_scan(path):
            continue
        files.append(path)
    return files


def test_no_physical_field_residue() -> None:
    offenders: list[str] = []
    for path in _iter_files():
        rel = _rel_posix(path)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            if RESIDUE_RE.search(line):
                offenders.append(f"{rel}:{i}: {line.strip()}")
    assert not offenders, (
        "Legacy PhysicalField-era residue outside allowlist:\n"
        + "\n".join(offenders[:200])
        + (f"\n... and {len(offenders) - 200} more" if len(offenders) > 200 else "")
    )
