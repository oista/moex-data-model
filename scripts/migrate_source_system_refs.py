#!/usr/bin/env python3
"""Propose LogicalEntity.source_system_refs from entity_physical mappings (ADR-056 PR-7f).

For each LogicalEntity, collect DataCarrier.system_ref values from
EntityPhysicalMapping (carrier → entity) and set ``source_system_refs`` when
the slot is absent. Does not override existing declarations or attribute-level
sources.

Usage (repo root)::

    python scripts/migrate_source_system_refs.py --check
    python scripts/migrate_source_system_refs.py --write

Uses ruamel.yaml to preserve comments/key order. Idempotent.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ruamel.yaml import YAML

REPO = Path(__file__).resolve().parents[1]

DEFAULT_TARGETS = (
    REPO / "model-assets" / "implementations" / "solutions" / "ucd" / "ucd-solution-model.yaml",
    REPO / "model-assets" / "implementations" / "solutions" / "mdm" / "mdm-solution-model.yaml",
    REPO / "model-assets" / "implementations" / "solutions" / "esed" / "esed-solution-model.yaml",
    REPO / "model-assets" / "implementations" / "solutions" / "crm" / "crm-solution-model.yaml",
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "requirements"
    / "examples"
    / "it-solution-model.example.yaml",
)


def _yaml() -> YAML:
    y = YAML(typ="rt")
    y.preserve_quotes = True
    y.width = 4096
    return y


def _carrier_system_map(data: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    for carrier in data.get("data_carriers") or []:
        if not isinstance(carrier, dict):
            continue
        eid = str(carrier.get("element_id") or "")
        sys_ref = carrier.get("system_ref")
        if eid and sys_ref:
            out[eid] = str(sys_ref)
    return out


def _entity_systems_from_mappings(
    data: dict, carrier_systems: dict[str, str]
) -> dict[str, list[str]]:
    """LogicalEntity element_id → ordered unique system refs."""
    collected: dict[str, list[str]] = {}
    for mapping in data.get("entity_physical_mappings") or []:
        if not isinstance(mapping, dict):
            continue
        if str(mapping.get("mapping_type") or "") not in ("", "entity_physical"):
            # typed collection already implies type; tolerate missing mapping_type
            pass
        sources = [str(s) for s in (mapping.get("source_refs") or [])]
        targets = [str(t) for t in (mapping.get("target_refs") or [])]
        systems = [carrier_systems[s] for s in sources if s in carrier_systems]
        if not systems:
            continue
        for tid in targets:
            bucket = collected.setdefault(tid, [])
            for sys_ref in systems:
                if sys_ref not in bucket:
                    bucket.append(sys_ref)
    return collected


def migrate_package(data: dict) -> list[str]:
    notes: list[str] = []
    if not isinstance(data, dict):
        return notes
    carrier_systems = _carrier_system_map(data)
    by_entity = _entity_systems_from_mappings(data, carrier_systems)
    for ent in data.get("logical_entities") or []:
        if not isinstance(ent, dict):
            continue
        eid = str(ent.get("element_id") or "")
        if "source_system_refs" in ent:
            continue
        systems = by_entity.get(eid) or []
        if not systems:
            notes.append(f"SKIP {eid or ent.get('name')}: no mapped carrier system")
            continue
        ent["source_system_refs"] = list(systems)
        notes.append(f"SET {eid}: {systems}")
    return notes


def process(path: Path, *, write: bool) -> tuple[bool, list[str]]:
    y = _yaml()
    data = y.load(path.read_text(encoding="utf-8"))
    notes = migrate_package(data)
    changed = any(n.startswith("SET ") for n in notes)
    if write and changed:
        with path.open("w", encoding="utf-8", newline="\n") as fh:
            y.dump(data, fh)
    return changed, notes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Report proposed changes")
    mode.add_argument("--write", action="store_true", help="Apply changes")
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Optional package YAML paths (default: ucd/mdm/esed/crm + example)",
    )
    args = parser.parse_args(argv)
    targets = [p.resolve() for p in args.paths] if args.paths else list(DEFAULT_TARGETS)
    any_change = False
    for path in targets:
        if not path.is_file():
            print(f"MISSING {path}", file=sys.stderr)
            return 2
        changed, notes = process(path, write=args.write)
        any_change = any_change or changed
        print(f"{'WRITE' if args.write and changed else 'CHECK'} {path.relative_to(REPO)}")
        for note in notes:
            print(f"  {note}")
    if args.check and any_change:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
