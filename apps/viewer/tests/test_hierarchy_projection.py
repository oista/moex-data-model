"""Tests for moex.hierarchy projection (OWL/CDM/LDM graph + YAML artifact)."""

from __future__ import annotations

import json
import re
from pathlib import Path

from moex_publication_viewer.build import (
    build,
    compile_catalog,
    compile_modules,
    enrich_publication_modules,
    group_hierarchy_impl_nav,
    impl_section_nav_children,
)
from moex_publication_viewer.models.catalog_models import CatalogNode
from moex_publication_viewer.models.publication_models import (
    PublicationItem,
    PublicationModule,
    PublicationSection,
)
from moex_publication_viewer.normalizers.hierarchy_projection import (
    HIERARCHY_MODULE_ID,
    HIERARCHY_SECTION_ID,
    build_hierarchy_graph_and_items,
    build_hierarchy_yaml,
)
from moex_publication_viewer.serve import ViewerServeState

REPO = Path(__file__).resolve().parents[3]
VIEWER = Path(__file__).resolve().parents[1]


def _assert_hierarchy_section_enriched(modules: list[PublicationModule]) -> None:
    mod = next(m for m in modules if m.module_id == HIERARCHY_MODULE_ID)
    sec = next(s for s in mod.sections if s.id == HIERARCHY_SECTION_ID)
    attrs = sec.attributes or {}
    assert attrs.get("glossary_scope") == "hierarchy", attrs
    graph = attrs.get("hierarchy_graph") or {}
    assert isinstance(graph.get("nodes"), list) and len(graph["nodes"]) > 0


def test_hierarchy_nav_groups_three_folders():
    leaves = [
        PublicationItem(
            id="implnav:moex-hierarchy:overview",
            title="Overview",
            attributes={"kind": "section_ref", "section_id": "overview"},
        ),
        PublicationItem(
            id="implnav:moex-hierarchy:conformance",
            title="Conformance",
            attributes={"kind": "section_ref", "section_id": "conformance"},
        ),
        PublicationItem(
            id="implnav:moex-hierarchy:entity-hierarchy",
            title="Entity hierarchy",
            attributes={"kind": "section_ref", "section_id": "entity-hierarchy"},
        ),
        PublicationItem(
            id="implnav:moex-hierarchy:artifact-model-body",
            title="Полная модель moex",
            attributes={"kind": "section_ref", "section_id": "artifact-model-body"},
        ),
        PublicationItem(
            id="implnav:moex-hierarchy:artifact-envelope",
            title="Конверт",
            attributes={"kind": "section_ref", "section_id": "artifact-envelope"},
        ),
    ]
    grouped = group_hierarchy_impl_nav("moex-hierarchy", leaves)
    assert [g.title for g in grouped] == ["Overview", "Entity hierarchy", "Артефакты"]
    assert grouped[1].attributes.get("kind") == "section_ref"
    assert grouped[1].attributes.get("section_id") == "entity-hierarchy"
    assert grouped[1].children == []


def test_hierarchy_impl_section_nav_from_module():
    mod = PublicationModule(
        module_id=HIERARCHY_MODULE_ID,
        title="moex.hierarchy",
        sections=[
            PublicationSection(id="overview", title="Overview", type="markdown-doc"),
            PublicationSection(id="conformance", title="Conformance", type="key-value"),
            PublicationSection(
                id="entity-hierarchy", title="Entity hierarchy", type="glossary"
            ),
            PublicationSection(
                id="artifact-model-body", title="Body", type="source-file"
            ),
            PublicationSection(
                id="artifact-envelope", title="Envelope", type="source-file"
            ),
        ],
    )
    kids = impl_section_nav_children("moex-hierarchy", mod)
    assert [c.title for c in kids] == ["Overview", "Entity hierarchy", "Артефакты"]


