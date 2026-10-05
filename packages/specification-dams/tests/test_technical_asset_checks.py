"""Negative fixtures for TechnicalAsset semantic checks (Variant B)."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_modeling import DiagnosticSeverity
from moex_standard_linkml.domain.body import LinkMLImplementationBody

from moex_dams.rules.formal_checks import check_formal_requirements
from moex_dams.rules.technical_assets import check_technical_assets

REPO = Path(__file__).resolve().parents[3]
CATALOG = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "requirements"
    / "it-solution-requirements.yaml"
)
EXAMPLE = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "requirements"
    / "examples"
    / "it-solution-model.example.yaml"
)


def _body(data: dict, path: str = "memory.yaml") -> LinkMLImplementationBody:
    return LinkMLImplementationBody(
        source_path=path,
        target_class="ModelPackage",
        data=data,
    )


def _example() -> dict:
    return yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))


def _errors_from_technical(data: dict) -> list:
    return [
        d
        for d in check_technical_assets(data)
        if d.severity == DiagnosticSeverity.ERROR
    ]


def _codes(diags) -> set[str]:
    return {d.diagnostic_code for d in diags}


def _base_carrier(**overrides) -> dict:
    base = {
        "element_id": "dams:physical/neg/carrier-a",
        "name": "carrier_a",
        "description": "Neg test carrier",
        "lifecycle_status": "active",
        "system_ref": "eam:system/EXAMPLE_CORE",
        "asset_namespace": "postgres://EXAMPLE_CORE",
        "qualified_name": "public.carrier_a",
        "technology": "PostgreSQL",
        "asset_kind": "relational_table",
        "structure_ref": "urn:schema:a",
        "direction": "internal",
        "mapping_coverage_status": "technical-only",
        "mapping_rationale": "neg fixture",
    }
    base.update(overrides)
    return base


def test_parent_ref_cycle() -> None:
    data = _example()
    data["data_carriers"] = [
        _base_carrier(
            element_id="dams:physical/neg/a",
            qualified_name="public.a",
            parent_ref="dams:physical/neg/b",
        ),
        _base_carrier(
            element_id="dams:physical/neg/b",
            name="carrier_b",
            qualified_name="public.b",
            parent_ref="dams:physical/neg/a",
        ),
    ]
    codes = _codes(_errors_from_technical(data))
    assert any("PDM-006" in c for c in codes)


def test_duplicate_asset_namespace_qualified_name() -> None:
    data = _example()
    data["data_carriers"] = [
        _base_carrier(element_id="dams:physical/neg/a", qualified_name="dup.key"),
        _base_carrier(element_id="dams:physical/neg/b", name="b", qualified_name="dup.key"),
    ]
    assert "DAMS-REQ-PDM-005.c1" in _codes(_errors_from_technical(data))


def test_operation_without_interface_ref() -> None:
    data = _example()
    data["access_points"] = [
        {
            "element_id": "dams:physical/neg/op",
            "name": "getParty",
            "description": "Operation without interface",
            "lifecycle_status": "active",
            "system_ref": "eam:system/EXAMPLE_CORE",
            "asset_namespace": "https://EXAMPLE_CORE",
            "qualified_name": "/api/party",
            "technology": "REST",
            "asset_kind": "operation",
        }
    ]
    assert "DAMS-REQ-PDM-011.c1" in _codes(_errors_from_technical(data))


def test_in_memory_with_location_uri() -> None:
    data = _example()
    data["data_carriers"] = [
        _base_carrier(
            element_id="dams:physical/neg/mem",
            asset_kind="in_memory",
            qualified_name="cache.party",
            location_uri="redis://localhost/0",
            structure_ref=None,
        )
    ]
    # Remove None keys that would confuse presence checks
    data["data_carriers"][0].pop("structure_ref", None)
    assert "DAMS-REQ-PDM-012.c1" in _codes(_errors_from_technical(data))


def test_wrong_asset_kind() -> None:
    data = _example()
    data["data_carriers"] = [
        _base_carrier(asset_kind="database")  # container kind on carrier
    ]
    assert "DAMS-REQ-PDM-007.c1" in _codes(_errors_from_technical(data))


def test_entity_physical_wrong_endpoint_types() -> None:
    data = _example()
    data["data_containers"] = [
        {
            "element_id": "dams:physical/neg/db",
            "name": "db",
            "description": "container",
            "lifecycle_status": "active",
            "system_ref": "eam:system/EXAMPLE_CORE",
            "asset_namespace": "postgres://EXAMPLE_CORE",
            "qualified_name": "example",
            "technology": "PostgreSQL",
            "asset_kind": "database",
        }
    ]
    # Point entity_physical at DataContainer instead of DataCarrier
    logical_id = data["logical_entities"][0]["element_id"]
    data["mappings"] = [
        {
            "element_id": "dams:mapping/neg/bad-ep",
            "name": "bad_entity_physical",
            "description": "Wrong ends",
            "lifecycle_status": "active",
            "mapping_type": "entity_physical",
            "source_refs": [logical_id],
            "target_refs": ["dams:physical/neg/db"],
        }
    ]
    assert "DAMS-REQ-PDM-009.c1" in _codes(_errors_from_technical(data))


def test_carrier_refs_pointing_at_data_container() -> None:
    data = _example()
    data["data_containers"] = [
        {
            "element_id": "dams:physical/neg/bucket",
            "name": "bucket",
            "description": "S3 bucket",
            "lifecycle_status": "active",
            "system_ref": "eam:system/EXAMPLE_CORE",
            "asset_namespace": "s3://EXAMPLE_CORE",
            "qualified_name": "party-bucket",
            "technology": "S3",
            "asset_kind": "bucket",
        }
    ]
    data["data_flows"] = [
        {
            "element_id": "dams:flow/neg/1",
            "name": "bad_flow",
            "description": "Flow with container in carrier_refs",
            "lifecycle_status": "active",
            "entity_bindings": [
                {
                    "element_id": "dams:flow/neg/1/bind",
                    "name": "bind",
                    "description": "bad binding",
                    "lifecycle_status": "active",
                    "carrier_refs": ["dams:physical/neg/bucket"],
                }
            ],
        }
    ]
    assert "DAMS-REQ-PDM-010.c1" in _codes(_errors_from_technical(data))


def test_direction_on_data_container() -> None:
    data = _example()
    data["data_containers"] = [
        {
            "element_id": "dams:physical/neg/db",
            "name": "db",
            "description": "container with direction",
            "lifecycle_status": "active",
            "system_ref": "eam:system/EXAMPLE_CORE",
            "asset_namespace": "postgres://EXAMPLE_CORE",
            "qualified_name": "example",
            "technology": "PostgreSQL",
            "asset_kind": "database",
            "direction": "internal",
        }
    ]
    assert "DAMS-REQ-PDM-008.c1" in _codes(_errors_from_technical(data))


def test_technical_checks_wired_into_formal_requirements() -> None:
    """Sanity: formal_checks runner surfaces PDM-005+ diagnostics."""
    data = _example()
    data["data_carriers"] = [
        _base_carrier(element_id="dams:physical/neg/a", qualified_name="dup.key"),
        _base_carrier(element_id="dams:physical/neg/b", name="b", qualified_name="dup.key"),
    ]
    diags = check_formal_requirements(_body(data), catalog_path=CATALOG)
    codes = {d.diagnostic_code for d in diags if d.severity == DiagnosticSeverity.ERROR}
    assert "DAMS-REQ-PDM-005.c1" in codes
