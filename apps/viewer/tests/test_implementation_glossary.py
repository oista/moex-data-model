"""Aggregated implementations glossary under DAMS Реализации."""

from __future__ import annotations

from pathlib import Path

from moex_publication_viewer.build import (
    compile_catalog,
    compile_modules,
    enrich_dams_explorer_implementations,
    enrich_dams_implementation_glossary,
)
from moex_publication_viewer.models.catalog_models import CatalogNode
from moex_publication_viewer.models.publication_models import (
    PublicationItem,
    PublicationModule,
    PublicationSection,
)
from moex_publication_viewer.normalizers.implementation_glossary import (
    IMPLEMENTATIONS_GLOSSARY_ID,
    IMPLEMENTATIONS_GLOSSARY_NAV_ID,
    DefinitionMode,
    build_implementation_glossary_items,
    build_implementation_glossary_section,
    resolve_definition,
    DefinitionIndex,
)

REPO = Path(__file__).resolve().parents[3]
DAMS_MODULE = "moex:module:dams"


def _mod(
    module_id: str,
    title: str,
    sections: list[PublicationSection],
) -> PublicationModule:
    return PublicationModule(
        module_id=module_id,
        title=title,
        profile="implementation",
        sections=sections,
    )


def _entity_section(
    section_id: str,
    instance_of: str,
    rows: list[dict],
) -> PublicationSection:
    items = []
    for row in rows:
        eid = row["element_id"]
        attrs = {k: v for k, v in row.items() if k not in ("element_id", "title", "description")}
        items.append(
            PublicationItem(
                id=eid,
                title=row.get("title") or row.get("name") or eid,
                description=row.get("description"),
                attributes=attrs,
            )
        )
    return PublicationSection(
        id=section_id,
        title=section_id,
        type="entity-table",
        kind="classes",
        instance_of=instance_of,
        items=items,
    )


def test_resolve_definition_modes():
    idx = DefinitionIndex()
    idx.add(
        "dams:concept/A",
        "ConceptualEntity",
        {
            "element_id": "dams:concept/A",
            "description": "Concept A.",
        },
    )
    own = resolve_definition(
        {"element_id": "x", "description": "Own text."},
        idx,
        level="ConceptualEntity",
    )
    assert own.mode is DefinitionMode.OWN
    assert own.text == "Own text."

    adapted = resolve_definition(
        {
            "element_id": "y",
            "description": "Adapted.",
            "definition_source_ref": "dams:concept/A",
        },
        idx,
        level="ConceptualEntity",
    )
    assert adapted.mode is DefinitionMode.OWN_ADAPTED

    inherited = resolve_definition(
        {
            "element_id": "dams:logical/sol/A",
            "conceptual_entity_refs": ["dams:concept/A"],
        },
        idx,
        level="LogicalEntity",
    )
    assert inherited.mode is DefinitionMode.INHERITED
    assert inherited.text == "Concept A."
    assert inherited.source_element_id == "dams:concept/A"

    unresolved = resolve_definition(
        {"element_id": "z"},
        idx,
        level="ConceptualEntity",
    )
    assert unresolved.mode is DefinitionMode.UNRESOLVED


