"""Unit tests for DAMS explorer roots helper."""

from __future__ import annotations

from pathlib import Path

from moex_publication_viewer.normalizers.dams_explorer_roots import (
    build_spec_file_items,
    is_dams_specification_dir,
    wrap_dams_explorer_roots,
)
from moex_publication_viewer.models.publication_models import PublicationItem


def test_is_dams_specification_dir(tmp_path: Path):
    schemas = tmp_path / "schemas"
    schemas.mkdir()
    schema = schemas / "moex-dams.yaml"
    schema.write_text("id: x\n", encoding="utf-8")
    assert is_dams_specification_dir(schema) is False
    (tmp_path / "specification.yaml").write_text("id: s\n", encoding="utf-8")
    assert is_dams_specification_dir(schema) is True


def test_build_spec_file_items_repo():
    repo = Path(__file__).resolve().parents[3]
    spec_dir = repo / "model-assets" / "specifications" / "moex-dams" / "0.1"
    items = build_spec_file_items(spec_dir)
    ids = {i.id for i in items}
    assert "file:specification.yaml" in ids
    assert "file:schemas/moex-core.yaml" in ids
    assert all(i.attributes.get("kind") == "source_file" for i in items)
    assert all(i.attributes.get("text") for i in items)


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
        "group:classes",
        "group:spec-files",
        "group:implementations",
    ]
    assert roots[0].children[0].id == "group:pkg"
    assert roots[1].children
    assert roots[2].children == []
