"""Tests for migrate_logical_attribute_semantics.py."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from migrate_logical_attribute_semantics import (  # noqa: E402
    is_denied,
    migrate_package,
)


def test_denylist_moex_dams_full(tmp_path: Path):
    p = tmp_path / "moex-dams-full.yaml"
    p.write_text("element_id: x\n", encoding="utf-8")
    assert is_denied(p)


def test_migrate_attr_without_domain():
    data = {
        "implementation_scope": "solution",
        "logical_entities": [
            {
                "element_id": "dams:logical/t/E",
                "attributes": [
                    {
                        "element_id": "dams:logical/t/E/a",
                        "name": "a",
                        "logical_type": "string",
                        "required": True,
                        "multivalued": False,
                    }
                ],
            }
        ],
    }
    report = migrate_package(data, apply=True)
    assert report["attributes_before"] == 1
    attr = data["logical_entities"][0]["attributes"][0]
    assert attr["data_type_ref"] == "dams:datatype/string"
    assert "logical_type" not in attr
    assert "value_domain_ref" not in attr
    report2 = migrate_package(data, apply=True)
    assert report2["attrs_updated"] == []


def test_migrate_attr_with_format():
    data = {
        "logical_entities": [
            {
                "element_id": "dams:logical/t/E",
                "attributes": [
                    {
                        "element_id": "dams:logical/t/E/a",
                        "name": "a",
                        "logical_type": "string",
                        "format_pattern": r"\d{10}",
                        "required": True,
                        "multivalued": False,
                    }
                ],
            }
        ],
    }
    report = migrate_package(data, apply=True)
    attr = data["logical_entities"][0]["attributes"][0]
    assert attr.get("value_domain_ref")
    assert attr.get("data_type_ref") == "dams:datatype/string"
    assert "format_pattern" not in attr
    assert "logical_type" not in attr
    assert report["domains_created"]
    vd = data["value_domains"][0]
    assert "generated" in (vd.get("tags") or [])
    assert vd["format_pattern"] == r"\d{10}"


def test_propose_identifying():
    data = {
        "name": "solA",
        "solution_ref": "solA",
        "logical_entities": [
            {
                "element_id": "dams:logical/a/E",
                "key_attribute_refs": ["dams:logical/a/E/id"],
                "attributes": [
                    {
                        "element_id": "dams:logical/a/E/id",
                        "name": "inn",
                        "data_type_ref": "dams:datatype/string",
                        "required": True,
                        "multivalued": False,
                    }
                ],
            }
        ],
    }
    report = migrate_package(data, apply=False)
    assert any("identifying" in (p.get("basis") or []) for p in report["proposed_properties"])


def test_denylist_does_not_mutate(tmp_path: Path):
    # script main path — unit for is_denied only
    p = tmp_path / "moex-dams-full.yaml"
    p.write_text("# не редактировать вручную\nx: 1\n", encoding="utf-8")
    assert is_denied(p)


def test_apply_with_binding_issues_new_revision():
    data = {
        "implementation_scope": "solution",
        "logical_entities": [
            {
                "element_id": "dams:logical/t/E",
                "attributes": [
                    {
                        "element_id": "dams:logical/t/E/a",
                        "name": "a",
                        "logical_type": "string",
                        "required": True,
                        "multivalued": False,
                    }
                ],
            }
        ],
        "data_model_bindings": [
            {
                "element_id": "dams:binding/t/1.0.0",
                "model_package_ref": "pkg",
                "model_version": "0.1.0",
                "model_revision": "oldrev",
                "selections": [],
                "compatibility_mode": "backward",
                "integrity_digest": "sha256:" + ("a" * 64),
            }
        ],
    }
    report = migrate_package(data, apply=True, demo=False)
    assert report["attrs_updated"] or report.get("deprecated_keys_stripped")
    b = data["data_model_bindings"][0]
    assert b["model_revision"] != "oldrev"
    assert b["compatibility_baseline_ref"].endswith("/rev/oldrev")
    assert any("NEW_REVISION" in line for line in report["binding_revisions"])
    assert "logical_type" not in data["logical_entities"][0]["attributes"][0]
