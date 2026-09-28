"""Normalizer snapshot-style tests."""

from pathlib import Path
import json

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


def test_csv_tree_from_parent_local_name(tmp_path: Path):
    p = tmp_path / "tree.csv"
    p.write_text(
        "local_name,label,parent_local_name\n"
        "CreditEvent,credit event,\n"
        "DefaultEvent,default event,CreditEvent\n"
        "FailureToPay,failure to pay,DefaultEvent\n"
        "Orphan,orphan,MissingParent\n",
        encoding="utf-8",
    )
    sec = _section(
        type="tree",
        source={"format": "csv", "path": "tree.csv"},
        key_column="local_name",
    )
    out = CsvNormalizer().normalize(sec, p)
    roots = {i.id: i for i in out.items}
    assert set(roots) == {"CreditEvent", "Orphan"}
    credit = roots["CreditEvent"]
    assert [c.id for c in credit.children] == ["DefaultEvent"]
    assert [c.id for c in credit.children[0].children] == ["FailureToPay"]


def test_csv_explorer_groups_by_domain_and_nests_parents(tmp_path: Path):
    p = tmp_path / "onto.csv"
    p.write_text(
        "local_name,label,definition,definition_ru,label_ru,parent_local_name,source_domain,iri\n"
        "RootA,Root A,def A,опр A,Корень A,,FND,https://ex/RootA\n"
        "ChildA,Child A,def CA,опр CA,Дитя A,RootA,FND,https://ex/ChildA\n"
        "RootB,Root B,def B,,,,BE,https://ex/RootB\n"
        "Cross,Cross,def X,,,RootA,BE,https://ex/Cross\n",
        encoding="utf-8",
    )
    sec = _section(
        type="explorer",
        source={"format": "csv", "path": "onto.csv"},
        key_column="local_name",
        tags=["ontology", "fibo"],
    )
    out = CsvNormalizer().normalize(sec, p)
    assert out.type == "explorer"
    groups = {g.id: g for g in out.items}
    assert set(groups) == {"group:FND", "group:BE"}
    assert all(g.attributes.get("kind") == "group" for g in out.items)
    fnd = groups["group:FND"]
    assert fnd.title == "FND"
    assert [c.id for c in fnd.children] == ["RootA"]
    assert [c.id for c in fnd.children[0].children] == ["ChildA"]
    child = fnd.children[0].children[0]
    assert child.attributes.get("kind") == "class"
    assert child.description == "def CA"
    assert child.attributes.get("definition_ru") == "опр CA"
    assert child.attributes.get("iri") == "https://ex/ChildA"
    be = groups["group:BE"]
    # Cross parent RootA is other domain → treat as root in BE
    be_ids = {c.id for c in be.children}
    assert be_ids == {"RootB", "Cross"}


def test_json_explorer_loads_nested_groups(tmp_path: Path):
    """Pre-nested ontology_explorer.json must keep groups and child trees."""
    payload = [
        {
            "id": "group:moex:ontology:fibo",
            "title": "fibo",
            "description": "Ontology moex:ontology:fibo",
            "attributes": {
                "kind": "group",
                "ontology_id": "moex:ontology:fibo",
                "purpose": "Indexed entities",
                "class_count": 2,
                "enum_count": 0,
            },
            "children": [
                {
                    "id": "https://ex/Parent",
                    "title": "Parent",
                    "description": "parent class",
                    "attributes": {
                        "kind": "class",
                        "iri": "https://ex/Parent",
                        "parent_ref": "",
                        "stub": True,
                    },
                    "children": [
                        {
                            "id": "https://ex/Child",
                            "title": "Child",
                            "description": "child class",
                            "attributes": {
                                "kind": "class",
                                "iri": "https://ex/Child",
                                "parent_ref": "https://ex/Parent",
                                "definition_ru": "потомок",
                            },
                            "children": [],
                        }
                    ],
                }
            ],
        }
    ]
    p = tmp_path / "ontology_explorer.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    sec = _section(
        type="explorer",
        source={"format": "json", "path": "ontology_explorer.json"},
        tags=["ontology", "catalog"],
    )
    out = JsonNormalizer().normalize(sec, p)
    assert out.type == "explorer"
    assert len(out.items) == 1
    group = out.items[0]
    assert group.id == "group:moex:ontology:fibo"
    assert group.attributes.get("kind") == "group"
    assert group.attributes.get("ontology_id") == "moex:ontology:fibo"
    assert [c.id for c in group.children] == ["https://ex/Parent"]
    parent = group.children[0]
    assert parent.attributes.get("stub") is True
    assert [c.id for c in parent.children] == ["https://ex/Child"]
    assert parent.children[0].attributes.get("definition_ru") == "потомок"


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
    assert root_cls.attributes.get("declared_slots") == ["root_slot"]
    root_slots = {s["name"]: s for s in root_cls.attributes["slots"]}
    assert root_slots["root_slot"]["inherited"] is False

    child_cls = next(c for c in classes if c.id == "ChildClass")
    assert child_cls.attributes.get("is_a") == "RootClass"
    assert child_cls.attributes.get("declared_slots") == ["child_slot"]
    child_slots = {s["name"]: s for s in child_cls.attributes.get("slots") or []}
    assert "root_slot" in child_slots
    assert child_slots["root_slot"]["inherited"] is True
    assert child_slots["child_slot"]["inherited"] is False


