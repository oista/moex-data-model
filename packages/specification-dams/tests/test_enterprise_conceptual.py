"""Enterprise conceptual model fixture invariants (ADR-021)."""

from __future__ import annotations

from pathlib import Path

import yaml

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
    participant = next(r for r in rels if r["name"] == "participant")
    assert participant["source_entity_ref"] == "dams:concept/TradingParticipation"
    assert participant["target_entity_ref"] == "dams:concept/LegalEntity"
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
