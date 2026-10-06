"""Schema semantic-diff classification fixtures (phase-1-tail table)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from moex_modeling import ChangeCategory
from moex_dams.application.schema_diff import diff_schemas, recommend_version


_MINIMAL_PREFIX = """
id: https://example.org/schema-diff-fixture
name: schema_diff_fixture
prefixes:
  ex: https://example.org/
  linkml: https://w3id.org/linkml/
default_prefix: ex
default_range: string
"""


def _write_schema(path: Path, body: dict[str, Any]) -> Path:
    data = yaml.safe_load(_MINIMAL_PREFIX) or {}
    data.update(body)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def test_remove_class_breaking(tmp_path: Path) -> None:
    left = _write_schema(
        tmp_path / "left.yaml",
        {"classes": {"Keep": {}, "Gone": {"description": "x"}}},
    )
    right = _write_schema(tmp_path / "right.yaml", {"classes": {"Keep": {}}})
    result = diff_schemas(left, right)
    removes = [c for c in result.report.changes if c.change_code.endswith("CLASS-REMOVE")]
    assert removes and removes[0].category is ChangeCategory.BREAKING
    assert recommend_version(result.report) == "major"


def test_remove_slot_and_enum_value_breaking(tmp_path: Path) -> None:
    left = _write_schema(
        tmp_path / "left.yaml",
        {
            "classes": {"Thing": {"slots": ["a", "b"]}},
            "slots": {"a": {"range": "string"}, "b": {"range": "string"}},
            "enums": {
                "Kind": {
                    "permissible_values": {"one": {}, "two": {}},
                }
            },
        },
    )
    right = _write_schema(
        tmp_path / "right.yaml",
        {
            "classes": {"Thing": {"slots": ["a"]}},
            "slots": {"a": {"range": "string"}},
            "enums": {"Kind": {"permissible_values": {"one": {}}}},
        },
    )
    result = diff_schemas(left, right)
    codes = {c.change_code for c in result.report.changes}
    assert "DAMS-SCHEMA-SLOT-REMOVE" in codes
    assert "DAMS-SCHEMA-ENUM-VALUE-REMOVE" in codes
    assert result.has_breaking


def test_rename_without_replaced_by_is_delete_plus_add(tmp_path: Path) -> None:
    left = _write_schema(
        tmp_path / "left.yaml",
        {
            "classes": {"Thing": {"slots": ["old_name"]}},
            "slots": {"old_name": {"range": "string"}},
        },
    )
    right = _write_schema(
        tmp_path / "right.yaml",
        {
            "classes": {"Thing": {"slots": ["new_name"]}},
            "slots": {"new_name": {"range": "string"}},
        },
    )
    result = diff_schemas(left, right)
    codes = {c.change_code for c in result.report.changes}
    assert "DAMS-SCHEMA-SLOT-REMOVE" in codes
    assert "DAMS-SCHEMA-SLOT-ADD" in codes
    assert any(c.category is ChangeCategory.BREAKING for c in result.report.changes)


def test_incompatible_range_breaking(tmp_path: Path) -> None:
    left = _write_schema(
        tmp_path / "left.yaml",
        {"slots": {"x": {"range": "string"}}, "classes": {"T": {"slots": ["x"]}}},
    )
    right = _write_schema(
        tmp_path / "right.yaml",
        {"slots": {"x": {"range": "integer"}}, "classes": {"T": {"slots": ["x"]}}},
    )
    result = diff_schemas(left, right)
    ranges = [c for c in result.report.changes if c.change_code == "DAMS-SCHEMA-SLOT-RANGE"]
    assert ranges and ranges[0].category is ChangeCategory.BREAKING


def test_cardinality_tighten_and_relax(tmp_path: Path) -> None:
    left = _write_schema(
        tmp_path / "left.yaml",
        {
            "slots": {
                "opt": {"range": "string", "required": False},
                "multi": {"range": "string", "multivalued": True},
            },
            "classes": {"T": {"slots": ["opt", "multi"]}},
        },
    )
    right = _write_schema(
        tmp_path / "right.yaml",
        {
            "slots": {
                "opt": {"range": "string", "required": True},
                "multi": {"range": "string", "multivalued": False},
            },
            "classes": {"T": {"slots": ["opt", "multi"]}},
        },
    )
    result = diff_schemas(left, right)
    codes = {c.change_code: c.category for c in result.report.changes}
    assert codes["DAMS-SCHEMA-SLOT-REQUIRED"] is ChangeCategory.BREAKING
    assert codes["DAMS-SCHEMA-SLOT-SINGLE"] is ChangeCategory.BREAKING

    relaxed = diff_schemas(right, left)
    r_codes = {c.change_code: c.category for c in relaxed.report.changes}
    assert r_codes["DAMS-SCHEMA-SLOT-OPTIONAL"] is ChangeCategory.BACKWARD_COMPATIBLE
    assert r_codes["DAMS-SCHEMA-SLOT-MULTI"] is ChangeCategory.BACKWARD_COMPATIBLE
    assert recommend_version(relaxed.report) == "minor"


def test_additive_optional_field_class_enum_value(tmp_path: Path) -> None:
    left = _write_schema(
        tmp_path / "left.yaml",
        {
            "classes": {"Old": {}},
            "slots": {},
            "enums": {"K": {"permissible_values": {"a": {}}}},
        },
    )
    right = _write_schema(
        tmp_path / "right.yaml",
        {
            "classes": {"Old": {"slots": ["extra"]}, "New": {}},
            "slots": {"extra": {"range": "string", "required": False}},
            "enums": {"K": {"permissible_values": {"a": {}, "b": {}}}},
        },
    )
    result = diff_schemas(left, right)
    assert result.has_breaking is False
    assert any(c.change_code == "DAMS-SCHEMA-CLASS-ADD" for c in result.report.changes)
    assert any(c.change_code == "DAMS-SCHEMA-SLOT-ADD" for c in result.report.changes)
    assert any(
        c.change_code == "DAMS-SCHEMA-ENUM-VALUE-ADD" for c in result.report.changes
    )
    assert recommend_version(result.report) == "minor"


def test_cosmetic_description_and_tags(tmp_path: Path) -> None:
    left = _write_schema(
        tmp_path / "left.yaml",
        {
            "classes": {"T": {"description": "old", "slots": ["x"]}},
            "slots": {
                "x": {
                    "range": "string",
                    "description": "a",
                    "annotations": {"note": "t1"},
                }
            },
        },
    )
    right = _write_schema(
        tmp_path / "right.yaml",
        {
            "classes": {"T": {"description": "new", "slots": ["x"]}},
            "slots": {
                "x": {
                    "range": "string",
                    "description": "b",
                    "annotations": {"note": "t2"},
                }
            },
        },
    )
    result = diff_schemas(left, right)
    assert result.has_breaking is False
    assert all(c.category is ChangeCategory.NON_BREAKING for c in result.report.changes)
    assert recommend_version(result.report) == "patch"


def test_slot_marked_deprecated(tmp_path: Path) -> None:
    left = _write_schema(
        tmp_path / "left.yaml",
        {"slots": {"x": {"range": "string"}}, "classes": {"T": {"slots": ["x"]}}},
    )
    right = _write_schema(
        tmp_path / "right.yaml",
        {
            "slots": {"x": {"range": "string", "deprecated": "use y"}},
            "classes": {"T": {"slots": ["x"]}},
        },
    )
    result = diff_schemas(left, right)
    deps = [c for c in result.report.changes if c.change_code.endswith("DEPRECATED")]
    assert deps and deps[0].category is ChangeCategory.DEPRECATION
    assert result.has_breaking is False
    assert recommend_version(result.report) == "patch"


def test_remove_previously_deprecated_marked(tmp_path: Path) -> None:
    left = _write_schema(
        tmp_path / "left.yaml",
        {
            "classes": {"Legacy": {"deprecated": "gone"}},
            "slots": {"old": {"range": "string", "deprecated": "gone"}},
            "enums": {"E": {"deprecated": "gone", "permissible_values": {"a": {}}}},
        },
    )
    right = _write_schema(tmp_path / "right.yaml", {"classes": {}, "slots": {}, "enums": {}})
    result = diff_schemas(left, right)
    msgs = [c.message for c in result.report.changes if c.category is ChangeCategory.BREAKING]
    assert any("was deprecated" in m for m in msgs)
    assert result.has_breaking


def test_changelog_covers_breaking(tmp_path: Path) -> None:
    left = _write_schema(
        tmp_path / "left.yaml",
        {"classes": {"LegacyWidget": {}}},
    )
    right = _write_schema(tmp_path / "right.yaml", {"classes": {}})
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(
        "Breaking: removed LegacyWidget class.\n",
        encoding="utf-8",
    )
    result = diff_schemas(
        left,
        right,
        changelog_path=changelog,
        has_compatibility_baseline_ref=False,
    )
    assert result.has_breaking
    assert result.uncovered_breaking == ()