def test_synthetic_composite_ids_levels_and_redundant_override():
    modules = [
        _mod(
            "moex:module:enterprise-conceptual",
            "Enterprise CDM",
            [
                _entity_section(
                    "conceptual",
                    "ConceptualEntity",
                    [
                        {
                            "element_id": "dams:concept/PERSON",
                            "name": "PERSON",
                            "title": "Физическое лицо",
                            "description": "ФЛ.",
                        }
                    ],
                ),
                _entity_section(
                    "relation-terms",
                    "RelationTerm",
                    [
                        {
                            "element_id": "dams:relterm/owns",
                            "name": "owns",
                            "title": "владеет / принадлежит",
                            "description": "Владение.",
                            "forward_label": "владеет",
                            "inverse_label": "принадлежит",
                        }
                    ],
                ),
            ],
        ),
        _mod(
            "moex:module:mdm-solution",
            "MDM",
            [
                _entity_section(
                    "conceptual",
                    "ConceptualEntity",
                    [
                        {
                            "element_id": "dams:concept/PERSON",
                            "name": "PERSON",
                            "title": "ФЛ (MDM)",
                            "description": "ФЛ.",
                        }
                    ],
                ),
                _entity_section(
                    "logical",
                    "LogicalEntity",
                    [
                        {
                            "element_id": "dams:logical/mdm/PERSON",
                            "name": "PERSON",
                            "title": "ФЛ LDM",
                            "description": "ФЛ.",
                            "conceptual_entity_refs": ["dams:concept/PERSON"],
                        }
                    ],
                ),
            ],
        ),
        _mod(
            "moex:module:ucd-solution",
            "UCD",
            [
                _entity_section(
                    "conceptual",
                    "ConceptualEntity",
                    [
                        {
                            "element_id": "dams:concept/PERSON",
                            "name": "PERSON",
                            "title": "ФЛ (UCD)",
                            "description": "Другое определение ФЛ.",
                        }
                    ],
                ),
            ],
        ),
    ]
    nodes = [
        CatalogNode(
            id="moex-enterprise-conceptual-model",
            role="specification_implementation",
            title="Enterprise CDM",
            conforms_to="moex-dams",
            module_id="moex:module:enterprise-conceptual",
        ),
        CatalogNode(
            id="mdm-solution",
            role="specification_implementation",
            title="MDM",
            conforms_to="moex-dams",
            module_id="moex:module:mdm-solution",
        ),
        CatalogNode(
            id="ucd-solution",
            role="specification_implementation",
            title="UCD",
            conforms_to="moex-dams",
            module_id="moex:module:ucd-solution",
        ),
    ]
    items = build_implementation_glossary_items(modules, nodes)
    ids = {i.id for i in items}
    assert "mdm-solution:dams:concept/PERSON" in ids
    assert "ucd-solution:dams:concept/PERSON" in ids
    assert "moex-enterprise-conceptual-model:dams:concept/PERSON" in ids
    assert "moex-enterprise-conceptual-model:dams:relterm/owns" in ids
    assert "mdm-solution:dams:logical/mdm/PERSON" in ids

    mdm_person = next(i for i in items if i.id == "mdm-solution:dams:concept/PERSON")
    assert mdm_person.attributes["model_level"] == "CDM"
    assert mdm_person.attributes["solution"] == "MDM"
    assert mdm_person.attributes["kind"] == "entity"

    ldm = next(i for i in items if i.id == "mdm-solution:dams:logical/mdm/PERSON")
    assert ldm.attributes["model_level"] == "LDM"
    assert ldm.attributes["definition_mode"] == "own"
    assert ldm.attributes["redundant_override"] is True
    parents = ldm.attributes["taxonomy_parents"]
    assert any(
        p["id"] == "mdm-solution:dams:concept/PERSON" for p in parents
    )

    cdm = next(i for i in items if i.id == "mdm-solution:dams:concept/PERSON")
    children = cdm.attributes["taxonomy_children"]
    assert any(c["id"] == ldm.id for c in children)

    see = cdm.attributes["see_also"]
    see_ids = {e["id"] for e in see}
    assert "ucd-solution:dams:concept/PERSON" in see_ids
    assert "moex-enterprise-conceptual-model:dams:concept/PERSON" in see_ids

    section = build_implementation_glossary_section(modules, nodes)
    assert section is not None
    assert section.id == IMPLEMENTATIONS_GLOSSARY_ID
    assert section.attributes.get("term_cards") is True
    assert "model_level" in section.filterable


def test_repo_implementations_glossary_nav_and_coverage():
    modules = compile_modules(REPO, enforce_publication_contract=False)
    catalog = compile_catalog(REPO, modules)
    enrich_dams_explorer_implementations(modules, catalog)
    enrich_dams_implementation_glossary(modules, catalog)

    dams = next(m for m in modules if m.module_id == DAMS_MODULE)
    gloss = next(
        (s for s in dams.sections if s.id == IMPLEMENTATIONS_GLOSSARY_ID),
        None,
    )
    assert gloss is not None
    assert gloss.type == "glossary"
    assert gloss.attributes.get("term_cards") is True
    assert gloss.items

    ids = {i.id for i in gloss.items}
    assert any(i.startswith("moex-enterprise-conceptual-model:") for i in ids)
    assert any(i.startswith("mdm-solution:") for i in ids)
    assert any(i.startswith("trading-solution:") for i in ids)

    levels = {i.attributes.get("model_level") for i in gloss.items}
    assert "CDM" in levels
    assert "LDM" in levels
    kinds = {i.attributes.get("kind") for i in gloss.items}
    assert "entity" in kinds
    assert "relation-term" in kinds

    explorer = next(s for s in dams.sections if s.type == "explorer")
    impls = next(i for i in explorer.items if i.id == "group:implementations")
    assert impls.children[0].id == IMPLEMENTATIONS_GLOSSARY_NAV_ID
    assert impls.children[0].attributes.get("section_id") == IMPLEMENTATIONS_GLOSSARY_ID
    assert impls.children[0].attributes.get("nav_glyph") == "glossary"
    assert impls.children[1].id == "group:implementations-it-solutions"
