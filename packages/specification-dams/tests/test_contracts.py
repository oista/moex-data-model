"""Generated DAMS contracts smoke tests."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from moex_dams.application.assess import assess_implementation
from moex_dams.contracts import ModelPackage


def test_model_package_loads_mdm_solution(mdm_solution: Path) -> None:
    data = yaml.safe_load(mdm_solution.read_text(encoding="utf-8"))
    pkg = ModelPackage.model_validate(data)
    assert pkg.element_id == "dams:model/mdm/0.1.0"
    assert pkg.name == "mdm_solution_model"
    # Enterprise concepts live in conceptual_implementation_ref (ADR-029);
    # solution may omit local conceptual_entities.
    assert data.get("conceptual_implementation_ref")
    enterprise = next(e for e in data["logical_entities"] if e["name"] == "ENTERPRISE")
    assert "dams:concept/LegalEntity" in (enterprise.get("conceptual_entity_refs") or [])
    assert getattr(pkg, "data_carriers", None) or data.get("data_carriers")


def test_assess_uses_typed_model_package(
    dams_schema: Path, mdm_solution: Path
) -> None:
    result = assess_implementation(
        schema_path=dams_schema,
        implementation_path=mdm_solution,
        implementation_id="moex:implementation:mdm:0.1.0",
    )
    assert result.report.is_conformant
    assert result.implementation.name == "mdm_solution_model"
