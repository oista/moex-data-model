"""Report Mapping labels (ADR-044 / D3). Uses ruamel.yaml to preserve order/comments.

In DAMS 2.1.0 Mapping.name is optional+deprecated; label =
source_refs -> target_refs [mapping_type]; name remains fallback.
Does not strip name (that is PR-6 / --strip-deprecated).

Usage:
  python scripts/migrate_mapping_labels.py --report docs/migration/mapping-name-report.md
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ruamel.yaml import YAML

REPO = Path(__file__).resolve().parents[1]
IMPL_ROOT = REPO / "model-assets" / "implementations"
DENYLIST = frozenset({"moex-dams-full.yaml"})
DEPRECATED_MAPPING_SLOTS = ("name", "title", "aliases", "glossary_term_refs", "tags")


def _yaml() -> YAML:
    y = YAML()
    y.preserve_quotes = True
    y.width = 4096
    y.allow_duplicate_keys = True
    return y


def mapping_label(m: dict) -> str:
    sources = m.get("source_refs") or []
    targets = m.get("target_refs") or []
    mtype = m.get("mapping_type") or "?"
    src = ", ".join(str(x) for x in sources) if sources else "?"
    tgt = ", ".join(str(x) for x in targets) if targets else "?"
    return f"{src} -> {tgt} [{mtype}]"


def _iter_mappings(node) -> list[tuple[list, int, dict]]:
    found: list[tuple[list, int, dict]] = []
    if isinstance(node, dict):
        items = node.get("mappings")
        if isinstance(items, list):
            for i, m in enumerate(items):
                if isinstance(m, dict) and (
                    "mapping_type" in m or "source_refs" in m or "target_refs" in m
                ):
                    found.append((items, i, m))
        for v in node.values():
            found.extend(_iter_mappings(v))
    elif isinstance(node, list):
        for v in node:
            found.extend(_iter_mappings(v))
    return found


def scan_file(path: Path) -> list[dict]:
    data = _yaml().load(path.read_text(encoding="utf-8"))
    if data is None:
        return []
    try:
        rel = str(path.resolve().relative_to(REPO)).replace("\\", "/")
    except ValueError:
        rel = str(path)
    rows = []
    for _parent, _i, m in _iter_mappings(data):
        rows.append(
            {
                "file": rel,
                "element_id": m.get("element_id"),
                "name": m.get("name"),
                "label": mapping_label(m),
                "mapping_type": m.get("mapping_type"),
            }
        )
    return rows


def strip_deprecated_mapping_slots(path: Path) -> int:
    """PR-6 only: remove identity slots removed in DAMS 3.0.0."""
    y = _yaml()
    data = y.load(path.read_text(encoding="utf-8"))
    if data is None:
        return 0
    changed = 0
    for parent, i, m in _iter_mappings(data):
        touched = False
        for key in DEPRECATED_MAPPING_SLOTS:
            if key in m:
                del m[key]
                touched = True
                changed += 1
        if touched:
            parent[i] = m
    if changed:
        from io import StringIO

        buf = StringIO()
        y.dump(data, buf)
        path.write_text(buf.getvalue(), encoding="utf-8", newline="\n")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=IMPL_ROOT)
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--strip-deprecated",
        action="store_true",
        help="PR-6: remove name/title/aliases/tags/glossary_term_refs via ruamel",
    )
    args = parser.parse_args()

    files = sorted(args.root.rglob("*.yaml"))
    all_rows: list[dict] = []
    stripped = 0
    for path in files:
        if path.name in DENYLIST:
            continue
        all_rows.extend(scan_file(path))
        if args.strip_deprecated:
            stripped += strip_deprecated_mapping_slots(path)

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# Mapping.name inventory (ADR-044)",
            "",
            f"Scanned `{args.root.as_posix()}` — {len(all_rows)} Mapping records.",
            "",
            "| file | element_id | name | computed label | mapping_type |",
            "|---|---|---|---|---|",
        ]
        for r in all_rows:
            lines.append(
                f"| `{r['file']}` | `{r['element_id']}` | `{r['name']}` | `{r['label']}` | `{r['mapping_type']}` |"
            )
        lines.append("")
        args.report.write_text("\n".join(lines), encoding="utf-8", newline="\n")
        print(f"wrote {args.report} ({len(all_rows)} rows)")
    else:
        print(f"mappings={len(all_rows)}")
    if args.strip_deprecated:
        print(f"stripped_fields={stripped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
