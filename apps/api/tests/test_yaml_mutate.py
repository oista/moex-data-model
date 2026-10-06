"""Unit tests for YAML controlled mutations."""

from __future__ import annotations

import pytest

from moex_model_api.yaml_mutate import (
    MutationConflict,
    MutationError,
    apply_mutation,
    load_yaml,
)


SAMPLE = """\
element_id: dams:model/mdm/0.1.0
name: mdm_solution_model
domain_contexts:
  - element_id: dams:context/mdm
logical_entities:
  - element_id: dams:logical/mdm/Client
    name: ENTERPRISE
    attributes:
      - element_id: dams:logical/mdm/Client/ENTERPRISE_ID
        name: ENTERPRISE_ID
        data_type_ref: dams:datatype/identifier
"""


def test_add_entity_and_attribute() -> None:
    out = apply_mutation(
        SAMPLE,
        {
            "op": "add_logical_entity",
            "entity": {
                "element_id": "dams:logical/mdm/OrderBook",
                "name": "OrderBook",
                "title": "OrderBook",
            },
        },
    )
    data = load_yaml(out)
    ids = [e["element_id"] for e in data["logical_entities"]]
    assert "dams:logical/mdm/OrderBook" in ids

    out2 = apply_mutation(
        out,
        {
            "op": "add_logical_attribute",
            "owner_element_id": "dams:logical/mdm/Client",
            "attribute": {
                "element_id": "dams:logical/mdm/Client/nick",
                "name": "nick",
                "data_type_ref": "dams:datatype/string",
            },
        },
    )
    assert "dams:logical/mdm/Client/nick" in out2


def test_duplicate_entity_conflict() -> None:
    with pytest.raises(MutationConflict):
        apply_mutation(
            SAMPLE,
            {
                "op": "add_logical_entity",
                "entity": {
                    "element_id": "dams:logical/mdm/Client",
                    "name": "Dup",
                },
            },
        )


def test_update_logical_entity() -> None:
    out = apply_mutation(
        SAMPLE,
        {
            "op": "update_logical_entity",
            "element_id": "dams:logical/mdm/Client",
            "patch": {"title": "Updated Client", "description": "Patched"},
        },
    )
    data = load_yaml(out)
    client = next(
        e
        for e in data["logical_entities"]
        if e["element_id"] == "dams:logical/mdm/Client"
    )
    assert client["title"] == "Updated Client"
    assert client["description"] == "Patched"


def test_delete_logical_entity_cascades_attributes() -> None:
    out = apply_mutation(
        SAMPLE,
        {
            "op": "delete_logical_entity",
            "element_id": "dams:logical/mdm/Client",
        },
    )
    data = load_yaml(out)
    ids = [e["element_id"] for e in data.get("logical_entities") or []]
    assert "dams:logical/mdm/Client" not in ids
    assert "dams:logical/mdm/Client/ENTERPRISE_ID" not in out


def test_update_and_delete_logical_attribute() -> None:
    out = apply_mutation(
        SAMPLE,
        {
            "op": "update_logical_attribute",
            "element_id": "dams:logical/mdm/Client/ENTERPRISE_ID",
            "patch": {"required": True, "title": "Client ID"},
        },
    )
    data = load_yaml(out)
    client = next(
        e
        for e in data["logical_entities"]
        if e["element_id"] == "dams:logical/mdm/Client"
    )
    attr = client["attributes"][0]
    assert attr["required"] is True
    assert attr["title"] == "Client ID"

    out2 = apply_mutation(
        out,
        {
            "op": "delete_logical_attribute",
            "element_id": "dams:logical/mdm/Client/ENTERPRISE_ID",
        },
    )
    data2 = load_yaml(out2)
    client2 = next(
        e
        for e in data2["logical_entities"]
        if e["element_id"] == "dams:logical/mdm/Client"
    )
    assert client2.get("attributes") in (None, [], [])
    assert not list(client2.get("attributes") or [])


