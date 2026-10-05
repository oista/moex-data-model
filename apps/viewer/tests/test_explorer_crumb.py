"""Explorer breadcrumb trails include implementation_ref and all ancestors."""

from __future__ import annotations

from pathlib import Path

from moex_publication_viewer.build import (
    DAMS_MODULE_ID,
    compile_catalog,
    compile_modules,
    enrich_dams_explorer_implementations,
)
from moex_publication_viewer.models.publication_models import PublicationItem
from moex_publication_viewer.nav_crumb import (
    explorer_crumb,
    explorer_crumb_text,
    find_explorer_item_with_ancestors,
)

REPO = Path(__file__).resolve().parents[3]


def _dams_explorer_items() -> tuple[str, list[PublicationItem]]:
    modules = compile_modules(REPO, enforce_publication_contract=False)
    catalog = compile_catalog(REPO, modules)
    enrich_dams_explorer_implementations(modules, catalog)
    dams = next(m for m in modules if m.module_id == DAMS_MODULE_ID)
    explorer = next(s for s in dams.sections if s.type == "explorer")
    return dams.title, explorer.items


def test_explorer_crumb_collapses_duplicate_titles() -> None:
    overview_group = PublicationItem(
        id="group:overview",
        title="Overview",
        attributes={"kind": "group"},
    )
    overview_ref = PublicationItem(
        id="implnav:x:overview",
        title="Overview",
        attributes={"kind": "section_ref"},
    )
    segs = explorer_crumb("moex.dams", [overview_group], overview_ref)
    assert [s.title for s in segs] == ["moex.dams", "Overview"]
    assert segs[0].kind == "module"
    # Collapse keeps the first occurrence (group), drops duplicate section_ref.
    assert segs[1].kind == "group"


def test_explorer_crumb_includes_implementation_ref() -> None:
    ancestors = [
        PublicationItem(
            id="group:implementations",
            title="Реализации",
            attributes={"kind": "group"},
        ),
        PublicationItem(
            id="moex-enterprise-conceptual-model",
            title="moex.concept-data-model",
            attributes={"kind": "implementation_ref"},
        ),
    ]
    item = PublicationItem(
        id="implnav:moex-enterprise-conceptual-model:group:conceptual",
        title="Концептуальная модель",
        attributes={"kind": "group"},
    )
    text = explorer_crumb_text("moex.dams", ancestors, item)
    assert text == (
        "moex.dams / Реализации / moex.concept-data-model / Концептуальная модель"
    )
    kinds = [s.kind for s in explorer_crumb("moex.dams", ancestors, item)]
    assert "implementation_ref" in kinds


def test_repo_cdm_folder_crumb_includes_impl_title() -> None:
    module_title, roots = _dams_explorer_items()
    item_id = "implnav:moex-enterprise-conceptual-model:group:conceptual"
    hit = find_explorer_item_with_ancestors(roots, item_id)
    assert hit is not None
    item, ancestors = hit
    text = explorer_crumb_text(module_title, ancestors, item)
    assert "Реализации" in text
    assert "moex.concept-data-model" in text
    assert "Концептуальная модель" in text
    assert text.startswith(module_title)
    kinds = [s.kind for s in explorer_crumb(module_title, ancestors, item)]
    assert "implementation_ref" in kinds


def test_repo_mdm_logical_crumb_includes_it_solutions_and_impl() -> None:
    module_title, roots = _dams_explorer_items()
    item_id = "implnav:mdm-solution:group:logical"
    hit = find_explorer_item_with_ancestors(roots, item_id)
    assert hit is not None
    item, ancestors = hit
    text = explorer_crumb_text(module_title, ancestors, item)
    assert "Реализации" in text
    assert "ИТ-решения" in text
    assert "Модель данных MDM" in text
    assert "Логическая модель" in text
    kinds = [s.kind for s in explorer_crumb(module_title, ancestors, item)]
    assert "implementation_ref" in kinds


def test_repo_classes_package_crumb_includes_classes_root() -> None:
    module_title, roots = _dams_explorer_items()
    classes = next(r for r in roots if r.id == "group:classes")
    # First package group under Классы (LinkML schema package).
    packages = [
        c for c in (classes.children or []) if (c.attributes or {}).get("kind") == "group"
    ]
    assert packages, "expected package groups under Классы"
    pkg = packages[0]
    classes_leaf = None
    for child in pkg.children or []:
        if (child.attributes or {}).get("kind") == "class":
            classes_leaf = child
            break
        for grand in child.children or []:
            if (grand.attributes or {}).get("kind") == "class":
                classes_leaf = grand
                break
        if classes_leaf:
            break
    assert classes_leaf is not None
    hit = find_explorer_item_with_ancestors(roots, classes_leaf.id)
    assert hit is not None
    item, ancestors = hit
    text = explorer_crumb_text(module_title, ancestors, item)
    assert "Классы" in text
    assert pkg.title in text or any(a.title == pkg.title for a in ancestors)
    assert item.title in text
    assert "implementation_ref" not in [
        s.kind for s in explorer_crumb(module_title, ancestors, item)
    ]


def test_repo_requirements_conceptual_crumb_has_no_implementation_ref() -> None:
    module_title, roots = _dams_explorer_items()
    hit = find_explorer_item_with_ancestors(roots, "group:requirements-conceptual")
    assert hit is not None
    item, ancestors = hit
    segs = explorer_crumb(module_title, ancestors, item)
    assert "implementation_ref" not in [s.kind for s in segs]
    text = " / ".join(s.title for s in segs)
    assert "Требования" in text
    assert "Концептуальная модель" in text
    assert "moex.concept-data-model" not in text
