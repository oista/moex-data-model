"""ADR-026: ConceptualEntity tier/genesis, RelationTerm, glossary, match_kind."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_dams.rules.conceptual_entity import check_conceptual_entities
from moex_dams.rules.definitions import (
    DefinitionMode,
    ExternalDefinition,
    MappingExternalProvider,
    build_definition_index,
    resolve_definition,
)
from moex_dams.rules.glossary import build_model_glossary
from moex_dams.rules.relation_terms import check_relation_terms, relation_label

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


def _drawio_slice() -> dict:
    """Minimal package inspired by CModel_content04 (not a full import)."""
    return {
        "element_id": "dams:model/enterprise/drawio-slice",
        "name": "drawio_slice",
        "description": "Drawio-inspired conceptual slice for ADR-026 tests.",
        "lifecycle_status": "draft",
        "api_version": "dams.moex/v0.1",
        "model_version": "0.1.0",
        "implementation_scope": "enterprise",
        "conceptual_entities": [
            {
                "element_id": "dams:concept/TradingParticipant",
                "name": "TradingParticipant",
                "title": "Участник торгов",
                "description": "Участник торгов на бирже.",
                "lifecycle_status": "active",
                "entity_tier": "primary",
                "genesis_kind": "native",
            },
            {
                "element_id": "dams:concept/Trade",
                "name": "Trade",
                "title": "Сделка",
                "description": "Сделка ТКС — самостоятельная транзакционная сущность.",
                "lifecycle_status": "active",
                "entity_tier": "primary",
                "genesis_kind": "native",
            },
            {
                "element_id": "dams:concept/Asset",
                "name": "Asset",
                "title": "Актив",
                "description": "Базовый актив.",
                "lifecycle_status": "active",
                "entity_tier": "primary",
                "genesis_kind": "native",
            },
            {
                "element_id": "dams:concept/AssetPool",
                "name": "AssetPool",
                "title": "Пул активов",
                "description": "Пул активов.",
                "lifecycle_status": "active",
                "entity_tier": "primary",
                "genesis_kind": "native",
            },
            {
                "element_id": "dams:concept/AssetPoolMembership",
                "name": "AssetPoolMembership",
                "title": "Состав пулов активов",
                "description": "Ассоциативная сущность состава пула.",
                "lifecycle_status": "active",
                "entity_tier": "dependent",
                "dependency_kind": "associative",
                "depends_on_refs": [
                    "dams:concept/AssetPool",
                    "dams:concept/Asset",
                ],
                "genesis_kind": "native",
            },
        ],
        "relation_terms": [
            {
                "element_id": "dams:relterm/participates",
                "name": "participates",
                "title": "участвует / совершается",
                "description": "Участник участвует в сделке; сделка совершается участником.",
                "lifecycle_status": "active",
                "forward_label": "участвует",
                "forward_label_en": "participates in",
                "inverse_label": "совершается",
                "inverse_label_en": "is performed by",
                "symmetric": False,
            },
            {
                "element_id": "dams:relterm/memberOfPool",
                "name": "memberOfPool",
                "title": "входит в пул / содержит",
                "description": "Актив входит в пул.",
                "lifecycle_status": "active",
                "forward_label": "входит в пул",
                "inverse_label": "содержит",
                "symmetric": False,
            },
        ],
        "relationships": [
            {
                "element_id": "dams:rel/Trade/byParticipant",
                "name": "byParticipant",
                "title": "Trade by participant",
                "description": "Сделка совершается участником (one record; labels from term).",
                "lifecycle_status": "active",
                "source_entity_ref": "dams:concept/Trade",
                "target_entity_ref": "dams:concept/TradingParticipant",
                "source_min_cardinality": 1,
                "source_max_cardinality": 1,
                "target_min_cardinality": 0,
                "target_max_cardinality": 999,
                "relation_term_ref": "dams:relterm/participates",
                "term_direction": "inverse",
            },
            {
                "element_id": "dams:rel/AssetPoolMembership/ofPool",
                "name": "ofPool",
                "lifecycle_status": "active",
                "source_entity_ref": "dams:concept/AssetPoolMembership",
                "target_entity_ref": "dams:concept/AssetPool",
                "source_min_cardinality": 1,
                "source_max_cardinality": 1,
                "identifying": True,
                "relation_term_ref": "dams:relterm/memberOfPool",
                "term_direction": "forward",
            },
            {
                "element_id": "dams:rel/AssetPoolMembership/ofAsset",
                "name": "ofAsset",
                "lifecycle_status": "active",
                "source_entity_ref": "dams:concept/AssetPoolMembership",
                "target_entity_ref": "dams:concept/Asset",
                "source_min_cardinality": 1,
                "source_max_cardinality": 1,
                "identifying": True,
                "relation_term_ref": "dams:relterm/memberOfPool",
                "term_direction": "forward",
            },
        ],
    }


def test_trade_is_primary_despite_fk():
    data = _drawio_slice()
    diags = check_conceptual_entities(data)
    codes = {d.diagnostic_code for d in diags}
    assert "DAMS-CM-TIER-003" not in codes
    trade = next(
        e for e in data["conceptual_entities"] if e["name"] == "Trade"
    )
    assert trade["entity_tier"] == "primary"
    assert not trade.get("depends_on_refs")


def test_asset_pool_membership_associative():
    data = _drawio_slice()
    diags = check_conceptual_entities(data)
    errors = [d for d in diags if d.severity.value == "error"]
    assert errors == [], [d.diagnostic_message for d in errors]
    membership = next(
        e
        for e in data["conceptual_entities"]
        if e["name"] == "AssetPoolMembership"
    )
    assert membership["dependency_kind"] == "associative"
    assert len(membership["depends_on_refs"]) == 2


def test_relation_term_forward_inverse_labels():
    data = _drawio_slice()
    term = data["relation_terms"][0]
    assert relation_label(term, direction="forward") == "участвует"
    assert relation_label(term, direction="inverse") == "совершается"
    diags = check_relation_terms(data)
    errors = [d for d in diags if d.severity.value == "error"]
    assert errors == []


def test_depends_on_cycle_detected():
    data = {
        "implementation_scope": "enterprise",
        "conceptual_entities": [
            {
                "element_id": "dams:concept/A",
                "name": "A",
                "lifecycle_status": "active",
                "entity_tier": "dependent",
                "dependency_kind": "characteristic",
                "depends_on_refs": ["dams:concept/B"],
                "genesis_kind": "native",
            },
            {
                "element_id": "dams:concept/B",
                "name": "B",
                "lifecycle_status": "active",
                "entity_tier": "dependent",
                "dependency_kind": "characteristic",
                "depends_on_refs": ["dams:concept/A"],
                "genesis_kind": "native",
            },
        ],
        "relationships": [
            {
                "element_id": "dams:rel/A/B",
                "source_entity_ref": "dams:concept/A",
                "target_entity_ref": "dams:concept/B",
                "source_min_cardinality": 1,
                "identifying": True,
                "lifecycle_status": "active",
            },
            {
                "element_id": "dams:rel/B/A",
                "source_entity_ref": "dams:concept/B",
                "target_entity_ref": "dams:concept/A",
                "source_min_cardinality": 1,
                "identifying": True,
                "lifecycle_status": "active",
            },
        ],
    }
    diags = check_conceptual_entities(data)
    assert any(d.diagnostic_code == "DAMS-CM-TIER-008" for d in diags)


def test_genesis_external_requires_refs():
    data = {
        "conceptual_entities": [
            {
                "element_id": "dams:concept/X",
                "name": "X",
                "lifecycle_status": "active",
                "entity_tier": "primary",
                "genesis_kind": "external",
            }
        ]
    }
    diags = check_conceptual_entities(data)
    assert any(d.diagnostic_code == "DAMS-CM-GENESIS-001" for d in diags)


def test_genesis_native_forbids_refs():
    data = {
        "conceptual_entities": [
            {
                "element_id": "dams:concept/X",
                "name": "X",
                "lifecycle_status": "active",
                "entity_tier": "primary",
                "genesis_kind": "native",
                "external_class_refs": [
                    {
                        "external_class_ref_id": "dams:extref/X",
                        "target_ref": "fibo:Thing",
                        "match_kind": "close",
                        "source_kind": "ontology",
                    }
                ],
            }
        ]
    }
    diags = check_conceptual_entities(data)
    assert any(d.diagnostic_code == "DAMS-CM-GENESIS-002" for d in diags)


def test_match_kind_exact_allows_inherit():
    entity = {
        "element_id": "dams:concept/FromOnto",
        "name": "FromOnto",
        "lifecycle_status": "active",
        "definition_source_ref": "fibo:LegalPerson",
        "external_class_refs": [
            {
                "external_class_ref_id": "dams:extref/FromOnto",
                "target_ref": "fibo:LegalPerson",
                "match_kind": "exact",
                "source_kind": "ontology",
            }
        ],
    }
    provider = MappingExternalProvider(
        {
            "fibo:LegalPerson": ExternalDefinition(
                id="fibo:LegalPerson",
                text="FIBO Legal Person definition.",
                language="en",
                exact=False,  # provider says non-exact; match_kind overrides
            )
        }
    )
    idx = build_definition_index({"conceptual_entities": [entity]}, providers=(provider,))
    prov = resolve_definition(entity, idx, level="ConceptualEntity")
    assert prov.mode is DefinitionMode.INHERITED
    assert prov.text == "FIBO Legal Person definition."


def test_match_kind_close_blocks_inherit():
    entity = {
        "element_id": "dams:concept/FromOnto",
        "name": "FromOnto",
        "lifecycle_status": "active",
        "definition_source_ref": "fibo:LegalPerson",
        "external_class_refs": [
            {
                "external_class_ref_id": "dams:extref/FromOnto",
                "target_ref": "fibo:LegalPerson",
                "match_kind": "close",
                "source_kind": "ontology",
            }
        ],
    }
    provider = MappingExternalProvider(
        {
            "fibo:LegalPerson": ExternalDefinition(
                id="fibo:LegalPerson",
                text="FIBO Legal Person definition.",
                language="en",
                exact=True,  # provider exact; match_kind=close wins
            )
        }
    )
    idx = build_definition_index({"conceptual_entities": [entity]}, providers=(provider,))
    prov = resolve_definition(entity, idx, level="ConceptualEntity")
    assert prov.mode is DefinitionMode.UNRESOLVED
    assert "exact match" in (prov.diagnostic or "")


def test_glossary_includes_entities_and_relation_terms():
    data = _drawio_slice()
    rows = build_model_glossary(data)
    kinds = {r["kind"] for r in rows}
    assert "entity" in kinds
    assert "relation-term" in kinds
    trade = next(r for r in rows if r["id"] == "dams:concept/Trade")
    assert trade["entity_tier"] == "primary"
    assert trade["definition_mode"] == "own"
    participates = next(
        r for r in rows if r["id"] == "dams:relterm/participates"
    )
    assert participates["forward_label"] == "участвует"
    assert participates["inverse_label"] == "совершается"


def test_enterprise_model_passes_cmd_checks():
    data = yaml.safe_load(ENTERPRISE.read_text(encoding="utf-8"))
    diags = check_conceptual_entities(data) + check_relation_terms(data)
    errors = [d for d in diags if d.severity.value == "error"]
    assert errors == [], [f"{d.diagnostic_code}: {d.diagnostic_message}" for d in errors]
    legal = next(
        e for e in data["conceptual_entities"] if e["name"] == "LegalEntity"
    )
    assert legal["genesis_kind"] == "external"
    assert legal["external_class_refs"][0]["match_kind"] == "close"
    assert data.get("relation_terms")
    # Inverse duplicate TradingParticipation/participant removed
    rel_ids = {r["element_id"] for r in data["relationships"]}
    assert "dams:rel/TradingParticipation/participant" not in rel_ids
    assert "dams:rel/TradingParticipation/ofLegalEntity" in rel_ids


def test_non_symmetric_term_requires_inverse():
    data = {
        "implementation_scope": "enterprise",
        "relation_terms": [
            {
                "element_id": "dams:relterm/bad",
                "name": "bad",
                "lifecycle_status": "active",
                "forward_label": "foo",
                "symmetric": False,
            }
        ],
        "relationships": [],
    }
    diags = check_relation_terms(data)
    assert any(d.diagnostic_code == "DAMS-CM-RELTERM-002" for d in diags)
