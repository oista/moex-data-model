"""Schema URI / prefix lint (ADR-030)."""

from __future__ import annotations

from pathlib import Path

from moex_dams.rules.identifiers import load_merged_schema_prefix_map
from moex_dams.rules.ontology_uris import check_ontology_uris


def test_dams_schema_has_no_ontology_uri_errors(dams_schema: Path) -> None:
    diags = check_ontology_uris(dams_schema)
    assert diags == (), [d.diagnostic_message for d in diags]


def test_merged_prefix_map_includes_xsd_from_imports(dams_schema: Path) -> None:
    prefixes, default = load_merged_schema_prefix_map(dams_schema)
    assert default == "dams"
    assert prefixes["dams"].startswith("https://")
    assert prefixes["xsd"].endswith("#")
    assert "linkml" in prefixes


def test_collision_emits_moex_ont_001(tmp_path: Path) -> None:
    schema = tmp_path / "collision.yaml"
    schema.write_text(
        """
id: https://example.com/collision
name: collision
prefixes:
  ex: https://example.com/
default_prefix: ex
classes:
  Foo:
    attributes:
      x:
        range: string
slots:
  Foo:
    range: string
""",
        encoding="utf-8",
    )
    codes = [d.diagnostic_code for d in check_ontology_uris(schema)]
    assert "MOEX-ONT-001" in codes


def test_bad_class_uri_emits_moex_ont_002(tmp_path: Path) -> None:
    schema = tmp_path / "bad_uri.yaml"
    schema.write_text(
        """
id: https://example.com/bad
name: bad_uri
prefixes:
  ex: https://example.com/
default_prefix: ex
classes:
  Person:
    class_uri: zzz:Person
""",
        encoding="utf-8",
    )
    diags = check_ontology_uris(schema)
    assert any(d.diagnostic_code == "MOEX-ONT-002" for d in diags)


def test_prefix_conflict_emits_moex_ont_003(tmp_path: Path) -> None:
    child = tmp_path / "child.yaml"
    child.write_text(
        """
id: https://example.com/child
name: child
prefixes:
  ex: https://other.example.com/
default_prefix: ex
classes:
  Child:
    attributes:
      n:
        range: string
""",
        encoding="utf-8",
    )
    root = tmp_path / "root.yaml"
    root.write_text(
        """
id: https://example.com/root
name: root
prefixes:
  ex: https://example.com/
  linkml: https://w3id.org/linkml/
imports:
  - child
default_prefix: ex
classes:
  Root:
    attributes:
      n:
        range: string
""",
        encoding="utf-8",
    )
    diags = check_ontology_uris(root)
    assert any(d.diagnostic_code == "MOEX-ONT-003" for d in diags)


def test_prefix_without_terminator_emits_moex_ont_004(tmp_path: Path) -> None:
    schema = tmp_path / "bad_prefix.yaml"
    schema.write_text(
        """
id: https://example.com/badprefix
name: bad_prefix
prefixes:
  ex: https://example.com
default_prefix: ex
classes:
  Thing:
    attributes:
      n:
        range: string
""",
        encoding="utf-8",
    )
    diags = check_ontology_uris(schema)
    assert any(d.diagnostic_code == "MOEX-ONT-004" for d in diags)
