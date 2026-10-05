"""Workbench must not hardcode a single implementation slug or SlicePaths default."""

from __future__ import annotations

import ast
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC_ROOTS = (
    REPO / "apps" / "api" / "src",
    REPO / "apps" / "web" / "src",
)
SKIP_NAME_PARTS = (".test.", ".spec.", "__pycache__", "node_modules")
TRADING_RE = re.compile(r"(?<![A-Za-z0-9_-])trading(?![A-Za-z0-9_-])")
SLICE_DEFAULT_RE = re.compile(
    r"SlicePaths\.resolve\s*\(\s*(?:root\s*=\s*[^,)]+\s*)?\)"
)


def _iter_source_files() -> list[Path]:
    files: list[Path] = []
    for root in SRC_ROOTS:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in {".py", ".ts", ".tsx"}:
                continue
            name = path.name
            if any(part in name for part in SKIP_NAME_PARTS):
                continue
            if path.suffix in {".ts", ".tsx"} and (
                name.endswith(".test.ts")
                or name.endswith(".test.tsx")
                or name.endswith(".spec.ts")
                or name.endswith(".spec.tsx")
            ):
                continue
            files.append(path)
    return files


def test_no_trading_literal_in_workbench_src() -> None:
    offenders: list[str] = []
    for path in _iter_source_files():
        text = path.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), start=1):
            stripped = line.lstrip()
            if stripped.startswith("#") or stripped.startswith("//"):
                continue
            if TRADING_RE.search(line):
                offenders.append(f"{path.relative_to(REPO)}:{i}: {line.strip()}")
    assert not offenders, "trading literal found:\n" + "\n".join(offenders)


def test_no_default_slice_paths_resolve_in_api_src() -> None:
    api_src = REPO / "apps" / "api" / "src"
    offenders: list[str] = []
    for path in api_src.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        # Catch SlicePaths.resolve(root=...) without schema=/implementation=
        for i, line in enumerate(text.splitlines(), start=1):
            if "SlicePaths.resolve" not in line:
                continue
            if "schema=" in line or "implementation=" in line:
                continue
            # Multi-line calls: also flag bare resolve( with only root on same line
            if re.search(r"SlicePaths\.resolve\s*\(", line):
                # Look ahead a few lines for schema=/implementation=
                window = "\n".join(text.splitlines()[i - 1 : i + 6])
                if "schema=" not in window and "implementation=" not in window:
                    offenders.append(
                        f"{path.relative_to(REPO)}:{i}: {line.strip()}"
                    )
    assert not offenders, "default SlicePaths.resolve found:\n" + "\n".join(
        offenders
    )


def test_slice_paths_helper_always_passes_explicit_paths() -> None:
    """paths_for_asset must pass schema and implementation into SlicePaths."""
    support = (
        REPO
        / "apps"
        / "api"
        / "src"
        / "moex_model_api"
        / "implementation_support.py"
    )
    tree = ast.parse(support.read_text(encoding="utf-8"))
    found = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "resolve":
            keywords = {kw.arg for kw in node.keywords if kw.arg}
            if {"schema", "implementation"} <= keywords:
                found = True
    assert found, "paths_for_asset must call SlicePaths.resolve with schema+implementation"
