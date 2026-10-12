"""CLI for catalog snapshot materialize / check (ADR-048)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from moex_dams.catalog.drift import has_blocking_errors
from moex_dams.catalog.materialize import (
    check_topology_view,
    discover_flow_paths,
    materialize_topology_view,
)
from moex_dams.catalog.snapshot import default_snapshot_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="moex-dams-catalog")
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root (default: cwd)",
    )
    common.add_argument(
        "--snapshot",
        type=Path,
        default=None,
        help="Catalog snapshot JSON (default: model-assets/catalog-snapshots/clinkr/...)",
    )

    mat = sub.add_parser(
        "materialize",
        parents=[common],
        help="Write generated/topology/TopologyView from snapshot + flows",
    )
    mat.add_argument(
        "--flows",
        type=Path,
        nargs="*",
        default=None,
        help="DataFlow YAML paths (default: discover examples + *.data-flow.yaml)",
    )

    chk = sub.add_parser(
        "check",
        parents=[common],
        help="Fail on blocking drift or hand-edited TopologyView",
    )

    args = parser.parse_args(argv)
    root = args.root.resolve()
    snap = args.snapshot or default_snapshot_path(root)

    if args.command == "materialize":
        flows = list(args.flows) if args.flows else None
        if flows is None:
            flows = discover_flow_paths(root)
        out, _view, findings = materialize_topology_view(
            root, snapshot_path=snap, flow_paths=flows, write=True
        )
        print(f"wrote {out}")
        for f in findings:
            print(f"[{f.severity}] {f.code}: {f.message}")
        return 1 if has_blocking_errors(findings) else 0

    if args.command == "check":
        errors = check_topology_view(root, snapshot_path=snap)
        for e in errors:
            print(e, file=sys.stderr)
        if errors:
            return 1
        print("check-topology OK")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
