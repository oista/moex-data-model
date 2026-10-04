"""Enterprise conceptual model fixture invariants (ADR-021 / ADR-029)."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_modeling import DiagnosticSeverity
from moex_dams.rules.conceptual_entity import check_conceptual_entities
from moex_dams.rules.relation_terms import check_relation_terms

REPO = Path(__file__).resolve().parents[3]
ENTERPRISE = (
    REPO
    / "model-assets"
    / "implementations"
    / "enterprise"
    / "moex-enterprise-conceptual-model"
    / "0.1"
    / "enterprise-conceptual-model.yaml"
)


def test_trading_participation_is_reified_entity() -> None:
    data = yaml.safe_load(ENTERPRISE.read_text(encoding="utf-8"))
    assert data["implementation_scope"] == "enterprise"
    assert not data.get("physical_objects")
    concepts = {c["name"]: c for c in data["conceptual_entities"]}
    assert "TradingParticipation" in concepts
    assert "LegalEntity" in concepts
    # Not modeled as subclass-only: has own concept id and relationships
    tp = concepts["TradingParticipation"]
    assert tp["element_id"] == "dams:concept/TradingParticipation"
    rels = data["relationships"]
    # ADR-026: single owner link (merged former participant + hasTradingParticipation)
    owner = next(
        r
        for r in rels
        if r["source_entity_ref"] == "dams:concept/TradingParticipation"
        and r["target_entity_ref"] == "dams:concept/LegalEntity"
    )
    assert owner.get("identifying") is True
    assert owner.get("relation_term_ref") == "dams:relterm/hasParticipation"
    # No relationship that treats TradingParticipation as LegalEntity subclass alias
    for r in rels:
        if r["source_entity_ref"] == "dams:concept/TradingParticipation":
            assert r["name"] != "subclassOf"


def test_required_party_concepts_present() -> None:
    data = yaml.safe_load(ENTERPRISE.read_text(encoding="utf-8"))
    names = {c["name"] for c in data["conceptual_entities"]}
    required = {
        "Organization",
        "LegalEntity",
        "CorporateGroup",
        "OrganizationIdentifier",
        "TradingParticipation",
        "TradingVenue",
        "TradingSection",
        "Admission",
        "Agreement",
        "AccountRelationship",
        "RegistrationAction",
        "SupportingDocument",
    }
    assert required <= names


def test_trading_slice_concepts_present() -> None:
    data = yaml.safe_load(ENTERPRISE.read_text(encoding="utf-8"))
    names = {c["name"] for c in data["conceptual_entities"]}
    required = {
        "Person",
        "Client",
        "Issuer",
        "Asset",
        "Instrument",
        "Trade",
        "Order",
        "TradingSystem",
        "TradingMode",
        "SettlementCode",
        "TradingAccount",
        "ClientAccount",
    }
    assert required <= names


def test_client_is_primary_xor_not_depends_on() -> None:
    data = yaml.safe_load(ENTERPRISE.read_text(encoding="utf-8"))
    client = next(c for c in data["conceptual_entities"] if c["name"] == "Client")
    assert client["entity_tier"] == "primary"
    assert not client.get("depends_on_refs")
    assert client["element_id"] == "dams:concept/Client"


def test_issuer_and_participation_not_legal_entity_subclass() -> None:
    data = yaml.safe_load(ENTERPRISE.read_text(encoding="utf-8"))
    concepts = {c["name"]: c for c in data["conceptual_entities"]}
    assert concepts["Issuer"].get("parent_concept_ref") is None
    assert concepts["TradingParticipation"].get("parent_concept_ref") is None
    assert concepts["Issuer"]["entity_tier"] == "dependent"
    assert concepts["Issuer"]["depends_on_refs"] == ["dams:concept/LegalEntity"]
    for r in data["relationships"]:
        assert r.get("name") != "subclassOf"


def test_settlement_code_specializes_account_relationship() -> None:
    data = yaml.safe_load(ENTERPRISE.read_text(encoding="utf-8"))
    sc = next(c for c in data["conceptual_entities"] if c["name"] == "SettlementCode")
    assert sc["parent_concept_ref"] == "dams:concept/AccountRelationship"
    assert sc["depends_on_refs"] == ["dams:concept/TradingParticipation"]


def test_enterprise_cm_checks_clean() -> None:
    data = yaml.safe_load(ENTERPRISE.read_text(encoding="utf-8"))
    diags = check_conceptual_entities(data) + check_relation_terms(data)
    errors = [d for d in diags if d.severity == DiagnosticSeverity.ERROR]
    assert errors == []