def test_update_missing_and_empty_patch() -> None:
    with pytest.raises(MutationError, match="not found"):
        apply_mutation(
            SAMPLE,
            {
                "op": "update_logical_entity",
                "element_id": "dams:logical/mdm/Missing",
                "patch": {"name": "X"},
            },
        )
    with pytest.raises(MutationError, match="patch"):
        apply_mutation(
            SAMPLE,
            {
                "op": "update_logical_entity",
                "element_id": "dams:logical/mdm/Client",
                "patch": {},
            },
        )
    with pytest.raises(MutationError, match="element_id cannot"):
        apply_mutation(
            SAMPLE,
            {
                "op": "update_logical_attribute",
                "element_id": "dams:logical/mdm/Client/ENTERPRISE_ID",
                "patch": {"element_id": "other"},
            },
        )


SAMPLE_WITH_MAP = (
    SAMPLE
    + """\
mappings:
  - element_id: dams:mapping/mdm/wb-map-id
    name: map_client_id
    description: existing
    lifecycle_status: active
    source_refs:
      - dams:logical/mdm/Client/ENTERPRISE_ID
    target_refs:
      - dams:physical/mdm/client-topic/client_id
    mapping_type: field_mapping
    mapping_cardinality: one_to_one
"""
)


def test_add_update_delete_relationship() -> None:
    out = apply_mutation(
        SAMPLE,
        {
            "op": "add_relationship",
            "relationship": {
                "element_id": "dams:rel/mdm/ENTERPRISE-OrderBook",
                "name": "client_orders",
                "description": "Client places orders",
                "lifecycle_status": "draft",
                "source_entity_ref": "dams:logical/mdm/Client",
                "target_entity_ref": "dams:logical/mdm/OrderBook",
            },
        },
    )
    data = load_yaml(out)
    rels = data["relationships"]
    assert len(rels) == 1
    assert rels[0]["element_id"] == "dams:rel/mdm/ENTERPRISE-OrderBook"
    assert rels[0]["source_entity_ref"] == "dams:logical/mdm/Client"

    out2 = apply_mutation(
        out,
        {
            "op": "update_relationship",
            "element_id": "dams:rel/mdm/ENTERPRISE-OrderBook",
            "patch": {
                "title": "Client OrderBooks",
                "source_role": "client",
                "target_min_cardinality": 0,
            },
        },
    )
    data2 = load_yaml(out2)
    rel = data2["relationships"][0]
    assert rel["title"] == "Client OrderBooks"
    assert rel["source_role"] == "client"
    assert rel["target_min_cardinality"] == 0

    out3 = apply_mutation(
        out2,
        {
            "op": "delete_relationship",
            "element_id": "dams:rel/mdm/ENTERPRISE-OrderBook",
        },
    )
    data3 = load_yaml(out3)
    assert list(data3.get("relationships") or []) == []


def test_add_update_delete_mapping() -> None:
    out = apply_mutation(
        SAMPLE,
        {
            "op": "add_mapping",
            "mapping": {
                "element_id": "dams:mapping/mdm/new",
                "name": "map_new",
                "description": "New mapping",
                "lifecycle_status": "draft",
                "source_refs": ["dams:logical/mdm/Client/ENTERPRISE_ID"],
                "target_refs": ["dams:physical/mdm/x/id"],
                "mapping_type": "field_mapping",
                "mapping_cardinality": "one_to_one",
            },
        },
    )
    data = load_yaml(out)
    maps = data["mappings"]
    assert any(m["element_id"] == "dams:mapping/mdm/new" for m in maps)

    out2 = apply_mutation(
        SAMPLE_WITH_MAP,
        {
            "op": "update_mapping",
            "element_id": "dams:mapping/mdm/wb-map-id",
            "patch": {
                "title": "Client ID map",
                "transformation_expression": "identity",
            },
        },
    )
    data2 = load_yaml(out2)
    m = next(
        x
        for x in data2["mappings"]
        if x["element_id"] == "dams:mapping/mdm/wb-map-id"
    )
    assert m["title"] == "Client ID map"
    assert m["transformation_expression"] == "identity"

    out3 = apply_mutation(
        out2,
        {
            "op": "delete_mapping",
            "element_id": "dams:mapping/mdm/wb-map-id",
        },
    )
    data3 = load_yaml(out3)
    ids = [x["element_id"] for x in data3.get("mappings") or []]
    assert "dams:mapping/mdm/wb-map-id" not in ids


