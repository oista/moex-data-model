"""Tests for moex.hierarchy projection (OWL/CDM/LDM graph + YAML artifact)."""

from __future__ import annotations

from pathlib import Path

from moex_publication_viewer.build import (
    build,
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
    build_hierarchy_graph_and_items,
    build_hierarchy_yaml,
)

REPO = Path(__file__).resolve().parents[3]
VIEWER = Path(__file__).resolve().parents[1]


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
    assert "glossary_scope" in text
    assert '"hierarchy"' in text or "hierarchy" in text
    # Vendored elkjs must be inlined, no CDN.
    assert "elk.algorithm" in text or "ELK" in text
    assert "cdn.jsdelivr" not in text.lower()


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
