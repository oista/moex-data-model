"""Unit tests for moex_publication_viewer.edits (Task 1)."""

from __future__ import annotations

from pathlib import Path

import pytest

from moex_publication_viewer.edits import (
    EditError,
    EditTarget,
    apply_edit,
    make_edit_target,
    parse_yaml_path,
    resolve_under_root,
    value_hash,
)


def _fixture_yaml(tmp_path: Path) -> Path:
    p = tmp_path / "model.yaml"
    p.write_text(
        "# header comment\n"
        "element_id: dams:model/demo\n"
        "logical_entities:\n"
        "  - element_id: dams:logical/A\n"
        "    name: A\n"
        "    title: Alpha\n"
        "    description: First entity\n"
        "    aliases:\n"
        "      - aka-a\n"
        "  - element_id: dams:logical/B\n"
        "    name: B\n"
        "    title: Beta\n"
        "    description: Second\n",
        encoding="utf-8",
    )
    return p


def test_value_hash_stable():
    assert value_hash("hello") == value_hash("hello")
    assert value_hash(["a", "b"]) != value_hash(["b", "a"])


def test_parse_yaml_path_map_and_list():
    segs = parse_yaml_path(
        "logical_entities[element_id=dams:logical/A].description"
    )
    assert segs[0] == ("logical_entities", "element_id", "dams:logical/A")
    assert segs[1] == ("description", None, None)
    segs2 = parse_yaml_path("classes.Foo.description")
    assert segs2 == [("classes", None, None), ("Foo", None, None), ("description", None, None)]


def test_round_trip_preserves_comments_and_order(tmp_path: Path):
    p = _fixture_yaml(tmp_path)
    before = p.read_text(encoding="utf-8")
    target = make_edit_target(
        file="model.yaml",
        yaml_path="logical_entities[element_id=dams:logical/A].description",
        field="description",
        value="First entity",
    )
    registry = {EditTarget.from_dict(target).registry_key(): EditTarget.from_dict(target)}
    result = apply_edit(tmp_path, target, "Updated description", registry)
    assert result.ok
    after = p.read_text(encoding="utf-8")
    assert "# header comment" in after
    assert "Updated description" in after
    assert "element_id: dams:model/demo" in after
    # Only the description line for A should change among content lines
    assert before.count("First entity") == 1
    assert "First entity" not in after
    # Key order: name still before title
    a_block = after.split("element_id: dams:logical/A")[1].split("element_id: dams:logical/B")[0]
    assert a_block.index("name:") < a_block.index("title:") < a_block.index("description:")


def test_aliases_replace_whole_list(tmp_path: Path):
    p = _fixture_yaml(tmp_path)
    target = make_edit_target(
        file="model.yaml",
        yaml_path="logical_entities[element_id=dams:logical/A].aliases",
        field="aliases",
        value=["aka-a"],
    )
    registry = {EditTarget.from_dict(target).registry_key(): EditTarget.from_dict(target)}
    apply_edit(tmp_path, target, ["one", "two"], registry)
    text = p.read_text(encoding="utf-8")
    assert "aka-a" not in text
    assert "- one" in text
    assert "- two" in text


def test_path_escape_rejected(tmp_path: Path):
    _fixture_yaml(tmp_path)
    with pytest.raises(EditError) as ei:
        resolve_under_root(tmp_path, "../outside.yaml")
    assert ei.value.status == 403


def test_non_yaml_extension_rejected(tmp_path: Path):
    p = tmp_path / "notes.txt"
    p.write_text("x", encoding="utf-8")
    with pytest.raises(EditError) as ei:
        resolve_under_root(tmp_path, "notes.txt")
    assert ei.value.status == 422


def test_unknown_registry_key(tmp_path: Path):
    _fixture_yaml(tmp_path)
    target = make_edit_target(
        file="model.yaml",
        yaml_path="logical_entities[element_id=dams:logical/A].description",
        field="description",
        value="First entity",
    )
    with pytest.raises(EditError) as ei:
        apply_edit(tmp_path, target, "x", registry={})
    assert ei.value.status == 404


def test_base_hash_mismatch(tmp_path: Path):
    _fixture_yaml(tmp_path)
    target = EditTarget(
        file="model.yaml",
        yaml_path="logical_entities[element_id=dams:logical/A].description",
        field="description",
        base_hash=value_hash("stale"),
    )
    registry = {target.registry_key(): target}
    with pytest.raises(EditError) as ei:
        apply_edit(tmp_path, target, "new", registry)
    assert ei.value.status == 409


def test_empty_title_rejected(tmp_path: Path):
    _fixture_yaml(tmp_path)
    target = make_edit_target(
        file="model.yaml",
        yaml_path="logical_entities[element_id=dams:logical/A].title",
        field="title",
        value="Alpha",
    )
    registry = {EditTarget.from_dict(target).registry_key(): EditTarget.from_dict(target)}
    with pytest.raises(EditError) as ei:
        apply_edit(tmp_path, target, "   ", registry)
    assert ei.value.status == 422


def test_duplicate_sibling_title_rejected(tmp_path: Path):
    _fixture_yaml(tmp_path)
    target = make_edit_target(
        file="model.yaml",
        yaml_path="logical_entities[element_id=dams:logical/A].title",
        field="title",
        value="Alpha",
    )
    registry = {EditTarget.from_dict(target).registry_key(): EditTarget.from_dict(target)}
    with pytest.raises(EditError) as ei:
        apply_edit(tmp_path, target, "Beta", registry)
    assert ei.value.status == 422
    assert "duplicate" in ei.value.message.lower()


def test_rebuild_failure_restores_bytes(tmp_path: Path):
    p = _fixture_yaml(tmp_path)
    original = p.read_bytes()
    target = make_edit_target(
        file="model.yaml",
        yaml_path="logical_entities[element_id=dams:logical/A].description",
        field="description",
        value="First entity",
    )
    registry = {EditTarget.from_dict(target).registry_key(): EditTarget.from_dict(target)}

    def boom() -> None:
        raise RuntimeError("compile failed")

    with pytest.raises(EditError) as ei:
        apply_edit(tmp_path, target, "Should rollback", registry, rebuild=boom)
    assert ei.value.status == 422
    assert p.read_bytes() == original
    assert b"Should rollback" not in p.read_bytes()
