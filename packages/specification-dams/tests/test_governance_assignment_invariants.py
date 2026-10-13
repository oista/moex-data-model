"""INV-054…INV-056 governance assignment L2 fixtures (ADR-049; renumbered on land)."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_dams.application.diff import diff_governance_assignments
from moex_dams.rules.constraint_matrix import _collect_invariant_ids, _run_l2_package_checks

ROOT = Path(__file__).resolve().parents[3]
L2 = ROOT / "model-assets/specifications/moex-dams/0.1/examples/invariants/l2"


def _load(name: str) -> dict:
    return yaml.safe_load((L2 / name).read_text(encoding="utf-8"))


def test_inv_054_through_056_fixtures() -> None:
    for iid in ("INV-054", "INV-055", "INV-056"):
        valid = _load(f"{iid}.valid.yaml")
        invalid = _load(f"{iid}.invalid.yaml")
        assert iid not in _collect_invariant_ids(_run_l2_package_checks(valid)), iid
        assert iid in _collect_invariant_ids(_run_l2_package_checks(invalid)), iid


def test_diff_governance_assignments_add_remove_change() -> None:
    left = {
        "classification_assignments": [
            {
                "assignment_id": "dams:asg/1",
                "target_element_ref": "dams:logical/X",
                "governance_classification": "internal",
            }
        ]
    }
    right = {
        "classification_assignments": [
            {
                "assignment_id": "dams:asg/1",
                "target_element_ref": "dams:logical/X",
                "governance_classification": "confidential",
            },
            {
                "assignment_id": "dams:asg/2",
                "target_element_ref": "dams:logical/Y",
                "governance_classification": "public",
            },
        ]
    }
    codes = {c.change_code for c in diff_governance_assignments(left, right)}
    assert "DAMS-DIFF-ASG-CHANGE" in codes
    assert "DAMS-DIFF-ASG-ADD" in codes
    codes_rm = {
        c.change_code for c in diff_governance_assignments(right, left)
    }
    assert "DAMS-DIFF-ASG-REMOVE" in codes_rm
