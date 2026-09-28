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
