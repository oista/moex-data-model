"""Schema metadata checks for deprecated LogicalAttribute slots."""

from __future__ import annotations

from pathlib import Path

from linkml_runtime.utils.schemaview import SchemaView

SCHEMA = (
    Path(__file__).resolve().parents[3]
    / "model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml"
)

DEPRECATED_SLOTS = {
    "logical_type": "dams:data_type_ref",
    "format_pattern": "dams:value_domain_ref",
    "value_set_ref": "dams:value_domain_ref",
    "unit_code": "dams:value_domain_ref",
}


def test_deprecated_slots_have_linkml_metadata():
    sv = SchemaView(str(SCHEMA))
    for name, replacement in DEPRECATED_SLOTS.items():
        slot = sv.get_slot(name)
        assert slot is not None, name
        assert slot.deprecated, f"{name} missing deprecated text"
        assert (
            str(slot.deprecated_element_has_possible_replacement) == replacement
        ), name


def test_concept_ref_not_required_on_logical_attribute():
    sv = SchemaView(str(SCHEMA))
    cls = sv.get_class("LogicalAttribute")
    assert cls is not None
    induced = sv.induced_slot("concept_ref", "LogicalAttribute")
    assert induced.required is not True
