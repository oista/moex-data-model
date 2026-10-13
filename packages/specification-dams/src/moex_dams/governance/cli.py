"""CLI for EffectiveGovernanceView materialize / check (ADR-049)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from moex_dams.governance.materialize import (
    check_governance_view,
    discover_package_paths,
    load_as_of,
    materialize_governance_view,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="moex-dams-governance")
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root (default: cwd)",
    )
    common.add_argument(
        "--as-of",
        type=str,
        default=None,
        help="Resolution date (default: moex-governance-view/0.1/as_of.txt)",
    )

    mat = sub.add_parser(
        "materialize",
        parents=[common],
        help="Write generated/governance/EffectiveGovernanceView",
    )
    mat.add_argument(
        "--packages",
        type=Path,
        nargs="*",
        default=None,
        help="ModelPackage YAML paths (default: discover curated examples)",
    )

    sub.add_parser(
        "check",
        parents=[common],
        help="Fail on blocking diagnostics or hand-edited EffectiveGovernanceView",
    )

    args = parser.parse_args(argv)
    root = args.root.resolve()
    as_of = args.as_of or load_as_of(root)

    if args.command == "materialize":
        packages = list(args.packages) if args.packages else None
        if packages is None:
            packages = discover_package_paths(root)
        out, _view, findings = materialize_governance_view(
            root, as_of=as_of, package_paths=packages, write=True
        )
        print(f"wrote {out}")
        for f in findings:
            print(f"[{f.severity}] {f.code}: {f.message}")
        if any(f.severity == "error" for f in findings):
            return 1
        return 0

    if args.command == "check":
        errors = check_governance_view(root, as_of=as_of)
        for e in errors:
            print(e, file=sys.stderr)
        if errors:
            return 1
        print("check-governance OK")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
