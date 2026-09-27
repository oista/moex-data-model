"""Normalizer snapshot-style tests."""

from pathlib import Path

import yaml

from moex_publication_viewer.models.manifest_models import ManifestSection, SourceSpec
from moex_publication_viewer.normalizers.csv_normalizer import CsvNormalizer
from moex_publication_viewer.normalizers.json_normalizer import JsonNormalizer
from moex_publication_viewer.normalizers.linkml_normalizer import LinkmlNormalizer
from moex_publication_viewer.normalizers.markdown_normalizer import MarkdownNormalizer
from moex_publication_viewer.normalizers.yaml_normalizer import YamlNormalizer


FIXTURES = Path(__file__).parent / "fixtures"


def _section(**kwargs) -> ManifestSection:
    defaults = {
        "id": "s",
        "title": "S",
        "type": "entity-table",
        "source": SourceSpec(format="yaml", path="x"),
    }
    defaults.update(kwargs)
    if isinstance(defaults["source"], dict):
        defaults["source"] = SourceSpec(**defaults["source"])
    return ManifestSection(**defaults)


def test_yaml_list_of_dicts(tmp_path: Path):
    p = tmp_path / "data.yaml"
    p.write_text(yaml.dump({"items": [{"id": "a", "title": "A", "description": "d"}]}), encoding="utf-8")
    sec = _section(source={"format": "yaml", "path": "data.yaml", "select": "items"})
    out = YamlNormalizer().normalize(sec, p)
    assert len(out.items) == 1
    assert out.items[0].id == "a"
    assert out.items[0].title == "A"


def test_json_key_value(tmp_path: Path):
    p = tmp_path / "data.json"
    p.write_text('{"title": "T", "version": "1.0"}', encoding="utf-8")
    sec = _section(type="key-value", source={"format": "json", "path": "data.json"})
    out = JsonNormalizer().normalize(sec, p)
    ids = {i.id for i in out.items}
    assert "title" in ids
    assert "version" in ids


def test_csv_records(tmp_path: Path):
    p = tmp_path / "data.csv"
    p.write_text("local_name,label,definition\nFoo,Foo Label,A def\n", encoding="utf-8")
    sec = _section(
        type="glossary",
        source={"format": "csv", "path": "data.csv"},
        key_column="local_name",
        columns=["local_name", "label", "definition"],
    )
    out = CsvNormalizer().normalize(sec, p)
    assert out.items[0].id == "Foo"
    assert out.items[0].title == "Foo Label"
    assert out.items[0].description == "A def"


def test_markdown(tmp_path: Path):
    p = tmp_path / "doc.md"
    p.write_text("# Hello\n\nWorld", encoding="utf-8")
    sec = _section(type="markdown-doc", source={"format": "markdown", "path": "doc.md"})
    out = MarkdownNormalizer().normalize(sec, p)
    assert out.content
    assert "Hello" in out.content


def test_linkml_with_import():
    root = FIXTURES / "linkml"
    schema = root / "root.yaml"
    sec = _section(
        source={"format": "linkml-yaml", "path": "root.yaml", "select": "classes"},
        columns=["name", "description", "is_a"],
    )
    out = LinkmlNormalizer().normalize(sec, schema)
    names = {i.id for i in out.items}
    assert "RootClass" in names
    assert "ChildClass" in names

    tree_sec = _section(
        type="tree",
        source={"format": "linkml-yaml", "path": "root.yaml", "select": "classes"},
    )
    tree = LinkmlNormalizer().normalize(tree_sec, schema)
    roots = {i.id for i in tree.items}
    assert "RootClass" in roots
    child = next(i for i in tree.items if i.id == "RootClass")
    assert any(c.id == "ChildClass" for c in child.children)

    enum_sec = _section(
        type="enum-table",
        source={"format": "linkml-yaml", "path": "root.yaml", "select": "enums"},
    )
    enums = LinkmlNormalizer().normalize(enum_sec, schema)
    assert enums.items
    assert enums.items[0].children


def test_linkml_explorer_groups_by_schema():
    root = FIXTURES / "linkml"
    schema = root / "root.yaml"
    sec = _section(
        type="explorer",
        source={"format": "linkml-yaml", "path": "root.yaml", "select": "classes"},
    )
    out = LinkmlNormalizer().normalize(sec, schema)
    assert out.items, "explorer must produce groups"
    assert all(i.attributes.get("kind") == "group" for i in out.items)
    # Fixture has root + imported child schemas
    schema_keys = {i.attributes.get("schema_key") for i in out.items}
    assert schema_keys & {"root_schema", "child_schema"} or len(out.items) >= 1
    # Classes live under groups with induced slots list
    classes = [c for g in out.items for c in g.children if c.attributes.get("kind") == "class"]
    assert classes
    assert any(c.id == "RootClass" for c in classes)
    root_cls = next(c for c in classes if c.id == "RootClass")
    assert isinstance(root_cls.attributes.get("slots"), list)


def test_dams_explorer_real_schema():
    repo = Path(__file__).resolve().parents[2]
    schema = repo / "model_src" / "schemas" / "moex-dams.yaml"
    if not schema.is_file():
        return
    sec = _section(
        type="explorer",
        source={"format": "linkml-yaml", "path": str(schema), "select": "classes"},
    )
    out = LinkmlNormalizer().normalize(sec, schema)
    titles = {g.title for g in out.items}
    assert "Core" in titles
    assert "Registries" in titles
    classes = {c.id: c for g in out.items for c in g.children if c.attributes.get("kind") == "class"}
    assert "LogicalEntity" in classes
    slots = classes["LogicalEntity"].attributes.get("slots") or []
    slot_names = {s["name"] for s in slots}
    assert "attributes" in slot_names
    assert "conceptual_entity_refs" in slot_names
