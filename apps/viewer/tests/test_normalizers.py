"""Normalizer snapshot-style tests."""

from pathlib import Path
import json

import yaml

from moex_publication_viewer.models.manifest_models import ManifestSection, SourceSpec
from moex_publication_viewer.normalizers.csv_normalizer import CsvNormalizer
from moex_publication_viewer.normalizers.json_normalizer import JsonNormalizer
from moex_publication_viewer.normalizers.linkml_normalizer import LinkmlNormalizer
from moex_publication_viewer.normalizers.markdown_normalizer import MarkdownNormalizer
from moex_publication_viewer.normalizers.mermaid_diagram_normalizer import (
    MermaidDiagramNormalizer,
)
from moex_publication_viewer.normalizers.yaml_normalizer import YamlNormalizer


FIXTURES = Path(__file__).parent / "fixtures"


def _walk_classes(nodes) -> dict:
    """Collect kind=class items recursively (explorer nests by is_a)."""
    out: dict = {}
    for node in nodes or []:
        attrs = node.attributes or {}
        if attrs.get("kind") == "class":
            out[node.id] = node
        out.update(_walk_classes(node.children))
    return out


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


def test_yaml_flattened_publication_requirements(tmp_path: Path):
    from moex_publication_viewer.normalizers.helpers import (
        flatten_publication_requirements,
    )

    raw = {
        "profiles": [
            {
                "id": "dams-logical-modeling",
                "requirements": [
                    {
                        "id": "dams:overview",
                        "title": "Overview",
                        "description": "Must publish overview",
                        "obligation": "required",
                        "semantic_capability": "overview",
                    },
                    {
                        "id": "dams:relationships",
                        "obligation": "recommended",
                        "semantic_capability": "relationships",
                    },
                ],
            },
            {
                "id": "dams-logical-and-physical",
                "requirements": [
                    {
                        "id": "dams:physical-objects",
                        "obligation": "required",
                        "semantic_capability": "physical-objects",
                    },
                ],
            },
        ]
    }
    rows = flatten_publication_requirements(raw)
    assert len(rows) == 3
    by_id = {r["id"]: r for r in rows}
    assert by_id["dams:overview"]["name"] == "Overview"
    assert by_id["dams:overview"]["profile"] == "dams-logical-modeling"
    assert by_id["dams:overview"]["required"] == "required"
    assert by_id["dams:relationships"]["required"] == "recommended"
    assert by_id["dams:relationships"]["name"] == "dams:relationships"
    assert by_id["dams:physical-objects"]["profile"] == "dams-logical-and-physical"

    p = tmp_path / "publication-requirements.yaml"
    p.write_text(yaml.dump(raw), encoding="utf-8")
    sec = _section(
        id="publication-requirements",
        source={
            "format": "yaml",
            "path": "publication-requirements.yaml",
            "select": "flattened_requirements",
        },
        columns=["id", "name", "description", "profile", "required"],
    )
    out = YamlNormalizer().normalize(sec, p)
    assert len(out.items) == 3
    assert {i.id for i in out.items} == {
        "dams:overview",
        "dams:relationships",
        "dams:physical-objects",
    }
    overview = next(i for i in out.items if i.id == "dams:overview")
    assert overview.title == "Overview"
    assert overview.attributes.get("profile") == "dams-logical-modeling"
    assert overview.attributes.get("required") == "required"


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


def test_markdown_wraps_tables(tmp_path: Path):
    p = tmp_path / "doc.md"
    p.write_text("| A | B |\n| --- | --- |\n| 1 | 2 |\n", encoding="utf-8")
    sec = _section(type="markdown-doc", source={"format": "markdown", "path": "doc.md"})
    out = MarkdownNormalizer().normalize(sec, p)
    assert out.content
    assert 'class="table-scroll"' in out.content or "table-scroll" in out.content
    assert "data-table" in out.content
    assert "<table" in out.content


