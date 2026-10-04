"""Tests for edit_targets emission from YAML / LinkML normalizers."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_publication_viewer.models.manifest_models import ManifestSection, SourceSpec
from moex_publication_viewer.normalizers.csv_normalizer import CsvNormalizer
from moex_publication_viewer.normalizers.linkml_normalizer import LinkmlNormalizer
from moex_publication_viewer.normalizers.yaml_normalizer import YamlNormalizer


def _section(**kwargs) -> ManifestSection:
    defaults = {
        "id": "s",
        "title": "S",
        "type": "entity-table",
        "source": SourceSpec(format="yaml", path="x"),
        "key_column": "element_id",
    }
    defaults.update(kwargs)
    if isinstance(defaults["source"], dict):
        defaults["source"] = SourceSpec(**defaults["source"])
    return ManifestSection(**defaults)


def test_yaml_list_emits_edit_targets(tmp_path: Path):
    p = tmp_path / "model.yaml"
    p.write_text(
        yaml.dump(
            {
                "logical_entities": [
                    {
                        "element_id": "dams:logical/A",
                        "name": "A",
                        "title": "Alpha",
                        "description": "First",
                        "aliases": ["aka"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    sec = _section(
        source={"format": "yaml", "path": "model.yaml", "select": "logical_entities"},
        key_column="element_id",
    )
    out = YamlNormalizer().normalize(sec, p)
    assert len(out.items) == 1
    et = out.items[0].edit_targets
    assert et is not None
    assert set(et) == {"description", "title", "aliases"}
    assert et["description"]["yaml_path"] == (
        "logical_entities[element_id=dams:logical/A].description"
    )
    assert et["title"]["field"] == "title"
    assert "model.yaml" in et["description"]["file"].replace("\\", "/")
    assert et["aliases"]["yaml_path"].endswith(".aliases")


def test_model_glossary_select_has_no_edit_targets(tmp_path: Path):
    p = tmp_path / "model.yaml"
    p.write_text(
        yaml.dump(
            {
                "conceptual_entities": [
                    {
                        "element_id": "dams:concept/T",
                        "name": "T",
                        "title": "Term",
                        "description": "Def",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    sec = _section(
        type="glossary",
        source={"format": "yaml", "path": "model.yaml", "select": "model_glossary"},
    )
    out = YamlNormalizer().normalize(sec, p)
    assert out.items
    assert all(i.edit_targets is None for i in out.items)


def test_csv_has_no_edit_targets(tmp_path: Path):
    p = tmp_path / "rows.csv"
    p.write_text("id,name,description\n1,A,d\n", encoding="utf-8")
    sec = _section(
        source={"format": "csv", "path": "rows.csv"},
        columns=["id", "name", "description"],
    )
    out = CsvNormalizer().normalize(sec, p)
    assert out.items
    assert all(getattr(i, "edit_targets", None) is None for i in out.items)


def test_linkml_class_edit_targets_use_package_file(tmp_path: Path):
    """Class defined in package file, not the root aggregator."""
    schemas = tmp_path / "schemas"
    schemas.mkdir()
    (schemas / "pkg-core.yaml").write_text(
        """
id: https://example.org/pkg-core
name: pkg_core
prefixes:
  linkml: https://w3id.org/linkml/
  ex: https://example.org/
default_prefix: ex
classes:
  Foo:
    description: A foo class
    aliases:
      - FooAlias
""",
        encoding="utf-8",
    )
    (schemas / "pkg-root.yaml").write_text(
        """
id: https://example.org/pkg-root
name: pkg_root
imports:
  - pkg-core
""",
        encoding="utf-8",
    )
    sec = _section(
        type="entity-table",
        source={"format": "linkml-yaml", "path": "schemas/pkg-root.yaml", "select": "classes"},
    )
    out = LinkmlNormalizer().normalize(sec, schemas / "pkg-root.yaml")
    foo = next(i for i in out.items if i.id == "Foo")
    assert foo.edit_targets is not None
    assert "description" in foo.edit_targets
    assert "aliases" in foo.edit_targets
    assert "title" not in foo.edit_targets
    assert foo.edit_targets["description"]["yaml_path"] == "classes.Foo.description"
    file_posix = foo.edit_targets["description"]["file"].replace("\\", "/")
    assert file_posix.endswith("pkg-core.yaml")
    assert not file_posix.endswith("pkg-root.yaml")