def test_duplicate_relationship_and_mapping_conflict() -> None:
    with pytest.raises(MutationConflict):
        apply_mutation(
            SAMPLE_WITH_MAP,
            {
                "op": "add_mapping",
                "mapping": {
                    "element_id": "dams:mapping/mdm/wb-map-id",
                    "name": "dup",
                    "description": "d",
                    "source_refs": ["a"],
                    "target_refs": ["b"],
                    "mapping_type": "field_mapping",
                    "mapping_cardinality": "one_to_one",
                },
            },
        )
    seeded = apply_mutation(
        SAMPLE,
        {
            "op": "add_relationship",
            "relationship": {
                "element_id": "dams:rel/mdm/X",
                "name": "x",
                "description": "d",
                "source_entity_ref": "dams:logical/mdm/Client",
                "target_entity_ref": "dams:logical/mdm/Client",
            },
        },
    )
    with pytest.raises(MutationConflict):
        apply_mutation(
            seeded,
            {
                "op": "add_relationship",
                "relationship": {
                    "element_id": "dams:rel/mdm/X",
                    "name": "x2",
                    "description": "d",
                    "source_entity_ref": "a",
                    "target_entity_ref": "b",
                },
            },
        )

def test_add_update_delete_physical_object_and_field() -> None:
    out = apply_mutation(
        SAMPLE,
        {
            "op": "add_physical_object",
            "physical_object": {
                "element_id": "dams:physical/mdm/orders",
                "name": "orders_table",
                "title": "OrderBooks",
                "object_kind": "table",
            },
        },
    )
    data = load_yaml(out)
    objs = data["data_carriers"]
    assert any(o["element_id"] == "dams:physical/mdm/orders" for o in objs)

    out2 = apply_mutation(
        out,
        {
            "op": "add_schema_node",
            "owner_element_id": "dams:physical/mdm/orders",
            "schema_node": {
                "name": "id",
                "native_type": "uuid",
                "required": True,
            },
        },
    )
    data2 = load_yaml(out2)
    obj = next(
        o
        for o in data2["data_carriers"]
        if o["element_id"] == "dams:physical/mdm/orders"
    )
    assert obj["structure_ref"]
    st = next(
        s
        for s in data2["data_structures"]
        if s["element_id"] == obj["structure_ref"]
    )
    scalars = [n for n in st["nodes"] if n.get("node_kind") == "scalar"]
    assert scalars[0]["native_type"] == "uuid"
    assert obj["asset_kind"] == "relational_table"
    node_ref = f"{st['element_id']}#{scalars[0]['local_key']}"

    out3 = apply_mutation(
        out2,
        {
            "op": "update_physical_object",
            "element_id": "dams:physical/mdm/orders",
            "patch": {"title": "OrderBooks Table", "asset_kind": "relational_table"},
        },
    )
    data3 = load_yaml(out3)
    obj3 = next(
        o
        for o in data3["data_carriers"]
        if o["element_id"] == "dams:physical/mdm/orders"
    )
    assert obj3["title"] == "OrderBooks Table"

    out4 = apply_mutation(
        out3,
        {
            "op": "update_schema_node",
            "element_id": node_ref,
            "patch": {"native_type": "varchar"},
        },
    )
    data4 = load_yaml(out4)
    obj4 = next(
        o
        for o in data4["data_carriers"]
        if o["element_id"] == "dams:physical/mdm/orders"
    )
    st4 = next(
        s
        for s in data4["data_structures"]
        if s["element_id"] == obj4["structure_ref"]
    )
    scalars4 = [n for n in st4["nodes"] if n.get("node_kind") == "scalar"]
    assert scalars4[0]["native_type"] == "varchar"

    out5 = apply_mutation(
        out4,
        {
            "op": "delete_schema_node",
            "element_id": node_ref,
        },
    )
    data5 = load_yaml(out5)
    obj5 = next(
        o
        for o in data5["data_carriers"]
        if o["element_id"] == "dams:physical/mdm/orders"
    )
    st5 = next(
        s
        for s in data5["data_structures"]
        if s["element_id"] == obj5["structure_ref"]
    )
    assert [n for n in st5["nodes"] if n.get("node_kind") == "scalar"] == []

    out6 = apply_mutation(
        out5,
        {
            "op": "delete_physical_object",
            "element_id": "dams:physical/mdm/orders",
        },
    )
    data6 = load_yaml(out6)
    ids = [o["element_id"] for o in data6.get("data_carriers") or []]
    assert "dams:physical/mdm/orders" not in ids
