"""Migrate legacy ``mappings:`` into typed collections (ADR-046 PR-3).

Uses ruamel.yaml to preserve comments and key order.

Mapping type → collection:
  realizes         → realizes_mappings
  entity_physical  → entity_physical_mappings
  field_mapping    → field_mappings
  aligns_with      → aligns_with_mappings

Unknown mapping_type values fail with a clear error listing element_id.

Usage:
  python scripts/migrate_mappings_to_typed_collections.py          # dry-run
  python scripts/migrate_mappings_to_typed_collections.py --dry-run
  python scripts/migrate_mappings_to_typed_collections.py --apply
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from io import StringIO
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

REPO = Path(__file__).resolve().parents[1]
MODEL_ASSETS = REPO / "model-assets"
IMPL_ROOT = MODEL_ASSETS / "implementations"
EXAMPLES_ROOT = (
    MODEL_ASSETS
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "requirements"
    / "examples"
)
DENYLIST = frozenset({"moex-dams-full.yaml"})

TYPE_TO_COLLECTION: dict[str, str] = {
    "realizes": "realizes_mappings",
    "entity_physical": "entity_physical_mappings",
    "field_mapping": "field_mappings",
    "aligns_with": "aligns_with_mappings",
}
LEGACY_KEY = "mappings"


def _yaml() -> YAML:
    y = YAML()
    y.preserve_quotes = True
    y.width = 4096
    y.allow_duplicate_keys = True
    return y


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO)).replace("\\", "/")
    except ValueError:
        return str(path)


def _is_mapping_item(item: Any) -> bool:
    return isinstance(item, dict) and (
        "mapping_type" in item or "source_refs" in item or "target_refs" in item
    )


def _ensure_typed_seq(owner: dict, key: str) -> list:
    if key not in owner or owner[key] is None:
        if isinstance(owner, CommentedMap):
            owner[key] = CommentedSeq()
        else:
            owner[key] = []
    seq = owner[key]
    if not isinstance(seq, list):
        raise TypeError(f"{key} must be a sequence")
    return seq


def _typed_element_ids(owner: dict) -> set[str]:
    ids: set[str] = set()
    for key in TYPE_TO_COLLECTION.values():
        for item in owner.get(key) or []:
            if isinstance(item, dict) and item.get("element_id"):
                ids.add(str(item["element_id"]))
    return ids


def _migrate_owner(owner: dict) -> tuple[Counter[str], list[str], bool]:
    """Move legacy mappings on ``owner`` into typed collections.

    Returns (moved_by_type, unknown_errors, changed).
    """
    moved: Counter[str] = Counter()
    unknowns: list[str] = []
    changed = False
    legacy = owner.get(LEGACY_KEY)
    if not isinstance(legacy, list):
        return moved, unknowns, changed

    typed_ids = _typed_element_ids(owner)
    remaining: list[Any] = []
    # Rebuild remaining as CommentedSeq when possible
    for item in list(legacy):
        if not _is_mapping_item(item):
            remaining.append(item)
            continue
        mtype = str(item.get("mapping_type") or "").strip()
        eid = str(item.get("element_id") or "") or "?"
        collection = TYPE_TO_COLLECTION.get(mtype)
        if collection is None:
            unknowns.append(f"{eid} (mapping_type={mtype!r})")
            remaining.append(item)
            continue
        if eid != "?" and eid in typed_ids:
            # Already present in typed collection — drop legacy duplicate
            moved[mtype] += 1
            changed = True
            continue
        seq = _ensure_typed_seq(owner, collection)
        seq.append(item)
        if eid != "?":
            typed_ids.add(eid)
        moved[mtype] += 1
        changed = True

    if unknowns:
        return moved, unknowns, False

    if changed:
        if remaining:
            if isinstance(legacy, CommentedSeq):
                del legacy[:]
                for item in remaining:
                    legacy.append(item)
            else:
                owner[LEGACY_KEY] = remaining
        else:
            # Prefer delete empty key
            if LEGACY_KEY in owner:
                del owner[LEGACY_KEY]

    return moved, unknowns, changed


def _walk_owners(node: Any) -> list[dict]:
    """Find dicts that own a legacy ``mappings`` list of Mapping instances."""
    owners: list[dict] = []
    if isinstance(node, dict):
        items = node.get(LEGACY_KEY)
        if isinstance(items, list) and any(_is_mapping_item(x) for x in items):
            owners.append(node)
        for v in node.values():
            owners.extend(_walk_owners(v))
    elif isinstance(node, list):
        for v in node:
            owners.extend(_walk_owners(v))
    return owners


def migrate_file(path: Path, *, apply: bool) -> tuple[Counter[str], list[str], bool]:
    """Migrate one YAML file. Returns (moved_by_type, errors, written)."""
    y = _yaml()
    text = path.read_text(encoding="utf-8")
    data = y.load(text)
    if data is None:
        return Counter(), [], False

    total_moved: Counter[str] = Counter()
    all_unknowns: list[str] = []
    any_changed = False
    for owner in _walk_owners(data):
        moved, unknowns, changed = _migrate_owner(owner)
        total_moved.update(moved)
        all_unknowns.extend(unknowns)
        any_changed = any_changed or changed

    if all_unknowns:
        return total_moved, all_unknowns, False

    written = False
    if apply and any_changed:
        buf = StringIO()
        y.dump(data, buf)
        path.write_text(buf.getvalue(), encoding="utf-8", newline="\n")
        written = True
    return total_moved, [], written


def iter_scan_files() -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()
    roots = [IMPL_ROOT, EXAMPLES_ROOT]
    for root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.yaml")):
            if path.name in DENYLIST:
                continue
            rp = path.resolve()
            if rp in seen:
                continue
            seen.add(rp)
            files.append(path)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Report counts only (default when --apply is omitted)",
    )
    mode.add_argument(
        "--apply",
        action="store_true",
        help="Write migrated YAML files",
    )
    args = parser.parse_args()
    apply = bool(args.apply)

    files = iter_scan_files()
    grand: Counter[str] = Counter()
    files_touched = 0
    files_with_moves = 0
    errors: list[str] = []

    for path in files:
        moved, unknowns, written = migrate_file(path, apply=apply)
        if unknowns:
            rel = _rel(path)
            for u in unknowns:
                errors.append(f"{rel}: {u}")
            continue
        if sum(moved.values()) == 0:
            continue
        files_with_moves += 1
        if written:
            files_touched += 1
        grand.update(moved)
        rel = _rel(path)
        parts = ", ".join(f"{k}={v}" for k, v in sorted(moved.items()))
        print(f"{rel}: moved {sum(moved.values())} ({parts})")

    if errors:
        print("ERROR: unknown/legacy mapping_type — leave in mappings and fix:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    print("---")
    print(f"mode={'apply' if apply else 'dry-run'}")
    print(f"files_with_moves={files_with_moves}")
    if apply:
        print(f"files_written={files_touched}")
    print(f"total_moved={sum(grand.values())}")
    for mtype, coll in TYPE_TO_COLLECTION.items():
        print(f"  {mtype} -> {coll}: {grand.get(mtype, 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
