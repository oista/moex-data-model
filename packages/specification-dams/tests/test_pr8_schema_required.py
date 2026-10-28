"""ADR-056 PR-8: catalog slot_required that belong in LinkML required."""

from __future__ import annotations

from pathlib import Path

from linkml_runtime.utils.schemaview import SchemaView

from moex_standard_linkml.validation import error_results, make_linkml_validator

REPO = Path(__file__).resolve().parents[3]
SCHEMA = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "schemas"
    / "moex-dams.yaml"
)


def _required(class_name: str) -> set[str]:
    sv = SchemaView(str(SCHEMA))
    return {s.name for s in sv.class_induced_slots(class_name) if s.required}


def test_package_identity_slots_already_required() -> None:
    req = _required("ModelPackage")
    assert {
        "element_id",
        "name",
        "description",
        "lifecycle_status",
        "api_version",
        "model_version",
    } <= req


def test_attribute_and_relationship_slot_required_already_in_schema() -> None:
    attr = _required("LogicalAttribute")
    assert {"element_id", "name", "lifecycle_status", "owner_entity_ref", "required", "multivalued"} <= attr
    rel = _required("Relationship")
    assert {"source_entity_ref", "target_entity_ref"} <= rel
    node = _required("SchemaNode")
    assert "local_key" in node
    carrier = _required("DataCarrier")
    assert {
        "system_ref",
        "asset_kind",
        "qualified_name",
        "asset_namespace",
        "lifecycle_status",
    } <= carrier


def test_logical_entity_title_required_class_slot_usage() -> None:
    assert "title" in _required("LogicalEntity")
    assert "title" not in _required("ConceptualEntity")
    sv = SchemaView(str(SCHEMA))
    assert sv.get_slot("title").required is not True


def test_data_carrier_technology_required_not_other_assets() -> None:
    assert "technology" in _required("DataCarrier")
    assert "technology" not in _required("AccessPoint")
    assert "technology" not in _required("DataContainer")
    assert "technology" not in _required("ExecutionAsset")


def test_linkml_rejects_logical_entity_without_title() -> None:
    validator = make_linkml_validator(SCHEMA)
    base = {
        "element_id": "dams:logical/pr8/E",
        "name": "E",
        "title": "Сущность",
        "lifecycle_status": "active",
        "context_ref": "dams:context/pr8",
        "solution_data_role": "producer",
    }
    assert error_results(validator.validate(base, target_class="LogicalEntity")) == []
    missing = dict(base)
    missing.pop("title")
    assert error_results(validator.validate(missing, target_class="LogicalEntity"))


def test_linkml_rejects_data_carrier_without_technology() -> None:
    validator = make_linkml_validator(SCHEMA)
    base = {
        "element_id": "dams:physical/pr8/T",
        "name": "T",
        "description": "table",
        "lifecycle_status": "active",
        "system_ref": "eam:system/X",
        "asset_kind": "relational_table",
        "asset_namespace": "ns",
        "qualified_name": "T",
        "technology": "PostgreSQL",
    }
    assert error_results(validator.validate(base, target_class="DataCarrier")) == []
    missing = dict(base)
    missing.pop("technology")
    assert error_results(validator.validate(missing, target_class="DataCarrier"))
