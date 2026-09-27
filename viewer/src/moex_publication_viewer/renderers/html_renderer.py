"""Jinja HTML renderer dispatcher."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from moex_publication_viewer.models.publication_models import PublicationModule, PublicationSection

SECTION_TEMPLATES = {
    "entity-table": "section_table.html.j2",
    "enum-table": "section_table.html.j2",
    "glossary": "section_glossary.html.j2",
    "tree": "section_tree.html.j2",
    "markdown-doc": "section_markdown.html.j2",
    "key-value": "section_keyvalue.html.j2",
}


def _item_to_dict(item) -> dict[str, Any]:
    return {
        "id": item.id,
        "title": item.title,
        "description": item.description,
        "attributes": item.attributes,
        "children": [_item_to_dict(c) for c in item.children],
        "tags": item.tags,
        "source_ref": item.source_ref,
    }


def section_payload(section: PublicationSection) -> dict[str, Any]:
    return {
        "id": section.id,
        "title": section.title,
        "description": section.description,
        "type": section.type,
        "columns": section.columns,
        "filterable": section.filterable,
        "groupby": section.groupby,
        "sort_by": section.sort_by,
        "sort_order": section.sort_order,
        "items": [_item_to_dict(i) for i in section.items],
        "content": section.content,
        "tags": section.tags,
        "default_collapsed": section.default_collapsed,
    }


def modules_payload(modules: list[PublicationModule]) -> list[dict[str, Any]]:
    return [
        {
            "module_id": m.module_id,
            "title": m.title,
            "description": m.description,
            "icon": m.icon,
            "version": m.version,
            "order": m.order,
            "sections": [section_payload(s) for s in m.sections],
        }
        for m in modules
    ]


def render_viewer(
    modules: list[PublicationModule],
    search_index: list[dict],
    viewer_root: Path,
) -> str:
    templates_dir = viewer_root / "templates"
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    env.globals["section_template"] = lambda t: SECTION_TEMPLATES.get(t, "section_table.html.j2")

    template = env.get_template("base.html.j2")
    return template.render(
        modules=modules,
        modules_json=json.dumps(modules_payload(modules), ensure_ascii=False),
        search_index_json=json.dumps(search_index, ensure_ascii=False),
        section_templates=SECTION_TEMPLATES,
    )
