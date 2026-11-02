"""Assess auto-loads related ModelPackage bodies for LDM-04 / CDM-01 (ADR-025)."""

from __future__ import annotations

from pathlib import Path

import yaml
from moex_modeling import DiagnosticSeverity
from moex_standard_linkml.domain.body import LinkMLImplementationBody

from moex_dams.rules.formal_checks import (
    check_formal_requirements,
    check_formal_requirements_for_repo,
    load_related_definition_packages,
)

ENTERPRISE_ID = "moex:implementation:moex-enterprise-conceptual-model:0.1"
CATALOG = (
    Path(__file__).resolve().parents[3]
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "requirements"
    / "it-solution-requirements.yaml"
)


def _write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def _make_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "model-assets").mkdir(parents=True)
    (root / "packages").mkdir(parents=True)
    return root


def _write_envelope(
    root: Path,
    *,
    rel_dir: str,
    impl_id: str,
    body_name: str,
    body: dict,
) -> Path:
    folder = root / "model-assets" / "implementations" / rel_dir
    body_path = folder / body_name
    _write_yaml(body_path, body)
    _write_yaml(
        folder / "implementation.yaml",
        {
            "id": impl_id,
            "name": body.get("name") or "pkg",
            "body_ref": body_name,
            "implementation_body": body_name,
        },
    )
    return body_path


def _enterprise_body() -> dict:
    return {
        "element_id": "dams:model/enterprise/related-test",
        "name": "enterprise_related_test",
        "description": "enterprise package",
        "lifecycle_status": "draft",
        "api_version": "dams.moex/v0.1",
        "model_version": "0.1.0",
        "implementation_scope": "enterprise",
        "conceptual_entities": [
            {
                "element_id": "dams:concept/LegalEntity",
                "name": "LegalEntity",
                "title": "Юридическое лицо",
                "description": "Эталонное определение LegalEntity в КМД.",
                "lifecycle_status": "active",
                "entity_type": "core",
                "data_class": "master_data",
                "business_importance": "high",
            }
        ],
    }


def _solution_body(*, conceptual_ref: str | None = ENTERPRISE_ID) -> dict:
    data = {
        "element_id": "dams:model/sol/related-test",
        "name": "sol_related_test",
        "description": "solution package",
        "lifecycle_status": "draft",
        "api_version": "dams.moex/v0.1",
        "model_version": "0.1.0",
        "implementation_scope": "solution",
        "solution_ref": "eam:solution/RELATED",
        "data_owner_ref": "org:role/OWNER",
        "data_steward_ref": "org:role/STEWARD",
        "logical_entities": [
            {
                "element_id": "dams:logical/sol/LegalEntity",
                "name": "LegalEntity",
                "title": "Юридическое лицо",
                "lifecycle_status": "draft",
                "context_ref": "dams:context/sol",
                "solution_data_role": "producer",
                "conceptual_entity_refs": ["dams:concept/LegalEntity"],
                "conceptual_alignment_status": "aligned",
                "attributes": [
                    {
                        "element_id": "dams:logical/sol/LegalEntity/inn",
                        "name": "inn",
                        "title": "ИНН",
                        "description": "Идентификационный номер налогоплательщика.",
                        "lifecycle_status": "draft",
                        "owner_entity_ref": "dams:logical/sol/LegalEntity",
                        "data_type_ref": "dams:datatype/string",
                        "required": True,
                        "multivalued": False,
                    }
                ],
            }
        ],
    }
    if conceptual_ref is not None:
        data["conceptual_implementation_ref"] = conceptual_ref
    return data


def _error_codes(diags) -> set[str]:
    return {
        d.diagnostic_code
        for d in diags
        if d.severity == DiagnosticSeverity.ERROR
    }


def test_ldm04_inherits_via_conceptual_implementation_ref(
    tmp_path: Path,
) -> None:
    root = _make_repo(tmp_path)
    _write_envelope(
        root,
        rel_dir="enterprise/cmd/0.1",
        impl_id=ENTERPRISE_ID,
        body_name="enterprise-conceptual-model.yaml",
        body=_enterprise_body(),
    )
    sol_path = _write_envelope(
        root,
        rel_dir="solutions/demo",
        impl_id="moex:implementation:demo:0.1",
        body_name="demo-solution-model.yaml",
        body=_solution_body(),
    )
    body = LinkMLImplementationBody(
        source_path=str(sol_path),
        target_class="ModelPackage",
        data=yaml.safe_load(sol_path.read_text(encoding="utf-8")),
    )
    diags = check_formal_requirements_for_repo(body)
    assert "DAMS-REQ-LDM-002.c3" not in _error_codes(diags)


