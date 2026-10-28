"""RequirementCatalog self-validation (LinkML target + semantic gate)."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_dams.rules.catalog_validate import (
    CODE_PATTERN,
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


def test_real_catalog_passes_linkml_requirement_catalog_vacuous() -> None:
    """Vacuous Validator(schema) — kept until FormalCheck schema/data fix (C1a)."""
    from linkml.validator import Validator

    data = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    report = Validator(SCHEMA).validate(data, target_class="RequirementCatalog")
    errors = [
        r
        for r in report.results
        if "ERROR" in str(getattr(r, "severity", r)).upper()
    ]
    assert errors == [], errors[:10]


def test_real_catalog_passes_under_jsonschema_plugin() -> None:
    """PR-C3d: FormalCheck.description / effective are declared; catalog validates."""
    from moex_standard_linkml.validation import error_results, make_linkml_validator

    data = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    errors = error_results(
        make_linkml_validator(SCHEMA).validate(data, target_class="RequirementCatalog")
    )
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


def test_code_pattern_accepts_two_digit_backbone_and_three_digit_legacy() -> None:
    assert CODE_PATTERN.match("CDM-01")
    assert CODE_PATTERN.match("LDM-13")
    assert CODE_PATTERN.match("PDM-02")
    assert CODE_PATTERN.match("GEN-001")
    assert CODE_PATTERN.match("LDM-001")
    assert not CODE_PATTERN.match("CM-GEN-001")
    assert not CODE_PATTERN.match("LDM-1")
    assert not CODE_PATTERN.match("LDM-0011")


def test_empty_formal_checks_allowed_for_manual_rules() -> None:
    data = {
        "catalog_id": "dams:req-catalog/manual/0.1",
        "name": "manual",
        "requirements": [
            {
                "element_id": "dams:req/LDM-03",
                "code": "LDM-03",
                "title": "catalog registration",
                "description": "manual",
                "lifecycle_status": "approved",
                "requirement_level": "it_solution",
                "requirement_section": "LDM",
                "obligation": "mandatory",
                "responsible_role": "it_owner",
                "statement": "Модель ИТ-решения зарегистрирована в Дата-каталоге",
                "applies_to": {
                    "applicability_id": "appl:LDM-03",
                    "applies_target_class": "ModelPackage",
                },
                "formal_checks": [],
            }
        ],
    }
    issues = validate_requirement_catalog(data)
    assert issues == [], [f"{i.code}: {i.message}" for i in issues]
