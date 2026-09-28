"""DamsAssetRepository + rule runner wiring."""

from __future__ import annotations

from pathlib import Path

from moex_modeling import SpecificationRef

from moex_dams import DamsAssetRepository, assess_implementation, default_dams_rule_sets
from moex_dams.application.repository import DAMS_SPEC_ID, DAMS_VERSION


def test_repository_loads_trading(dams_schema: Path, trading_solution: Path) -> None:
    repo = DamsAssetRepository(default_schema_path=dams_schema)
    spec = repo.load_specification(
        SpecificationRef(
            specification_id=DAMS_SPEC_ID,
            specification_version=DAMS_VERSION,
            specification_revision=DAMS_VERSION,
        )
    )
    assert spec.root_class == "MOEXModelRepository"
    from moex_modeling import ImplementationRef

    body = repo.load_implementation(
        ImplementationRef(
            implementation_id="moex:implementation:trading",
            implementation_revision="1",
        ),
        path=trading_solution,
    )
    assert body.data.get("element_id") == "dams:model/trading/1.0.0"


def test_assess_uses_repository_not_bare_provider(
    dams_schema: Path, trading_solution: Path
) -> None:
    result = assess_implementation(
        schema_path=dams_schema,
        implementation_path=trading_solution,
    )
    assert result.report.is_conformant
    sets = default_dams_rule_sets(DamsAssetRepository(default_schema_path=dams_schema))
    assert len(sets) == 5
    assert any(s.assessment_id == "assessment:identifiers" for s in sets)
    assert any(s.assessment_id == "assessment:dams-levels" for s in sets)
