"""ER diagram wire payload keeps scene/layout and drops bulky SVG."""

from __future__ import annotations

from moex_publication_viewer.models.publication_models import PublicationSection
from moex_publication_viewer.renderers.html_renderer import section_payload


def test_mermaid_payload_drops_svg_when_scene_present():
    sec = PublicationSection(
        id="logical-erd",
        title="Logical ER",
        type="mermaid-diagram",
        content="<svg xmlns='http://www.w3.org/2000/svg'><rect/></svg>",
        attributes={
            "mermaid_source": "erDiagram\n",
            "erd_scene": {"version": 1, "nodes": [], "edges": []},
            "erd_layout": {"version": 1, "nodes": {}, "edges": {}},
        },
    )
    payload = section_payload(sec)
    assert payload["content"] == ""
    assert "mermaid_svg" not in (payload["attributes"] or {})
    assert payload["attributes"]["erd_scene"]["version"] == 1


def test_mermaid_payload_keeps_svg_without_scene():
    sec = PublicationSection(
        id="logical-erd",
        title="Logical ER",
        type="mermaid-diagram",
        content="<svg xmlns='http://www.w3.org/2000/svg'><rect/></svg>",
        attributes={"mermaid_source": "erDiagram\n"},
    )
    payload = section_payload(sec)
    assert payload["content"].startswith("<svg")
