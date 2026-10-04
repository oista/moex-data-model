"""ADR-026 model glossary projection (viewer fallback)."""

from __future__ import annotations

from moex_publication_viewer.normalizers.model_glossary_projection import (
    project_model_glossary,
)


def test_project_model_glossary_entities_and_terms():
    data = {
        "conceptual_entities": [
            {
                "element_id": "dams:concept/Trade",
                "name": "Trade",
                "title": "Сделка",
                "description": "Сделка ТКС.",
                "entity_tier": "primary",
                "genesis_kind": "native",
            }
        ],
        "relation_terms": [
            {
                "element_id": "dams:relterm/participates",
                "name": "participates",
                "title": "участвует / совершается",
                "description": "Участие в сделке.",
                "forward_label": "участвует",
                "inverse_label": "совершается",
            }
        ],
    }
    rows = project_model_glossary(data)
    assert len(rows) == 2
    kinds = {r["kind"] for r in rows}
    assert kinds == {"entity", "relation-term"}
    trade = next(r for r in rows if r["id"] == "dams:concept/Trade")
    assert trade["definition_mode"] == "own"
    assert trade["entity_tier"] == "primary"
