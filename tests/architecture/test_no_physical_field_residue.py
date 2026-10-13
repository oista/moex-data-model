"""Acceptance: PhysicalField-era tokens only in allowlisted migration/history paths."""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Assemble tokens so this file does not itself contain contiguous banned literals.
_CLS = "Physical" + "Field"
_COLL = "physical" + "_fields"
# Note: message_type is a live DataCarrierKindEnum value (ADR-040) — not residue.
RESIDUE_RE = re.compile(rf"{re.escape(_CLS)}|\b{re.escape(_COLL)}\b")

# Path prefixes (posix, relative to repo root) where residue is allowed.
# docs/ is NOT blanket-allowlisted: only migration/history/ADR paths (R2-2).
ALLOW_PREFIXES = (
    "scripts/archive/",
    "scripts/spike_schema_node_generators.py",
    "scripts/migrate_physical_to_technical_asset.py",
    "tests/migration/",
    "tests/architecture/test_no_physical_field_residue.py",
    "tests/architecture/test_architecture_docs_current.py",
    "docs/migration/",
    "docs/changelog/",
    "docs/adr/",
    "docs/audit/",
    "docs/superpowers/",
    "docs/architecture/model-element-inventory-report.md",
    "docs/architecture/invariant-candidates.csv",
    "docs/architecture/uml/description.md",
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

_HISTORICAL_MARKERS = (
    "removed",
    "replaces",
    "вместо",
    "заменя",
    "удал",
    "legacy",
    "deprecated",
    "прежн",
    "historical",
    "историч",
)


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


def _is_historical_line(line: str) -> bool:
    lower = line.lower()
    return any(marker in lower for marker in _HISTORICAL_MARKERS)


def test_no_physical_field_residue() -> None:
    offenders: list[str] = []
    for path in _iter_files():
        rel = _rel_posix(path)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            # Allow explicit historical notes in otherwise-scanned docs
            # (UML "PhysicalField removed", glossary "вместо PhysicalField").
            if rel.startswith("docs/") and _is_historical_line(line):
                continue
            if RESIDUE_RE.search(line):
                offenders.append(f"{rel}:{i}: {line.strip()}")
    assert not offenders, (
        "Legacy PhysicalField-era residue outside allowlist:\n"
        + "\n".join(offenders[:200])
        + (f"\n... and {len(offenders) - 200} more" if len(offenders) > 200 else "")
    )
