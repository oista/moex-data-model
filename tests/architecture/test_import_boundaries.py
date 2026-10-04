"""Fitness: standard-linkml must not import moex_dams (ADR-022 / ADR-004)."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LINKML_SRC = ROOT / "packages" / "standard-linkml" / "src"


def _imports_moex_dams(path: Path) -> list[str]:
    hits: list[str] = []
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "moex_dams" or alias.name.startswith("moex_dams."):
                    hits.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod == "moex_dams" or mod.startswith("moex_dams."):
                hits.append(mod)
    return hits


def test_standard_linkml_does_not_import_moex_dams():
    offenders: list[str] = []
    for path in LINKML_SRC.rglob("*.py"):
        for mod in _imports_moex_dams(path):
            offenders.append(f"{path.relative_to(ROOT)}: {mod}")
    assert not offenders, (
        "moex_standard_linkml must not import moex_dams "
        "(assess orchestration belongs in apps/cli):\n" + "\n".join(offenders)
    )
