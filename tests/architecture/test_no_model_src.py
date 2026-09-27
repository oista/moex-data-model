"""Guard: live code/config must not point at the retired model_src/ tree."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

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
    "agent-transcripts",
    ".cursor",
}

# Executable / config surfaces that must use model-assets paths.
SCAN_SUFFIXES = {".py", ".ps1", ".toml"}
SCAN_NAMES = {"Makefile"}


def test_no_live_model_src_path_references() -> None:
    """Fail if Python/PowerShell/TOML/Makefile still reference model_src."""
    offenders: list[str] = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_NAMES or part.endswith(".egg-info") for part in path.parts):
            continue
        if path.name == "test_no_model_src.py":
            continue
        if path.suffix.lower() not in SCAN_SUFFIXES and path.name not in SCAN_NAMES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if "model_src" in text:
            offenders.append(path.relative_to(REPO_ROOT).as_posix())

    assert offenders == [], (
        "stale model_src references in code/config "
        "(use model-assets/; document history only under docs/migration/):\n"
        + "\n".join(f"  - {o}" for o in offenders)
    )


def test_model_src_directory_absent_or_empty() -> None:
    root = REPO_ROOT / "model_src"
    if not root.exists():
        return
    remaining = [p for p in root.rglob("*") if p.is_file()]
    assert remaining == [], f"model_src still contains files: {remaining}"
