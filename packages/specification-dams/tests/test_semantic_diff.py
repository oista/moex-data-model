"""Semantic diff classification over mdm solution mutations."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

from moex_modeling import ChangeCategory
from moex_dams.application.diff import diff_implementations


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _write_yaml(path: Path, data: dict[str, Any]) -> Path:
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return path


def _logical_enterprise(data: dict[str, Any]) -> dict[str, Any]:
    for entity in data.get("logical_entities") or []:
        if entity.get("element_id") == "dams:logical/mdm/ENTERPRISE":
            return entity
    raise AssertionError("ENTERPRISE logical entity missing")


def _attr(entity: dict[str, Any], element_id: str) -> dict[str, Any]:
    for attr in entity.get("attributes") or []:
        if attr.get("element_id") == element_id:
            return attr
    raise AssertionError(f"attribute {element_id} missing")


def test_identical_no_changes(
    dams_schema: Path, mdm_solution: Path, tmp_path: Path
) -> None:
    left = tmp_path / "left.yaml"
    right = tmp_path / "right.yaml"
    text = mdm_solution.read_text(encoding="utf-8")
    left.write_text(text, encoding="utf-8")
    right.write_text(text, encoding="utf-8")
    report = diff_implementations(
        schema_path=dams_schema,
        left_path=left,
        right_path=right,
    )
    assert report.changes == ()
    assert report.has_breaking is False


def test_remove_attribute_breaking(
    dams_schema: Path, mdm_solution: Path, tmp_path: Path
) -> None:
    left = _write_yaml(tmp_path / "left.yaml", _load_yaml(mdm_solution))
    data = _load_yaml(mdm_solution)
    client = _logical_enterprise(data)
    client["attributes"] = [
        a
        for a in client["attributes"]
        if a.get("element_id") != "dams:logical/mdm/ENTERPRISE/SHORT_NAME"
    ]
    right = _write_yaml(tmp_path / "right.yaml", data)
    report = diff_implementations(
        schema_path=dams_schema,
        left_path=left,
        right_path=right,
    )
    removes = [
        c
        for c in report.changes
        if c.change_code == "DAMS-DIFF-REMOVE"
        and c.subject_ref == "dams:logical/mdm/ENTERPRISE/SHORT_NAME"
    ]
    assert removes
    assert removes[0].category is ChangeCategory.BREAKING
    assert report.has_breaking is True


def test_add_optional_attribute_compatible(
    dams_schema: Path, mdm_solution: Path, tmp_path: Path
) -> None:
    left = _write_yaml(tmp_path / "left.yaml", _load_yaml(mdm_solution))
    data = _load_yaml(mdm_solution)
    client = _logical_enterprise(data)
    client["attributes"].append(
        {
            "element_id": "dams:logical/mdm/ENTERPRISE/nickname",
            "name": "nickname",
            "title": "Nickname",
            "description": "Optional nickname",
            "lifecycle_status": "active",
            "owner_entity_ref": "dams:logical/mdm/ENTERPRISE",
            "data_type_ref": "dams:datatype/string",
            "required": False,
            "multivalued": False,
        }
    )
    right = _write_yaml(tmp_path / "right.yaml", data)
    report = diff_implementations(
        schema_path=dams_schema,
        left_path=left,
        right_path=right,
    )
    adds = [
        c
        for c in report.changes
        if c.change_code == "DAMS-DIFF-ADD"
        and c.subject_ref == "dams:logical/mdm/ENTERPRISE/nickname"
    ]
    assert len(adds) == 1
    assert adds[0].category is ChangeCategory.BACKWARD_COMPATIBLE
    assert report.has_breaking is False


def test_required_true_is_breaking(
    dams_schema: Path, mdm_solution: Path, tmp_path: Path
) -> None:
    data = _load_yaml(mdm_solution)
    # Start from optional, then flip to required.
    client = _logical_enterprise(data)
    attr = _attr(client, "dams:logical/mdm/ENTERPRISE/ENTERPRISE_ID")
    attr["required"] = False
    left = _write_yaml(tmp_path / "left.yaml", data)
    data2 = copy.deepcopy(data)
    _attr(_logical_enterprise(data2), "dams:logical/mdm/ENTERPRISE/ENTERPRISE_ID")["required"] = True
    right = _write_yaml(tmp_path / "right.yaml", data2)
    report = diff_implementations(
        schema_path=dams_schema,
        left_path=left,
        right_path=right,
    )
    req = [c for c in report.changes if c.change_code == "DAMS-DIFF-REQUIRED"]
    assert req
    assert req[0].category is ChangeCategory.BREAKING


def test_description_only_non_breaking(
    dams_schema: Path, mdm_solution: Path, tmp_path: Path
) -> None:
    left = _write_yaml(tmp_path / "left.yaml", _load_yaml(mdm_solution))
    data = _load_yaml(mdm_solution)
    _logical_enterprise(data)["description"] = "Updated documentation only."
    right = _write_yaml(tmp_path / "right.yaml", data)
    report = diff_implementations(
        schema_path=dams_schema,
        left_path=left,
        right_path=right,
    )
    docs = [c for c in report.changes if c.change_code == "DAMS-DIFF-DOC"]
    assert docs
    assert docs[0].category is ChangeCategory.NON_BREAKING
    assert report.has_breaking is False


def test_governance_change(
    dams_schema: Path, mdm_solution: Path, tmp_path: Path
) -> None:
    left = _write_yaml(tmp_path / "left.yaml", _load_yaml(mdm_solution))
    data = _load_yaml(mdm_solution)
    _logical_enterprise(data)["governance_classification"] = "restricted"
    right = _write_yaml(tmp_path / "right.yaml", data)
    report = diff_implementations(
        schema_path=dams_schema,
        left_path=left,
        right_path=right,
    )
    gov = [c for c in report.changes if c.change_code == "DAMS-DIFF-GOV"]
    assert gov
    assert gov[0].category is ChangeCategory.GOVERNANCE


def test_clearing_was_deprecated_slots_is_breaking(
    dams_schema: Path, tmp_path: Path
) -> None:
    """PR-5: removing formerly-deprecated attr keys is BREAKING + 'was deprecated'."""
    left_data = {
        "element_id": "dams:model/t/0.1",
        "name": "t",
        "implementation_scope": "solution",
        "logical_entities": [
            {
                "element_id": "dams:logical/t/E",
                "name": "E",
                "description": "e",
                "lifecycle_status": "active",
                "attributes": [
                    {
                        "element_id": "dams:logical/t/E/a",
                        "name": "a",
                        "description": "a",
                        "lifecycle_status": "active",
                        "owner_entity_ref": "dams:logical/t/E",
                        "logical_type": "string",
                        "data_type_ref": "dams:datatype/string",
                        "required": True,
                        "multivalued": False,
                    }
                ],
            }
        ],
    }
    right_data = copy.deepcopy(left_data)
    del right_data["logical_entities"][0]["attributes"][0]["logical_type"]
    left = _write_yaml(tmp_path / "left.yaml", left_data)
    right = _write_yaml(tmp_path / "right.yaml", right_data)
    report = diff_implementations(
        schema_path=dams_schema,
        left_path=left,
        right_path=right,
    )
    hits = [
        c
        for c in report.changes
        if c.change_code == "DAMS-DIFF-DEPRECATE-REMOVE"
    ]
    assert hits
    assert hits[0].category is ChangeCategory.BREAKING
    assert "was deprecated" in hits[0].message
    assert report.has_breaking is True