def test_yaml_nested_attributes_become_children(tmp_path: Path):
    p = tmp_path / "model.yaml"
    p.write_text(
        yaml.dump(
            {
                "logical_entities": [
                    {
                        "element_id": "dams:logical/demo/doc",
                        "name": "document",
                        "title": "Document",
                        "description": "A document",
                        "attributes": [
                            {
                                "element_id": "dams:logical/demo/doc/id",
                                "name": "id",
                                "title": "Id",
                                "data_type_ref": "dams:datatype/identifier",
                                "required": True,
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    sec = _section(
        source={"format": "yaml", "path": "model.yaml", "select": "logical_entities"},
        key_column="element_id",
        instance_of="LogicalEntity",
    )
    out = YamlNormalizer().normalize(sec, p)
    assert out.instance_of == "LogicalEntity"
    assert len(out.items) == 1
    assert out.items[0].id == "dams:logical/demo/doc"
    assert len(out.items[0].children) == 1
    assert out.items[0].children[0].id == "dams:logical/demo/doc/id"
    assert out.items[0].children[0].attributes.get("data_type_ref") == "dams:datatype/identifier"
    assert "attributes" not in out.items[0].attributes or not isinstance(
        out.items[0].attributes.get("attributes"), list
    )


def test_mermaid_diagram_with_svg(tmp_path: Path):
    md = tmp_path / "logical.erd.md"
    md.write_text(
        "```mermaid\nerDiagram\n    Client {\n        string id PK\n    }\n```\n",
        encoding="utf-8",
    )
    svg = tmp_path / "logical.erd.svg"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script>'
        '<rect width="10" height="10"/></svg>',
        encoding="utf-8",
    )
    (tmp_path / "logical.dbml").write_text(
        "Table Client {\n  id string [not null]\n}\n",
        encoding="utf-8",
    )
    sec = _section(
        type="mermaid-diagram",
        source={"format": "markdown", "path": "logical.erd.md"},
    )
    out = MermaidDiagramNormalizer().normalize(sec, md)
    assert out.content
    assert "<svg" in out.content
    assert "<script" not in out.content.lower()
    assert out.attributes["mermaid_source"].startswith("erDiagram")
    assert out.attributes["svg_missing"] is False
    assert out.attributes["dbml_source"].startswith("Table Client")
    assert out.attributes["dbml_missing"] is False


def test_mermaid_diagram_without_svg(tmp_path: Path):
    md = tmp_path / "logical.erd.md"
    md.write_text(
        "```mermaid\nerDiagram\n    Client {\n        string id PK\n    }\n```\n",
        encoding="utf-8",
    )
    sec = _section(
        type="mermaid-diagram",
        source={"format": "markdown", "path": "logical.erd.md"},
    )
    out = MermaidDiagramNormalizer().normalize(sec, md)
    assert out.content == ""
    assert out.attributes["mermaid_source"].startswith("erDiagram")
    assert out.attributes["svg_missing"] is True
    assert out.attributes["dbml_source"] == ""
    assert out.attributes["dbml_missing"] is True


def test_mermaid_diagram_loads_clickmap(tmp_path: Path):
    md = tmp_path / "conceptual.erd.md"
    md.write_text(
        "```mermaid\nerDiagram\n    LegalEntity {\n        string concept\n    }\n```\n",
        encoding="utf-8",
    )
    clickmap = {
        "profile": "conceptual",
        "entities": {
            "LegalEntity": {
                "element_id": "dams:concept/LegalEntity",
                "section_id": "conceptual",
            }
        },
        "edges": [],
    }
    (tmp_path / "conceptual.erd.clickmap.json").write_text(
        json.dumps(clickmap), encoding="utf-8"
    )
    sec = _section(
        type="mermaid-diagram",
        source={"format": "markdown", "path": "conceptual.erd.md"},
    )
    out = MermaidDiagramNormalizer().normalize(sec, md)
    assert out.attributes["erd_clickmap"]["entities"]["LegalEntity"][
        "element_id"
    ] == "dams:concept/LegalEntity"


def test_mermaid_diagram_loads_scene_and_layout(tmp_path: Path):
    # Nest under model-assets so erd_layout_path is repo-relative.
    pub = tmp_path / "model-assets" / "impl" / "publications"
    pub.mkdir(parents=True)
    md = pub / "logical.erd.md"
    md.write_text(
        "```mermaid\nerDiagram\n    Client {\n        string id PK\n    }\n```\n",
        encoding="utf-8",
    )
    scene = {
        "version": 1,
        "profile": "logical",
        "nodes": [
            {
                "name": "Client",
                "title": "Client",
                "element_id": "dams:logical/Client",
                "columns": [{"name": "id", "type": "identifier", "keys": ["PK"]}],
            }
        ],
        "edges": [],
    }
    layout = {
        "version": 1,
        "profile": "logical",
        "nodes": {"dams:logical/Client": {"x": 10, "y": 20, "color": "#4285F4"}},
        "edges": {},
    }
    (pub / "logical.scene.json").write_text(json.dumps(scene), encoding="utf-8")
    (pub / "logical.layout.json").write_text(json.dumps(layout), encoding="utf-8")
    sec = _section(
        type="mermaid-diagram",
        source={"format": "markdown", "path": "logical.erd.md"},
    )
    out = MermaidDiagramNormalizer().normalize(sec, md)
    assert out.attributes["erd_scene"]["nodes"][0]["name"] == "Client"
    assert out.attributes["erd_layout"]["nodes"]["dams:logical/Client"]["x"] == 10
    assert out.attributes["erd_layout_path"].endswith(
        "model-assets/impl/publications/logical.layout.json"
    )
    assert out.attributes["erd_layout_hash"]


def test_mermaid_diagram_without_scene_keeps_svg_path(tmp_path: Path):
    md = tmp_path / "logical.erd.md"
    md.write_text(
        "```mermaid\nerDiagram\n    Client {\n        string id PK\n    }\n```\n",
        encoding="utf-8",
    )
    (tmp_path / "logical.erd.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>',
        encoding="utf-8",
    )
    sec = _section(
        type="mermaid-diagram",
        source={"format": "markdown", "path": "logical.erd.md"},
    )
    out = MermaidDiagramNormalizer().normalize(sec, md)
    assert "erd_scene" not in out.attributes
    assert out.content.startswith("<svg")


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
    assert [i.id for i in out.items[:2]] == ["group:overview", "group:classes"]
    assert out.items[0].attributes.get("section_root") == "overview"
    assert out.items[1].attributes.get("section_root") == "classes"
    package_groups = out.items[1].children
    assert package_groups
    assert all(i.attributes.get("kind") == "group" for i in package_groups)
    # Fixture has root + imported child schemas
    schema_keys = {i.attributes.get("schema_key") for i in package_groups}
    assert schema_keys & {"root_schema", "child_schema"} or len(package_groups) >= 1
    # Classes live under schema packages under Classes root (nested by is_a)
    classes = {}
    for g in package_groups:
        classes.update(_walk_classes(g.children))
    assert classes
    assert "RootClass" in classes
    root_cls = classes["RootClass"]
    assert isinstance(root_cls.attributes.get("slots"), list)
    assert root_cls.attributes.get("declared_slots") == ["root_slot"]
    root_slots = {s["name"]: s for s in root_cls.attributes["slots"]}
    assert root_slots["root_slot"]["inherited"] is False

    # Same-package is_a → nested children
    assert any(c.id == "MidClass" for c in root_cls.children)
    mid = next(c for c in root_cls.children if c.id == "MidClass")
    assert mid.attributes.get("is_a") == "RootClass"

    # Cross-package is_a → local root in child package (parent not in by_id)
    child_cls = classes["ChildClass"]
    assert child_cls.attributes.get("is_a") == "RootClass"
    assert child_cls.attributes.get("declared_slots") == ["child_slot"]
    child_slots = {s["name"]: s for s in child_cls.attributes.get("slots") or []}
    assert "root_slot" in child_slots
    assert child_slots["root_slot"]["inherited"] is True
    assert child_slots["child_slot"]["inherited"] is False
    child_pkg = next(
        g for g in package_groups if g.attributes.get("schema_key") == "child_schema"
    )
    assert any(c.id == "ChildClass" for c in child_pkg.children)


def test_dsp_explorer_nests_is_a_hierarchy():
    repo = Path(__file__).resolve().parents[3]
    schema = (
        repo
        / "model-assets"
        / "specifications"
        / "moex-dsp"
        / "0.1"
        / "schemas"
        / "moex-dsp.yaml"
    )
    if not schema.is_file():
        return
    sec = _section(
        type="explorer",
        source={"format": "linkml-yaml", "path": str(schema), "select": "classes"},
    )
    out = LinkmlNormalizer().normalize(sec, schema)
    classes_root = next(g for g in out.items if g.id == "group:classes")
    assert classes_root.children
    pkg = classes_root.children[0]
    assert pkg.id == "group:moex_dsp"
    named = next(c for c in pkg.children if c.id == "NamedElement")
    kid_ids = {c.id for c in named.children}
    assert "CatalogNode" in kid_ids
    assert "PublicationModule" in kid_ids
    catalog = next(c for c in named.children if c.id == "CatalogNode")
    assert any(c.id == "ReferenceSpecification" for c in catalog.children)


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
    assert [g.id for g in out.items[:6]] == [
        "group:overview",
        "group:classes",
        "section:glossary",
        "group:spec-files",
        "group:requirements",
        "group:implementations",
    ]
    overview = out.items[0]
    assert overview.attributes.get("section_root") == "overview"
    assert "section_id" not in (overview.attributes or {})
    kids = overview.children
    assert [c.attributes.get("section_id") for c in kids] == [
        "overview",
        "classes",
        "slots",
        "enums",
    ]
    assert all(c.attributes.get("kind") == "section_ref" for c in kids)
    assert [c.title for c in kids] == [
        "Overview",
        "All classes",
        "All slots",
        "All enumerations",
    ]
    assert "group:overview-glossary" not in {c.id for c in kids}
    gloss_ref = out.items[2]
    assert gloss_ref.id == "section:glossary"
    assert gloss_ref.title == "Глоссарий"
    assert gloss_ref.attributes.get("section_id") == "glossary"
    assert gloss_ref.attributes.get("kind") == "section_ref"
    assert "nav_glyph" not in (gloss_ref.attributes or {})

    classes_root = next(g for g in out.items if g.id == "group:classes")
    titles = {g.title for g in classes_root.children}
    assert "Core" in titles
    assert "Registries" in titles
    assert "Requirements" in titles
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

    classes = {}
    for g in classes_root.children:
        classes.update(_walk_classes(g.children))
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
    assert envelope.title == "Конверт спецификации"
    assert envelope.attributes.get("file_name") == "specification.yaml"
    assert "specification_kind" in (envelope.attributes.get("text") or "")
    assert "file:schemas/moex-dams.yaml" in (envelope.attributes.get("refs_out") or [])

    req_root = next(g for g in out.items if g.id == "group:requirements")
    assert {c.id for c in req_root.children} == {
        "group:requirements-conceptual",
        "group:requirements-it-solutions",
        "group:requirements-publication",
    }
    conceptual = next(
        c for c in req_root.children if c.id == "group:requirements-conceptual"
    )
    assert {c.id for c in conceptual.children} == {
        "group:requirements-conceptual-list",
        "group:requirements-conceptual-spec",
    }
    it = next(c for c in req_root.children if c.id == "group:requirements-it-solutions")
    assert {c.id for c in it.children} == {
        "group:requirements-list",
        "group:requirements-it-spec",
        "group:requirements-model-example",
    }
    list_group = next(c for c in it.children if c.id == "group:requirements-list")
    assert any(
        c.id == "group:requirements-section-GEN"
        and c.attributes.get("group_style") == "section_folder"
        for c in list_group.children
    )
    gen_group = next(
        c for c in list_group.children if c.id == "group:requirements-section-GEN"
    )
    assert any(c.attributes.get("code") == "GEN-001" for c in gen_group.children)

    pub = next(
        c for c in req_root.children if c.id == "group:requirements-publication"
    )
    assert {c.id for c in pub.children} == {
        "group:requirements-publication-list",
        "group:requirements-publication-spec",
    }

    impls_root = next(g for g in out.items if g.id == "group:implementations")
    assert impls_root.children == []  # filled at build time

    assert "SpecificationRequirement" in classes
    lifecycle = classes["HasLifecycle"]
    assert lifecycle.attributes.get("mixin") is True
    assert lifecycle.attributes.get("is_a") in (None, "")


def test_json_fibo_profile_explorer_wraps_roots(tmp_path: Path):
    repo = Path(__file__).resolve().parents[3]
    src = (
        repo
        / "model-assets"
        / "specifications"
        / "moex-fibo-profile"
        / "0.1"
        / "publications"
        / "fibo_profile_explorer.json"
    )
    p = tmp_path / "fibo_profile_explorer.json"
    p.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    sec = _section(
        type="explorer",
        source={"format": "json", "path": "fibo_profile_explorer.json"},
        tags=["fibo-profile", "ontology"],
    )
    out = JsonNormalizer().normalize(sec, p)
    ids = [i.id for i in out.items]
    assert ids == [
        "group:overview",
        "group:classes",
        "group:schema-files",
        "group:identity",
        "group:implementations",
    ]
    assert "group:taxonomy" not in ids
    assert "group:glossary" not in ids
    classes = next(i for i in out.items if i.id == "group:classes")
    assert classes.children == []
    modules = next(i for i in out.items if i.id == "group:schema-files")
    assert any(c.id == "group:fibo-domains" for c in modules.children)
    assert any(c.id == "domain:FND" for c in modules.children[0].children)
    identity = next(i for i in out.items if i.id == "group:identity")
    assert {c.id for c in identity.children} >= {
        "group:fibo-patterns",
        "group:fibo-annotations",
    }
    overview = next(i for i in out.items if i.id == "group:overview")
    assert "section_id" not in (overview.attributes or {})
    gloss = next(c for c in overview.children if c.id == "group:overview-glossary")
    assert gloss.children[0].attributes.get("section_id") == "glossary"
