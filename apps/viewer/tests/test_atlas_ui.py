"""Atlas UI contract tests (post-redesign)."""

from pathlib import Path

from moex_publication_viewer.assets import assemble_css, assemble_js, assert_no_required_cdn
from moex_publication_viewer.build import build


def test_assembled_css_has_atlas_tokens():
    css = assemble_css()
    assert "--brand: #d71920" in css or "--brand:#d71920" in css
    assert "--app-bg:" in css
    assert "@media print" in css
    assert ".nav-group-children[hidden]" in css
    assert "display: none" in css
    assert "MOEX UI" in css
    assert "data:font/woff2;base64," in css


def test_build_inlines_assets_and_has_no_cdn(tmp_path: Path):
    (tmp_path / "mod").mkdir()
    (tmp_path / "mod" / "data.csv").write_text(
        "id,name,description\n1,Alpha,First\n", encoding="utf-8"
    )
    (tmp_path / "mod" / "publish.yaml").write_text(
        """
module_id: moex:module:tmp-atlas
kind: publication_module
title: Tmp Atlas
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
    assert "MOEX Model Explorer" in html
    assert 'id="viewer-css"' in html
    assert 'id="viewer-js"' in html
    assert 'href="viewer.css"' not in html
    assert 'src="viewer.js"' not in html
    assert "--brand:" in html
    assert "data:font/woff2;base64," in html
    assert_no_required_cdn(html)
    # Dev copies still written
    assert (dist / "viewer.css").is_file()
    assert (dist / "viewer.js").is_file()
    js = assemble_js()
    assert "openSearchDialog" in js
    assert "renderYamlFold" in js
