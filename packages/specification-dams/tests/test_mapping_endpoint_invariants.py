"""ADR-046 PR-4: Mapping endpoint invariants INV-033..036."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_dams.mappings.iter_mappings import LEGACY_MAPPING_KEY, TYPED_MAPPING_KEYS
from moex_dams.rules.constraint_matrix import (
    _collect_invariant_ids,
    _run_l2_package_checks,
    repo_root,
)
from moex_dams.rules.technical_assets import check_mapping_endpoint_types, check_technical_assets

REPO = repo_root()
L2 = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "examples"
    / "invariants"
    / "l2"
)
EXAMPLE = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "requirements"
    / "examples"
    / "it-solution-model.example.yaml"
)


def test_l2_fixtures_inv_033_036() -> None:
    for iid in ("INV-033", "INV-034", "INV-035", "INV-036"):
        valid = yaml.safe_load((L2 / f"{iid}.valid.yaml").read_text(encoding="utf-8"))
        invalid = yaml.safe_load(
            (L2 / f"{iid}.invalid.yaml").read_text(encoding="utf-8")
        )
        assert iid not in _collect_invariant_ids(_run_l2_package_checks(valid)), iid
        assert iid in _collect_invariant_ids(_run_l2_package_checks(invalid)), iid


def test_entity_physical_direction_aware() -> None:
    """Correct carrier→logical passes; reversed fails INV-033 / PDM-009.c1."""
    data = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
    logical_id = data["logical_entities"][0]["element_id"]
    carrier_id = data["data_carriers"][0]["element_id"]
    for key in (*TYPED_MAPPING_KEYS, LEGACY_MAPPING_KEY):
        data.pop(key, None)

    good = {
        **data,
        "entity_physical_mappings": [
            {
                "element_id": "dams:mapping/pos/ep",
                "description": "ok",
                "lifecycle_status": "active",
                "mapping_type": "entity_physical",
                "mapping_cardinality": "one_to_one",
                "source_refs": [carrier_id],
                "target_refs": [logical_id],
            }
        ],
    }
    codes = {d.diagnostic_code for d in check_mapping_endpoint_types(good)}
    assert "DAMS-REQ-PDM-009.c1" not in codes

    bad = {
        **data,
        "entity_physical_mappings": [
            {
                "element_id": "dams:mapping/neg/ep",
                "description": "reversed",
                "lifecycle_status": "active",
                "mapping_type": "entity_physical",
                "mapping_cardinality": "one_to_one",
                "source_refs": [logical_id],
                "target_refs": [carrier_id],
            }
        ],
    }
    diags = check_mapping_endpoint_types(bad)
    assert any(d.diagnostic_code == "DAMS-REQ-PDM-009.c1" for d in diags)
    assert "INV-033" in _collect_invariant_ids(diags)


def test_example_package_endpoint_checks_pass() -> None:
    """Curated example still passes direction-aware PDM-009 / INV-033..036."""
    data = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
    ids = _collect_invariant_ids(list(check_technical_assets(data)))
    assert not (ids & {"INV-033", "INV-034", "INV-035", "INV-036"})
