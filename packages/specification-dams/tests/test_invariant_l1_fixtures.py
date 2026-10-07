"""PR-C2: L1 invariant fixtures — valid pass, invalid fail under JsonschemaValidationPlugin."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_standard_linkml.validation import error_results, make_linkml_validator

REPO = Path(__file__).resolve().parents[3]
SCHEMA = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "schemas"
    / "moex-dams.yaml"
)
MANIFEST = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "examples"
    / "invariants"
    / "manifest.yaml"
)


def test_all_l1_fixtures_negative_mode() -> None:
    man = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    validator = make_linkml_validator(SCHEMA)
    inv_dir = MANIFEST.parent
    assert len(man["cases"]) == 17
    for case in man["cases"]:
        target = case["target_class"]
        valid = yaml.safe_load((inv_dir / case["valid"]).read_text(encoding="utf-8"))
        invalid = yaml.safe_load(
            (inv_dir / case["invalid"]).read_text(encoding="utf-8")
        )
        assert (
            error_results(validator.validate(valid, target_class=target)) == []
        ), case["id"]
        assert error_results(
            validator.validate(invalid, target_class=target)
        ), f"{case['id']} invalid must be rejected"

