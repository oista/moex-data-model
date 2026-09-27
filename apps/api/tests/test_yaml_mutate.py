"""Unit tests for YAML controlled mutations."""

from __future__ import annotations

import pytest

from moex_model_api.yaml_mutate import (
    MutationConflict,
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
