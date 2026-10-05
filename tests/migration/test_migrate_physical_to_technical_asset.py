"""Tests for PhysicalObject → TechnicalAsset migration script."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

from migrate_physical_to_technical_asset import migrate_document  # noqa: E402


MINI = {
    "element_id": "dams:pkg/mini",
    "name": "mini",
    "description": "mini",
    "lifecycle_status": "draft",
    "api_version": "v1",
    "model_version": "0.1.0",
    "physical_objects": [
        {
            "element_id": "dams:physical/mini/T1",
            "name": "T1",
            "description": "table",
            "lifecycle_status": "draft",
            "system_ref": "eam:system/MDM",
            "object_kind": "table",
            "qualified_name": "SCHEMA.T1",
            "technology": "Oracle",
            "native_schema_ref": "oracle:SCHEMA.T1",
            "direction": "internal",
            "physical_fields": [
                {
                    "element_id": "dams:physical/mini/T1/ID",
                    "name": "ID",
                    "description": "id",
                    "lifecycle_status": "draft",
                    "physical_object_ref": "dams:physical/mini/T1",
                    "native_name": "ID",
                    "native_type": "NUMBER",
                    "required": True,
                }
            ],
        },
        {
            "element_id": "dams:physical/mini/API1",
            "name": "API1",
            "description": "api",
            "lifecycle_status": "draft",
            "system_ref": "eam:system/MDM",
            "object_kind": "api",
            "qualified_name": "/v1",
            "technology": "REST",
            "native_schema_ref": "openapi:/v1",
            "direction": "outbound",
        },
        {
            "element_id": "dams:physical/mini/EP1",
            "name": "EP1",
            "description": "endpoint",
            "lifecycle_status": "draft",
            "system_ref": "eam:system/MDM",
            "object_kind": "endpoint",
            "qualified_name": "/v1/clients",
            "technology": "REST",
            "native_schema_ref": "openapi:/v1/clients",
            "direction": "outbound",
        },
        {
            "element_id": "dams:physical/mini/MSG1",
            "name": "MSG1",
            "description": "message",
            "lifecycle_status": "draft",
            "system_ref": "eam:system/MDM",
            "object_kind": "message",
            "qualified_name": "ClientCreated",
            "technology": "Kafka",
            "native_schema_ref": "avro:ClientCreated",
            "direction": "outbound",
        },
    ],
}


def test_migrate_kinds_and_fields():
    data = copy.deepcopy(MINI)
    result = migrate_document(data)
    assert result["changed"] is True
    assert "physical_objects" not in data
    assert len(data["data_carriers"]) == 2  # table + message
    assert len(data["access_points"]) == 2  # api + endpoint
    carriers = {c["element_id"]: c for c in data["data_carriers"]}
    t1 = carriers["dams:physical/mini/T1"]
    assert t1["asset_kind"] == "relational_table"
    assert t1["asset_namespace"] == "oracle://MDM"
    assert t1["structure_ref"] == "oracle:SCHEMA.T1"
    assert t1["physical_fields"][0]["carrier_ref"] == "dams:physical/mini/T1"
    assert "physical_object_ref" not in t1["physical_fields"][0]
    msg = carriers["dams:physical/mini/MSG1"]
    assert msg["asset_kind"] == "message_type"
    assert "transitional" in (msg.get("tags") or [])
    ops = [a for a in data["access_points"] if a["asset_kind"] == "operation"]
    assert len(ops) == 1
    assert ops[0]["interface_ref"] == "dams:physical/mini/API1"


def test_idempotent():
    data = copy.deepcopy(MINI)
    migrate_document(data)
    snapshot = copy.deepcopy(data)
    result2 = migrate_document(data)
    assert result2["changed"] is False
    assert data == snapshot


def test_ambiguous_endpoint_errors():
    data = copy.deepcopy(MINI)
    # Second api with overlapping qn
    data["physical_objects"].append(
        {
            "element_id": "dams:physical/mini/API2",
            "name": "API2",
            "description": "api2",
            "lifecycle_status": "draft",
            "system_ref": "eam:system/MDM",
            "object_kind": "api",
            "qualified_name": "/v1",
            "technology": "REST",
            "native_schema_ref": "openapi:/v1b",
            "direction": "outbound",
        }
    )
    result = migrate_document(data)
    assert any("ambiguous" in e for e in result["errors"])
