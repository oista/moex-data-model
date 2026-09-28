"""RequirementCatalog self-validation (LinkML target + semantic gate)."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_dams.rules.catalog_validate import (
    validate_requirement_catalog,
    validate_requirement_catalog_file,
)

REPO = Path(__file__).resolve().parents[3]
CATALOG = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "requirements"
    / "it-solution-requirements.yaml"
)
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "requirements"
SCHEMA = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "schemas"
    / "moex-dams.yaml"
)


def test_real_catalog_passes_semantic_gate() -> None:
    issues = validate_requirement_catalog_file(CATALOG)
    assert issues == [], [f"{i.code}: {i.message}" for i in issues]


def test_real_catalog_passes_linkml_requirement_catalog() -> None:
    from linkml.validator import Validator

    data = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    report = Validator(SCHEMA).validate(data, target_class="RequirementCatalog")
    errors = [
        r
        for r in report.results
        if "ERROR" in str(getattr(r, "severity", r)).upper()
    ]
    assert errors == [], errors[:10]


def test_unknown_check_kind() -> None:
    issues = validate_requirement_catalog_file(FIXTURES / "bad-unknown-kind.yaml")
    assert any(i.code == "CATALOG-CHECK-KIND" for i in issues)


def test_missing_statement() -> None:
    issues = validate_requirement_catalog_file(FIXTURES / "bad-missing-statement.yaml")
    assert any(i.code == "CATALOG-STATEMENT-MISSING" for i in issues)


def test_duplicate_requirement_id() -> None:
    issues = validate_requirement_catalog_file(
        FIXTURES / "bad-duplicate-requirement-id.yaml"
    )
    assert any(i.code == "CATALOG-ID-DUP" for i in issues)


def test_unknown_target_class() -> None:
    issues = validate_requirement_catalog_file(FIXTURES / "bad-unknown-target-class.yaml")
    assert any(i.code == "CATALOG-TARGET-CLASS" for i in issues)


def test_duplicate_check_id_detected() -> None:
    data = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    # Clone first check id onto second requirement
    reqs = data["requirements"]
    reqs[1]["formal_checks"][0]["check_id"] = reqs[0]["formal_checks"][0]["check_id"]
    issues = validate_requirement_catalog(data)
    assert any(i.code == "CATALOG-CHECK-ID-DUP" for i in issues)
