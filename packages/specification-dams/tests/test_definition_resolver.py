"""ADR-025 definition cascade: own / inherited / scoped / exact / diagnostics."""

from __future__ import annotations

from pathlib import Path

from moex_modeling import DiagnosticSeverity
from moex_standard_linkml.domain.body import LinkMLImplementationBody

from moex_dams.rules.definitions import (
    DefinitionMode,
    ExternalDefinition,
    MappingExternalProvider,
    build_definition_index,
    find_redundant_definition_overrides,
    resolve_definition,
)
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


def _enterprise() -> dict:
    return {
        "element_id": "dams:model/enterprise/def-test",
        "name": "enterprise_def_test",
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
            },
            {
                "element_id": "dams:concept/FromOnto",
                "name": "FromOnto",
                "title": "From ontology",
                "lifecycle_status": "active",
                "definition_source_ref": "fibo:LegalPerson",
                "entity_type": "core",
                "data_class": "master_data",
                "business_importance": "high",
            },
        ],
    }


def _solution(**entity_overrides) -> dict:
    entity = {
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
                "logical_type": "string",
                "required": True,
                "multivalued": False,
            }
        ],
    }
    entity.update(entity_overrides)
    return {
        "element_id": "dams:model/sol/def-test",
        "name": "sol_def_test",
        "description": "solution package",
        "lifecycle_status": "draft",
        "api_version": "dams.moex/v0.1",
        "model_version": "0.1.0",
        "implementation_scope": "solution",
        "solution_ref": "eam:solution/DEF",
        "data_owner_ref": "org:role/OWNER",
        "logical_entities": [entity],
        "domain_contexts": [
            {
                "element_id": "dams:context/sol",
                "name": "sol",
                "description": "ctx",
                "lifecycle_status": "draft",
                "domain_ref": "eam:domain/X",
                "namespace": "https://example.com/sol",
            }
        ],
    }


def test_own_definition() -> None:
    ent = {
        "element_id": "dams:logical/x",
        "name": "X",
        "description": "Own text.",
    }
    idx = build_definition_index()
    prov = resolve_definition(ent, idx, level="LogicalEntity")
    assert prov.mode is DefinitionMode.OWN
    assert prov.text == "Own text."
    assert prov.source_element_id == "dams:logical/x"
    assert prov.source_hash


def test_own_adapted() -> None:
    ent = {
        "element_id": "dams:concept/LE",
        "description": "Adapted MOEX wording.",
        "definition_source_ref": "fibo:LegalPerson",
    }
    idx = build_definition_index()
    prov = resolve_definition(ent, idx, level="ConceptualEntity")
    assert prov.mode is DefinitionMode.OWN_ADAPTED


def test_inherit_from_conceptual() -> None:
    enterprise = _enterprise()
    sol = _solution()  # no description on entity
    # strip default description if any
    sol["logical_entities"][0].pop("description", None)
    idx = build_definition_index(enterprise, sol)
    eid = "dams:logical/sol/LegalEntity"
    prov = resolve_definition(sol["logical_entities"][0], idx, level="LogicalEntity")
    assert prov.mode is DefinitionMode.INHERITED
    assert prov.text == "Эталонное определение LegalEntity в КМД."
    assert prov.source_element_id == "dams:concept/LegalEntity"


def test_inherit_from_exact_ontology() -> None:
    provider = MappingExternalProvider(
        {
            "fibo:LegalPerson": ExternalDefinition(
                id="fibo:LegalPerson",
                text="A legal person in the sense of FIBO.",
                language="en",
                level="OntologyClass",
                exact=True,
            )
        }
    )
    enterprise = _enterprise()
    idx = build_definition_index(enterprise, providers=(provider,))
    from_onto = enterprise["conceptual_entities"][1]
    prov = resolve_definition(from_onto, idx, level="ConceptualEntity")
    assert prov.mode is DefinitionMode.INHERITED
    assert "FIBO" in (prov.text or "")
    assert prov.language == "en"


def test_close_match_does_not_inherit() -> None:
    provider = MappingExternalProvider(
        {
            "fibo:LegalPerson": ExternalDefinition(
                id="fibo:LegalPerson",
                text="Close only.",
                exact=False,
            )
        }
    )
    ent = {
        "element_id": "dams:concept/X",
        "definition_source_ref": "fibo:LegalPerson",
    }
    idx = build_definition_index(providers=(provider,))
    prov = resolve_definition(ent, idx, level="ConceptualEntity")
    assert prov.mode is DefinitionMode.UNRESOLVED
    assert prov.diagnostic and "exact" in prov.diagnostic.lower()


def test_ambiguous_multi_conceptual_refs() -> None:
    ent = {
        "element_id": "dams:logical/x",
        "conceptual_entity_refs": ["dams:concept/A", "dams:concept/B"],
        "conceptual_alignment_status": "aligned",
    }
    idx = build_definition_index()
    prov = resolve_definition(ent, idx, level="LogicalEntity")
    assert prov.mode is DefinitionMode.UNRESOLVED
    assert "ambiguous" in (prov.diagnostic or "").lower()


