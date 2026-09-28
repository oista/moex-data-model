"""Tests for ADR-016 publication profiles."""

from __future__ import annotations

from moex_publication_viewer.models.publication_models import (
    PublicationItem,
    PublicationModule,
    PublicationSection,
)
from moex_publication_viewer.publication_profiles import get_renderer_mode, profile_spec
from moex_publication_viewer.validators import check_publication_profiles


def test_renderer_mode_classes_by_profile():
    assert get_renderer_mode("classes", "linkml-specification") == "data-structure"
    assert get_renderer_mode("classes", "ontology") == "ontology-list"
    assert get_renderer_mode("taxonomy", "ontology") == "taxonomy"


def test_profile_spec_ontology_forbids_schema_files():
    spec = profile_spec("ontology")
    assert spec is not None
    assert "taxonomy" in spec.required
    assert "schema-files" in spec.forbidden
    assert "taxonomy" in profile_spec("linkml-specification").forbidden


def test_check_publication_profiles_soft_warnings():
    module = PublicationModule(
        module_id="moex:module:demo",
        title="Demo",
        profile="ontology",
        sections=[
            PublicationSection(
                id="overview",
                title="Overview",
                type="markdown-doc",
                kind="overview",
                content="# hi",
            )
        ],
        manifest_path="demo/publish.yaml",
    )
    warnings = check_publication_profiles([module])
    assert any("missing required kinds" in w for w in warnings)
    assert any("taxonomy" in w for w in warnings)


def test_check_ok_when_explorer_roots_cover_kinds():
    module = PublicationModule(
        module_id="moex:module:fibo-like",
        title="F",
        profile="ontology",
        sections=[
            PublicationSection(
                id="overview",
                title="O",
                type="markdown-doc",
                kind="overview",
                content="x",
            ),
            PublicationSection(
                id="explorer",
                title="E",
                type="explorer",
                kind="taxonomy",
                items=[
                    PublicationItem(
                        id="group:taxonomy",
                        title="Taxonomy",
                        attributes={"section_root": "taxonomy"},
                    ),
                    PublicationItem(
                        id="group:glossary",
                        title="Glossary",
                        attributes={"section_root": "glossary"},
                    ),
                ],
            ),
            PublicationSection(
                id="glossary",
                title="G",
                type="glossary",
                kind="glossary",
                items=[PublicationItem(id="t1", title="t")],
            ),
        ],
    )
    warnings = check_publication_profiles([module])
    assert not any("missing required" in w for w in warnings)
