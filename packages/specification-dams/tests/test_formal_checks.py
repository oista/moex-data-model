"""IT-solution formal_checks runner (ADR-013 Wave 1)."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_modeling import DiagnosticSeverity
from moex_standard_linkml.domain.body import LinkMLImplementationBody

from moex_dams.rules.formal_checks import check_formal_requirements

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


def _body_from_dict(data: dict, path: str = "memory.yaml") -> LinkMLImplementationBody:
    return LinkMLImplementationBody(
        source_path=path,
        target_class="ModelPackage",
        data=data,
    )


def test_example_package_has_no_errors() -> None:
    data = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
    diags = check_formal_requirements(
        _body_from_dict(data, str(EXAMPLE)),
        catalog_path=CATALOG,
    )
    errors = [d for d in diags if d.severity == DiagnosticSeverity.ERROR]
    assert errors == [], [d.diagnostic_message for d in errors]


def test_negative_missing_identity_rule() -> None:
    data = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
    for ent in data["logical_entities"]:
        ent.pop("identity_rule", None)
        ent["business_key_kind"] = "surrogate"
        ent.pop("key_attribute_refs", None)
    diags = check_formal_requirements(
        _body_from_dict(data, str(EXAMPLE)),
        catalog_path=CATALOG,
    )
    codes = {d.diagnostic_code for d in diags if d.severity == DiagnosticSeverity.ERROR}
    assert any("LDM-004" in c for c in codes)
    assert any("Remediation:" in d.diagnostic_message for d in diags)


def test_naming_warning_for_camel_case() -> None:
    data = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
    data["logical_entities"][0]["attributes"][0]["name"] = "partyId"
    diags = check_formal_requirements(
        _body_from_dict(data, str(EXAMPLE)),
        catalog_path=CATALOG,
    )
    warns = [
        d
        for d in diags
        if d.severity == DiagnosticSeverity.WARNING and "ATR-002" in d.diagnostic_code
    ]
    assert warns
    errors = [d for d in diags if d.severity == DiagnosticSeverity.ERROR]
    assert errors == []


def test_empty_package_fails_gen003() -> None:
    data = {
        "element_id": "dams:model/empty",
        "name": "empty",
        "description": "empty",
        "lifecycle_status": "draft",
        "api_version": "dams.moex/v0.1",
        "model_version": "1.0.0",
        "implementation_scope": "solution",
        "solution_ref": "eam:solution/X",
        "data_owner_ref": "org:role/X",
    }
    diags = check_formal_requirements(
        _body_from_dict(data),
        catalog_path=CATALOG,
    )
    assert any(d.diagnostic_code == "DAMS-REQ-GEN-003.c1" for d in diags)
