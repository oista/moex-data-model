"""Tests for semantic_layer rules (ConceptualProperty / domains / types)."""

from __future__ import annotations

from moex_modeling import DiagnosticSeverity

from moex_dams.rules.semantic_layer import check_semantic_layer


def _codes(diags):
    return {d.diagnostic_code for d in diags}


def test_missing_concept_ref_is_silent():
    data = {
        "implementation_scope": "solution",
        "logical_entities": [
            {
                "element_id": "dams:logical/x/E",
                "name": "E",
                "description": "e",
                "lifecycle_status": "active",
                "context_ref": "dams:ctx/x",
                "solution_data_role": "producer",
                "attributes": [
                    {
                        "element_id": "dams:logical/x/E/a",
                        "name": "a",
                        "description": "a",
                        "lifecycle_status": "active",
                        "owner_entity_ref": "dams:logical/x/E",
                        "logical_type": "string",
                        "required": True,
                        "multivalued": False,
                    }
                ],
            }
        ],
    }
    diags = check_semantic_layer(data)
    assert not any("CONCEPT" in d.diagnostic_code and d.severity in {
        DiagnosticSeverity.ERROR, DiagnosticSeverity.WARNING
    } for d in diags if "concept_ref" in d.diagnostic_message.lower() or d.diagnostic_code.endswith("CONCEPT"))
    # specifically: no diagnostic about missing concept_ref
    assert not any("concept_ref" in (d.diagnostic_message or "") and "отсутств" in (d.diagnostic_message or "").lower() for d in diags)


def test_property_without_significance_basis_errors():
    data = {
        "implementation_scope": "enterprise",
        "conceptual_entities": [
            {"element_id": "dams:concept/C", "name": "C", "description": "c", "lifecycle_status": "active"}
        ],
        "conceptual_properties": [
            {
                "element_id": "dams:concept/C/p",
                "name": "p",
                "description": "p",
                "lifecycle_status": "active",
                "property_owner_entity_ref": "dams:concept/C",
                "significance_basis": [],
                "property_kind": "descriptive",
                "genesis_kind": "native",
            }
        ],
    }
    assert "DAMS-SEM-PROP-BASIS" in _codes(check_semantic_layer(data))


def test_conceptual_property_in_solution_errors():
    data = {
        "implementation_scope": "solution",
        "conceptual_properties": [
            {
                "element_id": "dams:concept/C/p",
                "name": "p",
                "description": "p",
                "lifecycle_status": "active",
                "property_owner_entity_ref": "dams:concept/C",
                "significance_basis": ["identifying"],
                "property_kind": "identifying",
                "is_identifying": True,
                "genesis_kind": "native",
            }
        ],
    }
    assert "DAMS-SEM-PROP-SCOPE" in _codes(check_semantic_layer(data))


def test_enumerated_domain_without_values_errors():
    data = {
        "implementation_scope": "enterprise",
        "conceptual_domains": [
            {
                "element_id": "dams:cd/1",
                "name": "cd",
                "description": "d",
                "lifecycle_status": "active",
                "conceptual_domain_kind": "enumerated",
                "value_meanings": [],
            }
        ],
    }
    assert "DAMS-SEM-CD-ENUM" in _codes(check_semantic_layer(data))


def test_described_domain_with_meanings_errors():
    data = {
        "implementation_scope": "enterprise",
        "conceptual_domains": [
            {
                "element_id": "dams:cd/1",
                "name": "cd",
                "description": "d",
                "lifecycle_status": "active",
                "conceptual_domain_kind": "described",
                "value_meanings": [{"meaning_key": "x"}],
            }
        ],
    }
    assert "DAMS-SEM-CD-DESC" in _codes(check_semantic_layer(data))


def test_precision_on_string_errors():
    data = {
        "implementation_scope": "enterprise",
        "data_types": [
            {
                "element_id": "dams:datatype/string",
                "name": "string",
                "description": "s",
                "lifecycle_status": "active",
                "type_name": "string",
                "type_family": "string",
                "precision": 10,
            }
        ],
    }
    assert "DAMS-SEM-DT-PREC" in _codes(check_semantic_layer(data))


def test_scale_gt_precision_errors():
    data = {
        "implementation_scope": "enterprise",
        "data_types": [
            {
                "element_id": "dams:datatype/decimal",
                "name": "decimal",
                "description": "d",
                "lifecycle_status": "active",
                "type_name": "decimal",
                "type_family": "decimal",
                "precision": 5,
                "scale": 8,
            }
        ],
    }
    assert "DAMS-SEM-DT-SCALE-LE" in _codes(check_semantic_layer(data))


def test_attribute_without_type_errors():
    data = {
        "implementation_scope": "solution",
        "logical_entities": [
            {
                "element_id": "dams:logical/x/E",
                "name": "E",
                "description": "e",
                "lifecycle_status": "active",
                "context_ref": "dams:ctx/x",
                "solution_data_role": "producer",
                "attributes": [
                    {
                        "element_id": "dams:logical/x/E/a",
                        "name": "a",
                        "description": "a",
                        "lifecycle_status": "active",
                        "owner_entity_ref": "dams:logical/x/E",
                        "required": True,
                        "multivalued": False,
                    }
                ],
            }
        ],
    }
    assert "DAMS-SEM-ATTR-TYPE" in _codes(check_semantic_layer(data))


def test_explicit_decision_requires_rationale():
    data = {
        "implementation_scope": "enterprise",
        "conceptual_entities": [
            {"element_id": "dams:concept/C", "name": "C", "description": "c", "lifecycle_status": "active"}
        ],
        "conceptual_properties": [
            {
                "element_id": "dams:concept/C/p",
                "name": "p",
                "description": "p",
                "lifecycle_status": "active",
                "property_owner_entity_ref": "dams:concept/C",
                "significance_basis": ["explicit_decision"],
                "property_kind": "descriptive",
                "genesis_kind": "native",
            }
        ],
    }
    assert "DAMS-SEM-PROP-RATIONALE" in _codes(check_semantic_layer(data))


def test_is_identifying_without_basis_errors():
    data = {
        "implementation_scope": "enterprise",
        "conceptual_entities": [
            {"element_id": "dams:concept/C", "name": "C", "description": "c", "lifecycle_status": "active"}
        ],
        "conceptual_properties": [
            {
                "element_id": "dams:concept/C/p",
                "name": "p",
                "description": "p",
                "lifecycle_status": "active",
                "property_owner_entity_ref": "dams:concept/C",
                "significance_basis": ["regulatory"],
                "property_kind": "descriptive",
                "is_identifying": True,
                "genesis_kind": "native",
            }
        ],
    }
    assert "DAMS-SEM-PROP-IDENT" in _codes(check_semantic_layer(data))
