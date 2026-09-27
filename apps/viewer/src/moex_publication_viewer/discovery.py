"""Discover publish.yaml files under a repository root."""

from __future__ import annotations

from pathlib import Path

SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    "dist",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "egg-info",
}


def discover_manifest_paths(root: Path) -> list[Path]:
    """Return sorted paths to publish.yaml, skipping ignored directories."""
    root = root.resolve()
    found: list[Path] = []
    for path in root.rglob("publish.yaml"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_NAMES or part.endswith(".egg-info") for part in path.parts):
            continue
        found.append(path)
    return sorted(found)
