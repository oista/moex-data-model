"""Seamless Spec→Impl nav nest + catalog publication-contract gate."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from moex_publication_viewer.build import (
    assert_impl_section_nav_coverage,
    attach_impl_section_nav_children,
    compile_catalog,
    compile_modules,
    enrich_dams_explorer_implementations,
    enrich_fibo_explorer_classes,
    enrich_fibo_explorer_implementations,
    impl_nav_section_ids,
    impl_section_nav_children,
    module_section_ids,
)
from moex_publication_viewer.catalog_loader import load_architecture_catalog
from moex_publication_viewer.models.catalog_models import ArchitectureCatalog, CatalogNode
from moex_publication_viewer.models.publication_models import (
    PublicationItem,
    PublicationModule,
    PublicationSection,
)
from moex_publication_viewer.validators import (
    ValidationError,
    check_catalog_publication_contract_gate,
)

REPO = Path(__file__).resolve().parents[3]
DAMS_MODULE = "moex:module:dams"
FIBO_PROFILE = "moex:module:fibo-profile"
FIBO_APP = "moex:module:fibo-application"


def test_impl_section_nav_children_includes_explorer_as_section_leaf() -> None:
    mod = PublicationModule(
        module_id="moex:module:demo",
        title="Demo",
        sections=[
            PublicationSection(
                id="explorer", title="Classes", type="explorer", items=[]
            ),
            PublicationSection(
                id="overview", title="Overview", type="markdown-doc", kind="overview"
            ),
            PublicationSection(
                id="conformance",
                title="Conformance",
                type="key-value",
                kind="conformance",
            ),
        ],
    )
    kids = impl_section_nav_children("demo-impl", mod)
    assert [c.id for c in kids] == [
        "implnav:demo-impl:explorer",
        "implnav:demo-impl:overview",
        "implnav:demo-impl:conformance",
    ]
    assert kids[0].title == "Classes"
    assert kids[0].attributes["target_module_id"] == "moex:module:demo"
    assert kids[0].attributes["section_id"] == "explorer"
    assert kids[0].children == []


def test_attach_impl_section_nav_children() -> None:
    modules = [
        PublicationModule(
            module_id="moex:module:x",
            title="X",
            sections=[
                PublicationSection(
                    id="overview", title="Overview", type="markdown-doc"
                )
            ],
        )
    ]
    refs = [
        PublicationItem(
            id="x-impl",
            title="X",
            attributes={"kind": "implementation_ref", "module_id": "moex:module:x"},
        )
    ]
    out = attach_impl_section_nav_children(refs, modules)
    assert len(out[0].children) == 1
    assert out[0].attributes["nav_section_count"] == 1


def test_repo_fibo_impl_nested_under_implementations() -> None:
    modules = compile_modules(REPO, enforce_publication_contract=False)
    catalog = compile_catalog(REPO, modules)
    enrich_fibo_explorer_classes(modules)
    enrich_fibo_explorer_implementations(modules, catalog)
    profile = next(m for m in modules if m.module_id == FIBO_PROFILE)
    explorer = next(s for s in profile.sections if s.type == "explorer")
    impls = next(i for i in explorer.items if i.id == "group:implementations")
    app = next(c for c in impls.children if c.id == "moex-fibo-application")
    assert app.attributes.get("kind") == "implementation_ref"
    assert app.children, "expected build-time section_ref children"
    ids = {c.attributes.get("section_id") for c in app.children}
    assert {"overview", "conformance", "classes", "bindings", "source"} <= ids
    assert all(c.attributes.get("target_module_id") == FIBO_APP for c in app.children)
    # Spec explorer roots remain (no body swap at build layer)
    roots = {i.id for i in explorer.items}
    assert "group:overview" in roots
    assert "group:classes" in roots
    assert "group:schema-files" in roots
    assert "group:implementations" in roots
    assert "group:taxonomy" not in roots


def _find_item(items: list[PublicationItem], item_id: str) -> PublicationItem | None:
    for item in items or []:
        if item.id == item_id:
            return item
        hit = _find_item(item.children or [], item_id)
        if hit is not None:
            return hit
    return None


def _iter_implementation_refs(items: list[PublicationItem]):
    for item in items or []:
        if (item.attributes or {}).get("kind") == "implementation_ref":
            yield item
        yield from _iter_implementation_refs(item.children or [])


def test_repo_dams_trading_has_nested_section_refs() -> None:
    modules = compile_modules(REPO, enforce_publication_contract=False)
    catalog = compile_catalog(REPO, modules)
    enrich_dams_explorer_implementations(modules, catalog)
    dams = next(m for m in modules if m.module_id == DAMS_MODULE)
    explorer = next(s for s in dams.sections if s.type == "explorer")
    impls = next(i for i in explorer.items if i.id == "group:implementations")
    trading = _find_item(impls.children or [], "trading-solution")
    assert trading is not None
    assert trading.children
    assert all(
        c.attributes.get("target_module_id") == "moex:module:trading-solution"
        for c in trading.children
    )


def test_repo_dams_impl_folders_group_solutions_and_projects() -> None:
    modules = compile_modules(REPO, enforce_publication_contract=False)
    catalog = compile_catalog(REPO, modules)
    enrich_dams_explorer_implementations(modules, catalog)
    dams = next(m for m in modules if m.module_id == DAMS_MODULE)
    explorer = next(s for s in dams.sections if s.type == "explorer")
    impls = next(i for i in explorer.items if i.id == "group:implementations")
    top_ids = [c.id for c in impls.children or []]
    assert top_ids[:2] == [
        "group:implementations-it-solutions",
        "group:implementations-projects",
    ]
    assert "moex-dsp" in top_ids
    assert "moex-enterprise-conceptual-model" in top_ids
    it_folder = next(
        c for c in impls.children if c.id == "group:implementations-it-solutions"
    )
    proj_folder = next(
        c for c in impls.children if c.id == "group:implementations-projects"
    )
    assert {c.id for c in it_folder.children} == {
        "mdm-solution",
        "ucd-solution",
        "crm-solution",
        "esed-solution",
    }
    assert "trading-solution" in {c.id for c in proj_folder.children}
    assert "client-accounts-csv-draft" in {c.id for c in proj_folder.children}
    assert it_folder.attributes.get("group_style") == "section_folder"
    assert proj_folder.attributes.get("group_style") == "section_folder"


def test_repo_dams_dsp_includes_classes_explorer_section_ref() -> None:
    """moex.dsp Classes is type=explorer; must still appear under Реализации."""
    modules = compile_modules(REPO, enforce_publication_contract=False)
    catalog = compile_catalog(REPO, modules)
    enrich_dams_explorer_implementations(modules, catalog)
    dams = next(m for m in modules if m.module_id == DAMS_MODULE)
    explorer = next(s for s in dams.sections if s.type == "explorer")
    impls = next(i for i in explorer.items if i.id == "group:implementations")
    dsp = next(c for c in impls.children if c.id == "moex-dsp")
    titles = {c.title for c in dsp.children}
    assert "Overview" in titles
    assert "Classes" in titles
    assert "Glossary" in titles
    classes = next(c for c in dsp.children if c.title == "Classes")
    assert classes.attributes.get("section_id") == "explorer"
    assert classes.attributes.get("target_module_id") == "moex:module:dsp"
    # section leaf only — no class-tree expansion under Impl
    assert classes.children == []


def test_repo_impl_section_nav_covers_all_module_sections() -> None:
    """Golden: every Impl under DAMS/FIBO nests exactly its PublicationSections."""
    modules = compile_modules(REPO, enforce_publication_contract=False)
    catalog = compile_catalog(REPO, modules)
    enrich_dams_explorer_implementations(modules, catalog)
    enrich_fibo_explorer_classes(modules)
    enrich_fibo_explorer_implementations(modules, catalog)

    by_id = {m.module_id: m for m in modules}
    checked = 0
    for host_id in (DAMS_MODULE, FIBO_PROFILE):
        host = by_id.get(host_id)
        if host is None:
            continue
        explorer = next((s for s in host.sections if s.type == "explorer"), None)
        if explorer is None:
            continue
        impls = next(
            (i for i in explorer.items if i.id == "group:implementations"), None
        )
        if impls is None:
            continue
        for ref in _iter_implementation_refs(impls.children or []):
            mid = (ref.attributes or {}).get("module_id")
            if not mid or mid not in by_id:
                continue
            assert_impl_section_nav_coverage(ref, modules)
            assert impl_nav_section_ids(ref) == module_section_ids(by_id[mid])
            checked += 1
    assert checked >= 2, "expected at least DAMS and FIBO Impl nests"


def test_catalog_gate_passes_repo() -> None:
    modules = compile_modules(REPO, enforce_publication_contract=False)
    catalog = load_architecture_catalog(REPO)
    assert catalog is not None
    check_catalog_publication_contract_gate(catalog, modules, REPO)


def test_catalog_gate_fails_without_implements(tmp_path: Path) -> None:
    catalog = ArchitectureCatalog(
        nodes=[
            CatalogNode(
                id="spec-a",
                role="reference_specification",
                title="A",
                version="0.1",
                module_id="moex:module:a",
            ),
            CatalogNode(
                id="impl-a",
                role="specification_implementation",
                title="Impl",
                conforms_to="spec-a",
                module_id="moex:module:impl-a",
            ),
        ]
    )
    # Spec requirements file present
    spec_dir = tmp_path / "model-assets" / "specifications" / "spec-a" / "0.1"
    spec_dir.mkdir(parents=True)
    (spec_dir / "publication-requirements.yaml").write_text(
        yaml.dump(
            {
                "version": "0.1",
                "specification_ref": "spec-a@0.1",
                "profiles": [{"id": "p", "requirements": []}],
            }
        ),
        encoding="utf-8",
    )
    modules = [
        PublicationModule(
            module_id="moex:module:impl-a",
            title="Impl",
            profile="implementation",
            implements=[],
            sections=[],
        )
    ]
    with pytest.raises(ValidationError, match="missing implements"):
        check_catalog_publication_contract_gate(catalog, modules, tmp_path)


def test_catalog_gate_fails_without_requirements_file(tmp_path: Path) -> None:
    catalog = ArchitectureCatalog(
        nodes=[
            CatalogNode(
                id="spec-b",
                role="reference_specification",
                title="B",
                version="0.1",
            ),
            CatalogNode(
                id="impl-b",
                role="specification_implementation",
                title="Impl",
                conforms_to="spec-b",
                module_id="moex:module:impl-b",
            ),
        ]
    )
    modules = [
        PublicationModule(
            module_id="moex:module:impl-b",
            title="Impl",
            profile="implementation",
            implements=[
                {
                    "specification_ref": "spec-b@0.1",
                    "profile_ref": "p",
                }
            ],
            sections=[],
        )
    ]
    with pytest.raises(ValidationError, match="publication-requirements.yaml"):
        check_catalog_publication_contract_gate(catalog, modules, tmp_path)


def test_catalog_gate_exempt_skips_implements() -> None:
    catalog = ArchitectureCatalog(
        nodes=[
            CatalogNode(
                id="spec-c",
                role="reference_specification",
                title="C",
                version="0.1",
            ),
            CatalogNode(
                id="impl-c",
                role="specification_implementation",
                title="Preview",
                conforms_to="spec-c",
                module_id="moex:module:impl-c",
                contract_exempt=True,
            ),
        ]
    )
    modules = [
        PublicationModule(
            module_id="moex:module:impl-c",
            title="Preview",
            profile="implementation",
            implements=[],
            sections=[],
        )
    ]
    # No Spec requirements needed when only exempt Impls
    check_catalog_publication_contract_gate(catalog, modules, Path("."))


def test_viewer_js_drops_body_swap() -> None:
    js = (REPO / "apps" / "viewer" / "static" / "viewer.js").read_text(
        encoding="utf-8"
    )
    assert "never swap to Impl" in js or "seamless nest" in js
    assert "Reveal sections" in js
    assert "Open implementation" not in js
    assert "target_module_id" in js
    # Folder mark for section_folder even without requirement_section code.
    assert "if (isSectionFolder)" in js
    assert "nav-kind-folder" in js
