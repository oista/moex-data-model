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