def test_build_hierarchy_graph_has_owl_and_ldm_links():
    enterprise = PublicationModule(
        module_id="moex:module:enterprise-conceptual",
        title="enterprise",
        sections=[
            PublicationSection(
                id="conceptual",
                title="Conceptual",
                type="entity-table",
                instance_of="ConceptualEntity",
                items=[
                    PublicationItem(
                        id="dams:concept/LegalEntity",
                        title="Юридическое лицо",
                        description="LE",
                        attributes={
                            "name": "LegalEntity",
                            "parent_concept_ref": "dams:concept/Organization",
                            "external_class_refs": [
                                {
                                    "target_ref": (
                                        "https://spec.edmcouncil.org/fibo/ontology/"
                                        "BE/LegalEntities/LegalPersons/LegalPerson"
                                    ),
                                    "match_kind": "close",
                                }
                            ],
                        },
                    ),
                    PublicationItem(
                        id="dams:concept/Organization",
                        title="Организация",
                        description="Org",
                        attributes={"name": "Organization"},
                    ),
                ],
            ),
            PublicationSection(
                id="relationships",
                title="Relationships",
                type="entity-table",
                instance_of="Relationship",
                items=[
                    PublicationItem(
                        id="dams:rel/LegalEntity/memberOf",
                        title="memberOf",
                        attributes={
                            "name": "memberOf",
                            "source_entity_ref": "dams:concept/LegalEntity",
                            "target_entity_ref": "dams:concept/Organization",
                        },
                    )
                ],
            ),
        ],
    )
    mdm = PublicationModule(
        module_id="moex:module:mdm-solution",
        title="MDM",
        sections=[
            PublicationSection(
                id="conceptual",
                title="CDM",
                type="entity-table",
                instance_of="ConceptualEntity",
                items=[
                    PublicationItem(
                        id="dams:concept/ENTERPRISE",
                        title="Юридические лица (ЮЛ)",
                        description="MDM ЮЛ",
                        attributes={"name": "ENTERPRISE"},
                    )
                ],
            ),
            PublicationSection(
                id="logical",
                title="LDM",
                type="entity-table",
                instance_of="LogicalEntity",
                items=[
                    PublicationItem(
                        id="dams:logical/mdm/ENTERPRISE",
                        title="ENTERPRISE",
                        description="logical",
                        attributes={
                            "name": "ENTERPRISE",
                            "conceptual_entity_refs": ["dams:concept/ENTERPRISE"],
                        },
                    )
                ],
            ),
        ],
    )
    nodes = [
        CatalogNode(
            id="moex-enterprise-conceptual-model",
            role="specification_implementation",
            title="enterprise",
            conforms_to="moex-dams",
            module_id="moex:module:enterprise-conceptual",
            order=108,
        ),
        CatalogNode(
            id="mdm-solution",
            role="specification_implementation",
            title="MDM",
            conforms_to="moex-dams",
            module_id="moex:module:mdm-solution",
            order=111,
        ),
    ]
    items, graph = build_hierarchy_graph_and_items([enterprise, mdm], nodes)
    ids = {i.id for i in items}
    assert "moex-enterprise-conceptual-model:dams:concept/LegalEntity" in ids
    assert "mdm-solution:dams:concept/ENTERPRISE" in ids
    assert "mdm-solution:dams:logical/mdm/ENTERPRISE" in ids
    fibo = (
        "https://spec.edmcouncil.org/fibo/ontology/"
        "BE/LegalEntities/LegalPersons/LegalPerson"
    )
    assert fibo in ids
    owl_edges = [
        e
        for e in graph["edges"]
        if e["target"] == fibo or e["source"] == fibo
    ]
    assert owl_edges
    ldm_edges = [
        e
        for e in graph["edges"]
        if e["rel"] == "conceptual_entity_ref"
        and "dams:logical/mdm/ENTERPRISE" in e["source"]
    ]
    assert ldm_edges

    yaml_text = build_hierarchy_yaml([enterprise, mdm], nodes, items)
    assert "attributes:" not in yaml_text
    assert "physical_objects:" not in yaml_text
    assert "dams:concept/LegalEntity" in yaml_text
    assert "dams:logical/mdm/ENTERPRISE" in yaml_text


def test_enrich_hierarchy_on_repo_build_tmp(tmp_path: Path):
    """Full viewer build includes moex.hierarchy with glossary_scope hierarchy."""
    html = build(REPO, dist_dir=tmp_path / "dist")
    assert html.is_file()
    text = html.read_text(encoding="utf-8")
    assert "moex.hierarchy" in text
    # Vendored elkjs must be inlined, no CDN.
    assert "elk.algorithm" in text or "ELK" in text
    assert "cdn.jsdelivr" not in text.lower()
    # Payload invariant: parse publication-data, not substring search.
    m = re.search(
        r'<script id="publication-data" type="application/json">(.*?)</script>',
        text,
        re.DOTALL,
    )
    assert m, "publication-data script missing"
    payload = json.loads(m.group(1))
    mod = next(x for x in payload if x.get("module_id") == HIERARCHY_MODULE_ID)
    sec = next(s for s in mod["sections"] if s.get("id") == HIERARCHY_SECTION_ID)
    assert (sec.get("attributes") or {}).get("glossary_scope") == "hierarchy"
    nodes = ((sec.get("attributes") or {}).get("hierarchy_graph") or {}).get("nodes")
    assert isinstance(nodes, list) and len(nodes) > 0


