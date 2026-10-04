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
    build_dsp_documentation_sidebar_siblings,
    enrich_dams_explorer_implementations,
    enrich_fibo_explorer_classes,
    enrich_fibo_explorer_implementations,
    group_enterprise_conceptual_impl_nav,
    group_solution_impl_nav,
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


def test_impl_section_nav_children_stamps_level_glyphs() -> None:
    mod = PublicationModule(
        module_id="moex:module:mdm",
        title="MDM",
        sections=[
            PublicationSection(id="conceptual", title="Conceptual", type="entity-table"),
            PublicationSection(id="logical", title="Logical", type="entity-table"),
            PublicationSection(id="logical-erd", title="Logical ER", type="mermaid-diagram"),
            PublicationSection(id="physical", title="Physical", type="entity-table"),
            PublicationSection(id="physical-erd", title="Physical ER", type="mermaid-diagram"),
            PublicationSection(id="overview", title="Overview", type="markdown-doc"),
        ],
    )
    kids = impl_section_nav_children("mdm", mod)
    # Incomplete solution set → flat leaves; glyphs stay on section_refs.
    by_sid = {c.attributes["section_id"]: c.attributes.get("nav_glyph") for c in kids}
    assert by_sid == {
        "conceptual": "cdm",
        "logical": "ldm",
        "logical-erd": "ldm",
        "physical": "pdm",
        "physical-erd": "pdm",
        "overview": None,
    }


def _solution_sections() -> list[PublicationSection]:
    return [
        PublicationSection(id="package", title="Package", type="key-value", kind="overview"),
        PublicationSection(id="conceptual", title="Conceptual entities", type="entity-table"),
        PublicationSection(id="logical", title="Logical entities", type="entity-table"),
        PublicationSection(
            id="logical-erd", title="Logical ER diagram", type="mermaid-diagram"
        ),
        PublicationSection(id="physical", title="Physical objects", type="entity-table"),
        PublicationSection(
            id="physical-erd", title="Physical ER diagram", type="mermaid-diagram"
        ),
        PublicationSection(
            id="slice-summary", title="Vertical slice summary", type="key-value"
        ),
        PublicationSection(id="slice-nodes", title="Slice graph nodes", type="entity-table"),
        PublicationSection(
            id="slice-relations", title="Slice universe relations", type="entity-table"
        ),
        PublicationSection(
            id="model-assessment",
            title="Оценка соответствия требованиям модели",
            type="entity-table",
        ),
    ]


def test_group_solution_impl_nav_nests_five_folders() -> None:
    mod = PublicationModule(
        module_id="moex:module:crm",
        title="CRM",
        sections=_solution_sections(),
    )
    kids = impl_section_nav_children("crm-solution", mod)
    assert [c.id for c in kids] == [
        "implnav:crm-solution:group:overview",
        "implnav:crm-solution:group:conceptual",
        "implnav:crm-solution:group:logical",
        "implnav:crm-solution:group:physical",
        "implnav:crm-solution:group:requirements",
    ]
    overview = kids[0]
    assert overview.attributes.get("kind") == "group"
    assert overview.attributes.get("nav_group") == "overview"
    assert overview.attributes.get("section_root") is None
    assert overview.attributes.get("section_id") is None
    assert [c.attributes["section_id"] for c in overview.children] == [
        "package",
        "slice-summary",
        "slice-relations",
        "slice-nodes",
    ]
    assert kids[1].title == "Концептуальная модель"
    assert kids[1].attributes.get("group_style") == "section_folder"
    assert kids[1].attributes.get("nav_glyph") == "cdm"
    assert [c.attributes["section_id"] for c in kids[1].children] == ["conceptual"]
    assert [c.attributes["section_id"] for c in kids[2].children] == [
        "logical",
        "logical-erd",
    ]
    assert kids[2].attributes.get("nav_glyph") == "ldm"
    assert [c.attributes["section_id"] for c in kids[3].children] == [
        "physical",
        "physical-erd",
    ]
    assert kids[3].attributes.get("nav_glyph") == "pdm"
    assert [c.attributes["section_id"] for c in kids[4].children] == ["model-assessment"]
    assert kids[4].title == "Требования"


