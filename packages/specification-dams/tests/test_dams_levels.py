"""Tests for DAMS package-level enterprise/solution body rules."""

from __future__ import annotations

from moex_dams.rules.dams_levels import check_dams_model_level
from moex_modeling import DiagnosticSeverity
from moex_standard_linkml.domain.body import LinkMLImplementationBody


def _body(data: dict) -> LinkMLImplementationBody:
    return LinkMLImplementationBody(
        source_path="memory://test.yaml",
        target_class="ModelPackage",
        data=data,
    )


def test_legacy_missing_scope_warns() -> None:
    diags = check_dams_model_level(
        _body(
            {
                "element_id": "dams:model/x",
                "name": "x",
                "description": "x",
                "lifecycle_status": "draft",
                "api_version": "dams.moex/v0.1",
                "model_version": "0.1.0",
            }
        )
    )
    assert any(d.diagnostic_code == "DAMS-LEVEL-000" for d in diags)
    assert all(d.severity is not DiagnosticSeverity.ERROR for d in diags)


def test_enterprise_forbids_technical_assets() -> None:
    diags = check_dams_model_level(
        _body(
            {
                "element_id": "dams:model/enterprise",
                "name": "ent",
                "description": "ent",
                "lifecycle_status": "draft",
                "api_version": "dams.moex/v0.1",
                "model_version": "0.1.0",
                "implementation_scope": "enterprise",
                "conceptual_entities": [
                    {
                        "element_id": "dams:concept/LegalEntity",
                        "name": "LegalEntity",
                        "description": "LE",
                        "lifecycle_status": "active",
                    }
                ],
                "data_carriers": [
                    {
                        "element_id": "dams:physical/x",
                        "name": "x",
                        "description": "bad",
                        "lifecycle_status": "active",
                    }
                ],
            }
        )
    )
    assert any(d.diagnostic_code == "DAMS-LEVEL-003" for d in diags)


def test_solution_requires_realizes() -> None:
    diags = check_dams_model_level(
        _body(
            {
                "element_id": "dams:model/sol",
                "name": "sol",
                "description": "sol",
                "lifecycle_status": "draft",
                "api_version": "dams.moex/v0.1",
                "model_version": "0.1.0",
                "implementation_scope": "solution",
                "solution_ref": "eam:solution/TRADING",
                "conceptual_implementation_ref": (
                    "moex:implementation:moex-enterprise-conceptual-model:0.1"
                ),
                "logical_entities": [
                    {
                        "element_id": "dams:logical/x",
                        "name": "X",
                        "description": "x",
                        "lifecycle_status": "active",
                    }
                ],
                "mappings": [],
            }
        )
    )
    assert any(d.diagnostic_code == "DAMS-LEVEL-007" for d in diags)


def test_solution_with_realizes_ok() -> None:
    diags = check_dams_model_level(
        _body(
            {
                "element_id": "dams:model/sol",
                "name": "sol",
                "description": "sol",
                "lifecycle_status": "draft",
                "api_version": "dams.moex/v0.1",
                "model_version": "0.1.0",
                "implementation_scope": "solution",
                "solution_ref": "eam:solution/TRADING",
                "conceptual_implementation_ref": (
                    "moex:implementation:moex-enterprise-conceptual-model:0.1"
                ),
                "logical_entities": [
                    {
                        "element_id": "dams:logical/x",
                        "name": "X",
                        "description": "x",
                        "lifecycle_status": "active",
                    }
                ],
                "mappings": [
                    {
                        "element_id": "dams:mapping/r1",
                        "name": "r1",
                        "description": "realizes",
                        "lifecycle_status": "active",
                        "source_refs": ["dams:logical/x"],
                        "target_refs": ["dams:concept/LegalEntity"],
                        "mapping_type": "realizes",
                        "mapping_cardinality": "one_to_one",
                    }
                ],
            }
        )
    )
    assert not any(d.severity is DiagnosticSeverity.ERROR for d in diags)
