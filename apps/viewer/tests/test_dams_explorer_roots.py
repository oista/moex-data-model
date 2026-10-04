"""Unit tests for DAMS explorer roots helper."""

from __future__ import annotations

from pathlib import Path

from moex_publication_viewer.normalizers.dams_explorer_roots import (
    build_spec_file_items,
    is_dams_specification_dir,
    wrap_dams_explorer_roots,
)
from moex_publication_viewer.models.publication_models import PublicationItem
from moex_publication_viewer.normalizers.minimal_schema_projection import (
    project_required_only_schema,
)
from moex_publication_viewer.normalizers.model_skeleton_projection import (
    project_it_solution_model_skeleton,
)


REPO = Path(__file__).resolve().parents[3]
DAMS_SPEC = REPO / "model-assets" / "specifications" / "moex-dams" / "0.1"


def test_is_dams_specification_dir(tmp_path: Path):
    schemas = tmp_path / "schemas"
    schemas.mkdir()
    schema = schemas / "moex-dams.yaml"
    schema.write_text("id: x\n", encoding="utf-8")
    assert is_dams_specification_dir(schema) is False
    (tmp_path / "specification.yaml").write_text("id: s\n", encoding="utf-8")
    assert is_dams_specification_dir(schema) is True


def test_build_spec_file_items_repo():
    items = build_spec_file_items(DAMS_SPEC)
    ids = {i.id for i in items}
    assert "file:specification.yaml" in ids
    assert "file:schemas/moex-core.yaml" in ids
    assert all(i.attributes.get("kind") == "source_file" for i in items)
    assert all(i.attributes.get("text") for i in items)
    by_file = {i.attributes["file_name"]: i for i in items}
    assert by_file["specification.yaml"].title == "Конверт спецификации"
    assert by_file["moex-core.yaml"].title == "Ядро модели данных"
    assert by_file["moex-dams.yaml"].title == "Корневая схема"
    for item in items:
        name = item.attributes["file_name"]
        assert item.title != name
        desc = item.description or ""
        assert 100 <= len(desc) <= 200, (name, len(desc), desc)


def test_wrap_roots_placeholder_implementations(tmp_path: Path):
    schemas = tmp_path / "schemas"
    schemas.mkdir()
    (tmp_path / "specification.yaml").write_text(
        "version: '0.1'\ndescription: env\nschema_body: schemas/a.yaml\n",
        encoding="utf-8",
    )
    (schemas / "a.yaml").write_text("id: a\nname: a\n", encoding="utf-8")
    pkg = PublicationItem(
        id="group:pkg",
        title="Pkg",
        attributes={"kind": "group", "class_count": 1},
        children=[
            PublicationItem(
                id="C1",
                title="C1",
                attributes={"kind": "class"},
            )
        ],
    )
    roots = wrap_dams_explorer_roots([pkg], tmp_path)
    assert [r.id for r in roots] == [
        "group:overview",
        "group:classes",
        "group:spec-files",
        "group:requirements",
        "group:implementations",
    ]
    assert roots[0].attributes.get("section_root") == "overview"
    assert all(
        c.attributes.get("kind") == "section_ref" for c in roots[0].children[:4]
    )
    assert roots[0].children[4].id == "group:overview-glossary"
    assert roots[1].children[0].id == "group:pkg"
    assert roots[2].children
    unknown = next(
        c
        for c in roots[2].children
        if (c.attributes or {}).get("path") == "schemas/a.yaml"
    )
    assert unknown.title == "a.yaml"
    envelope = next(
        c for c in roots[2].children if c.id == "file:specification.yaml"
    )
    assert envelope.title == "Конверт спецификации"
    assert roots[3].id == "group:requirements"
    assert {c.id for c in roots[3].children} == {
        "group:requirements-conceptual",
        "group:requirements-it-solutions",
        "group:requirements-publication",
    }
    conceptual = roots[3].children[0]
    assert conceptual.id == "group:requirements-conceptual"
    assert {c.id for c in conceptual.children} == {
        "group:requirements-conceptual-list",
        "group:requirements-conceptual-min-spec",
        "group:requirements-conceptual-model-spec",
    }
    assert "group:requirements-conceptual-model-example" not in {
        c.id for c in conceptual.children
    }
    it = next(
        c for c in roots[3].children if c.id == "group:requirements-it-solutions"
    )
    assert {c.id for c in it.children} == {
        "group:requirements-list",
        "group:requirements-min-spec",
        "group:requirements-model-spec",
        "group:requirements-model-example",
    }
    pub = next(c for c in roots[3].children if c.id == "group:requirements-publication")
    assert {c.id for c in pub.children} == {
        "group:requirements-publication-list",
        "group:requirements-publication-spec",
    }
    assert roots[4].children == []


