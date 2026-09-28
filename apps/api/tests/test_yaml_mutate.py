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
element_id: dams:model/trading/1.0.0
name: trading_solution_model
domain_contexts:
  - element_id: dams:context/trading
logical_entities:
  - element_id: dams:logical/trading/Client
    name: TradingClient
    attributes:
      - element_id: dams:logical/trading/Client/clientId
        name: clientId
        logical_type: identifier
"""


def test_add_entity_and_attribute() -> None:
    out = apply_mutation(
        SAMPLE,
        {
            "op": "add_logical_entity",
            "entity": {
                "element_id": "dams:logical/trading/Order",
                "name": "Order",
                "title": "Order",
            },
        },
    )
    data = load_yaml(out)
    ids = [e["element_id"] for e in data["logical_entities"]]
    assert "dams:logical/trading/Order" in ids

    out2 = apply_mutation(
        out,
        {
            "op": "add_logical_attribute",
            "owner_element_id": "dams:logical/trading/Client",
            "attribute": {
                "element_id": "dams:logical/trading/Client/nick",
                "name": "nick",
                "logical_type": "string",
            },
        },
    )
    assert "dams:logical/trading/Client/nick" in out2


def test_duplicate_entity_conflict() -> None:
    with pytest.raises(MutationConflict):
        apply_mutation(
            SAMPLE,
            {
                "op": "add_logical_entity",
                "entity": {
                    "element_id": "dams:logical/trading/Client",
                    "name": "Dup",
                },
            },
        )


def test_update_logical_entity() -> None:
    out = apply_mutation(
        SAMPLE,
        {
            "op": "update_logical_entity",
            "element_id": "dams:logical/trading/Client",
            "patch": {"title": "Updated Client", "description": "Patched"},
        },
    )
    data = load_yaml(out)
    client = next(
        e
        for e in data["logical_entities"]
        if e["element_id"] == "dams:logical/trading/Client"
    )
    assert client["title"] == "Updated Client"
    assert client["description"] == "Patched"


def test_delete_logical_entity_cascades_attributes() -> None:
    out = apply_mutation(
        SAMPLE,
        {
            "op": "delete_logical_entity",
            "element_id": "dams:logical/trading/Client",
        },
    )
    data = load_yaml(out)
    ids = [e["element_id"] for e in data.get("logical_entities") or []]
    assert "dams:logical/trading/Client" not in ids
    assert "dams:logical/trading/Client/clientId" not in out


def test_update_and_delete_logical_attribute() -> None:
    out = apply_mutation(
        SAMPLE,
        {
            "op": "update_logical_attribute",
            "element_id": "dams:logical/trading/Client/clientId",
            "patch": {"required": True, "title": "Client ID"},
        },
    )
    data = load_yaml(out)
    client = next(
        e
        for e in data["logical_entities"]
        if e["element_id"] == "dams:logical/trading/Client"
    )
    attr = client["attributes"][0]
    assert attr["required"] is True
    assert attr["title"] == "Client ID"

    out2 = apply_mutation(
        out,
        {
            "op": "delete_logical_attribute",
            "element_id": "dams:logical/trading/Client/clientId",
        },
    )
    data2 = load_yaml(out2)
    client2 = next(
        e
        for e in data2["logical_entities"]
        if e["element_id"] == "dams:logical/trading/Client"
    )
    assert client2.get("attributes") in (None, [], [])
    assert not list(client2.get("attributes") or [])


def test_update_missing_and_empty_patch() -> None:
    with pytest.raises(MutationError, match="not found"):
        apply_mutation(
            SAMPLE,
            {
                "op": "update_logical_entity",
                "element_id": "dams:logical/trading/Missing",
                "patch": {"name": "X"},
            },
        )
    with pytest.raises(MutationError, match="patch"):
        apply_mutation(
            SAMPLE,
            {
                "op": "update_logical_entity",
                "element_id": "dams:logical/trading/Client",
                "patch": {},
            },
        )
    with pytest.raises(MutationError, match="element_id cannot"):
        apply_mutation(
            SAMPLE,
            {
                "op": "update_logical_attribute",
                "element_id": "dams:logical/trading/Client/clientId",
                "patch": {"element_id": "other"},
            },
        )


SAMPLE_WITH_MAP = (
    SAMPLE
    + """\
