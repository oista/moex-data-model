#!/usr/bin/env python3
"""Fill LogicalEntity.title and DataCarrier.technology on test fixtures (ADR-056 PR-8).

Authored solution packages already have both slots. This script only patches
L2 invariant fixtures and package unit-test YAML that omit them, so they stay
complete packages after class slot_usage required.

Usage (repo root)::

    python scripts/migrate_pr8_required_slots.py --check
    python scripts/migrate_pr8_required_slots.py --write

Uses ruamel.yaml to preserve comments/key order. Idempotent.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ruamel.yaml import YAML

REPO = Path(__file__).resolve().parents[1]

DEFAULT_TARGETS = (
    REPO / "model-assets" / "specifications" / "moex-dams" / "0.1" / "examples" / "invariants" / "l2",
    REPO / "model-assets" / "specifications" / "moex-dams" / "0.1" / "examples" / "invariants",
    REPO / "packages" / "specification-dams" / "tests" / "fixtures" / "semantic" / "attr-removed-slots-only.yaml",
    REPO / "packages" / "specification-dams" / "tests" / "fixtures" / "data-structure" / "relational-table.yaml",
)

FIXTURE_TECHNOLOGY = "fixture"
CARRIER_KINDS = frozenset(
    {
        "relational_table",
        "relational_view",
        "file",
        "dataset",
        "stream_topic",
        "stream_queue",
        "in_memory",
        "api_resource",
        "other",
    }
)


def _yaml() -> YAML:
    y = YAML(typ="rt")
    y.preserve_quotes = True
    y.width = 4096
    return y


def _iter_files(targets: tuple[Path, ...]) -> list[Path]:
    out: list[Path] = []
    for t in targets:
        if t.is_file():
            out.append(t)
        elif t.is_dir():
            out.extend(sorted(t.glob("*.yaml")))
    return out


def _is_carrier_document(data: dict) -> bool:
    kind = str(data.get("asset_kind") or "")
    return kind in CARRIER_KINDS and "data_carriers" not in data


def _fill(data: dict) -> list[str]:
    changes: list[str] = []
    if _is_carrier_document(data):
        if not str(data.get("technology") or "").strip():
            data["technology"] = FIXTURE_TECHNOLOGY
            changes.append(f"technology {data.get('element_id')}")
        return changes
    for ent in data.get("logical_entities") or []:
        if not isinstance(ent, dict):
            continue
        if str(ent.get("title") or "").strip():
            continue
        name = str(ent.get("name") or ent.get("element_id") or "entity")
        ent["title"] = name
        changes.append(f"title {ent.get('element_id')}")
    for car in data.get("data_carriers") or []:
        if not isinstance(car, dict):
            continue
        if str(car.get("technology") or "").strip():
            continue
        car["technology"] = FIXTURE_TECHNOLOGY
        changes.append(f"technology {car.get('element_id')}")
    return changes


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()

    yaml = _yaml()
    pending = 0
    for path in _iter_files(DEFAULT_TARGETS):
        data = yaml.load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        changes = _fill(data)
        if not changes:
            continue
        pending += 1
        rel = path.relative_to(REPO)
        print(f"{rel}: {', '.join(changes)}")
        if args.write:
            with path.open("w", encoding="utf-8", newline="\n") as fh:
                yaml.dump(data, fh)
    if args.check:
        print(f"files needing fill: {pending}")
        return 1 if pending else 0
    print(f"wrote {pending} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
