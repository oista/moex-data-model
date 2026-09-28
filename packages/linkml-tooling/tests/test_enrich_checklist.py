"""Tests for enrich checklist analyzer."""

from __future__ import annotations

from moex_linkml_tooling.enrich_checklist import (
    build_enrich_checklist,
    checklist_summary_diagnostics,
)


MINI_SCHEMA = """
id: http://example.org/inferred
name: MiniInferred
classes:
  Person:
    attributes:
      name:
        range: string
      code:
        range: string
  ITSystem:
    attributes:
      title:
        range: string
"""


def test_build_enrich_checklist_covers_fields() -> None:
    items = build_enrich_checklist(MINI_SCHEMA)
    codes = {i.code for i in items}
    assert "IMPORT-ENRICH-DESC" in codes
    assert "IMPORT-ENRICH-RANGE" in codes
    assert "IMPORT-ENRICH-ID" in codes
    assert "IMPORT-ENRICH-REGISTRY" in codes
    fields = {i.field for i in items}
    assert fields >= {"description", "range", "id", "registry_link"}
    assert any(i.path.startswith("classes.ITSystem") for i in items)
    assert any("Person" in i.path for i in items)


def test_checklist_summary_diagnostic() -> None:
    items = build_enrich_checklist(MINI_SCHEMA)
    diags = checklist_summary_diagnostics(items)
    assert len(diags) == 1
    assert diags[0].diagnostic_code == "IMPORT-ENRICH-SUMMARY"
    assert "enrich checklist" in diags[0].diagnostic_message


def test_empty_checklist_when_enriched() -> None:
    schema = """
name: Good
classes:
  Widget:
    description: A widget
    class_uri: https://example.org/Widget
    attributes:
      id:
        identifier: true
        range: uriorcurie
        description: Stable id
      label:
        range: string
        description: Display label
"""
    items = build_enrich_checklist(schema)
    # label still has range string → range warning expected; id/desc/uri ok
    assert all(i.code != "IMPORT-ENRICH-ID" for i in items)
    assert all(
        not (i.code == "IMPORT-ENRICH-DESC" and i.path == "classes.Widget")
        for i in items
    )
    assert any(i.code == "IMPORT-ENRICH-RANGE" for i in items)
