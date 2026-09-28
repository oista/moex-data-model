"""Tests for ADR-016 publication profiles and ADR-019 contract coverage."""

from __future__ import annotations

from pathlib import Path

from moex_publication_viewer.models.publication_models import (
    PublicationItem,
    PublicationModule,
    PublicationSection,
)
from moex_publication_viewer.normalizers.linkml_spec_roots import (
    wrap_linkml_specification_roots,
)
from moex_publication_viewer.publication_profiles import get_renderer_mode, profile_spec
from moex_publication_viewer.validators import (
    check_publication_contract_coverage,
    check_publication_profiles,
)


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


def test_implementation_recommends_model_assessment():
    spec = profile_spec("implementation")
    assert spec is not None
    assert "model-assessment" in spec.recommended
    assert "model-assessment" not in spec.required


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


def test_wrap_linkml_specification_roots_nests_packages_under_classes():
    pkg = PublicationItem(
        id="group:moex_dsp",
        title="Dsp",
        attributes={"kind": "group", "class_count": 2, "enum_count": 1},
        children=[PublicationItem(id="NamedElement", title="NamedElement")],
    )
    roots = wrap_linkml_specification_roots([pkg])
    assert [r.id for r in roots] == ["group:overview", "group:classes"]
    assert roots[0].attributes.get("section_root") == "overview"
    assert roots[1].attributes.get("section_root") == "classes"
    assert roots[1].children[0].id == "group:moex_dsp"


def test_publication_contract_coverage_hard_fails_on_missing_satisfies(tmp_path: Path):
    root = tmp_path
    dams = root / "model-assets" / "specifications" / "moex-dams" / "0.1"
    dams.mkdir(parents=True)
    (dams / "publication-requirements.yaml").write_text(
        """
version: "0.1"
profiles:
  - id: demo-profile
    requirements:
      - id: dams:logical-entities
        kind: required-section
        obligation: required
        accepted_section_kinds: [classes]
        accepted_renderers: [entity-table]
      - id: dams:overview
        kind: required-section
        obligation: required
        accepted_section_kinds: [overview]
        accepted_renderers: [markdown-doc]
""",
        encoding="utf-8",
    )
    pub = root / "impl"
    pub.mkdir()
    (pub / "README.md").write_text("# hi\n", encoding="utf-8")
    manifest_path = pub / "publish.yaml"
    import yaml

    manifest_path.write_text(
        yaml.safe_dump(
            {
                "module_id": "moex:module:x",
                "kind": "publication_module",
                "title": "X",
                "profile": "implementation",
                "implements": [
                    {
                        "specification_ref": "moex-dams@0.1",
                        "profile_ref": "demo-profile",
                    }
                ],
                "sections": [
                    {
                        "id": "overview",
                        "title": "O",
                        "kind": "overview",
                        "type": "markdown-doc",
                        "satisfies": ["dams:overview"],
                        "source": {"format": "markdown", "path": "README.md"},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    module = PublicationModule(
        module_id="moex:module:x",
        title="X",
        profile="implementation",
        implements=[
            {
                "specification_ref": "moex-dams@0.1",
                "profile_ref": "demo-profile",
            }
        ],
        sections=[
            PublicationSection(
                id="overview",
                title="O",
                type="markdown-doc",
                kind="overview",
                satisfies=["dams:overview"],
                content="x",
            )
        ],
        manifest_path=str(manifest_path),
    )
    from moex_publication_viewer.validators import ValidationError
    import pytest

    with pytest.raises(ValidationError) as exc:
        check_publication_contract_coverage([module], root)
    assert any("logical-entities" in e for e in exc.value.errors)


def test_publication_contract_ok_when_satisfied(tmp_path: Path):
    root = tmp_path
    dams = root / "model-assets" / "specifications" / "moex-dams" / "0.1"
    dams.mkdir(parents=True)
    (dams / "publication-requirements.yaml").write_text(
        """
version: "0.1"
profiles:
  - id: demo-profile
    requirements:
      - id: dams:logical-entities
        kind: required-section
        obligation: required
        accepted_section_kinds: [classes]
        accepted_renderers: [entity-table]
      - id: dams:declared-binding
        kind: required-binding
        obligation: required
""",
        encoding="utf-8",
    )
    pub = root / "impl"
    pub.mkdir()
    (pub / "model.yaml").write_text("logical_entities: [{element_id: e1}]\n", encoding="utf-8")
    import yaml

    manifest_path = pub / "publish.yaml"
    manifest_path.write_text(
        yaml.safe_dump(
            {
                "module_id": "moex:module:x",
                "kind": "publication_module",
                "title": "X",
                "implements": [
                    {
                        "specification_ref": "moex-dams@0.1",
                        "profile_ref": "demo-profile",
                    }
                ],
                "sections": [
                    {
                        "id": "logical",
                        "title": "L",
                        "kind": "classes",
                        "type": "entity-table",
                        "satisfies": ["dams:logical-entities"],
                        "source": {
                            "format": "yaml",
                            "path": "model.yaml",
                            "select": "logical_entities",
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    module = PublicationModule(
        module_id="moex:module:x",
        title="X",
        implements=[
            {"specification_ref": "moex-dams@0.1", "profile_ref": "demo-profile"}
        ],
        sections=[
            PublicationSection(
                id="logical",
                title="L",
                type="entity-table",
                kind="classes",
                satisfies=["dams:logical-entities"],
            )
        ],
        manifest_path=str(manifest_path),
    )
    assert check_publication_contract_coverage([module], root) == []
