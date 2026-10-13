"""Tests for ADR-044 redundant mixin lint."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import yaml

from architecture_check.redundant_mixins import check_redundant_mixins

REPO = Path(__file__).resolve().parents[3]


def test_redundant_mixins_clean_on_current_schema():
    assert check_redundant_mixins(REPO) == []


def test_detects_mixin_already_induced_via_isa(tmp_path: Path):
    schemas = tmp_path / "model-assets/specifications/moex-dams/0.1/schemas"
    schemas.mkdir(parents=True)
    # Minimal LinkML graph: Parent mixins HasX; Child is_a Parent and re-lists HasX.
    (schemas / "moex-dams.yaml").write_text(
        dedent(
            """
            id: https://example.com/test
            name: test
            prefixes:
              linkml: https://w3id.org/linkml/
              ex: https://example.com/
            imports:
              - linkml:types
            default_prefix: ex
            default_range: string
            classes:
              HasX:
                mixin: true
                slots: [x]
              Parent:
                mixins: [HasX]
              Child:
                is_a: Parent
                mixins: [HasX]
            slots:
              x:
                range: string
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    errs = check_redundant_mixins(tmp_path)
    assert any("Child" in e and "HasX" in e and "is_a" in e for e in errs), errs


def test_detects_mixin_induced_by_sibling(tmp_path: Path):
    schemas = tmp_path / "model-assets/specifications/moex-dams/0.1/schemas"
    schemas.mkdir(parents=True)
    (schemas / "moex-dams.yaml").write_text(
        dedent(
            """
            id: https://example.com/test
            name: test
            prefixes:
              linkml: https://w3id.org/linkml/
              ex: https://example.com/
            imports:
              - linkml:types
            default_prefix: ex
            default_range: string
            classes:
              HasY:
                mixin: true
                slots: [y]
              HasX:
                mixin: true
                mixins: [HasY]
                slots: [x]
              Thing:
                mixins: [HasX, HasY]
            slots:
              x:
                range: string
              y:
                range: string
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    errs = check_redundant_mixins(tmp_path)
    assert any("Thing" in e and "HasY" in e and "sibling" in e for e in errs), errs


def test_synthetic_schema_parses(tmp_path: Path):
    """Sanity: yaml round-trip for fixture authoring."""
    p = tmp_path / "x.yaml"
    p.write_text("a: 1\n", encoding="utf-8")
    assert yaml.safe_load(p.read_text(encoding="utf-8")) == {"a": 1}
