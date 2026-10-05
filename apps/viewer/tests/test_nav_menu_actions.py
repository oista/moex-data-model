"""Static contracts for every sidebar menu action (expand/collapse/navigate)."""

from __future__ import annotations

from pathlib import Path

from moex_publication_viewer.assets import assemble_css

VIEWER = Path(__file__).resolve().parents[1]
JS = (VIEWER / "static" / "viewer.js").read_text(encoding="utf-8")


def _fn_body(name: str, next_name: str | None = None) -> str:
    start = JS.split(f"function {name}")[1]
    if next_name:
        return start.split(f"function {next_name}")[0]
    return start


def _subtree_focus_block() -> str:
    subtree = JS.split("function appendPublicationSubtree")[1].split(
        "function appendCatalogNav"
    )[0]
    focus = subtree.split("if (focus?.item)")[1].split(
        "function openPublicationSection"
    )[0]
    return focus


def test_focus_restore_does_not_force_open_focused_folder() -> None:
    focus = _subtree_focus_block()
    assert "openGroups.add(focused.item.id)" not in focus
    assert "focused.ancestors" in focus
    assert "openGroups.add(focused.group.id)" in focus
    assert "force-open the item itself" in focus or "do not" in focus.lower()


def test_navigate_to_node_opens_focus_item() -> None:
    body = _fn_body("navigateToNode", "navigateToModule")
    assert "if (f && f.item) openGroups.add(f.item)" in body


def test_apply_route_opens_hash_item_before_show_module() -> None:
    body = _fn_body("applyRoute")
    assert "if (item) openGroups.add(item)" in body
    assert body.index("if (item) openGroups.add(item)") < body.index("showModule")


def test_chevron_toggle_class_node_deletes_and_rerenders() -> None:
    node_fn = JS.split("function appendNavClassNode")[1].split(
        "explorerItems = filterExplorerItemsForPrefs"
    )[0]
    assert "openGroups.delete(node.id)" in node_fn
    assert "openGroups.add(node.id)" in node_fn
    assert "renderModuleNav({" in node_fn
    assert "e.stopPropagation()" in node_fn


def test_chevron_toggle_nav_group_deletes_and_rerenders() -> None:
    subtree = JS.split("function appendPublicationSubtree")[1].split(
        "function appendCatalogNav"
    )[0]
    # Group toggle lives after appendNavClassNode definition
    group_chunk = subtree.split("const gId = group.id")[1].split(
        "// No explorer: sections"
    )[0]
    assert "openGroups.delete(gId)" in group_chunk
    assert "openGroups.add(gId)" in group_chunk
    assert "renderModuleNav({" in group_chunk


def test_symmetric_label_collapse_on_class_and_group() -> None:
    subtree = JS.split("function appendPublicationSubtree")[1].split(
        "function appendCatalogNav"
    )[0]
    assert "node.id === selectedItemId && openGroups.has(node.id)" in subtree
    assert "gId === selectedItemId && openGroups.has(gId)" in subtree
    assert "openExplorerItem(node.id)" in subtree
    assert "openExplorerItem(gId)" in subtree
    # openExplorerItem must not re-add ordinary folders (breaks symmetric collapse)
    open_item = subtree.split("function openExplorerItem")[1].split(
        "function appendNavClassNode"
    )[0]
    assert 'attrs.kind === "implementation_ref"' in open_item
    assert "openGroups.add(itemId)" in open_item
    # Only under implementation_ref branch — not a blanket add for all items
    before_impl = open_item.split('attrs.kind === "implementation_ref"')[0]
    assert "openGroups.add(itemId)" not in before_impl


def test_catalog_spec_toggle_and_label_reclick_collapse() -> None:
    catalog = _fn_body("appendCatalogNav", "renderModuleNav")
    assert "openGroups.delete(cKey)" in catalog
    assert "openGroups.add(cKey)" in catalog
    assert "renderModuleNav({" in catalog
    assert "node.id === currentNodeId" in catalog
    assert "!selectedItemId" in catalog
    assert "navigateToNode(node)" in catalog


def test_sidebar_sibling_toggle_uses_sidebar_keys() -> None:
    sibling = _fn_body("appendSidebarSiblingNav", "appendSidebarSiblingsAfter")
    assert "sidebar:${sibling.id}" in sibling
    assert "openGroups.delete(mKey)" in sibling
    assert "openGroups.add(mKey)" in sibling
    assert "renderModuleNav(focus)" in sibling


def test_css_hidden_rules_actually_hide_nav_children() -> None:
    css = assemble_css()
    for sel in (".nav-group-children[hidden]", ".nav-tree-children[hidden]"):
        assert sel in css
        idx = css.index(sel)
        snippet = css[idx : idx + 80]
        assert "display: none" in snippet


def test_keyboard_expand_collapse_uses_aria_and_tree_toggle() -> None:
    assert "function bindPublicationTreeKeyboard" in JS
    kb = _fn_body("bindPublicationTreeKeyboard", "renderArchitectureCrumb")
    assert "ArrowRight" in kb
    assert "ArrowLeft" in kb
    assert ".tree-toggle:not(.is-leaf)" in kb
    assert "aria-expanded" in kb
    assert "toggle.click()" in kb
