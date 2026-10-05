"""Projection: LogicalEntity × conceptual_entity_refs → link rows."""

from __future__ import annotations

from moex_publication_viewer.normalizers.conceptual_entity_links_projection import (
    project_conceptual_entity_links,
)


def test_empty_package_yields_empty_list():
    assert project_conceptual_entity_links({}) == []
    assert project_conceptual_entity_links(None) == []
    assert project_conceptual_entity_links({"logical_entities": []}) == []


def test_one_entity_two_refs_yields_two_rows():
    data = {
        "logical_entities": [
            {
                "element_id": "dams:logical/crm/CLIENT",
                "name": "CLIENT",
                "title": "Клиент",
                "conceptual_entity_refs": [
                    "dams:concept/CUSTOMER",
                    "dams:concept/Client",
                ],
                "conceptual_alignment_status": "aligned",
                "alignment_rationale": "Local stub + enterprise.",
            }
        ]
    }
    rows = project_conceptual_entity_links(data)
    assert len(rows) == 2
    assert rows[0]["element_id"] == (
        "dams:logical/crm/CLIENT::dams:concept/CUSTOMER"
    )
    assert rows[0]["logical_entity_ref"] == "dams:logical/crm/CLIENT"
    assert rows[0]["logical_name"] == "CLIENT"
    assert rows[0]["logical_title"] == "Клиент"
    assert rows[0]["conceptual_entity_ref"] == "dams:concept/CUSTOMER"
    assert rows[0]["conceptual_alignment_status"] == "aligned"
    assert rows[0]["alignment_rationale"] == "Local stub + enterprise."
    assert rows[1]["conceptual_entity_ref"] == "dams:concept/Client"


def test_local_only_without_refs_yields_zero_rows():
    data = {
        "logical_entities": [
            {
                "element_id": "dams:logical/crm/TMP",
                "name": "TMP",
                "title": "Временная",
                "conceptual_alignment_status": "local-only",
                "alignment_rationale": "Solution-local.",
            }
        ]
    }
    assert project_conceptual_entity_links(data) == []