def test_cycle_detection() -> None:
    a = {
        "element_id": "dams:concept/A",
        "definition_source_ref": "dams:concept/B",
    }
    b = {
        "element_id": "dams:concept/B",
        "definition_source_ref": "dams:concept/A",
    }
    pkg = {
        "element_id": "dams:model/cycle",
        "conceptual_entities": [a, b],
    }
    idx = build_definition_index(pkg)
    prov = resolve_definition(a, idx, level="ConceptualEntity")
    assert prov.mode is DefinitionMode.UNRESOLVED
    assert "cycle" in (prov.diagnostic or "").lower()


def test_pending_requires_own() -> None:
    ent = {
        "element_id": "dams:logical/x",
        "conceptual_alignment_status": "pending",
        "conceptual_entity_refs": ["dams:concept/LegalEntity"],
    }
    idx = build_definition_index(_enterprise())
    prov = resolve_definition(ent, idx, level="LogicalEntity")
    assert prov.mode is DefinitionMode.UNRESOLVED
    assert "pending" in (prov.diagnostic or "")


def test_scoped_definition() -> None:
    ent = {
        "element_id": "dams:logical/x",
        "description": "Reference definition.",
        "scoped_definitions": [
            {
                "scoped_definition_id": "dams:scoped/x/sys1",
                "scope_kind": "system",
                "scope_ref": "eam:system/SYS1",
                "text": "System-local wording.",
                "relation_to_reference": "narrows",
            }
        ],
    }
    idx = build_definition_index()
    ref = resolve_definition(ent, idx, level="LogicalEntity")
    assert ref.mode is DefinitionMode.OWN
    scoped = resolve_definition(
        ent, idx, level="LogicalEntity", scope="eam:system/SYS1"
    )
    assert scoped.mode is DefinitionMode.SCOPED
    assert scoped.text == "System-local wording."
    assert scoped.scope == "eam:system/SYS1"


def test_redundant_definition_override() -> None:
    enterprise = _enterprise()
    sol = _solution(
        description="Эталонное определение LegalEntity в КМД.",
    )
    idx = build_definition_index(enterprise, sol)
    findings = find_redundant_definition_overrides(sol, idx)
    assert ("dams:logical/sol/LegalEntity", "dams:concept/LegalEntity") in findings


def test_formal_ldm002_c3_accepts_inherited() -> None:
    enterprise = _enterprise()
    sol = _solution()
    sol["logical_entities"][0].pop("description", None)
    # Minimal fields so other checks do not drown the assertion
    body = LinkMLImplementationBody(
        source_path="memory.yaml",
        target_class="ModelPackage",
        data=sol,
    )
    diags = check_formal_requirements(
        body,
        catalog_path=CATALOG,
        extra_definition_packages=(enterprise,),
    )
    ldm002_c3 = [
        d
        for d in diags
        if d.diagnostic_code == "DAMS-REQ-LDM-002.c3"
        and d.severity == DiagnosticSeverity.ERROR
    ]
    assert ldm002_c3 == []


def test_formal_ldm002_c3_rejects_missing() -> None:
    sol = _solution(
        conceptual_entity_refs=[],
        conceptual_alignment_status="local-only",
        alignment_rationale="local",
    )
    sol["logical_entities"][0].pop("description", None)
    body = LinkMLImplementationBody(
        source_path="memory.yaml",
        target_class="ModelPackage",
        data=sol,
    )
    diags = check_formal_requirements(body, catalog_path=CATALOG)
    codes = {d.diagnostic_code for d in diags if d.severity == DiagnosticSeverity.ERROR}
    assert "DAMS-REQ-LDM-002.c3" in codes


def test_description_eq_title_info() -> None:
    sol = _solution(description="Юридическое лицо", title="Юридическое лицо")
    body = LinkMLImplementationBody(
        source_path="memory.yaml",
        target_class="ModelPackage",
        data=sol,
    )
    diags = check_formal_requirements(body, catalog_path=CATALOG)
    infos = [
        d
        for d in diags
        if d.diagnostic_code == "DAMS-DEF-description-eq-title"
    ]
    assert infos


def test_scope_ref_invalid_error() -> None:
    sol = _solution(
        description="Own def.",
        scoped_definitions=[
            {
                "scoped_definition_id": "dams:scoped/1",
                "scope_kind": "system",
                "scope_ref": "eam:system/NOT_IN_SOLUTION",
                "text": "Scoped",
                "relation_to_reference": "refines",
            }
        ],
    )
    idx = build_definition_index(sol)
    idx.add_solution_systems("eam:solution/DEF", ["eam:system/SYS1"])
    body = LinkMLImplementationBody(
        source_path="memory.yaml",
        target_class="ModelPackage",
        data=sol,
    )
    diags = check_formal_requirements(
        body, catalog_path=CATALOG, definition_index=idx
    )
    errors = [
        d
        for d in diags
        if d.diagnostic_code == "DAMS-DEF-scope-ref-invalid"
        and d.severity == DiagnosticSeverity.ERROR
    ]
    assert errors


def test_override_without_rationale_warning() -> None:
    sol = _solution(
        description="Own adapted text.",
        definition_source_ref="dams:concept/LegalEntity",
    )
    body = LinkMLImplementationBody(
        source_path="memory.yaml",
        target_class="ModelPackage",
        data=sol,
    )
    diags = check_formal_requirements(
        body,
        catalog_path=CATALOG,
        extra_definition_packages=(_enterprise(),),
    )
    warns = [
        d
        for d in diags
        if d.diagnostic_code == "DAMS-DEF-override-without-rationale"
        and d.severity == DiagnosticSeverity.WARNING
    ]
    assert warns
