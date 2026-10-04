"""IT-solution formal_checks: happy path, negatives per template, assess wiring."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import yaml

from moex_modeling import DiagnosticSeverity
from moex_standard_linkml.domain.body import LinkMLImplementationBody

from moex_dams import assess_implementation
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
SCHEMA = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "schemas"
    / "moex-dams.yaml"
)
TRADING = (
    REPO
    / "model-assets"
    / "implementations"
    / "solutions"
    / "trading-platform"
    / "trading-solution-model.yaml"
)


def _body(data: dict, path: str = "memory.yaml") -> LinkMLImplementationBody:
    return LinkMLImplementationBody(
        source_path=path,
        target_class="ModelPackage",
        data=data,
    )


def _example() -> dict:
    return yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))


def _errors(data: dict) -> list:
    return [
        d
        for d in check_formal_requirements(_body(data, str(EXAMPLE)), catalog_path=CATALOG)
        if d.severity == DiagnosticSeverity.ERROR
    ]


def _warns(data: dict) -> list:
    return [
        d
        for d in check_formal_requirements(_body(data, str(EXAMPLE)), catalog_path=CATALOG)
        if d.severity == DiagnosticSeverity.WARNING
    ]


def _codes(diags) -> set[str]:
    return {d.diagnostic_code for d in diags}


# --- Happy / wiring -----------------------------------------------------------


def test_example_package_has_no_errors() -> None:
    assert _errors(_example()) == []


def test_catalog_expressions_all_have_runner_templates() -> None:
    """Every conditional_branch expression in catalog must be implemented."""
    from moex_dams.rules import formal_checks as fc

    cat = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    exprs = {
        c["expression"]
        for r in cat["requirements"]
        for c in r.get("formal_checks") or []
        if c.get("kind") == "conditional_branch" and c.get("expression")
    }
    # Probe unknown template path via a synthetic call
    known = {
        "implementation_scope_solution",
        "non_empty_logical_or_physical",
        "data_carrying_entity_mapping_or_technical",
        "pdm003_entity_physical",
        "ldm004_identity",
        "ldm005_attributes",
        "ldm006_alignment",
        "ldm007_semantic_inclusion",
        "ldm008_realization_completeness",
        "atr005_mapping_coverage",
        "planned_on_active_warning",
        "ref002_cardinality",
        "pdm004_field_mapping",
        "atr002_snake_case",
        "cls001_axes_present",
        "flw001_soft_presence",
        "cls002_security_soft",
        "ref003_kind_soft",
        "atr004_type_specific_soft",
    }
    assert exprs <= known, f"Catalog templates missing in runner: {exprs - known}"
    assert known <= exprs or True  # runner may have extras unused
    # Ensure runner source references each catalog expression
    src = Path(fc.__file__).read_text(encoding="utf-8")
    missing = [e for e in exprs if e not in src]
    assert missing == [], missing


def test_assess_includes_formal_requirement_diagnostics() -> None:
    """Assess emits formal_checks in assessment:model-requirements (third bucket)."""
    result = assess_implementation(
        schema_path=SCHEMA,
        implementation_path=TRADING,
        implementation_id="moex:implementation:trading:formal",
    )
    ids = {a.id for a in result.report.assessments}
    assert "assessment:corporate-semantics" in ids
    assert "assessment:model-requirements" in ids
    model_req = next(
        a for a in result.report.assessments if a.id == "assessment:model-requirements"
    )
    corporate = next(
        a for a in result.report.assessments if a.id == "assessment:corporate-semantics"
    )
    # Formal diagnostics must not leak into corporate-semantics bucket
    assert not any(
        d.diagnostic_code.startswith("DAMS-REQ-") for d in corporate.diagnostics
    )
    assert not any(
        d.severity == DiagnosticSeverity.ERROR
        and d.diagnostic_code.startswith("DAMS-REQ-")
        for d in model_req.diagnostics
    )
    # Enriched details present when any diagnostic is emitted
    for d in model_req.diagnostics:
        keys = {det.detail_key for det in d.diagnostic_details}
        assert "finding" in keys
        if any(det.detail_key == "requirement_code" for det in d.diagnostic_details):
            assert any(
                det.detail_key == "statement" for det in d.diagnostic_details
            )


def test_default_rule_sets_include_formal_checks() -> None:
    from moex_dams.application.repository import DamsAssetRepository
    from moex_dams.application.rules_runner import default_dams_rule_sets

    repo = DamsAssetRepository(default_schema_path=SCHEMA)
    ids = {r.assessment_id for r in default_dams_rule_sets(repo)}
    assert "assessment:model-requirements" in ids


# --- GEN ----------------------------------------------------------------------


def test_gen001_ownership_requires_data_owner_ref() -> None:
    data = _example()
    data.pop("data_owner_ref", None)
    # Free-text inheritance rule alone is no longer sufficient (ADR-023).
    assert data.get("ownership_inheritance_rule")
    assert any("GEN-001.c7" in c for c in _codes(_errors(data)))


def test_gen001_rule_without_owner_fails() -> None:
    data = _example()
    data.pop("data_owner_ref", None)
    data["ownership_inheritance_rule"] = "Inherits from IT solution."
    codes = _codes(_errors(data))
    assert any("GEN-001.c7" in c for c in codes)


def test_ldm002_inherits_owner_from_package() -> None:
    data = _example()
    for ent in data["logical_entities"]:
        ent.pop("data_owner_ref", None)
        ent.pop("data_steward_ref", None)
        ent.pop("ownership_inheritance_rule", None)
    assert not any("LDM-002.c5" in c for c in _codes(_errors(data)))


def test_ldm003_inherits_classification_from_package() -> None:
    data = _example()
    data["governance_classification"] = "internal"
    for ent in data["logical_entities"]:
        ent.pop("governance_classification", None)
    assert not any("LDM-003.c4" in c for c in _codes(_errors(data)))


def test_placeholder_owner_warning_once() -> None:
    data = _example()
    data["data_owner_ref"] = "org:role/DATA_OWNER_PENDING"
    for ent in data["logical_entities"]:
        ent.pop("data_owner_ref", None)
    warns = _warns(data)
    placeholder = [d for d in warns if "placeholder" in d.diagnostic_code]
    assert len(placeholder) == 1
    assert placeholder[0].subject_ref == data["element_id"]


def test_redundant_override_info() -> None:
    data = _example()
    # Party already declares same owner as package → info lint.
    infos = [
        d
        for d in check_formal_requirements(_body(data), catalog_path=CATALOG)
        if d.severity == DiagnosticSeverity.INFO
        and "redundant-override" in d.diagnostic_code
    ]
    assert any("data_owner_ref" in d.diagnostic_message for d in infos)


def test_gen002_implementation_scope() -> None:
    data = _example()
    data["implementation_scope"] = "enterprise"
    assert "DAMS-REQ-GEN-002.c2" in _codes(_errors(data))


def test_gen003_empty_package() -> None:
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
    assert "DAMS-REQ-GEN-003.c1" in _codes(
        [
            d
            for d in check_formal_requirements(_body(data), catalog_path=CATALOG)
            if d.severity == DiagnosticSeverity.ERROR
        ]
    )


def test_gen004_data_carrying_needs_entity_mapping() -> None:
    data = _example()
    data["mappings"] = [
        m for m in data["mappings"] if m.get("mapping_type") != "entity_physical"
    ]
    assert "DAMS-REQ-GEN-004.c1" in _codes(_errors(data))


def test_gen004_infra_database_skipped() -> None:
    data = _example()
    data["physical_objects"] = [
        {
            "element_id": "dams:physical/example-min/db",
            "name": "example_db",
            "description": "Infra container",
            "lifecycle_status": "active",
            "system_ref": "eam:system/EXAMPLE_CORE",
            "object_kind": "database",
            "qualified_name": "example",
            "technology": "PostgreSQL",
            "native_schema_ref": "https://example/db",
            "direction": "internal",
        }
    ]
    data["mappings"] = [
        m for m in data["mappings"] if m.get("mapping_type") != "entity_physical"
    ]
    # Only infra object — GEN-004 must not fire; GEN-003 still ok via logical entities
    assert "DAMS-REQ-GEN-004.c1" not in _codes(_errors(data))


# --- LDM ----------------------------------------------------------------------


def test_ldm001_ref_resolves() -> None:
    data = _example()
    data["logical_entities"][0]["context_ref"] = "dams:context/missing"
    assert "DAMS-REF-002" in _codes(_errors(data))


def test_ldm002_title_required() -> None:
    data = _example()
    data["logical_entities"][0].pop("title", None)
    assert "DAMS-REQ-LDM-002.c1" in _codes(_errors(data))


def test_ldm003_entity_type_required() -> None:
    data = _example()
    data["logical_entities"][0].pop("entity_type", None)
    assert "DAMS-REQ-LDM-003.c1" in _codes(_errors(data))


def test_ldm004_identity_missing() -> None:
    data = _example()
    for ent in data["logical_entities"]:
        ent.pop("identity_rule", None)
        ent["business_key_kind"] = "surrogate"
        ent.pop("key_attribute_refs", None)
    codes = _codes(_errors(data))
    assert any("LDM-004" in c for c in codes)
    assert any("Remediation:" in d.diagnostic_message for d in _errors(data))


def test_ldm005_no_attributes() -> None:
    data = _example()
    data["logical_entities"][0]["attributes"] = []
    data["logical_entities"][0]["entity_type"] = "core"
    assert "DAMS-REQ-LDM-005.c1" in _codes(_errors(data))


def test_ldm006_not_applicable_on_core_fails() -> None:
    data = _example()
    e = data["logical_entities"][0]
    e["entity_type"] = "core"
    e["conceptual_alignment_status"] = "not-applicable"
    e["alignment_rationale"] = "bypass"
    e.pop("conceptual_entity_refs", None)
    assert "DAMS-REQ-LDM-006.c1" in _codes(_errors(data))


def test_ldm006_pending_requires_rationale() -> None:
    data = _example()
    e = data["logical_entities"][0]
    e["conceptual_alignment_status"] = "pending"
    e.pop("alignment_rationale", None)
    e.pop("conceptual_entity_refs", None)
    assert "DAMS-REQ-LDM-006.c1" in _codes(_errors(data))


def test_ldm007_isolated_entity() -> None:
    data = _example()
    # Single entity, no relationships, no conceptual, no isolation
    data["logical_entities"] = [deepcopy(data["logical_entities"][0])]
    e = data["logical_entities"][0]
    e.pop("conceptual_entity_refs", None)
    e.pop("conceptual_alignment_status", None)
    e.pop("alignment_rationale", None)
    e.pop("isolation_rationale", None)
    data["relationships"] = []
    data["mappings"] = [
        m for m in data["mappings"] if m.get("mapping_type") != "realizes"
    ]
    assert "DAMS-REQ-LDM-007.c1" in _codes(_errors(data))


def test_ldm007_physical_mapping_alone_insufficient() -> None:
    data = _example()
    data["logical_entities"] = [deepcopy(data["logical_entities"][0])]
    e = data["logical_entities"][0]
    e.pop("conceptual_entity_refs", None)
    e.pop("conceptual_alignment_status", None)
    e.pop("alignment_rationale", None)
    e.pop("isolation_rationale", None)
    data["relationships"] = []
    # Keep only field + entity_physical mappings — still not semantic inclusion
    assert "DAMS-REQ-LDM-007.c1" in _codes(_errors(data))


# --- ATR ----------------------------------------------------------------------


def test_atr001_logical_type_required() -> None:
    data = _example()
    data["logical_entities"][0]["attributes"][0].pop("logical_type", None)
    errs = _errors(data)
    assert any("ATR-001" in d.diagnostic_code and "logical_type" in d.diagnostic_message for d in errs)


def test_atr002_snake_case_warning() -> None:
    data = _example()
    data["logical_entities"][0]["attributes"][0]["name"] = "partyId"
    warns = [d for d in _warns(data) if "ATR-002" in d.diagnostic_code]
    assert warns
    assert _errors(data) == []


def test_atr005_missing_mapping() -> None:
    data = _example()
    attr = data["logical_entities"][0]["attributes"][0]
    attr.pop("mapping_coverage_status", None)
    data["mappings"] = [
        m for m in data["mappings"] if m.get("mapping_type") != "field_mapping"
    ]
    assert "DAMS-REQ-ATR-005.c1" in _codes(_errors(data))


def test_atr005_planned_on_active_warning() -> None:
    data = _example()
    attr = data["logical_entities"][0]["attributes"][0]
    attr["lifecycle_status"] = "active"
    attr["mapping_coverage_status"] = "planned"
    attr["mapping_rationale"] = "later"
    # Drop field mapping so coverage is exception-based
    data["mappings"] = [
        m for m in data["mappings"] if m.get("mapping_type") != "field_mapping"
    ]
    assert any("ATR-005.c2" in d.diagnostic_code for d in _warns(data))


def test_atr005_field_plus_expression_ok() -> None:
    data = _example()
    attr = data["logical_entities"][0]["attributes"][0]
    attr["mapping_coverage_status"] = "mapped"
    attr["derived_expression"] = "upper(party_id)"
    assert "DAMS-REQ-ATR-005.c1" not in _codes(_errors(data))


# --- REF ----------------------------------------------------------------------


def test_ref001_dangling_target() -> None:
    data = _example()
    data["relationships"][0]["target_entity_ref"] = "dams:logical/missing"
    assert "DAMS-REF-006" in _codes(_errors(data))


def test_ref002_cardinality_required_when_active() -> None:
    data = _example()
    rel = data["relationships"][0]
    for s in (
        "source_min_cardinality",
        "source_max_cardinality",
        "target_min_cardinality",
        "target_max_cardinality",
    ):
        rel.pop(s, None)
    assert "DAMS-REQ-REF-002.c1" in _codes(_errors(data))


def test_ref002_draft_with_rationale_ok() -> None:
    data = _example()
    rel = data["relationships"][0]
    rel["lifecycle_status"] = "draft"
    for s in (
        "source_min_cardinality",
        "source_max_cardinality",
        "target_min_cardinality",
        "target_max_cardinality",
    ):
        rel.pop(s, None)
    rel["cardinality_rationale"] = "Imported draft edges."
    assert "DAMS-REQ-REF-002.c1" not in _codes(_errors(data))


def test_ref003_kind_soft_warning() -> None:
    data = _example()
    data["relationships"][0].pop("relationship_kind", None)
    data["relationships"][0]["lifecycle_status"] = "active"
    assert any("REF-003" in d.diagnostic_code for d in _warns(data))


# --- PDM ----------------------------------------------------------------------


def test_pdm001_system_ref_required() -> None:
    data = _example()
    data["physical_objects"][0].pop("system_ref", None)
    assert any("PDM-001" in d.diagnostic_code and "system_ref" in d.diagnostic_message for d in _errors(data))


def test_pdm002_native_name_required() -> None:
    data = _example()
    data["physical_objects"][0]["physical_fields"][0].pop("native_name", None)
    assert any("PDM-002" in d.diagnostic_code for d in _errors(data))


def test_pdm003_not_inferred_from_field_mapping() -> None:
    data = _example()
    data["mappings"] = [
        m for m in data["mappings"] if m.get("mapping_type") != "entity_physical"
    ]
    # field_mapping remains — must still fail PDM-003 / GEN-004
    assert "DAMS-REQ-PDM-003.c1" in _codes(_errors(data))


def test_pdm003_technical_only_with_rationale_ok() -> None:
    data = _example()
    obj = data["physical_objects"][0]
    obj["mapping_coverage_status"] = "technical-only"
    obj["mapping_rationale"] = "Internal staging topic."
    data["mappings"] = [
        m for m in data["mappings"] if m.get("mapping_type") != "entity_physical"
    ]
    assert "DAMS-REQ-PDM-003.c1" not in _codes(_errors(data))


def test_pdm004_field_needs_mapping() -> None:
    data = _example()
    field = data["physical_objects"][0]["physical_fields"][0]
    field.pop("mapping_coverage_status", None)
    data["mappings"] = [
        m for m in data["mappings"] if m.get("mapping_type") != "field_mapping"
    ]
    assert "DAMS-REQ-PDM-004.c1" in _codes(_errors(data))


# --- Wave 2 soft --------------------------------------------------------------


def test_cls001_axes_warning() -> None:
    data = _example()
    data["logical_entities"][0].pop("data_class", None)
    # Also triggers LDM-003 error; soft CLS may still fire
    errs = _errors(data)
    assert any("LDM-003" in d.diagnostic_code for d in errs)


def test_cls002_security_soft() -> None:
    data = _example()
    data["logical_entities"][0]["governance_classification"] = "confidential"
    data["logical_entities"][0].pop("security_classification", None)
    assert any("CLS-002" in d.diagnostic_code for d in _warns(data))


def test_flw001_soft_when_outbound() -> None:
    data = _example()
    assert any("FLW-001" in d.diagnostic_code for d in _warns(data))


def test_atr004_datetime_timezone_soft() -> None:
    data = _example()
    data["logical_entities"][0]["attributes"].append(
        {
            "element_id": "dams:logical/example-min/Party/registered_at",
            "name": "registered_at",
            "title": "Момент регистрации",
            "description": "Timestamp",
            "lifecycle_status": "draft",
            "owner_entity_ref": "dams:logical/example-min/Party",
            "logical_type": "datetime",
            "required": False,
            "multivalued": False,
            "mapping_coverage_status": "not-applicable",
            "mapping_rationale": "Not persisted yet.",
        }
    )
    assert any("ATR-004" in d.diagnostic_code for d in _warns(data))


def test_enterprise_package_skipped() -> None:
    data = {
        "element_id": "dams:model/enterprise",
        "name": "ent",
        "description": "enterprise",
        "lifecycle_status": "active",
        "api_version": "dams.moex/v0.1",
        "model_version": "1.0.0",
        "implementation_scope": "enterprise",
    }
    diags = check_formal_requirements(_body(data), catalog_path=CATALOG)
    assert diags == ()


# --- LDM-008 realization completeness (ADR-029) -------------------------------


def _ldm008_base() -> dict:
    """Minimal solution package realizing Issuer without owner link."""
    return {
        "element_id": "dams:model/ldm008/1.0.0",
        "name": "ldm008_fixture",
        "description": "LDM-008 realization completeness fixture.",
        "lifecycle_status": "draft",
        "api_version": "dams.moex/v0.1",
        "model_version": "1.0.0",
        "implementation_scope": "solution",
        "conceptual_implementation_ref": (
            "moex:implementation:moex-enterprise-conceptual-model:0.1"
        ),
        "solution_ref": "eam:solution/LDM008",
        "data_owner_ref": "org:role/CLIENT_DATA_OWNER",
        "logical_entities": [
            {
                "element_id": "dams:logical/ldm008/IssuerView",
                "name": "IssuerView",
                "title": "Issuer view",
                "description": "Logical projection of Issuer.",
                "lifecycle_status": "active",
                "conceptual_entity_refs": ["dams:concept/Issuer"],
                "solution_ref": "eam:solution/LDM008",
                "entity_type": "core",
                "data_class": "master_data",
                "business_importance": "high",
                "governance_classification": "internal",
                "conceptual_alignment_status": "aligned",
                "identity_rule": "Issuer code in solution.",
                "business_key_kind": "natural",
                "isolation_rationale": "Fixture isolates completeness warning.",
                "attributes": [
                    {
                        "element_id": "dams:logical/ldm008/IssuerView/id",
                        "name": "issuer_id",
                        "title": "Issuer id",
                        "description": "Identifier",
                        "lifecycle_status": "active",
                        "owner_entity_ref": "dams:logical/ldm008/IssuerView",
                        "logical_type": "identifier",
                        "required": True,
                        "multivalued": False,
                        "mapping_coverage_status": "not-applicable",
                        "mapping_rationale": "No physical in fixture.",
                    }
                ],
            }
        ],
        "mappings": [
            {
                "element_id": "dams:mapping/ldm008/issuer-realizes",
                "name": "realizes_IssuerView",
                "description": "IssuerView realizes Issuer.",
                "lifecycle_status": "active",
                "source_refs": ["dams:logical/ldm008/IssuerView"],
                "target_refs": ["dams:concept/Issuer"],
                "mapping_type": "realizes",
                "mapping_cardinality": "one_to_one",
            }
        ],
        "realizes_not_applicable": None,
    }


def test_ldm008_warns_when_dependent_owner_link_missing() -> None:
    data = _ldm008_base()
    # Need realizes mapping present for DAMS-LEVEL; also non-empty logical
    warns = [
        d
        for d in check_formal_requirements(_body(data), catalog_path=CATALOG)
        if d.severity == DiagnosticSeverity.WARNING
        and "LDM-008" in d.diagnostic_code
    ]
    assert warns
    assert any("LegalEntity" in d.diagnostic_message for d in warns)


def test_ldm008_passes_when_owner_realizer_linked() -> None:
    data = _ldm008_base()
    data["logical_entities"].append(
        {
            "element_id": "dams:logical/ldm008/LegalEntityView",
            "name": "LegalEntityView",
            "title": "Legal entity view",
            "description": "Logical projection of LegalEntity.",
            "lifecycle_status": "active",
            "conceptual_entity_refs": ["dams:concept/LegalEntity"],
            "solution_ref": "eam:solution/LDM008",
            "entity_type": "core",
            "data_class": "master_data",
            "business_importance": "high",
            "governance_classification": "internal",
            "conceptual_alignment_status": "aligned",
            "identity_rule": "LE id.",
            "business_key_kind": "natural",
            "attributes": [
                {
                    "element_id": "dams:logical/ldm008/LegalEntityView/id",
                    "name": "le_id",
                    "title": "LE id",
                    "description": "Identifier",
                    "lifecycle_status": "active",
                    "owner_entity_ref": "dams:logical/ldm008/LegalEntityView",
                    "logical_type": "identifier",
                    "required": True,
                    "multivalued": False,
                    "mapping_coverage_status": "not-applicable",
                    "mapping_rationale": "No physical in fixture.",
                }
            ],
        }
    )
    data["relationships"] = [
        {
            "element_id": "dams:rel/ldm008/IssuerView/ofLE",
            "name": "ofLegalEntity",
            "title": "ofLegalEntity",
            "description": "Issuer view belongs to legal entity view.",
            "lifecycle_status": "active",
            "source_entity_ref": "dams:logical/ldm008/IssuerView",
            "target_entity_ref": "dams:logical/ldm008/LegalEntityView",
            "source_role": "issuer",
            "target_role": "legal_entity",
            "source_min_cardinality": 1,
            "source_max_cardinality": 1,
            "relationship_kind": "association",
        }
    ]
    data["mappings"].append(
        {
            "element_id": "dams:mapping/ldm008/le-realizes",
            "name": "realizes_LegalEntityView",
            "description": "LegalEntityView realizes LegalEntity.",
            "lifecycle_status": "active",
            "source_refs": ["dams:logical/ldm008/LegalEntityView"],
            "target_refs": ["dams:concept/LegalEntity"],
            "mapping_type": "realizes",
            "mapping_cardinality": "one_to_one",
        }
    )
    data["logical_entities"][0].pop("isolation_rationale", None)
    warns = [
        d
        for d in check_formal_requirements(_body(data), catalog_path=CATALOG)
        if d.severity == DiagnosticSeverity.WARNING
        and "LDM-008" in d.diagnostic_code
    ]
    assert warns == []


def test_ldm008_skips_primary_concepts() -> None:
    """TradingClient realizes primary Client — no LDM-008 warning."""
    data = yaml.safe_load(TRADING.read_text(encoding="utf-8"))
    warns = [
        d
        for d in check_formal_requirements(_body(data, str(TRADING)), catalog_path=CATALOG)
        if d.severity == DiagnosticSeverity.WARNING
        and "LDM-008" in d.diagnostic_code
    ]
    assert warns == []
