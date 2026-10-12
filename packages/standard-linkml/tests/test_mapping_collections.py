"""Typed Mapping collection keys stay aligned with moex_dams (ADR-046)."""

from __future__ import annotations

import pytest

from moex_standard_linkml.mapping_collections import (
    MAPPING_TYPE_TO_COLLECTION,
    TYPED_MAPPING_KEYS,
    iter_package_mappings,
)


def test_iter_package_mappings_order_and_skip_non_dict() -> None:
    pkg = {
        "field_mappings": [{"element_id": "f1"}, "skip"],
        "realizes_mappings": [{"element_id": "r1"}],
        "mappings": [{"element_id": "legacy"}],  # ignored since ADR-046 PR-5
    }
    assert [m["element_id"] for m in iter_package_mappings(pkg)] == ["r1", "f1"]


def test_type_to_collection_covers_all_keys() -> None:
    assert set(MAPPING_TYPE_TO_COLLECTION.values()) == set(TYPED_MAPPING_KEYS)


def test_keys_match_moex_dams() -> None:
    dams = pytest.importorskip("moex_dams.mappings")
    assert TYPED_MAPPING_KEYS == dams.TYPED_MAPPING_KEYS
