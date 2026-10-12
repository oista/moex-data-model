"""Unit tests for iter_mappings (ADR-046)."""

from __future__ import annotations

from moex_dams.mappings import TYPED_MAPPING_KEYS, iter_mappings


def test_empty() -> None:
    assert list(iter_mappings({})) == []
    assert list(iter_mappings({"field_mappings": []})) == []
    # Legacy polymorphic key is ignored after ADR-046 PR-5.
    assert list(iter_mappings({"mappings": [{"element_id": "legacy"}]})) == []


def test_typed_only() -> None:
    data = {
        "realizes_mappings": [{"element_id": "r1", "mapping_type": "realizes"}],
        "entity_physical_mappings": [
            {"element_id": "e1", "mapping_type": "entity_physical"}
        ],
        "field_mappings": [{"element_id": "f1", "mapping_type": "field_mapping"}],
        "aligns_with_mappings": [
            {"element_id": "a1", "mapping_type": "aligns_with"}
        ],
    }
    got = list(iter_mappings(data))
    assert [m["element_id"] for m in got] == ["r1", "e1", "f1", "a1"]
    assert TYPED_MAPPING_KEYS == (
        "realizes_mappings",
        "entity_physical_mappings",
        "field_mappings",
        "aligns_with_mappings",
    )


def test_dedupe_prefers_first_typed() -> None:
    first = {
        "element_id": "m1",
        "mapping_type": "realizes",
        "name": "first",
    }
    second = {
        "element_id": "m1",
        "mapping_type": "realizes",
        "name": "second",
    }
    data = {
        "realizes_mappings": [first],
        "field_mappings": [second, {"element_id": "m2", "name": "other"}],
    }
    got = list(iter_mappings(data))
    assert [m["element_id"] for m in got] == ["m1", "m2"]
    assert got[0]["name"] == "first"


def test_skip_non_dict() -> None:
    data = {
        "field_mappings": [
            "skip-me",
            None,
            {"element_id": "f1"},
        ],
    }
    got = list(iter_mappings(data))
    assert [m["element_id"] for m in got] == ["f1"]


def test_missing_element_id_always_yielded() -> None:
    data = {
        "field_mappings": [
            {"name": "anon-a"},
            {"name": "anon-b"},
        ]
    }
    got = list(iter_mappings(data))
    assert len(got) == 2
