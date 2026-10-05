"""Acceptance: migrated solution attributes are not typed only via deprecated slots.

During the deprecation window (before PR-5 slot removal), every LogicalAttribute in
solution ModelPackage YAML must carry ``data_type_ref`` and/or ``value_domain_ref``.
``logical_type`` may still be present as a transitional mirror.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]

SOLUTION_ROOTS = (
    REPO / "model-assets" / "implementations" / "solutions",
    REPO / "model-assets" / "specifications" / "moex-dams" / "0.1" / "examples",
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "requirements"
    / "examples",
)

DENY_NAMES = frozenset({"moex-dams-full.yaml"})


def _iter_solution_packages() -> list[Path]:
    files: list[Path] = []
    for root in SOLUTION_ROOTS:
        if not root.is_dir():
            continue
        for path in root.rglob("*.yaml"):
            if path.name in DENY_NAMES:
                continue
            files.append(path)
    return files


def _attrs(data: dict) -> list[tuple[str, dict]]:
    out: list[tuple[str, dict]] = []
    for ent in data.get("logical_entities") or []:
        if not isinstance(ent, dict):
            continue
        for attr in ent.get("attributes") or []:
            if isinstance(attr, dict) and attr.get("element_id"):
                out.append((str(attr["element_id"]), attr))
    return out


def test_solution_attributes_have_typed_refs() -> None:
    offenders: list[str] = []
    scanned = 0
    for path in _iter_solution_packages():
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        # Skip non-package / schema dumps
        if "logical_entities" not in data and "classes" in data:
            continue
        rel = path.relative_to(REPO).as_posix()
        for eid, attr in _attrs(data):
            scanned += 1
            has_dt = bool(str(attr.get("data_type_ref") or "").strip())
            has_vd = bool(str(attr.get("value_domain_ref") or "").strip())
            has_lt = bool(str(attr.get("logical_type") or "").strip())
            if has_lt and not (has_dt or has_vd):
                offenders.append(f"{rel}: {eid} has logical_type without typed ref")
            if not (has_dt or has_vd or has_lt):
                offenders.append(f"{rel}: {eid} has no type representation")
    assert scanned > 0, "No LogicalAttribute instances found to scan"
    assert not offenders, (
        "Unmigrated attribute typing residue:\n" + "\n".join(offenders[:100])
    )
