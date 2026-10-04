"""Overview Glossary definition-site tree (ADR-024/027)."""

from __future__ import annotations

from pathlib import Path

from moex_publication_viewer.build import (
    compile_modules,
    enrich_fibo_explorer_classes,
    enrich_linkml_glossary_sections,
)
from moex_publication_viewer.normalizers.linkml_normalizer import get_schema_view
from moex_publication_viewer.normalizers.spec_glossary_tree import (
    OVERVIEW_GLOSSARY_ID,
    build_linkml_glossary_leaves,
    build_linkml_glossary_tree,
    build_ontology_glossary_tree,
    collect_glossary_leaf_canonical_ids,
    make_overview_glossary_folder,
)
from moex_publication_viewer.models.publication_models import PublicationItem

REPO = Path(__file__).resolve().parents[3]
FIBO_PROFILE = "moex:module:fibo-profile"
DAMS = "moex:module:dams"


def _class_ids(nodes: list[PublicationItem]) -> set[str]:
    ids: set[str] = set()
    for node in nodes:
        kind = (node.attributes or {}).get("kind") or "class"
        if kind == "class":
            ids.add(node.id)
        ids |= _class_ids(list(node.children or []))
    return ids


def test_linkml_glossary_tree_has_origin_chain_and_no_related_field():
    schema = (
        REPO
        / "model-assets"
        / "specifications"
        / "moex-dams"
        / "0.1"
        / "schemas"
        / "moex-dams.yaml"
    )
    sv = get_schema_view(schema)
    folders = build_linkml_glossary_tree(sv, spec_dir=schema.parent.parent)
    assert folders
    assert all(
        (f.attributes or {}).get("group_style") == "section_folder" for f in folders
    )
    leaves = build_linkml_glossary_leaves(sv, spec_dir=schema.parent.parent)
    assert leaves
    logical = next(L for L in leaves if L.attributes.get("name") == "LogicalEntity")
    attrs = logical.attributes or {}
    assert attrs.get("kind") == "class"
    assert attrs.get("origin") in ("own", "imported")
    assert "genesis_kind" not in attrs
    assert "related" not in attrs
    assert "related_terms" not in attrs
    assert attrs.get("defined_in") == attrs.get("schema_key")
    assert isinstance(attrs.get("is_a_chain"), list)
    parents = attrs.get("taxonomy_parents") or []
    parent_ids = {p["id"] for p in parents}
    # mixins stay in taxonomy, not see_also
    for m in attrs.get("mixins") or []:
        assert m in parent_ids
        assert m not in {e["id"] for e in (attrs.get("see_also") or [])}
    for entry in attrs.get("see_also") or []:
        assert entry["id"] not in parent_ids


def test_overview_glossary_folder_contains_az_and_sites():
    folder = make_overview_glossary_folder(
        [
            PublicationItem(
                id="group:glossary-site:demo",
                title="demo",
                attributes={"kind": "group", "group_style": "section_folder"},
                children=[],
            )
        ]
    )
    assert folder.id == OVERVIEW_GLOSSARY_ID
    assert folder.children[0].attributes.get("section_id") == "glossary"
    assert folder.children[0].title == "A–Z"
    assert folder.children[1].id == "group:glossary-site:demo"


def test_ontology_glossary_tree_see_also_empty_and_not_subclass_nested():
    items = [
        PublicationItem(
            id="Parent",
            title="Parent",
            attributes={
                "kind": "class",
                "source_domain": "FND",
                "module_path": "FND/A.rdf",
                "parent_local_name": "",
            },
        ),
        PublicationItem(
            id="Child",
            title="Child",
            attributes={
                "kind": "class",
                "source_domain": "FND",
                "module_path": "FND/A.rdf",
                "parent_local_name": "Parent",
            },
        ),
    ]
    folders = build_ontology_glossary_tree(items)
    assert len(folders) == 1
    # domain → module folder → leaves (flat siblings, not Parent>Child tree)
    domain = folders[0]
    module = domain.children[0]
    leaf_ids = {c.id for c in module.children}
    assert leaf_ids == {"glossary:Parent", "glossary:Child"}
    child = next(c for c in module.children if c.id == "glossary:Child")
    assert child.attributes.get("see_also") == []
    assert "related" not in (child.attributes or {})
    assert child.attributes.get("origin") == "own"
    parent_ids = {p["id"] for p in child.attributes.get("taxonomy_parents") or []}
    assert "Parent" in parent_ids


def test_dams_glossary_is_top_level_section_ref():
    modules = compile_modules(REPO, enforce_publication_contract=False)
    enrich_linkml_glossary_sections(modules)
    dams = next(m for m in modules if m.module_id == DAMS)
    explorer = next(s for s in dams.sections if s.type == "explorer")
    overview = next(i for i in explorer.items if i.id == "group:overview")
    assert OVERVIEW_GLOSSARY_ID not in {c.id for c in overview.children}
    classes = next(i for i in explorer.items if i.id == "group:classes")
    gloss_ref = next(i for i in explorer.items if i.id == "section:glossary")
    assert gloss_ref.title == "Глоссарий"
    assert gloss_ref.attributes.get("kind") == "section_ref"
    assert gloss_ref.attributes.get("section_id") == "glossary"
    root_ids = [i.id for i in explorer.items]
    assert root_ids.index(gloss_ref.id) == root_ids.index(classes.id) + 1
    glossary = next(s for s in dams.sections if s.id == "glossary")
    assert glossary.title == "Глоссарий"
    leaf_ids = {i.id for i in glossary.items}
    assert "LogicalEntity" in leaf_ids
    sample = next(i for i in glossary.items if i.id == "LogicalEntity")
    assert (sample.attributes or {}).get("origin")
    assert "related" not in (sample.attributes or {})


def test_fibo_overview_glossary_ids_match_classes_no_top_level_glossary():
    modules = compile_modules(REPO, enforce_publication_contract=False)
    enrich_fibo_explorer_classes(modules)
    profile = next(m for m in modules if m.module_id == FIBO_PROFILE)
    explorer = next(s for s in profile.sections if s.type == "explorer")
    assert "group:glossary" not in {i.id for i in explorer.items}
    overview = next(i for i in explorer.items if i.id == "group:overview")
    gloss = next(c for c in overview.children if c.id == OVERVIEW_GLOSSARY_ID)
    classes_root = next(i for i in explorer.items if i.id == "group:classes")
    class_ids = _class_ids(list(classes_root.children or []))
    overview_ids = collect_glossary_leaf_canonical_ids([gloss])
    glossary = next(s for s in profile.sections if s.id == "glossary")
    glossary_ids = {i.id for i in glossary.items}
    assert class_ids == overview_ids == glossary_ids
    assert len(class_ids) == 50
    for item in glossary.items:
        assert (item.attributes or {}).get("see_also") == []
        assert "related" not in (item.attributes or {})
        assert "genesis_kind" not in (item.attributes or {})
        parent = (item.attributes or {}).get("parent_local_name")
        if parent:
            see_ids = {e["id"] for e in (item.attributes or {}).get("see_also") or []}
            assert parent not in see_ids


def test_viewer_js_has_adr027_blocks_contract():
    js = (REPO / "apps" / "viewer" / "static" / "viewer.js").read_text(encoding="utf-8")
    assert "appendAdr027RelationBlocks" in js
    assert "glossary-adr027-taxonomy" in js
    assert "glossary-adr027-see-also" in js
    assert "renderGlossaryTermDetail" in js
    assert "isGlossaryViewItem" in js
