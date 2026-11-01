"""Count formal_checks diagnostics on solution and enterprise models.

Usage (repo root)::

    python scripts/report_requirement_impact.py

Prints per-file and total counts keyed by (requirement_code, diagnostic_code,
severity). Used as before/after evidence for ADR-056 PR-10c/10d/10f.
Does not write files.
"""

from __future__ import annotations

import collections
import sys
import types
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]


def _details_map(diag: object) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in getattr(diag, "details", None) or ():
        key = getattr(item, "detail_key", None)
        if key:
            out[str(key)] = str(getattr(item, "detail_value", "") or "")
    return out


def _severity(diag: object) -> str:
    raw = str(getattr(diag, "severity", "") or "")
    return raw.rsplit(".", 1)[-1]


def _count_file(path: Path, *, repo_root: Path) -> collections.Counter[tuple[str, str, str]]:
    from moex_dams.rules.formal_checks import check_formal_requirements

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return collections.Counter()
    body = types.SimpleNamespace(data=data, source_path=str(path))
    diags = check_formal_requirements(body, repo_root=repo_root)
    counts: collections.Counter[tuple[str, str, str]] = collections.Counter()
    for diag in diags:
        details = _details_map(diag)
        req = details.get("requirement_code") or "-"
        code = str(getattr(diag, "diagnostic_code", "") or "-")
        counts[(req, code, _severity(diag))] += 1
    return counts


def _iter_targets() -> list[Path]:
    roots = [
        REPO / "model-assets" / "implementations" / "solutions",
        REPO
        / "model-assets"
        / "implementations"
        / "enterprise"
        / "moex-enterprise-conceptual-model"
        / "0.1",
    ]
    out: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        out.extend(sorted(root.rglob("*-solution-model.yaml")))
        out.extend(sorted(root.glob("enterprise-conceptual-model.yaml")))
    return out


def main() -> int:
    sys.path.insert(0, str(REPO / "packages" / "specification-dams" / "src"))
    totals: collections.Counter[tuple[str, str, str]] = collections.Counter()
    for path in _iter_targets():
        counts = _count_file(path, repo_root=REPO)
        rel = path.relative_to(REPO)
        print(f"## {rel} {sum(counts.values())}")
        for key, n in sorted(counts.items()):
            print(f"   {key} {n}")
            totals[key] += n
    print("== TOTAL")
    for key, n in sorted(totals.items()):
        print(f"   {key} {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
