#!/usr/bin/env python3
"""Migrate legacy GovernanceAssignment slot names (ADR-049 PR-5).

Rewrites:
  classified_element_ref / policy_target_ref → target_element_ref
  policy_binding_id → assignment_id (when assignment_id absent)

Usage (repo root)::

    python scripts/migrate_governance_assignments.py --check
    python scripts/migrate_governance_assignments.py --write

Uses ruamel.yaml to preserve comments/key order. Idempotent.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ruamel.yaml import YAML

REPO = Path(__file__).resolve().parents[1]

_ASSIGNMENT_KEYS = (
    "classification_assignments",
    "policy_bindings",
    "ownership_assignments",
)


def _yaml() -> YAML:
    y = YAML(typ="rt")
    y.preserve_quotes = True
    y.width = 4096
    return y


def discover_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for base in (
        root / "model-assets" / "specifications" / "moex-dams" / "0.1" / "examples",
        root / "model-assets" / "implementations",
    ):
        if base.is_dir():
            paths.extend(sorted(base.rglob("*.yaml")))
    out: list[Path] = []
    seen: set[Path] = set()
    for p in paths:
        if not p.is_file():
            continue
        if p.name == "moex-dams-full.yaml":
            continue
        key = p.resolve()
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


def migrate_assignment(item: dict) -> list[str]:
    notes: list[str] = []
    target = item.get("target_element_ref")
    legacy_target = item.get("classified_element_ref") or item.get("policy_target_ref")
    if not target and legacy_target:
        item["target_element_ref"] = legacy_target
        notes.append(f"set target_element_ref from legacy ({legacy_target})")
    for legacy in ("classified_element_ref", "policy_target_ref"):
        if legacy in item:
            del item[legacy]
            notes.append(f"removed {legacy}")
    if not item.get("assignment_id") and item.get("policy_binding_id"):
        item["assignment_id"] = item["policy_binding_id"]
        notes.append("set assignment_id from policy_binding_id")
    if "policy_binding_id" in item:
        del item["policy_binding_id"]
        notes.append("removed policy_binding_id")
    if "assignment_scope" not in item:
        item["assignment_scope"] = "element"
        notes.append("set assignment_scope=element (default)")
    return notes


def migrate_document(data: dict) -> list[str]:
    notes: list[str] = []
    for key in _ASSIGNMENT_KEYS:
        items = data.get(key)
        if not isinstance(items, list):
            continue
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            for note in migrate_assignment(item):
                notes.append(f"{key}[{idx}]: {note}")
    # Nested model_packages under a repository wrapper.
    packages = data.get("model_packages")
    if isinstance(packages, list):
        for pidx, pkg in enumerate(packages):
            if isinstance(pkg, dict):
                for note in migrate_document(pkg):
                    notes.append(f"model_packages[{pidx}].{note}")
    return notes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO)
    parser.add_argument("--check", action="store_true", help="Report only")
    parser.add_argument("--write", action="store_true", help="Write changes")
    args = parser.parse_args(argv)
    if args.check == args.write:
        print("Specify exactly one of --check or --write", file=sys.stderr)
        return 2

    y = _yaml()
    changed = 0
    for path in discover_paths(args.root):
        text = path.read_text(encoding="utf-8")
        # Cheap filter: skip files with no assignment collections or legacy keys.
        if not any(
            marker in text
            for marker in (
                "classification_assignments",
                "policy_bindings",
                "ownership_assignments",
                "classified_element_ref",
                "policy_target_ref",
                "policy_binding_id",
            )
        ):
            continue
        try:
            data = y.load(text)
        except Exception as exc:  # noqa: BLE001 — skip unreadable YAML elsewhere
            print(f"skip {path.relative_to(args.root)}: {exc}", file=sys.stderr)
            continue
        if not isinstance(data, dict):
            continue
        notes = migrate_document(data)
        if not notes:
            continue
        changed += 1
        print(f"{path.relative_to(args.root)}:")
        for note in notes:
            print(f"  - {note}")
        if args.write:
            with path.open("w", encoding="utf-8", newline="\n") as fh:
                y.dump(data, fh)
    if changed == 0:
        print("no legacy governance assignment slots found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
