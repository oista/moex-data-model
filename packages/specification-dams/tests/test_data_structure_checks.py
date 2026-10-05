"""Minimal checks for DataStructure / SchemaNode semantic rules."""

from __future__ import annotations

from moex_dams.rules.data_structure import check_data_structures


def _pkg(**overrides) -> dict:
    base = {
        "element_id": "dams:model/struct/1",
        "name": "struct_pkg",
        "data_structures": [
            {
                "element_id": "dams:structure/struct/T",
                "name": "T",
                "schema_format": "relational",
                "structure_version": "1.0.0",
                "root_local_key": "root",
                "nodes": [
                    {
                        "local_key": "root",
                        "node_kind": "object",
                        "children": ["col"],
                    },
                    {
                        "local_key": "col",
                        "node_kind": "scalar",
                        "native_name": "col",
                        "native_type": "text",
                        "required": True,
                    },
                ],
            }
        ],
    }
    base.update(overrides)
    return base


def test_happy_path_no_errors() -> None:
    assert check_data_structures(_pkg()) == ()


def test_duplicate_local_key() -> None:
    data = _pkg()
    data["data_structures"][0]["nodes"].append(
        {
            "local_key": "col",
            "node_kind": "scalar",
            "native_name": "col2",
            "native_type": "text",
            "required": False,
        }
    )
    codes = {d.diagnostic_code for d in check_data_structures(data)}
    assert "DAMS-REQ-PDM-013.c1" in codes


def test_missing_root_local_key() -> None:
    data = _pkg()
    data["data_structures"][0]["root_local_key"] = "missing"
    codes = {d.diagnostic_code for d in check_data_structures(data)}
    assert "DAMS-REQ-PDM-015.c1" in codes
