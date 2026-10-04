"""Atlas UX polish contract tests."""

from pathlib import Path

from moex_publication_viewer.assets import assemble_css, assemble_js
from moex_publication_viewer.build import build

VIEWER = Path(__file__).resolve().parents[1]
JS = (VIEWER / "static" / "viewer.js").read_text(encoding="utf-8")


def test_css_neutral_hover_and_no_legacy_blue():
    css = assemble_css()
    assert "#0b5fff" not in css
    assert "--code-key:" in css
    assert ".nav-group-btn:hover, .nav-item-btn:hover, .nav-section-btn:hover { background: var(--surface-3); }" in css
    assert "background: var(--accent-soft)" not in css.split(".nav-group-btn:hover")[1][:80]


def test_js_has_tabs_and_icon_helpers():
    assert "function mountTabs" in JS
    assert 'id: "overview"' in JS
    assert 'id: "attributes"' in JS
    assert 'id: "relations"' in JS
    assert 'id: "source"' in JS
    assert 'id: "members"' in JS
    assert "function displayIcon" in JS
    assert "Extended_Pictographic" in JS
    assert "function setTreeToggle" in JS
    assert "function bindPublicationTreeKeyboard" in JS
    assert "searchFocusTrapHandler" in JS
    assert "shortcutModKey" in JS
    assert "Type to search classes" in JS


def test_js_nav_folds_orphan_sections_and_opens_focused_tables():
    """Impl modules must not bolt secondary strips; focused tables open expanded."""
    assert "function collectNestedSectionIds" in JS
    assert 'id: "group:overview"' in JS or "group:overview" in JS
    assert "Разделы" not in JS
    assert "forceOpen: true" in JS
    subtree = JS.split("function appendPublicationSubtree")[1].split(
        "function appendCatalogNav"
    )[0]
    assert 'className = "nav-secondary"' not in subtree
    assert "opts && opts.forceOpen" in JS


def test_js_explorer_roots_collapse_symmetrically():
    """Overview must not be force-reopened on every render; group clicks match Classes."""
    subtree = JS.split("function appendPublicationSubtree")[1].split(
        "function appendCatalogNav"
    )[0]
    assert 'section_root === "overview" ||' not in subtree
    assert 'section_root === "overview"' not in subtree.split(
        "function openExplorerItem"
    )[1].split("function appendNavClassNode")[0]
    open_item = subtree.split("function openExplorerItem")[1].split(
        "function appendNavClassNode"
    )[0]
    assert 'attrs.kind === "section_ref"' in open_item
    assert "openPublicationSection" in open_item
    assert "openGroups.add(found.group.id)" in open_item


def test_js_nav_implementations_band_class():
    subtree = JS.split("function appendPublicationSubtree")[1].split(
        "function appendCatalogNav"
    )[0]
    assert 'section_root === "implementations"' in subtree
    assert "nav-implementations" in subtree


def test_css_nav_implementations_darker_band():
    css = assemble_css()
    assert ".nav-group.nav-implementations" in css
    assert "color-mix(in srgb, var(--text) 5%, var(--surface-1))" in css


def test_css_active_gray_and_spec_pill_dark():
    css = assemble_css()
    assert "--selection-bg: #eef0f3" in css
    assert "box-shadow: inset 2px 0 0 var(--border-strong)" in css
    assert ".role-pill--spec" in css
    pill = css.split(".role-pill--spec")[1][:200]
    assert "background: var(--brand-active)" in pill
    assert "color: #ffffff" in pill


def test_css_level_glyph_tokens_and_slots():
    css = assemble_css()
    assert "--level-cmd-start:" in css
    assert "--level-ldm-start:" in css
    assert "--level-pdm-start:" in css
    assert ".nav-glyph--cmd" in css
    assert ".nav-glyph--ldm" in css
    assert ".nav-glyph--pdm" in css
    assert ".nav-glyph--menu" in css
    assert ".nav-glyph--card" in css


def test_js_nav_glyph_helpers():
    assert "function resolveNavGlyph" in JS
    assert "function navGlyphHtml" in JS
    assert 'LEVEL_GLYPHS = new Set(["cmd", "ldm", "pdm"])' in JS
    assert 'conceptual: "cmd"' in JS
    assert 'logical: "ldm"' in JS
    assert 'physical: "pdm"' in JS


def test_build_strips_emoji_from_nav_html():
    repo = Path(__file__).resolve().parents[3]
    dist = repo / "apps" / "viewer" / "dist"
    index = build(repo, dist)
    html = index.read_text(encoding="utf-8")
    assert "Data Specification Player" in html
    assert "function mountTabs" in html
    assert 'id="search-shortcut-kbd"' in html
    # Emoji icons from publish.yaml must not appear as module-icon content
    assert "🗺️" not in html or 'module-icon">🗺️' not in html
    # Brand token present
    assert "--brand:" in html
    js = assemble_js()
    assert "bindPublicationTreeKeyboard" in js