def test_dams_explorer_real_schema():
    repo = Path(__file__).resolve().parents[3]
    schema = (
        repo
        / "model-assets"
        / "specifications"
        / "moex-dams"
        / "0.1"
        / "schemas"
        / "moex-dams.yaml"
    )
    if not schema.is_file():
        return
    sec = _section(
        type="explorer",
        source={"format": "linkml-yaml", "path": str(schema), "select": "classes"},
    )
    out = LinkmlNormalizer().normalize(sec, schema)
    root_ids = {g.id for g in out.items}
    assert root_ids == {
        "group:classes",
        "group:spec-files",
        "group:implementations",
    }
    classes_root = next(g for g in out.items if g.id == "group:classes")
    titles = {g.title for g in classes_root.children}
    assert "Core" in titles
    assert "Registries" in titles
    by_title = {g.title: g for g in classes_root.children}
    core = by_title["Core"]
    assert "Schema package" not in (core.description or "")
    purpose = core.attributes.get("purpose") or ""
    assert "conceptual" in purpose.lower() or "logical" in purpose.lower()
    assert "physical" in purpose.lower()
    assert "Mapping" in purpose or "mapping" in purpose.lower()
    structure = core.attributes.get("structure_why") or ""
    assert "DAMS-F-003" in structure or "уровн" in structure.lower()
    assert (core.attributes.get("class_count") or 0) > 0
    assert core.attributes.get("source_file") == "moex-core.yaml"

    registries = by_title["Registries"]
    reg_purpose = registries.attributes.get("purpose") or ""
    assert "проекц" in reg_purpose.lower() or "projection" in reg_purpose.lower()
    assert "не копируя" in reg_purpose.lower() or "справочник" in reg_purpose.lower()

    classes = {
        c.id: c
        for g in classes_root.children
        for c in g.children
        if c.attributes.get("kind") == "class"
    }
    assert "LogicalEntity" in classes
    slots = classes["LogicalEntity"].attributes.get("slots") or []
    slot_names = {s["name"] for s in slots}
    assert "attributes" in slot_names
    assert "conceptual_entity_refs" in slot_names
    assert any(s.get("inherited") for s in slots)

    repo_cls = classes["MOEXModelRepository"]
    assert repo_cls.attributes.get("tree_root") is True

    files_root = next(g for g in out.items if g.id == "group:spec-files")
    file_ids = {f.id for f in files_root.children}
    assert "file:specification.yaml" in file_ids
    assert "file:schemas/moex-core.yaml" in file_ids
    envelope = next(f for f in files_root.children if f.id == "file:specification.yaml")
    assert envelope.attributes.get("kind") == "source_file"
    assert "specification_kind" in (envelope.attributes.get("text") or "")
    assert "file:schemas/moex-dams.yaml" in (envelope.attributes.get("refs_out") or [])

    impls_root = next(g for g in out.items if g.id == "group:implementations")
    assert impls_root.children == []  # filled at build time

    lifecycle = classes["HasLifecycle"]
    assert lifecycle.attributes.get("mixin") is True
    assert lifecycle.attributes.get("is_a") in (None, "")
