"""Unit smoke for audit Wave C package invariants (INV-042..053)."""

from __future__ import annotations

from moex_dams.rules.package_invariants import (
    check_alignment_dual_path_consistency,
    check_mapping_cardinality_consistency,
    check_package_element_id_uniqueness,
    check_selection_attribute_closure,
    check_solution_scope_refs,
)


def test_solution_scope_requires_refs() -> None:
    diags = check_solution_scope_refs({"implementation_scope": "solution"})
    assert {d.diagnostic_code for d in diags} == {"DAMS-INV-042"}
    assert all(
        any(det.detail_key == "invariant_id" and det.detail_value == "INV-042" for det in d.diagnostic_details)
        for d in diags
    )


def test_duplicate_element_id() -> None:
    data = {
        "conceptual_entities": [
            {"element_id": "dams:concept/X"},
            {"element_id": "dams:concept/X"},
        ]
    }
    diags = check_package_element_id_uniqueness(data)
    assert any(d.diagnostic_code == "DAMS-INV-050" for d in diags)


def test_selection_closure() -> None:
    data = {
        "logical_entities": [
            {
                "element_id": "dams:logical/E",
                "attributes": [{"element_id": "dams:logical/E/a"}],
            }
        ],
        "selections": [
            {
                "selected_entities": [
                    {
                        "logical_entity_ref": "dams:logical/E",
                        "selected_attributes": [
                            {
                                "element_id": "sel",
                                "logical_attribute_ref": "dams:logical/OTHER/x",
                            }
                        ],
                    }
                ]
            }
        ],
    }
    diags = check_selection_attribute_closure(data)
    assert any(d.diagnostic_code == "DAMS-INV-048" for d in diags)


def test_mapping_cardinality() -> None:
    data = {
        "realizes_mappings": [
            {
                "element_id": "dams:map/1",
                "mapping_type": "realizes",
                "mapping_cardinality": "one_to_one",
                "source_refs": ["a", "b"],
                "target_refs": ["c"],
            }
        ]
    }
    diags = check_mapping_cardinality_consistency(data)
    assert any(d.diagnostic_code == "DAMS-INV-051" for d in diags)


def test_alignment_dual_path_confidence_conflict() -> None:
    data = {
        "conceptual_entities": [
            {
                "element_id": "dams:concept/C",
                "external_class_refs": [
                    {
                        "target_ref": "https://example.org/T",
                        "confidence": 0.9,
                    }
                ],
            }
        ],
        "aligns_with_mappings": [
            {
                "element_id": "dams:map/a",
                "mapping_type": "aligns_with",
                "source_refs": ["dams:concept/C"],
                "target_refs": ["https://example.org/T"],
                "confidence": 0.1,
            }
        ],
    }
    diags = check_alignment_dual_path_consistency(data)
    assert any(d.diagnostic_code == "DAMS-INV-057" for d in diags)
