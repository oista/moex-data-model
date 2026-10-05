"""Ontology profile + schema URI semantic diff."""

from __future__ import annotations

from pathlib import Path

from moex_dams.application.ontology_report import (
    build_ontology_profile,
    diff_schema_element_uris,
    write_ontology_profile,
)
from moex_modeling import ChangeCategory


def test_build_ontology_profile_for_dams(dams_schema: Path) -> None:
    profile = build_ontology_profile(dams_schema)
    assert profile["schema_name"] == "moex_dams"
    assert profile["default_prefix"] == "dams"
    assert profile["schema_digest"].startswith("sha256:")
    assert any(c["name"] == "LogicalEntity" for c in profile["classes"])
    assert any(c.get("is_mixin") for c in profile["classes"])
    assert any(e["name"] == "ApprovalStatusEnum" for e in profile["enums"])
    assert profile["issues"] == []


def test_write_ontology_profile_deterministic(dams_schema: Path, tmp_path: Path) -> None:
    json_path = tmp_path / "ontology-profile.json"
    md_path = tmp_path / "ontology-profile.md"
    d1 = write_ontology_profile(dams_schema, json_path=json_path, md_path=md_path)
    d2 = write_ontology_profile(dams_schema, json_path=json_path, md_path=md_path)
    assert d1 == d2
    assert json_path.is_file()
    assert md_path.is_file()
    assert "Ontology profile" in md_path.read_text(encoding="utf-8")


def test_uri_diff_rename_is_breaking(tmp_path: Path) -> None:
    old = tmp_path / "old.yaml"
    new = tmp_path / "new.yaml"
    old.write_text(
        """
id: https://example.com/old
name: old
prefixes:
  ex: https://example.com/
default_prefix: ex
classes:
  Person:
    attributes:
      name:
        range: string
""",
        encoding="utf-8",
    )
    new.write_text(
        """
id: https://example.com/new
name: new
prefixes:
  ex: https://example.com/
default_prefix: ex
classes:
  Human:
    attributes:
      name:
        range: string
""",
        encoding="utf-8",
    )
    report = diff_schema_element_uris(old, new)
    assert report.has_breaking
    codes = {c.change_code for c in report.changes}
    assert "MOEX-ONT-010" in codes
    assert any(c.category is ChangeCategory.BREAKING for c in report.changes)
    assert any(c.category is ChangeCategory.NON_BREAKING for c in report.changes)
