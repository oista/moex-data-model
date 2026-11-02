#!/usr/bin/env python3
"""Fill relationship_kind on draft solution relationships (ADR-056 D7 / F4-3).

Sets ``relationship_kind: reference`` on every Relationship in the four
solution models that lacks the slot. Does not change lifecycle_status or
add relation_term_ref.

Usage (repo root)::

    python scripts/migrate_solution_relationship_kind.py --check
    python scripts/migrate_solution_relationship_kind.py --write

Uses ruamel.yaml to preserve comments/key order. Idempotent.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ruamel.yaml import YAML

REPO = Path(__file__).resolve().parents[1]
SOLUTIONS = REPO / "model-assets" / "implementations" / "solutions"
TARGETS = (
    SOLUTIONS / "crm" / "crm-solution-model.yaml",
    SOLUTIONS / "esed" / "esed-solution-model.yaml",
    SOLUTIONS / "mdm" / "mdm-solution-model.yaml",
    SOLUTIONS / "ucd" / "ucd-solution-model.yaml",
)
KIND = "reference"


def _yaml() -> YAML:
    y = YAML(typ="rt")
    y.preserve_quotes = True
    y.width = 4096
    return y


def _fill(data: dict) -> list[str]:
    changes: list[str] = []
    for rel in data.get("relationships") or []:
        if not isinstance(rel, dict):
            continue
        if str(rel.get("relationship_kind") or "").strip():
            continue
        rel["relationship_kind"] = KIND
        eid = rel.get("element_id") or rel.get("name") or "?"
        changes.append(str(eid))
    return changes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Report missing kinds; exit 1 if any")
    mode.add_argument("--write", action="store_true", help="Write relationship_kind: reference")
    args = parser.parse_args(argv)

    y = _yaml()
    total = 0
    for path in TARGETS:
        if not path.is_file():
            print(f"missing: {path}", file=sys.stderr)
            return 2
        data = y.load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            print(f"not a mapping: {path}", file=sys.stderr)
            return 2
        changes = _fill(data)
        total += len(changes)
        if changes:
            print(f"{path.relative_to(REPO)}: {len(changes)} missing")
            for eid in changes:
                print(f"  - {eid}")
            if args.write:
                with path.open("w", encoding="utf-8") as fh:
                    y.dump(data, fh)
        else:
            print(f"{path.relative_to(REPO)}: ok")

    if args.check and total:
        print(f"missing relationship_kind on {total} relationships", file=sys.stderr)
        return 1
    if args.write:
        print(f"wrote relationship_kind={KIND} on {total} relationships")
    else:
        print(f"all {sum(1 for _ in TARGETS)} solution models have relationship_kind filled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
