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


def test_js_table_links_and_instance_cards():
    assert "function itemHref" in JS
    assert "function ensureLinkIndex" in JS
    assert "function renderInstanceDetail" in JS
    assert "function findDamsClassItem" in JS
    assert 'target = "_blank"' in JS or 'target="_blank"' in JS
    assert "table-item-link" in JS
    assert "content--wide" in JS
    assert "instance_of" in JS


def test_css_tables_adapt_to_width():
    css = assemble_css()
    assert "width: max-content" not in css.split(".data-table")[1].split("}")[0]
    data_table = css.split(".data-table {")[1].split("}")[0]
    assert "width: 100%" in data_table
    assert "max-width: 360px" not in css.split(".data-table th, .data-table td")[1].split("}")[0]
    assert ".content.content--wide" in css
    assert "a.table-item-link" in css


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
    assert ".nav-group.nav-implementations > .nav-group-btn" in css
    impl_btn = css.split(".nav-group.nav-implementations > .nav-group-btn")[1][:80]
    assert "font-weight: 700" in impl_btn


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
    assert "--level-cdm-start:" in css
    assert "--level-ldm-start:" in css
    assert "--level-pdm-start:" in css
    assert "--level-impl-start:" in css
    assert ".nav-glyph--cdm" in css
    assert ".nav-glyph--ldm" in css
    assert ".nav-glyph--pdm" in css
    assert ".nav-glyph--menu" in css
    assert ".nav-glyph--card" in css
    assert ".nav-kind-folder--level" in css
    assert ".nav-kind-folder--cdm" in css
    level_folder = css.split(
        ".nav-kind.nav-kind-folder.nav-kind-folder--level {"
    )[1][:220]
    assert "min-width: 30px" in level_folder
    assert "height: 16px" in level_folder
    folder_glyph = css.split(
        ".nav-kind.nav-kind-folder.nav-kind-folder--level .nav-glyph {"
    )[1][:160]
    assert "font-size: 8px" in folder_glyph
    assert "line-height: 12px" in folder_glyph
    assert "padding: 0 3px" in folder_glyph


def test_js_nav_glyph_helpers():
    assert "function resolveNavGlyph" in JS
    assert "function navGlyphHtml" in JS
    assert 'LEVEL_GLYPHS = new Set(["cdm", "ldm", "pdm"])' in JS
    assert 'conceptual: "cdm"' in JS
    assert 'logical: "ldm"' in JS
    assert 'physical: "pdm"' in JS
    assert "nav-kind-folder--level" in JS
    assert 'implementation_ref: "M"' in JS
    assert "nav-kind--impl" in JS


def test_css_nav_kind_fixed_square_and_section_frame():
    css = assemble_css()
    nav = css.split(".nav-kind {")[1].split(".nav-kind.nav-kind-folder")[0]
    assert "min-width: 16px" in nav
    assert "flex: none" in nav
    assert "height: 16px" in nav
    assert ".nav-kind-section" in css
    assert "filter: saturate(1.18)" in css
    assert ".nav-kind.kind-enum" in css
    assert ".nav-kind.nav-kind--impl" in css
    impl = css.split(".nav-kind.nav-kind--impl")[1][:220]
    assert "border-radius: 50%" in impl
    assert "var(--level-impl-start)" in impl
    assert "var(--level-impl-end)" in impl
    assert ".badge-pill.badge-kind-mixin" in css
    assert ".badge-pill.badge-kind-enum" in css
    assert "text-overflow: ellipsis" in css


def test_js_class_icon_badges_and_section_majority():
    assert "function sectionMajorityRole" in JS
    assert "function sectionMajorityGlyphHtml" in JS
    assert "function isSchemaPackageGroup" in JS
    assert "has mixin" in JS
    assert "badge-kind-mixin" in JS
    assert "badge-kind-enum" in JS
    assert "slice(0, 4)" in JS
    assert 'if (attrs.kind === "enum") return "enum"' in JS
    assert "--class-color-enum" in JS
    assert "nav-kind-section" in JS


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