mappings:
  - element_id: dams:mapping/trading/client-id
    name: map_client_id
    description: existing
    lifecycle_status: active
    source_refs:
      - dams:logical/trading/Client/clientId
    target_refs:
      - dams:physical/trading/client-topic/client_id
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
                "element_id": "dams:rel/trading/Client-Order",
                "name": "client_orders",
                "description": "Client places orders",
                "lifecycle_status": "draft",
                "source_entity_ref": "dams:logical/trading/Client",
                "target_entity_ref": "dams:logical/trading/Order",
            },
        },
    )
    data = load_yaml(out)
    rels = data["relationships"]
    assert len(rels) == 1
    assert rels[0]["element_id"] == "dams:rel/trading/Client-Order"
    assert rels[0]["source_entity_ref"] == "dams:logical/trading/Client"

    out2 = apply_mutation(
        out,
        {
            "op": "update_relationship",
            "element_id": "dams:rel/trading/Client-Order",
            "patch": {
                "title": "Client Orders",
                "source_role": "client",
                "target_min_cardinality": 0,
            },
        },
    )
    data2 = load_yaml(out2)
    rel = data2["relationships"][0]
    assert rel["title"] == "Client Orders"
    assert rel["source_role"] == "client"
    assert rel["target_min_cardinality"] == 0

    out3 = apply_mutation(
        out2,
        {
            "op": "delete_relationship",
            "element_id": "dams:rel/trading/Client-Order",
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
                "element_id": "dams:mapping/trading/new",
                "name": "map_new",
                "description": "New mapping",
                "lifecycle_status": "draft",
                "source_refs": ["dams:logical/trading/Client/clientId"],
                "target_refs": ["dams:physical/trading/x/id"],
                "mapping_type": "field_mapping",
                "mapping_cardinality": "one_to_one",
            },
        },
    )
    data = load_yaml(out)
    maps = data["mappings"]
    assert any(m["element_id"] == "dams:mapping/trading/new" for m in maps)

    out2 = apply_mutation(
        SAMPLE_WITH_MAP,
        {
            "op": "update_mapping",
            "element_id": "dams:mapping/trading/client-id",
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
        if x["element_id"] == "dams:mapping/trading/client-id"
    )
    assert m["title"] == "Client ID map"
    assert m["transformation_expression"] == "identity"

    out3 = apply_mutation(
        out2,
        {
            "op": "delete_mapping",
            "element_id": "dams:mapping/trading/client-id",
        },
    )
    data3 = load_yaml(out3)
    ids = [x["element_id"] for x in data3.get("mappings") or []]
    assert "dams:mapping/trading/client-id" not in ids


def test_duplicate_relationship_and_mapping_conflict() -> None:
    with pytest.raises(MutationConflict):
        apply_mutation(
            SAMPLE_WITH_MAP,
            {
                "op": "add_mapping",
                "mapping": {
                    "element_id": "dams:mapping/trading/client-id",
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
                "element_id": "dams:rel/trading/X",
                "name": "x",
                "description": "d",
                "source_entity_ref": "dams:logical/trading/Client",
                "target_entity_ref": "dams:logical/trading/Client",
            },
        },
    )
    with pytest.raises(MutationConflict):
        apply_mutation(
            seeded,
            {
                "op": "add_relationship",
                "relationship": {
                    "element_id": "dams:rel/trading/X",
                    "name": "x2",
                    "description": "d",
                    "source_entity_ref": "a",
                    "target_entity_ref": "b",
                },
            },
        )
