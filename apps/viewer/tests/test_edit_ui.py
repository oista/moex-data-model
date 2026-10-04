"""UI contract tests for serve-mode inline edit."""

from __future__ import annotations

from pathlib import Path

from moex_publication_viewer.assets import assemble_css, assemble_js, assert_no_required_cdn
from moex_publication_viewer.build import build


def test_assembled_js_includes_edit_layer():
    js = assemble_js()
    assert "GET /api/capabilities" in js or "/api/capabilities" in js
    assert "Править" in js
    assert "__moexReplacePublicationData" in js


def test_assembled_css_includes_edit_styles():
    css = assemble_css()
    assert ".edit-btn" in css
    assert ".edit-field" in css


def test_static_build_has_no_cdn_and_inlines_edit(tmp_path: Path):
    (tmp_path / "mod").mkdir()
    (tmp_path / "mod" / "data.csv").write_text(
        "id,name,description\n1,Alpha,First\n", encoding="utf-8"
    )
    (tmp_path / "mod" / "publish.yaml").write_text(
        """
module_id: moex:module:tmp-edit-ui
kind: publication_module
title: Tmp Edit UI
sections:
  - id: rows
    title: Rows
    type: entity-table
    source:
      format: csv
      path: data.csv
    columns: [id, name, description]
""",
        encoding="utf-8",
    )
    dist = tmp_path / "out"
    index = build(tmp_path, dist)
    html = index.read_text(encoding="utf-8")
    assert_no_required_cdn(html)
    assert "/api/capabilities" in html
    assert "Править" in html
    # Static file:// has no live server — probe is in JS but harmless
    assert 'id="viewer-js"' in html
