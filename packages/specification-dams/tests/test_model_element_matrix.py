"""ADR-044: induced-slot matrix after ModelElement decomposition.

Allowed deltas vs docs/architecture/model-element-matrix-before.csv:
- ModelElement.description → opt (abstract DescribedElement default)
- Relationship.description → opt (global optional; no class slot_usage)
- DataStructure.description → rec
- Mapping.description → opt
- Mapping name/title/glossary_term_refs/tags → absent (3.0.0 IdentifiedElement)
"""

from __future__ import annotations

import csv
from pathlib import Path

from linkml_runtime.utils.schemaview import SchemaView

REPO = Path(__file__).resolve().parents[3]
SCHEMA = REPO / "model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml"
BEFORE = REPO / "docs/architecture/model-element-matrix-before.csv"

BASE_SLOTS = (
    "element_id",
    "name",
    "title",
    "description",
    "lifecycle_status",
    "valid_from",
    "valid_to",
    "glossary_term_refs",
    "tags",
)

ABSENT, REQ, REC, OPT = "-", "req", "rec", "opt"

ALLOWED_DELTAS: dict[tuple[str, str], str] = {
    ("ModelElement", "description"): OPT,
    ("Relationship", "description"): OPT,
    ("DataStructure", "description"): REC,
    ("Mapping", "description"): OPT,
    ("Mapping", "name"): ABSENT,
    ("Mapping", "title"): ABSENT,
    ("Mapping", "glossary_term_refs"): ABSENT,
    ("Mapping", "tags"): ABSENT,
}

MIXIN_SKIP = frozenset(
    {
        "HasLifecycle",
        "HasDefinition",
        "HasOwnership",
        "HasProvenance",
        "HasBusinessClassification",
        "HasGovernanceClassification",
        "HasPolicyBindings",
        "HasStructure",
        "HasLocation",
        "HasProtocolBinding",
        "Contains",
    }
)


def _cell(sv: SchemaView, cls: str, slot: str) -> str:
    slots = {s.name: s for s in sv.class_induced_slots(cls)}
    induced = slots.get(slot)
    if induced is None:
        return ABSENT
    if induced.required:
        return REQ
    if getattr(induced, "recommended", None):
        return REC
    return OPT


def test_matrix_required_invariant():
    assert BEFORE.is_file()
    sv = SchemaView(str(SCHEMA))
    with BEFORE.open(encoding="utf-8", newline="") as fh:
        before_rows = {row["class"]: row for row in csv.DictReader(fh)}

    mismatches: list[str] = []
    for cls, brow in sorted(before_rows.items()):
        if cls not in sv.all_classes():
            mismatches.append(f"missing class {cls}")
            continue
        if brow["role"] == "mixin" and cls in MIXIN_SKIP:
            continue
        for slot in BASE_SLOTS:
            expected = ALLOWED_DELTAS.get((cls, slot), brow[slot])
            actual = _cell(sv, cls, slot)
            if actual != expected:
                mismatches.append(
                    f"{cls}.{slot}: before={brow[slot]} expected={expected} after={actual}"
                )
    assert mismatches == [], "\n".join(mismatches)


def test_has_definition_induces_optional_description_with_skos_mapping():
    sv = SchemaView(str(SCHEMA))
    induced = sv.induced_slot("description", "LogicalEntity")
    assert induced.required is not True
    assert "skos:definition" in (induced.exact_mappings or [])


def test_mapping_is_identified_element_without_name():
    sv = SchemaView(str(SCHEMA))
    induced = {s.name for s in sv.class_induced_slots("Mapping")}
    assert "name" not in induced
    assert "title" not in induced
    assert "glossary_term_refs" not in induced
    assert "tags" not in induced
    assert "description" in induced
    assert "valid_from" in induced
    assert sv.get_class("Mapping").is_a == "IdentifiedElement"


def test_schema_version_is_3_0_0():
    sv = SchemaView(str(SCHEMA))
    assert sv.schema.version == "3.0.0"


def test_pydantic_field_required_sets_match_for_key_classes():
    from moex_dams_contracts import (
        ConceptualEntity,
        DataStructure,
        LogicalEntity,
        Mapping,
        ModelPackage,
        Relationship,
        SchemaNode,
    )

    sv = SchemaView(str(SCHEMA))
    pairs = [
        ("ModelPackage", ModelPackage),
        ("LogicalEntity", LogicalEntity),
        ("ConceptualEntity", ConceptualEntity),
        ("Relationship", Relationship),
        ("Mapping", Mapping),
        ("DataStructure", DataStructure),
        ("SchemaNode", SchemaNode),
    ]
    for cname, model in pairs:
        induced = {s.name: s for s in sv.class_induced_slots(cname)}
        fields = model.model_fields
        for sname, slot in induced.items():
            if sname not in fields:
                continue
            field_required = fields[sname].is_required()
            if slot.required:
                assert field_required, f"{cname}.{sname} required in schema but optional in pydantic"
            else:
                assert not field_required, f"{cname}.{sname} optional in schema but required in pydantic"
