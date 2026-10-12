"""CLI wrapper for ADR-045 constraint-matrix checks.

Logic lives in ``moex_dams.rules.constraint_matrix`` (PR-C3a).

Usage (repo root)::

    python scripts/check_constraint_matrix.py
    python scripts/check_constraint_matrix.py --no-write-doc
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument(
        "--no-write-doc",
        action="store_true",
        help="Do not write docs/architecture/constraint-matrix.md",
    )
    ap.add_argument(
        "--write-doc",
        action="store_true",
        help="Write generated markdown (default)",
    )
    ap.add_argument(
        "--gate-strict",
        action="store_true",
        help="PR-C5: fail on planned / implemented-untested overall status",
    )
    args = ap.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    # Ensure editable / src packages resolve when run as a script.
    src = REPO / "packages" / "specification-dams" / "src"
    std = REPO / "packages" / "standard-linkml" / "src"
    for p in (str(src), str(std)):
        if p not in sys.path:
            sys.path.insert(0, p)

    from moex_dams.rules.constraint_matrix import (
        load_yaml,
        matrix_path,
        render_markdown,
        repo_root,
        run_check,
        validate_matrix,
    )

    root = repo_root()
    write_doc = not args.no_write_doc
    code, errors = run_check(
        write_doc=write_doc, root=root, gate_strict=args.gate_strict
    )
    data = load_yaml(matrix_path(root))
    if write_doc:
        print(f"wrote docs/architecture/constraint-matrix.md")
    if errors:
        print(f"check-constraints FAIL ({len(errors)}):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(
        f"check-constraints OK invariants={len(data.get('invariants') or [])} "
        f"registry={len(data.get('invariant_id_registry') or [])}"
        f"{' gate_strict' if args.gate_strict else ''}"
    )
    # Re-export for tests that import this module by path.
    _ = (validate_matrix, render_markdown)
    return code


# Backward-compatible re-exports for tests that load this file via importlib.
def _lazy_exports() -> None:
    src = REPO / "packages" / "specification-dams" / "src"
    std = REPO / "packages" / "standard-linkml" / "src"
    for p in (str(src), str(std)):
        if p not in sys.path:
            sys.path.insert(0, p)
    from moex_dams.rules import constraint_matrix as _cm

    globals()["validate_matrix"] = _cm.validate_matrix
    globals()["render_markdown"] = _cm.render_markdown
    globals()["REPO"] = _cm.repo_root()


_lazy_exports()


if __name__ == "__main__":
    raise SystemExit(main())
