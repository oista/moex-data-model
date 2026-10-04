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
    assert 'id: "objects"' in JS
    assert 'id: "source"' in JS
    assert 'id: "members"' in JS
    assert "function displayIcon" in JS
    assert "Extended_Pictographic" in JS
    assert "function setTreeToggle" in JS
    assert "function bindPublicationTreeKeyboard" in JS
    assert "searchFocusTrapHandler" in JS
    assert "shortcutModKey" in JS
    assert "Type to search classes" in JS


def test_js_class_card_composition_and_objects():
    assert "function appendExplorerClassChips" in JS
    assert "function appendExplorerCompositionBlock" in JS
    assert "function collectClassAncestors" in JS
    assert "function collectClassDescendants" in JS
    assert "function collectClassInstances" in JS
    assert "function itSolutionModuleIds" in JS
    # Titles passed into appendExplorerCompositionBlock (count appended in helper).
    assert 'appendExplorerCompositionBlock(card, "\u0421\u043e\u0441\u0442\u0430\u0432"' in JS
    assert 'appendExplorerCompositionBlock(card, "\u041d\u0430\u0441\u043b\u0435\u0434\u043d\u0438\u043a\u0438"' in JS
    assert "IT solution: all" in JS
    assert "No instances of this class in compiled publications." in JS
    assert "explorer-chip" in JS
    assert 'label: "Objects"' in JS
    assert "group:implementations-it-solutions" in JS


def test_js_table_links_and_instance_cards():
    assert "function itemHref" in JS
    assert "function ensureLinkIndex" in JS
    assert "function renderInstanceDetail" in JS
    assert "function findDamsClassItem" in JS
    assert "function findExplorerLinkTarget" in JS
    assert 'target = "_blank"' in JS or 'target="_blank"' in JS
    assert "table-item-link" in JS
    assert "content--wide" in JS
    assert "instance_of" in JS


def test_js_glossary_section_tabs_and_term_links():
    assert "function renderGlossary" in JS
    assert "function renderGlossaryOverview" in JS
    assert "function renderGlossaryListTable" in JS
    assert "function renderGlossaryHierarchyTable" in JS
    assert "function resolveGlossaryTermPageTarget" in JS
    assert "function pickGlossaryListColumns" in JS
    assert "function buildGlossaryChildrenIndex" in JS
    assert "function glossaryDefinitionDependents" in JS
    gloss = JS.split("function renderGlossary(mod, section)")[1].split(
        "function renderTree"
    )[0]
    assert "mountTabs" in gloss
    assert 'id: "overview"' in gloss
    assert 'id: "list"' in gloss
    assert 'id: "hierarchy"' in gloss
    assert 'label: "Список"' in gloss
    assert 'label: "Иерархия"' in gloss
    assert 'col === "name" || col === "title"' in JS
    assert 'section.type === "glossary"' in JS
    assert (
        'No hierarchy or definition-override links in this glossary.' in JS
    )


def test_section_payload_includes_instance_of():
    from moex_publication_viewer.models.publication_models import PublicationSection
    from moex_publication_viewer.renderers.html_renderer import section_payload

    sec = PublicationSection(
        id="logical",
        title="Logical",
        type="entity-table",
        instance_of="LogicalEntity",
    )
    payload = section_payload(sec)
    assert payload["instance_of"] == "LogicalEntity"


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
    assert "--level-glossary-start:" in css
    assert ".nav-glyph--cdm" in css
    assert ".nav-glyph--ldm" in css
    assert ".nav-glyph--pdm" in css
    assert ".nav-glyph--menu" in css
    assert ".nav-glyph--card" in css
    assert ".nav-kind-folder--level" in css
    assert ".nav-kind-folder--cdm" in css
    assert ".nav-kind-folder-letter" in css
    level_folder = css.split(
        ".nav-kind.nav-kind-folder.nav-kind-folder--level {"
    )[1][:220]
    assert "var(--level-folder-edge" in level_folder
    folder_letter = css.split(
        ".nav-kind.nav-kind-folder.nav-kind-folder--level .nav-kind-folder-letter {"
    )[1][:200]
    assert "font-size: 9px" in folder_letter
    assert "font-weight: 300" in folder_letter


def test_js_nav_glyph_helpers():
    assert "function resolveNavGlyph" in JS
    assert "function navGlyphHtml" in JS
    assert 'LEVEL_GLYPHS = new Set(["cdm", "ldm", "pdm"])' in JS
    assert 'conceptual: "cdm"' in JS
    assert 'logical: "ldm"' in JS
    assert 'physical: "pdm"' in JS
    assert "nav-kind-folder--level" in JS
    assert "nav-kind-folder-letter" in JS
    assert "function folderShapeSvg" in JS
    assert "function folderMarkHtml" in JS
    assert 'implementation_ref: "M"' in JS
    assert "nav-kind--impl" in JS
    assert 'glossary: "G"' in JS
    assert "nav-kind--glossary" in JS
    assert "function yamlFileSvg" in JS
    assert "function yamlFileMarkHtml" in JS
    assert "nav-kind-yaml" in JS
    assert 'if (g === "source_file") return yamlFileMarkHtml()' in JS
    # Spec explorer top-level section_ref (Глоссарий) omits glyph; impl keeps it.
    assert "omitGlyph: true" in JS
    assert "opts.omitGlyph" in JS


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
    assert ".nav-kind.nav-kind--glossary" in css
    gloss = css.split(".nav-kind.nav-kind--glossary")[1][:280]
    assert "border-radius: 3px" in gloss
    assert "font-weight: 500" in gloss
    assert "color-mix(in srgb, var(--level-glossary-start) 12%, transparent)" in gloss
    assert "var(--level-glossary-start)" in gloss
    assert "border-radius: 50%" not in gloss.split("}")[0]
    assert ".nav-kind.nav-kind-yaml" in css
    yaml_icon = css.split(".nav-kind.nav-kind-yaml {")[1][:220]
    assert "height: 16px" in yaml_icon
    assert "background: transparent" in yaml_icon
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