def test_wrap_roots_loads_requirements_catalog():
    pkg = PublicationItem(
        id="group:pkg",
        title="Pkg",
        attributes={"kind": "group"},
        children=[],
    )
    roots = wrap_dams_explorer_roots([pkg], DAMS_SPEC)
    req_root = next(r for r in roots if r.id == "group:requirements")
    assert {c.id for c in req_root.children} == {
        "group:requirements-conceptual",
        "group:requirements-it-solutions",
        "group:requirements-publication",
    }
    assert req_root.children[0].id == "group:requirements-conceptual"
    assert req_root.children[0].title == "Концептуальная модель"
    conceptual = req_root.children[0]
    assert conceptual.attributes.get("nav_glyph") == "cdm"
    assert {c.id for c in conceptual.children} == {
        "group:requirements-conceptual-list",
        "group:requirements-conceptual-min-spec",
        "group:requirements-conceptual-model-spec",
    }
    assert all(
        "example" not in c.id for c in conceptual.children
    )
    conceptual_list = next(
        c for c in conceptual.children if c.id == "group:requirements-conceptual-list"
    )
    cm_codes = {c.attributes.get("code") for c in conceptual_list.children}
    assert "CM-GEN-001" in cm_codes
    assert "CM-CON-001" in cm_codes
    assert "CM-REF-001" in cm_codes
    assert "CM-PDM-000" in cm_codes
    assert all(
        c.attributes.get("requirement_level") == "conceptual_model"
        for c in conceptual_list.children
    )
    conceptual_skel = next(
        c
        for c in conceptual.children
        if c.id == "group:requirements-conceptual-model-spec"
    )
    assert conceptual_skel.children
    cm_skel_text = conceptual_skel.children[0].attributes.get("text") or ""
    assert "conceptual_entities:" in cm_skel_text
    assert "relationships:" in cm_skel_text
    assert "physical_objects:" not in cm_skel_text

    it = next(
        c for c in req_root.children if c.id == "group:requirements-it-solutions"
    )
    assert it.title == "ИТ-решения"
    list_group = next(c for c in it.children if c.id == "group:requirements-list")
    assert list_group.title == "Требования к модели"
    assert list_group.attributes.get("requirement_count") == sum(
        len(c.children or []) for c in list_group.children
    )
    assert [c.id for c in list_group.children] == [
        "group:requirements-section-LDM",
        "group:requirements-section-PDM",
        "group:requirements-section-REF",
        "group:requirements-section-ATR",
        "group:requirements-section-FLW",
        "group:requirements-section-CLS",
        "group:requirements-section-GEN",
    ]
    assert all(
        c.attributes.get("kind") == "group"
        and c.attributes.get("group_style") == "section_folder"
        for c in list_group.children
    )
    by_section = {c.attributes.get("requirement_section"): c for c in list_group.children}
    assert by_section["LDM"].attributes.get("nav_glyph") == "ldm"
    assert by_section["PDM"].attributes.get("nav_glyph") == "pdm"
    assert by_section["REF"].attributes.get("nav_glyph") is None
    assert by_section["GEN"].attributes.get("nav_glyph") is None
    req_leaves = [r for g in list_group.children for r in (g.children or [])]
    codes = {c.attributes.get("code") for c in req_leaves}
    assert "GEN-001" in codes
    assert "GEN-003" in codes
    assert "GEN-004" in codes
    assert "LDM-001" in codes
    assert "LDM-006" in codes
    assert "LDM-007" in codes
    assert "ATR-001" in codes
    assert "ATR-005" in codes
    assert "REF-001" in codes
    assert "REF-002" in codes
    assert "PDM-001" in codes
    assert "PDM-003" in codes
    assert "CLS-001" in codes
    assert all(c.attributes.get("kind") == "requirement" for c in req_leaves)
    assert all(c.attributes.get("statement") for c in req_leaves)
    assert all(c.attributes.get("formal_checks") for c in req_leaves)

    min_group = next(c for c in it.children if c.id == "group:requirements-min-spec")
    assert min_group.title == "Спецификация требований"
    assert min_group.children
    assert all(c.attributes.get("kind") == "source_file" for c in min_group.children)
    assert all("classes:" in (c.attributes.get("text") or "") for c in min_group.children)

    model_spec = next(
        c for c in it.children if c.id == "group:requirements-model-spec"
    )
    assert model_spec.title == "Спецификация модели"
    assert model_spec.children
    skel_text = model_spec.children[0].attributes.get("text") or ""
    assert "element_id:" in skel_text
    assert "logical_entities:" in skel_text
    assert "<required>" in skel_text or "<must-resolve-in-package>" in skel_text

    example = next(
        c for c in it.children if c.id == "group:requirements-model-example"
    )
    assert example.title == "Пример модели"
    assert example.children
    assert example.children[0].id == (
        "file:requirements/examples/it-solution-model.example.yaml"
    )
    assert "example_min_solution_model" in (example.children[0].attributes.get("text") or "")

    pub = next(
        c for c in req_root.children if c.id == "group:requirements-publication"
    )
    assert pub.title == "Публикация"
    pub_list = next(
        c for c in pub.children if c.id == "group:requirements-publication-list"
    )
    assert pub_list.title == "Требования публикации"
    assert pub_list.attributes.get("requirement_count", 0) >= 1
    assert any(
        (c.attributes or {}).get("section_id") == "publication-requirements"
        for c in pub_list.children
    )
    pub_spec = next(
        c for c in pub.children if c.id == "group:requirements-publication-spec"
    )
    assert pub_spec.title == "Спецификация"
    assert any(
        c.id == "file:publication-requirements.yaml" for c in pub_spec.children
    )
    assert "dams-logical-modeling" in (
        pub_spec.children[0].attributes.get("text") or ""
    )