def test_group_solution_impl_nav_passthrough_without_required_set() -> None:
    leaves = [
        PublicationItem(
            id="implnav:x:overview",
            title="Overview",
            attributes={
                "kind": "section_ref",
                "section_id": "overview",
                "target_module_id": "moex:module:x",
            },
        ),
        PublicationItem(
            id="implnav:x:classes",
            title="Classes",
            attributes={
                "kind": "section_ref",
                "section_id": "explorer",
                "target_module_id": "moex:module:x",
            },
        ),
    ]
    assert group_solution_impl_nav("x", leaves) is leaves


def _enterprise_conceptual_sections() -> list[PublicationSection]:
    return [
        PublicationSection(id="overview", title="Overview", type="markdown-doc"),
        PublicationSection(id="conformance", title="Conformance", type="key-value"),
        PublicationSection(
            id="conceptual", title="Conceptual entities", type="entity-table"
        ),
        PublicationSection(
            id="conceptual-erd", title="Conceptual diagram", type="mermaid-diagram"
        ),
        PublicationSection(id="glossary", title="Model glossary", type="glossary"),
        PublicationSection(
            id="relation-terms", title="Relation terms", type="entity-table"
        ),
        PublicationSection(
            id="relationships", title="Relationships", type="entity-table"
        ),
        PublicationSection(
            id="vocabularies", title="Controlled vocabularies", type="entity-table"
        ),
        PublicationSection(
            id="alignments", title="External alignments", type="entity-table"
        ),
        PublicationSection(id="source", title="Source artifacts", type="file-list"),
    ]


def test_group_enterprise_conceptual_impl_nav_nests_overview_and_glossary() -> None:
    mod = PublicationModule(
        module_id="moex:module:enterprise-conceptual",
        title="Enterprise conceptual",
        sections=_enterprise_conceptual_sections(),
    )
    kids = impl_section_nav_children("moex-enterprise-conceptual-model", mod)
    assert [c.title for c in kids] == [
        "Overview",
        "Концептуальная модель",
        "Model glossary",
        "Source artifacts",
    ]
    overview = kids[0]
    assert overview.id == "implnav:moex-enterprise-conceptual-model:group:overview"
    assert overview.attributes.get("kind") == "group"
    assert overview.attributes.get("nav_group") == "overview"
    assert [c.title for c in overview.children] == [
        "Overview",
        "Conformance",
        "External alignments",
    ]
    assert [c.attributes["section_id"] for c in overview.children] == [
        "overview",
        "conformance",
        "alignments",
    ]
    cdm = kids[1]
    assert cdm.id == "implnav:moex-enterprise-conceptual-model:group:conceptual"
    assert cdm.attributes.get("nav_glyph") == "cdm"
    assert cdm.attributes.get("nav_group") == "conceptual"
    assert [c.attributes["section_id"] for c in cdm.children] == [
        "conceptual",
        "conceptual-erd",
        "relationships",
    ]
    assert cdm.children[0].attributes.get("nav_glyph") == "cdm"
    assert cdm.children[1].attributes.get("nav_glyph") == "cdm"
    glossary = kids[2]
    assert glossary.id == "implnav:moex-enterprise-conceptual-model:group:glossary"
    assert glossary.attributes.get("kind") == "group"
    assert glossary.attributes.get("nav_group") == "glossary"
    assert glossary.attributes.get("nav_glyph") == "glossary"
    assert [c.title for c in glossary.children] == [
        "Model glossary",
        "Relation terms",
        "Controlled vocabularies",
    ]
    assert [c.attributes["section_id"] for c in glossary.children] == [
        "glossary",
        "relation-terms",
        "vocabularies",
    ]
    assert all(
        c.attributes.get("nav_glyph") == "glossary" for c in glossary.children
    )
    assert_impl_section_nav_coverage(
        PublicationItem(
            id="moex-enterprise-conceptual-model",
            title="Enterprise conceptual",
            attributes={"kind": "implementation_ref", "module_id": mod.module_id},
            children=kids,
        ),
        [mod],
    )


def test_group_enterprise_conceptual_impl_nav_passthrough_without_required_set() -> None:
    leaves = [
        PublicationItem(
            id="implnav:x:overview",
            title="Overview",
            attributes={
                "kind": "section_ref",
                "section_id": "overview",
                "target_module_id": "moex:module:x",
            },
        ),
        PublicationItem(
            id="implnav:x:conformance",
            title="Conformance",
            attributes={
                "kind": "section_ref",
                "section_id": "conformance",
                "target_module_id": "moex:module:x",
            },
        ),
    ]
    assert group_enterprise_conceptual_impl_nav("x", leaves) is leaves


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


