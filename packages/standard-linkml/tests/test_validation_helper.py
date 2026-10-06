"""PR-C1a: make_linkml_validator vs vacuous Validator(schema)."""

from __future__ import annotations

from pathlib import Path

import yaml
from linkml.validator import Validator

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
EXAMPLE = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "examples"
    / "client-contract-binding.yaml"
)


def test_vacuous_validator_misses_broken_instance() -> None:
    good = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
    bad = dict(good)
    bad["not_a_schema_slot"] = "x"
    assert error_results(Validator(SCHEMA).validate(bad, target_class="DataModelBinding")) == []


def test_make_linkml_validator_rejects_additional_property() -> None:
    good = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
    bad = dict(good)
    bad["not_a_schema_slot"] = "x"
    errors = error_results(
        make_linkml_validator(SCHEMA).validate(bad, target_class="DataModelBinding")
    )
    assert errors, "expected JsonschemaValidationPlugin to reject unknown property"


def test_make_linkml_validator_accepts_known_good_example() -> None:
    good = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
    errors = error_results(
        make_linkml_validator(SCHEMA).validate(good, target_class="DataModelBinding")
    )
    assert errors == []
