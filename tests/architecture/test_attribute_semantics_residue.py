"""Acceptance: removed LogicalAttribute slots must not reappear outside allowlist.

Banned on LogicalAttribute instance data: logical_type, format_pattern,
value_set_ref, unit_code (PR-5 / ADR-034 step 2).
``format_pattern`` / ``unit_code`` remain valid on ValueDomain.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]

BANNED_ATTR_KEYS = frozenset(
    {"logical_type", "format_pattern", "value_set_ref", "unit_code"}
)

SOLUTION_ROOTS = (
    REPO / "model-assets" / "implementations" / "solutions",
    REPO / "model-assets" / "implementations" / "imports",
    REPO / "model-assets" / "specifications" / "moex-dams" / "0.1" / "examples",
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "requirements"
    / "examples",
)

# Grep-style residue for removed slot names outside migration/history paths.
RESIDUE_TOKENS = (
    "logical_type",
    # value_set_ref is attribute-only deprecated; value_set_source stays
    "value_set_ref",
)

ALLOW_PREFIXES = (
    "scripts/migrate_logical_attribute_semantics.py",
    "scripts/_strip_deprecated_attr_slots.py",
    "docs/migration/",
    "docs/adr/ADR-034",
    "docs/adr/ADR-037",
    "docs/superpowers/",
    "tmp/",
    ".cursor/",
    "generated/",
    "tests/migration/",
    "packages/specification-dams/tests/test_deprecated",
    "packages/specification-dams/src/moex_dams/application/diff.py",
    "model-assets/transformations/",
)


def _iter_packages() -> list[Path]:
    files: list[Path] = []
    for root in SOLUTION_ROOTS:
        if not root.is_dir():
            continue
        files.extend(root.rglob("*.yaml"))
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
    for path in _iter_packages():
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict) or "logical_entities" not in data:
            continue
        rel = path.relative_to(REPO).as_posix()
        for eid, attr in _attrs(data):
            scanned += 1
            has_dt = bool(str(attr.get("data_type_ref") or "").strip())
            has_vd = bool(str(attr.get("value_domain_ref") or "").strip())
            if not (has_dt or has_vd):
                offenders.append(f"{rel}: {eid} missing data_type_ref/value_domain_ref")
            banned = sorted(BANNED_ATTR_KEYS & set(attr))
            if banned:
                offenders.append(f"{rel}: {eid} still has {banned}")
    assert scanned > 0, "No LogicalAttribute instances found to scan"
    assert not offenders, (
        "Attribute semantics residue:\n" + "\n".join(offenders[:100])
    )


def test_no_logical_type_slot_in_schema() -> None:
    from linkml_runtime.utils.schemaview import SchemaView

    schema = (
        REPO
        / "model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml"
    )
    sv = SchemaView(str(schema))
    assert sv.get_slot("logical_type") is None
    assert sv.get_slot("value_set_ref") is None
    cls = sv.get_class("LogicalAttribute")
    assert cls is not None
    induced = {s.name for s in sv.class_induced_slots("LogicalAttribute")}
    assert "logical_type" not in induced
    assert "format_pattern" not in induced
    assert "unit_code" not in induced
    assert "value_set_ref" not in induced
    assert "data_type_ref" in induced
    # ValueDomain still owns format/unit
    vd_slots = {s.name for s in sv.class_induced_slots("ValueDomain")}
    assert "format_pattern" in vd_slots
    assert "unit_code" in vd_slots
