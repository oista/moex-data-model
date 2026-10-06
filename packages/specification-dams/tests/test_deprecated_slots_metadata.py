"""Schema checks after PR-5 removal of deprecated LogicalAttribute slots."""

from __future__ import annotations

from pathlib import Path

from linkml_runtime.utils.schemaview import SchemaView

REPO = Path(__file__).resolve().parents[3]
SCHEMA = REPO / "model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml"
ARCHIVE = REPO / "docs/migration/archive/moex-deprecated-slots.yaml"
LIVE_DEPRECATED = (
    REPO
    / "model-assets/specifications/moex-dams/0.1/schemas/moex-deprecated-slots.yaml"
)

REMOVED = ("logical_type", "format_pattern", "value_set_ref", "unit_code")


def test_deprecated_attr_slots_removed_from_logical_attribute():
    sv = SchemaView(str(SCHEMA))
    induced = {s.name for s in sv.class_induced_slots("LogicalAttribute")}
    for name in REMOVED:
        assert name not in induced, name
    assert "data_type_ref" in induced
    assert "value_domain_ref" in induced


def test_concept_ref_not_required_on_logical_attribute():
    sv = SchemaView(str(SCHEMA))
    induced = sv.induced_slot("concept_ref", "LogicalAttribute")
    assert induced.required is not True


def test_moex_deprecated_slots_not_imported_archive_only():
    assert not LIVE_DEPRECATED.exists()
    assert ARCHIVE.is_file()
    text = SCHEMA.read_text(encoding="utf-8")
    assert "moex-deprecated-slots" not in text
    core = REPO / "model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml"
    assert "moex-deprecated-slots" not in core.read_text(encoding="utf-8")


def test_schema_major_version_bumped():
    sv = SchemaView(str(SCHEMA))
    assert sv.schema.version == "3.0.0"
