"""Unit smoke for audit Wave C package invariants (INV-042..053)."""

from __future__ import annotations

from moex_dams.rules.dams_levels import check_dams_model_level
from moex_dams.rules.package_invariants import (
    check_alignment_dual_path_consistency,
    check_mapping_cardinality_consistency,
    check_package_element_id_uniqueness,
    check_relationship_endpoint_kinds,
    check_selection_attribute_closure,
    check_solution_scope_refs,
)
from moex_modeling import DiagnosticSeverity
from moex_standard_linkml.domain.body import LinkMLImplementationBody


def _body(data: dict) -> LinkMLImplementationBody:
    return LinkMLImplementationBody(
        source_path="memory://test.yaml",
        target_class="ModelPackage",
        data=data,
    )


def test_solution_scope_requires_refs() -> None:
    diags = check_solution_scope_refs({"implementation_scope": "solution"})
    assert {d.diagnostic_code for d in diags} == {"DAMS-INV-042"}
    assert all(
        any(det.detail_key == "invariant_id" and det.detail_value == "INV-042" for det in d.diagnostic_details)
        for d in diags
    )


def test_dams_levels_defers_solution_refs_to_inv042() -> None:
    """R2-8: LEVEL-004/005 retired; INV-042 owns solution_ref checks."""
    data = {
        "element_id": "dams:model/sol",
        "name": "sol",
        "description": "sol",
        "lifecycle_status": "draft",
        "api_version": "dams.moex/v0.1",
        "model_version": "0.1.0",
        "implementation_scope": "solution",
        "logical_entities": [
            {
                "element_id": "dams:logical/x",
                "name": "X",
                "description": "x",
                "lifecycle_status": "active",
            }
        ],
        "realizes_not_applicable": {"rationale": "fixture"},
    }
    level_diags = check_dams_model_level(_body(data))
    level_codes = {d.diagnostic_code for d in level_diags}
    assert "DAMS-LEVEL-004" not in level_codes
    assert "DAMS-LEVEL-005" not in level_codes
    assert "DAMS-INV-042" not in level_codes

    inv_diags = check_solution_scope_refs(data)
    assert {d.diagnostic_code for d in inv_diags} == {"DAMS-INV-042"}
    assert len(inv_diags) == 2
    assert all(d.severity is DiagnosticSeverity.ERROR for d in inv_diags)


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


def test_mapping_cardinality_unknown_value_errors() -> None:
    """R2-8: unknown mapping_cardinality must not be silently ignored."""
    data = {
        "realizes_mappings": [
            {
                "element_id": "dams:map/unk",
                "mapping_type": "realizes",
                "mapping_cardinality": "one-to-one",
                "source_refs": ["a"],
                "target_refs": ["b"],
            }
        ]
    }
    diags = check_mapping_cardinality_consistency(data)
    assert any(d.diagnostic_code == "DAMS-INV-051" for d in diags)
    assert any("unknown" in d.diagnostic_message.lower() for d in diags)


def test_relationship_endpoint_rejects_nondams_unresolved() -> None:
    """R2-8: non-dams / cross-package ends that are not in-package entities fail."""
    data = {
        "logical_entities": [
            {"element_id": "dams:logical/E", "name": "E"},
        ],
        "relationships": [
            {
                "element_id": "dams:rel/r",
                "source_entity_ref": "dams:logical/E",
                "target_entity_ref": "eam:entity/Other",
            }
        ],
    }
    diags = check_relationship_endpoint_kinds(data)
    assert any(d.diagnostic_code == "DAMS-INV-053" for d in diags)
    assert any("eam:entity/Other" in d.diagnostic_message for d in diags)


def test_relationship_endpoint_rejects_cross_package_dams_ref() -> None:
    data = {
        "logical_entities": [
            {"element_id": "dams:logical/E", "name": "E"},
        ],
        "relationships": [
            {
                "element_id": "dams:rel/r",
                "source_entity_ref": "dams:logical/E",
                "target_entity_ref": "dams:concept/OtherPackageOnly",
            }
        ],
    }
    diags = check_relationship_endpoint_kinds(data)
    assert any(d.diagnostic_code == "DAMS-INV-053" for d in diags)


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


def test_alignment_dual_path_approval_status_conflict() -> None:
    data = {
        "conceptual_entities": [
            {
                "element_id": "dams:concept/C",
                "external_class_refs": [
                    {
                        "target_ref": "https://example.org/T",
                        "approval_status": "approved",
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
                "approval_status": "rejected",
            }
        ],
    }
    diags = check_alignment_dual_path_consistency(data)
    assert any(d.diagnostic_code == "DAMS-INV-057" for d in diags)
    msg = next(d.diagnostic_message for d in diags if d.diagnostic_code == "DAMS-INV-057")
    assert "approval_status" in msg
    assert all(
        any(det.detail_key == "invariant_id" and det.detail_value == "INV-057" for det in d.diagnostic_details)
        for d in diags
        if d.diagnostic_code == "DAMS-INV-057"
    )
