#!/usr/bin/env python3
"""Strip deprecated DataFlow topology slots after ADR-048 PR-5.

Usage (repo root)::

    python scripts/migrate_dataflow_topology.py --check
    python scripts/migrate_dataflow_topology.py --write

Uses ruamel.yaml to preserve comments/key order. Idempotent.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ruamel.yaml import YAML

REPO = Path(__file__).resolve().parents[1]

TOPOLOGY_KEYS = (
    "source_solution_ref",
    "target_solution_ref",
    "source_system_ref",
    "target_system_ref",
    "source_platform_ref",
    "target_platform_ref",
    "integration_level",
    "integration_class",
    "integration_channel",
    "integration_spec_ref",
)

DEFAULT_PATHS = [
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "examples"
    / "client-data-flow.yaml",
]


def _yaml() -> YAML:
    y = YAML(typ="rt")
    y.preserve_quotes = True
    y.width = 4096
    return y


def discover_paths(root: Path) -> list[Path]:
    paths = list(DEFAULT_PATHS)
    impl = root / "model-assets" / "implementations"
    if impl.is_dir():
        paths.extend(sorted(impl.rglob("*.data-flow.yaml")))
    out: list[Path] = []
    seen: set[Path] = set()
    for p in paths:
        if not p.is_file():
            continue
        key = p.resolve()
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


def migrate_flow(data: dict, *, catalog_revision: str | None) -> list[str]:
    """Mutate flow mapping; return list of human notes."""
    notes: list[str] = []
    removed = [k for k in TOPOLOGY_KEYS if k in data]
    for k in removed:
        del data[k]
    if removed:
        notes.append(f"removed topology keys: {', '.join(removed)}")
    if catalog_revision and not data.get("bound_catalog_revision"):
        data["bound_catalog_revision"] = catalog_revision
        notes.append(f"set bound_catalog_revision={catalog_revision}")
    return notes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO)
    parser.add_argument("--check", action="store_true", help="Report only")
    parser.add_argument("--write", action="store_true", help="Write changes")
    parser.add_argument(
        "--catalog-revision",
        default=None,
        help="bound_catalog_revision to set when missing",
    )
    args = parser.parse_args(argv)
    if args.check == args.write:
        print("Specify exactly one of --check or --write", file=sys.stderr)
        return 2

    rev = args.catalog_revision
    if rev is None:
        snap = (
            args.root
            / "model-assets"
            / "catalog-snapshots"
            / "clinkr"
            / "catalog-snapshot.json"
        )
        if snap.is_file():
            import json

            rev = json.loads(snap.read_text(encoding="utf-8")).get("catalog_revision")

    y = _yaml()
    changed = 0
    for path in discover_paths(args.root):
        data = y.load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        notes = migrate_flow(data, catalog_revision=rev)
        if not notes:
            print(f"OK (noop) {path}")
            continue
        changed += 1
        print(f"{'WRITE' if args.write else 'CHECK'} {path}")
        for n in notes:
            print(f"  {n}")
        if args.write:
            with path.open("w", encoding="utf-8") as fh:
                y.dump(data, fh)
    print(f"files_needing_change={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
