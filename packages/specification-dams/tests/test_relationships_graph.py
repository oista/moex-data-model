"""Relationship nodes in DamsModelGraphView."""

from __future__ import annotations

from moex_standard_linkml.domain.body import LinkMLImplementationBody

from moex_dams.domain.graph import EdgeKind, NodeKind
from moex_dams.mappings.dams_to_graph import build_dams_graph, package_index
from moex_dams.application.diff import diff_graphs
from moex_dams.application.element_index import build_element_index


def _body(data: dict) -> LinkMLImplementationBody:
    return LinkMLImplementationBody(
        source_path="memory://test.yaml",
        target_class="ModelPackage",
        data=data,
    )


def test_relationship_nodes_and_edges() -> None:
    data = {
        "element_id": "dams:model/demo",
        "name": "demo",
        "logical_entities": [
            {"element_id": "dams:logical/A", "name": "A"},
            {"element_id": "dams:logical/B", "name": "B"},
        ],
        "relationships": [
            {
                "element_id": "dams:rel/A-B",
                "name": "A_to_B",
                "source_entity_ref": "dams:logical/A",
                "target_entity_ref": "dams:logical/B",
            }
        ],
    }
    graph = build_dams_graph(_body(data))
    rels = graph.nodes_by_kind(NodeKind.RELATIONSHIP)
    assert len(rels) == 1
    assert rels[0].id == "dams:rel/A-B"
    relate = [
        e
        for e in graph.edges
        if e.kind is EdgeKind.RELATES_TO and e.source == "dams:rel/A-B"
    ]
    assert {e.target for e in relate} == {"dams:logical/A", "dams:logical/B"}
    assert "dams:rel/A-B" in package_index(data)
    ids = {e.element_id for e in build_element_index(data)}
    assert "dams:rel/A-B" in ids


def test_diff_add_remove_relationship() -> None:
    left_data = {
        "element_id": "dams:model/demo",
        "name": "demo",
        "logical_entities": [
            {"element_id": "dams:logical/A", "name": "A"},
            {"element_id": "dams:logical/B", "name": "B"},
        ],
        "relationships": [],
    }
    right_data = {
        **left_data,
        "relationships": [
            {
                "element_id": "dams:rel/A-B",
                "name": "A_to_B",
                "source_entity_ref": "dams:logical/A",
                "target_entity_ref": "dams:logical/B",
            }
        ],
    }
    left = build_dams_graph(_body(left_data))
    right = build_dams_graph(_body(right_data))
    report = diff_graphs(
        left,
        right,
        left_index=package_index(left_data),
        right_index=package_index(right_data),
    )
    add_codes = [c.change_code for c in report.changes if c.subject_ref == "dams:rel/A-B"]
    assert "DAMS-DIFF-ADD" in add_codes
