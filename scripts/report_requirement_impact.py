"""Count formal_checks diagnostics on solution and enterprise models.

Usage (repo root)::

    python scripts/report_requirement_impact.py

Prints per-file and total counts keyed by (requirement_code, diagnostic_code,
severity). Used as before/after evidence for ADR-056 PR-10c/10d/10f and
follow-up PR-11.

Does not write files.

Target discovery (documented limitation):
- Under ``model-assets/implementations/solutions/**``: ``*-solution-model.yaml``
  (all four current solutions use that name).
- Under the enterprise conceptual tree: ``enterprise-conceptual-model.yaml``.
"""

from __future__ import annotations

import collections
import sys
import types
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]


def _details_map(diag: object) -> dict[str, str]:
    """Read Diagnostic.diagnostic_details (kernel domain field name)."""
    out: dict[str, str] = {}
    details = getattr(diag, "diagnostic_details", None)
    if details is None:
        details = getattr(diag, "details", None)
    for item in details or ():
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


def _iter_targets(repo_root: Path | None = None) -> list[Path]:
    root = repo_root or REPO
    roots = [
        root / "model-assets" / "implementations" / "solutions",
        root
        / "model-assets"
        / "implementations"
        / "enterprise"
        / "moex-enterprise-conceptual-model"
        / "0.1",
    ]
    out: list[Path] = []
    for base in roots:
        if not base.is_dir():
            continue
        out.extend(sorted(base.rglob("*-solution-model.yaml")))
        out.extend(sorted(base.glob("enterprise-conceptual-model.yaml")))
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
