"""Tests for PhysicalField → SchemaNode migration."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

from migrate_physical_field_to_schema_node import (  # noqa: E402
    _collect_local_keys,
    build_nodes_from_fields,
    migrate_document,
)


def _pkg_with_carrier(fields: list[dict]) -> dict:
    carrier = {
        "element_id": "dams:physical/mini/T1",
        "name": "T1",
        "description": "table",
        "lifecycle_status": "active",
        "system_ref": "eam:system/MDM",
        "asset_namespace": "oracle://MDM",
        "qualified_name": "SCHEMA.T1",
        "asset_kind": "relational_table",
        "structure_ref": "oracle:SCHEMA.T1",
        "physical_fields": fields,
    }
    mappings = []
    for f in fields:
        mappings.append(
            {
                "element_id": f"dams:mapping/mini/{f['name']}",
                "name": f"map_{f['name']}",
                "description": "field map",
                "lifecycle_status": "active",
                "mapping_type": "field_mapping",
                "mapping_cardinality": "one_to_one",
                "source_refs": [f["element_id"]],
                "target_refs": [f"dams:logical/mini/Attr_{f['name']}"],
            }
        )
    return {
        "element_id": "dams:pkg/mini",
        "name": "mini",
        "description": "mini",
        "lifecycle_status": "draft",
        "api_version": "v1",
        "model_version": "0.1.0",
        "data_carriers": [carrier],
        "mappings": mappings,
    }


def test_flat_table_scalar_count_and_mapping():
    fields = [
        {
            "element_id": "dams:physical/mini/T1/ID",
            "name": "ID",
            "description": "id",
            "lifecycle_status": "active",
            "carrier_ref": "dams:physical/mini/T1",
            "native_name": "ID",
            "native_type": "NUMBER",
            "required": True,
            "ordinal_position": 1,
        },
        {
            "element_id": "dams:physical/mini/T1/NAME",
            "name": "NAME",
            "description": "name",
            "lifecycle_status": "active",
            "carrier_ref": "dams:physical/mini/T1",
            "native_name": "NAME",
            "native_type": "VARCHAR2",
            "required": False,
            "ordinal_position": 2,
        },
    ]
    data = _pkg_with_carrier(fields)
    result = migrate_document(data)
    assert result["before_fields"] == 2
    assert result["scalar_nodes"] == 2
    assert not data["data_carriers"][0].get("physical_fields")
    assert str(data["data_carriers"][0]["structure_ref"]).startswith("dams:structure/")
    structs = data["data_structures"]
    assert len(structs) == 1
    scalars = [n for n in structs[0]["nodes"] if n["node_kind"] == "scalar"]
    assert len(scalars) == 2
    assert len(data["mappings"]) == 2
    for m in data["mappings"]:
        assert "#" in m["source_refs"][0]
        assert m["source_refs"][0].startswith("dams:structure/")


def test_nested_schema_path():
    fields = [
        {
            "element_id": "dams:physical/mini/T1/X",
            "name": "X",
            "description": "nested",
            "lifecycle_status": "active",
            "carrier_ref": "dams:physical/mini/T1",
            "native_name": "c",
            "native_type": "string",
            "required": True,
            "schema_path": "a.b.c",
        }
    ]
    data = _pkg_with_carrier(fields)
    result = migrate_document(data)
    assert result["scalar_nodes"] == 1
    nodes = {n["local_key"]: n for n in data["data_structures"][0]["nodes"]}
    assert "root" in nodes
    assert "a" in nodes
    assert "a.b" in nodes
    assert "a.b.c" in nodes
    assert nodes["a"]["node_kind"] == "object"
    assert "a.b" in nodes["a"]["children"]
    assert nodes["a.b.c"]["node_kind"] == "scalar"


def test_idempotent_keys():
    fields = [
        {
            "element_id": "dams:physical/mini/T1/ID",
            "name": "ID",
            "description": "id",
            "lifecycle_status": "active",
            "carrier_ref": "dams:physical/mini/T1",
            "native_name": "ID",
            "native_type": "NUMBER",
            "required": True,
        }
    ]
    data = _pkg_with_carrier(fields)
    migrate_document(data)
    keys1 = _collect_local_keys(data)
    result2 = migrate_document(copy.deepcopy(data))
    keys2 = result2["after_keys"]
    assert keys1 == keys2
    assert result2["before_fields"] == 0
    assert result2["changed"] is False


def test_message_type_creates_message():
    data = {
        "element_id": "dams:pkg/mini",
        "name": "mini",
        "description": "mini",
        "lifecycle_status": "draft",
        "api_version": "v1",
        "model_version": "0.1.0",
        "data_carriers": [
            {
                "element_id": "dams:physical/mini/MSG",
                "name": "MSG",
                "description": "msg",
                "lifecycle_status": "active",
                "system_ref": "eam:system/MDM",
                "asset_namespace": "kafka://MDM",
                "qualified_name": "evt",
                "asset_kind": "message_type",
                "physical_fields": [
                    {
                        "element_id": "dams:physical/mini/MSG/id",
                        "name": "id",
                        "description": "id",
                        "lifecycle_status": "active",
                        "carrier_ref": "dams:physical/mini/MSG",
                        "native_name": "id",
                        "native_type": "string",
                        "required": True,
                    }
                ],
            }
        ],
        "access_points": [
            {
                "element_id": "dams:physical/mini/CH",
                "name": "CH",
                "description": "channel",
                "lifecycle_status": "active",
                "system_ref": "eam:system/MDM",
                "asset_namespace": "kafka://MDM",
                "qualified_name": "topic",
                "asset_kind": "channel",
                "serves_refs": ["dams:physical/mini/MSG"],
            }
        ],
    }
    result = migrate_document(data)
    assert not result.get("errors"), result.get("errors")
    assert data.get("messages")
    assert data["messages"][0]["payload_structure_ref"].startswith("dams:structure/")
    assert not any(
        c.get("asset_kind") == "message_type"
        for c in (data.get("data_carriers") or [])
        if isinstance(c, dict)
    )
    assert data["access_points"][0].get("message_refs")


def test_avro_like_union_hand_built():
    """Avro-like union is representable as flat nodes (hand-built after migrate)."""
    fields = [
        {
            "element_id": "dams:physical/mini/T1/ID",
            "name": "ID",
            "description": "id",
            "lifecycle_status": "active",
            "carrier_ref": "dams:physical/mini/T1",
            "native_name": "ID",
            "native_type": "NUMBER",
            "required": True,
        }
    ]
    data = _pkg_with_carrier(fields)
    migrate_document(data)
    data["data_structures"].append(
        {
            "element_id": "dams:structure/mini/AvroEvent",
            "name": "AvroEvent",
            "description": "hand-built avro-like union",
            "lifecycle_status": "draft",
            "schema_format": "avro",
            "structure_version": "1.0.0",
            "root_local_key": "root",
            "nodes": [
                {
                    "local_key": "root",
                    "node_kind": "object",
                    "children": ["payload"],
                },
                {
                    "local_key": "payload",
                    "node_kind": "union",
                    "children": ["payload.string", "payload.null"],
                },
                {
                    "local_key": "payload.string",
                    "node_kind": "scalar",
                    "native_type": "string",
                },
                {
                    "local_key": "payload.null",
                    "node_kind": "scalar",
                    "native_type": "null",
                },
            ],
        }
    )
    union = next(
        s
        for s in data["data_structures"]
        if s["element_id"] == "dams:structure/mini/AvroEvent"
    )
    nodes = {n["local_key"]: n for n in union["nodes"]}
    assert nodes["payload"]["node_kind"] == "union"
    assert set(nodes["payload"]["children"]) == {
        "payload.string",
        "payload.null",
    }
    snap = copy.deepcopy(union)
    result2 = migrate_document(data)
    assert result2["changed"] is False
    assert union == snap


def test_field_mapping_count_preserved():
    fields = [
        {
            "element_id": "dams:physical/mini/T1/ID",
            "name": "ID",
            "description": "id",
            "lifecycle_status": "active",
            "carrier_ref": "dams:physical/mini/T1",
            "native_name": "ID",
            "native_type": "NUMBER",
            "required": True,
        },
        {
            "element_id": "dams:physical/mini/T1/NAME",
            "name": "NAME",
            "description": "name",
            "lifecycle_status": "active",
            "carrier_ref": "dams:physical/mini/T1",
            "native_name": "NAME",
            "native_type": "VARCHAR2",
            "required": False,
        },
    ]
    data = _pkg_with_carrier(fields)
    before = sum(
        1 for m in data["mappings"] if m["mapping_type"] == "field_mapping"
    )
    result = migrate_document(data)
    after = sum(
        1 for m in data["mappings"] if m["mapping_type"] == "field_mapping"
    )
    assert after == before == result["after_mappings"]


def test_local_key_collision_suffix():
    nodes, fmap, collisions, errors = build_nodes_from_fields(
        [
            {
                "element_id": "dams:physical/x/F1",
                "native_name": "ID",
                "native_type": "int",
                "required": True,
            },
            {
                "element_id": "dams:physical/x/F2",
                "native_name": "id",
                "native_type": "int",
                "required": False,
            },
        ],
        structure_id="dams:structure/x/T",
        carrier_id="dams:physical/x/T",
    )
    assert errors == []
    keys = {n["local_key"] for n in nodes if n["node_kind"] == "scalar"}
    assert keys == {"id", "id-2"}
    assert collisions
    assert fmap["dams:physical/x/F1"] == "dams:structure/x/T#id"
    assert fmap["dams:physical/x/F2"] == "dams:structure/x/T#id-2"


def test_physical_field_refs_rewritten():
    fields = [
        {
            "element_id": "dams:physical/mini/T1/ID",
            "name": "ID",
            "description": "id",
            "lifecycle_status": "active",
            "carrier_ref": "dams:physical/mini/T1",
            "native_name": "ID",
            "native_type": "NUMBER",
            "required": True,
        }
    ]
    data = _pkg_with_carrier(fields)
    data["data_model_bindings"] = [
        {
            "element_id": "dams:binding/mini",
            "model_revision": "r1",
            "integrity_digest": "sha256:dead",
            "selections": [
                {
                    "selected_attributes": [
                        {
                            "logical_attribute_ref": "dams:logical/mini/Attr_ID",
                            "physical_field_refs": [
                                "dams:physical/mini/T1/ID",
                            ],
                        }
                    ]
                }
            ],
        }
    ]
    result = migrate_document(data, demo=True)
    assert result["changed"] is True
    attr = data["data_model_bindings"][0]["selections"][0]["selected_attributes"][0]
    assert "physical_field_refs" not in attr
    assert attr["schema_node_refs"] == ["dams:structure/mini/T1#id"]


def test_http_structure_ref_to_source_artifact():
    fields = [
        {
            "element_id": "dams:physical/mini/T1/ID",
            "name": "ID",
            "description": "id",
            "lifecycle_status": "active",
            "carrier_ref": "dams:physical/mini/T1",
            "native_name": "ID",
            "native_type": "NUMBER",
            "required": True,
        }
    ]
    data = _pkg_with_carrier(fields)
    data["data_carriers"][0]["structure_ref"] = "https://example.com/schema.json"
    data["mappings"] = []
    migrate_document(data)
    st = data["data_structures"][0]
    assert st["source_artifact_ref"] == "https://example.com/schema.json"
    assert data["data_carriers"][0]["structure_ref"] == "dams:structure/mini/T1"


def test_message_type_ambiguous_channel_errors():
    data = {
        "data_carriers": [
            {
                "element_id": "dams:physical/mini/MSG",
                "name": "MSG",
                "lifecycle_status": "active",
                "system_ref": "eam:system/MDM",
                "asset_namespace": "kafka://MDM",
                "qualified_name": "evt",
                "asset_kind": "message_type",
                "physical_fields": [
                    {
                        "element_id": "dams:physical/mini/MSG/id",
                        "name": "id",
                        "lifecycle_status": "active",
                        "native_name": "id",
                        "native_type": "string",
                        "required": True,
                    }
                ],
            }
        ],
        "access_points": [
            {
                "element_id": "dams:physical/mini/CH1",
                "name": "CH1",
                "lifecycle_status": "active",
                "system_ref": "eam:system/MDM",
                "asset_namespace": "kafka://MDM",
                "qualified_name": "a",
                "asset_kind": "channel",
                "serves_refs": ["dams:physical/mini/MSG"],
            },
            {
                "element_id": "dams:physical/mini/CH2",
                "name": "CH2",
                "lifecycle_status": "active",
                "system_ref": "eam:system/MDM",
                "asset_namespace": "kafka://MDM",
                "qualified_name": "b",
                "asset_kind": "channel",
                "serves_refs": ["dams:physical/mini/MSG"],
            },
        ],
    }
    result = migrate_document(data)
    assert any("ambiguous" in e for e in result["errors"])