def _iter_section_refs(items: list[PublicationItem]):
    for item in items or []:
        if (item.attributes or {}).get("kind") == "section_ref":
            yield item
        yield from _iter_section_refs(item.children or [])


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
    top_ids = [c.id for c in trading.children]
    # No local conceptual section: concepts live in enterprise (ADR-029).
    assert top_ids == [
        "implnav:trading-solution:group:overview",
        "implnav:trading-solution:group:logical",
        "implnav:trading-solution:group:physical",
        "implnav:trading-solution:group:requirements",
        "implnav:trading-solution:group:documentation",
    ]
    leaves = [
        c
        for c in _iter_section_refs(trading.children or [])
    ]
    assert leaves
    assert all(
        c.attributes.get("target_module_id") == "moex:module:trading-solution"
        for c in leaves
    )


def test_repo_dams_crm_solution_nav_folders() -> None:
    modules = compile_modules(REPO, enforce_publication_contract=False)
    catalog = compile_catalog(REPO, modules)
    enrich_dams_explorer_implementations(modules, catalog)
    dams = next(m for m in modules if m.module_id == DAMS_MODULE)
    explorer = next(s for s in dams.sections if s.type == "explorer")
    impls = next(i for i in explorer.items if i.id == "group:implementations")
    crm = _find_item(impls.children or [], "crm-solution")
    assert crm is not None
    assert [c.title for c in crm.children] == [
        "Overview",
        "Концептуальная модель",
        "Логическая модель",
        "Физическая модель",
        "Требования",
    ]
    assert_impl_section_nav_coverage(crm, modules)


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
    ecm = next(c for c in impls.children if c.id == "moex-enterprise-conceptual-model")
    assert [c.title for c in ecm.children] == [
        "Overview",
        "Концептуальная модель",
        "Model glossary",
        "Source artifacts",
    ]
    assert [c.title for c in ecm.children[0].children] == [
        "Overview",
        "Conformance",
        "External alignments",
    ]
    cdm = ecm.children[1]
    assert cdm.attributes.get("nav_glyph") == "cdm"
    assert [c.attributes["section_id"] for c in cdm.children] == [
        "conceptual",
        "conceptual-erd",
        "relationships",
    ]
    glossary = ecm.children[2]
    assert [c.title for c in glossary.children] == [
        "Model glossary",
        "Relation terms",
        "Controlled vocabularies",
    ]
    assert glossary.attributes.get("nav_glyph") == "glossary"
    assert all(
        c.attributes.get("nav_glyph") == "glossary" for c in glossary.children
    )
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


def test_repo_ontology_catalog_documentation_links_dsp_sections() -> None:
    """Sidebar sibling under Ontology Catalog → moex.dsp.classes / moex.dsp.glossary."""
    modules = compile_modules(REPO, enforce_publication_contract=False)
    siblings = build_dsp_documentation_sidebar_siblings(modules)
    assert len(siblings) == 1
    doc = siblings[0]
    assert doc["after_module_id"] == "moex:module:ontology-catalog"
    assert doc["id"] == "sidebar:documentation"
    assert doc["title"] == "Documentation"
    assert doc["attributes"].get("nav_group") == "documentation"
    assert [c["title"] for c in doc["children"]] == [
        "moex.dsp.classes",
        "moex.dsp.glossary",
    ]
    classes, glossary = doc["children"]
    assert classes["id"] == "ontcat:doc:moex.dsp.classes"
    assert classes["attributes"].get("kind") == "section_ref"
    assert classes["attributes"].get("section_id") == "explorer"
    assert classes["attributes"].get("target_module_id") == "moex:module:dsp"
    assert glossary["id"] == "ontcat:doc:moex.dsp.glossary"
    assert glossary["attributes"].get("section_id") == "glossary"
    assert glossary["attributes"].get("target_module_id") == "moex:module:dsp"
    assert glossary["attributes"].get("nav_glyph") == "glossary"
    # Must not nest inside Ontology Catalog explorer
    ontcat = next(m for m in modules if m.module_id == "moex:module:ontology-catalog")
    explorer = next(s for s in ontcat.sections if s.type == "explorer")
    assert not any(
        i.id == "group:ontology-catalog:documentation"
        for i in (explorer.items or [])
    )


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