def test_ldm04_errors_without_enterprise_package(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    sol_path = _write_envelope(
        root,
        rel_dir="solutions/demo",
        impl_id="moex:implementation:demo:0.1",
        body_name="demo-solution-model.yaml",
        body=_solution_body(),
    )
    body = LinkMLImplementationBody(
        source_path=str(sol_path),
        target_class="ModelPackage",
        data=yaml.safe_load(sol_path.read_text(encoding="utf-8")),
    )
    diags = check_formal_requirements_for_repo(body)
    assert "DAMS-REQ-LDM-002.c3" in _error_codes(diags)


def test_cdm01_inherits_via_sibling_definition_source_ref(
    tmp_path: Path,
) -> None:
    root = _make_repo(tmp_path)
    sibling = {
        "element_id": "dams:model/enterprise/sibling",
        "name": "sibling_defs",
        "description": "sibling enterprise package",
        "lifecycle_status": "draft",
        "api_version": "dams.moex/v0.1",
        "model_version": "0.1.0",
        "implementation_scope": "enterprise",
        "conceptual_entities": [
            {
                "element_id": "dams:concept/Party",
                "name": "Party",
                "title": "Сторона",
                "description": "Бизнес-актор независимо от формы реализации.",
                "lifecycle_status": "active",
            }
        ],
    }
    _write_envelope(
        root,
        rel_dir="enterprise/sibling/0.1",
        impl_id="moex:implementation:sibling-defs:0.1",
        body_name="sibling.yaml",
        body=sibling,
    )
    enterprise = {
        "element_id": "dams:model/enterprise/main",
        "name": "main_enterprise",
        "description": "main enterprise package",
        "lifecycle_status": "draft",
        "api_version": "dams.moex/v0.1",
        "model_version": "0.1.0",
        "implementation_scope": "enterprise",
        "conceptual_entities": [
            {
                "element_id": "dams:concept/LegalEntity",
                "name": "LegalEntity",
                "title": "Юридическое лицо",
                "lifecycle_status": "active",
                "definition_source_ref": "dams:concept/Party",
                "parent_concept_ref": "dams:concept/Party",
            }
        ],
    }
    ent_path = _write_envelope(
        root,
        rel_dir="enterprise/main/0.1",
        impl_id="moex:implementation:main-enterprise:0.1",
        body_name="main.yaml",
        body=enterprise,
    )
    body = LinkMLImplementationBody(
        source_path=str(ent_path),
        target_class="ModelPackage",
        data=yaml.safe_load(ent_path.read_text(encoding="utf-8")),
    )
    diags = check_formal_requirements_for_repo(body)
    assert "DAMS-REQ-CDM-01.c1" not in _error_codes(diags)


def test_cdm01_errors_without_sibling_package(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    enterprise = {
        "element_id": "dams:model/enterprise/main",
        "name": "main_enterprise",
        "description": "main enterprise package",
        "lifecycle_status": "draft",
        "api_version": "dams.moex/v0.1",
        "model_version": "0.1.0",
        "implementation_scope": "enterprise",
        "conceptual_entities": [
            {
                "element_id": "dams:concept/LegalEntity",
                "name": "LegalEntity",
                "title": "Юридическое лицо",
                "lifecycle_status": "active",
                "definition_source_ref": "dams:concept/Party",
            }
        ],
    }
    ent_path = _write_envelope(
        root,
        rel_dir="enterprise/main/0.1",
        impl_id="moex:implementation:main-enterprise:0.1",
        body_name="main.yaml",
        body=enterprise,
    )
    body = LinkMLImplementationBody(
        source_path=str(ent_path),
        target_class="ModelPackage",
        data=yaml.safe_load(ent_path.read_text(encoding="utf-8")),
    )
    diags = check_formal_requirements_for_repo(body)
    assert "DAMS-REQ-CDM-01.c1" in _error_codes(diags)


def test_explicit_extra_definition_packages_skips_autoload(
    tmp_path: Path,
) -> None:
    root = _make_repo(tmp_path)
    # No envelopes under implementations — autoload would fail without extras.
    sol = _solution_body(conceptual_ref=ENTERPRISE_ID)
    body = LinkMLImplementationBody(
        source_path=str(root / "memory.yaml"),
        target_class="ModelPackage",
        data=sol,
    )
    diags = check_formal_requirements(
        body,
        catalog_path=CATALOG,
        repo_root=root,
        extra_definition_packages=(_enterprise_body(),),
    )
    assert "DAMS-REQ-LDM-002.c3" not in _error_codes(diags)


def test_fibo_ref_does_not_load_neighbor_packages(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    neighbor = _enterprise_body()
    _write_envelope(
        root,
        rel_dir="enterprise/cmd/0.1",
        impl_id=ENTERPRISE_ID,
        body_name="enterprise-conceptual-model.yaml",
        body=neighbor,
    )
    data = {
        "element_id": "dams:model/enterprise/fibo-only",
        "name": "fibo_only",
        "description": "enterprise with external ontology source only",
        "lifecycle_status": "draft",
        "api_version": "dams.moex/v0.1",
        "model_version": "0.1.0",
        "implementation_scope": "enterprise",
        "conceptual_entities": [
            {
                "element_id": "dams:concept/FromOnto",
                "name": "FromOnto",
                "title": "From ontology",
                "lifecycle_status": "active",
                "definition_source_ref": "fibo:LegalPerson",
            }
        ],
    }
    related = load_related_definition_packages(data, root)
    assert related == ()