def test_enrich_publication_modules_sets_hierarchy_scope():
    """Shared enrich pipeline (build=serve) must set hierarchy glossary_scope."""
    modules = compile_modules(
        REPO, enforce_publication_contract=False, dist_dir=REPO / "apps" / "viewer" / "dist"
    )
    catalog = compile_catalog(REPO, modules)
    enrich_publication_modules(modules, catalog)
    _assert_hierarchy_section_enriched(modules)


def test_build_and_serve_share_enrich_publication_modules():
    """build.py and serve.py must call the same enrich_publication_modules."""
    build_py = (
        VIEWER / "src" / "moex_publication_viewer" / "build.py"
    ).read_text(encoding="utf-8")
    serve_py = (
        VIEWER / "src" / "moex_publication_viewer" / "serve.py"
    ).read_text(encoding="utf-8")
    assert "def enrich_publication_modules(" in build_py
    assert "enrich_dams_hierarchy_module(modules" in build_py.split(
        "def enrich_publication_modules"
    )[1].split("def build(")[0]
    assert "enrich_publication_modules(modules" in build_py
    assert "enrich_publication_modules" in serve_py
    assert "enrich_publication_modules(modules" in serve_py
    # Serve must not re-list individual enrich_* calls (drift risk).
    refresh = serve_py.split("def refresh_from_disk")[1].split("def rebuild")[0]
    assert "enrich_dams_hierarchy_module(" not in refresh
    assert "enrich_publication_modules(modules" in refresh


def test_serve_refresh_enriches_hierarchy_module(tmp_path: Path):
    """serve.refresh_from_disk must leave hierarchy section with glossary_scope."""
    state = ViewerServeState(REPO, tmp_path / "dist", port=0)
    state.refresh_from_disk(write_html=False)
    _assert_hierarchy_section_enriched(state.modules)


def test_atlas_hierarchy_tabs_in_js():
    js = (VIEWER / "static" / "viewer.js").read_text(encoding="utf-8")
    assert 'scope === "hierarchy"' in js
    assert 'label: "Визуализация"' in js
    assert "function renderHierarchyVisualization" in js
    assert "function collectHierarchyNeighborhood" in js
    assert "Скачать SVG" in js
    assert "Скачать PNG" in js
    # Default glossary tabs still present for non-hierarchy scope.
    gloss = js.split("function renderGlossary(mod, section)")[1].split(
        "function renderTree"
    )[0]
    assert 'id: "overview"' in gloss
    assert 'id: "list"' in gloss
    assert 'label: "Связи"' in gloss
    assert 'id: "hierarchy-mermaid"' in gloss
    assert 'label: "Mermaid"' in gloss
    assert "function hierarchyNeighborhoodToMermaid" in js
    assert "function renderHierarchyMermaidPane" in js
    gen = js.split("function hierarchyNeighborhoodToMermaid")[1].split(
        "function hierarchyNodeSize"
    )[0]
    assert "flowchart TB" in gen
    assert "subgraph" in gen
    # Nested IT-solution clusters inside OWL/CDM/LDM bands (mirror ELK viz).
    assert "solution_id" in gen
    assert "n.solution" in gen
    assert "sol_" in gen
    assert gen.count("subgraph") >= 2


def test_js_hierarchy_edges_snap_to_leaf_boxes():
    """Hierarchy viz must connect leaf boxes, not ELK compound-port polylines."""
    js = (VIEWER / "static" / "viewer.js").read_text(encoding="utf-8")
    assert "function hierarchyConnectPath" in js
    paint = js.split("function renderHierarchyVisualization")[1].split(
        "function renderGlossary("
    )[0]
    assert "neigh.edges" in paint
    assert "hierarchyConnectPath(" in paint
    # Must not paint from ELK edge sections inside the hierarchy viz.
    assert "elkEdgePoints(" not in paint