def test_minimal_schema_projection_has_required_slots():
    from linkml_runtime.utils.schemaview import SchemaView

    sv = SchemaView(str(DAMS_SPEC / "schemas" / "moex-dams.yaml"))
    out = project_required_only_schema(sv)
    assert "minimal/moex-dams.required.yaml" in out
    text = out["minimal/moex-dams.required.yaml"]
    assert "ModelPackage" in text
    assert "LogicalEntity" in text
    assert "SpecificationRequirement" in text
    assert "RequirementLevelEnum" in text


def test_model_skeleton_projection_from_formal_checks():
    catalog = DAMS_SPEC / "requirements" / "it-solution-requirements.yaml"
    out = project_it_solution_model_skeleton(catalog)
    assert "requirements/minimal/it-solution-model.skeleton.yaml" in out
    text = out["requirements/minimal/it-solution-model.skeleton.yaml"]
    assert "element_id:" in text
    assert "api_version:" in text
    assert "model_version:" in text
    assert "logical_entities:" in text
    assert "context_ref:" in text
    assert "solution_data_role:" in text
    assert "attributes:" in text
    assert "owner_entity_ref:" in text
    assert "relationships:" in text
    assert "physical_objects:" in text


def test_conceptual_model_skeleton_projection():
    from moex_publication_viewer.normalizers.model_skeleton_projection import (
        project_conceptual_model_skeleton,
    )

    catalog = DAMS_SPEC / "requirements" / "conceptual-model-requirements.yaml"
    out = project_conceptual_model_skeleton(catalog)
    assert "requirements/minimal/conceptual-model.skeleton.yaml" in out
    text = out["requirements/minimal/conceptual-model.skeleton.yaml"]
    assert "element_id:" in text
    assert "implementation_scope:" in text
    assert "conceptual_entities:" in text
    assert "relationships:" in text
    assert "physical_objects:" not in text
