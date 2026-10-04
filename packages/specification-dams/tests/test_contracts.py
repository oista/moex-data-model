"""Generated DAMS contracts smoke tests."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_dams.application.assess import assess_implementation
from moex_dams.contracts import ModelPackage


def test_model_package_loads_trading_solution(trading_solution: Path) -> None:
    data = yaml.safe_load(trading_solution.read_text(encoding="utf-8"))
    pkg = ModelPackage.model_validate(data)
    assert pkg.element_id == "dams:model/trading/1.0.0"
    assert pkg.name == "trading_solution_model"
    # Enterprise concepts live in conceptual_implementation_ref (ADR-029);
    # solution may omit local conceptual_entities.
    assert data.get("conceptual_implementation_ref")
    client = next(e for e in data["logical_entities"] if e["name"] == "TradingClient")
    assert "dams:concept/Client" in (client.get("conceptual_entity_refs") or [])


def test_assess_uses_typed_model_package(
    dams_schema: Path, trading_solution: Path
) -> None:
    result = assess_implementation(
        schema_path=dams_schema,
        implementation_path=trading_solution,
        implementation_id="moex:implementation:trading:1.0.0",
    )
    assert result.report.is_conformant
    assert result.implementation.name == "trading_solution_model"
