"""ADR-049: GovernanceAssignment overrides over ADR-023 cascade."""

from __future__ import annotations

from moex_dams.rules.assignment_resolver import diagnose_governance, resolve_governed


def _pkg(**overrides):
    base = {
        "element_id": "dams:model/cascade/1",
        "name": "cascade",
        "description": "cascade fixture",
        "lifecycle_status": "draft",
        "api_version": "dams.moex/v0.1",
        "model_version": "1.0.0",
        "implementation_scope": "solution",
        "solution_ref": "eam:solution/CASCADE",
        "data_owner_ref": "org:role/OWNER_A",
        "data_steward_ref": "org:role/STEWARD_S",
        "governance_classification": "internal",
        "policy_refs": ["pol:P1"],
        "logical_entities": [
            {
                "element_id": "dams:logical/cascade/X",
                "name": "X",
                "description": "entity X",
                "lifecycle_status": "draft",
                "context_ref": "dams:context/c",
                "solution_data_role": "producer",
                "attributes": [
                    {
                        "element_id": "dams:logical/cascade/X/a1",
                        "name": "a1",
                        "description": "attr a1",
                        "lifecycle_status": "draft",
                        "owner_entity_ref": "dams:logical/cascade/X",
                        "data_type_ref": "dams:datatype/string",
                        "required": False,
                        "multivalued": False,
                    },
                    {
                        "element_id": "dams:logical/cascade/X/a2",
                        "name": "a2",
                        "description": "attr a2",
                        "lifecycle_status": "draft",
                        "owner_entity_ref": "dams:logical/cascade/X",
                        "data_type_ref": "dams:datatype/string",
                        "required": False,
                        "multivalued": False,
                        "data_steward_ref": "org:role/STEWARD_T",
                        "policy_refs": ["pol:P2"],
                    },
                ],
            },
            {
                "element_id": "dams:logical/cascade/Y",
                "name": "Y",
                "description": "entity Y",
                "lifecycle_status": "draft",
                "context_ref": "dams:context/c",
                "solution_data_role": "producer",
                "data_owner_ref": "org:role/OWNER_B",
                "governance_classification": "confidential",
                "attributes": [
                    {
                        "element_id": "dams:logical/cascade/Y/y1",
                        "name": "y1",
                        "description": "attr y1",
                        "lifecycle_status": "draft",
                        "owner_entity_ref": "dams:logical/cascade/Y",
                        "data_type_ref": "dams:datatype/string",
                        "required": False,
                        "multivalued": False,
                    }
                ],
            },
        ],
    }
    base.update(overrides)
    return base


def test_no_assignments_matches_cascade() -> None:
    data = _pkg()
    resolved = resolve_governed(data)
    assert resolved["dams:logical/cascade/X/a1"]["governance_classification"].value == "internal"
    assert resolved["dams:logical/cascade/X/a1"]["governance_classification"].layer == "inline"


def test_subtree_classification_override() -> None:
    data = _pkg(
        classification_assignments=[
            {
                "assignment_id": "dams:asg/class/pkg",
                "target_element_ref": "dams:model/cascade/1",
                "assignment_scope": "subtree",
                "governance_classification": "confidential",
                "approval_status": "approved",
                "valid_from": "2026-01-01",
            }
        ]
    )
    resolved = resolve_governed(data, as_of="2026-06-01")
    a1 = resolved["dams:logical/cascade/X/a1"]
    assert a1["governance_classification"].value == "confidential"
    assert a1["governance_classification"].layer == "assignment"
    assert a1["governance_classification"].assignment_id == "dams:asg/class/pkg"
    # nearer inline override on Y still loses to package subtree assignment
    # (assignment is authoritative over cascade); element-scope exception wins:
    y = resolved["dams:logical/cascade/Y"]
    assert y["governance_classification"].value == "confidential"


def test_nearest_element_beats_subtree() -> None:
    data = _pkg(
        classification_assignments=[
            {
                "assignment_id": "dams:asg/class/pkg",
                "target_element_ref": "dams:model/cascade/1",
                "assignment_scope": "subtree",
                "governance_classification": "confidential",
                "approval_status": "approved",
            },
            {
                "assignment_id": "dams:asg/class/y",
                "target_element_ref": "dams:logical/cascade/Y",
                "assignment_scope": "element",
                "governance_classification": "public",
                "approval_status": "approved",
            },
        ]
    )
    resolved = resolve_governed(data)
    assert (
        resolved["dams:logical/cascade/Y"]["governance_classification"].value == "public"
    )
    assert (
        resolved["dams:logical/cascade/Y"]["governance_classification"].assignment_id
        == "dams:asg/class/y"
    )
    assert (
        resolved["dams:logical/cascade/X"]["governance_classification"].value
        == "confidential"
    )


def test_validity_window() -> None:
    data = _pkg(
        classification_assignments=[
            {
                "assignment_id": "dams:asg/class/win",
                "target_element_ref": "dams:logical/cascade/X",
                "assignment_scope": "subtree",
                "governance_classification": "restricted",
                "approval_status": "approved",
                "valid_from": "2026-01-01",
                "valid_to": "2026-03-31",
            }
        ]
    )
    inside = resolve_governed(data, as_of="2026-02-15")
    assert (
        inside["dams:logical/cascade/X"]["governance_classification"].value == "restricted"
    )
    outside = resolve_governed(data, as_of="2026-06-01")
    assert (
        outside["dams:logical/cascade/X"]["governance_classification"].value == "internal"
    )
    assert outside["dams:logical/cascade/X"]["governance_classification"].layer == "inline"


def test_unapproved_ignored() -> None:
    data = _pkg(
        classification_assignments=[
            {
                "assignment_id": "dams:asg/class/draft",
                "target_element_ref": "dams:logical/cascade/X",
                "assignment_scope": "element",
                "governance_classification": "restricted",
                "approval_status": "proposed",
            }
        ]
    )
    resolved = resolve_governed(data)
    assert (
        resolved["dams:logical/cascade/X"]["governance_classification"].value == "internal"
    )


def test_conflicting_assignments() -> None:
    data = _pkg(
        classification_assignments=[
            {
                "assignment_id": "dams:asg/class/a",
                "target_element_ref": "dams:logical/cascade/X",
                "assignment_scope": "element",
                "governance_classification": "confidential",
                "approval_status": "approved",
            },
            {
                "assignment_id": "dams:asg/class/b",
                "target_element_ref": "dams:logical/cascade/X",
                "assignment_scope": "element",
                "governance_classification": "public",
                "approval_status": "approved",
            },
        ]
    )
    findings = diagnose_governance(data)
    assert any(f.code == "conflicting_assignments" for f in findings)


def test_dangling_target() -> None:
    data = _pkg(
        classification_assignments=[
            {
                "assignment_id": "dams:asg/class/ghost",
                "target_element_ref": "dams:logical/missing",
                "assignment_scope": "element",
                "governance_classification": "confidential",
                "approval_status": "approved",
            }
        ]
    )
    findings = diagnose_governance(data)
    assert any(f.code == "dangling_target" for f in findings)


def test_shadowed_default() -> None:
    data = _pkg(
        classification_assignments=[
            {
                "assignment_id": "dams:asg/class/y",
                "target_element_ref": "dams:logical/cascade/Y",
                "assignment_scope": "element",
                "governance_classification": "public",
                "approval_status": "approved",
            }
        ]
    )
    # Y declares confidential inline; assignment says public
    findings = diagnose_governance(data)
    assert any(
        f.code == "shadowed_default"
        and f.element_id == "dams:logical/cascade/Y"
        and f.slot == "governance_classification"
        for f in findings
    )


def test_conflicting_policy_replace_bindings() -> None:
    data = _pkg(
        policy_bindings=[
            {
                "assignment_id": "dams:asg/pol/r1",
                "target_element_ref": "dams:logical/cascade/X",
                "assignment_scope": "element",
                "policy_ref": "pol:P3",
                "binding_effect": "replace",
                "approval_status": "approved",
            },
            {
                "assignment_id": "dams:asg/pol/r2",
                "target_element_ref": "dams:logical/cascade/X",
                "assignment_scope": "element",
                "policy_ref": "pol:P4",
                "binding_effect": "replace",
                "approval_status": "approved",
            },
        ]
    )
    findings = diagnose_governance(data)
    assert any(
        f.code == "conflicting_assignments" and f.slot == "policy_refs" for f in findings
    )


def test_policy_replace_and_add() -> None:
    data = _pkg(
        policy_bindings=[
            {
                "assignment_id": "dams:asg/pol/replace",
                "target_element_ref": "dams:logical/cascade/X",
                "assignment_scope": "subtree",
                "policy_ref": "pol:P3",
                "binding_effect": "replace",
                "approval_status": "approved",
            },
            {
                "assignment_id": "dams:asg/pol/add",
                "target_element_ref": "dams:logical/cascade/X",
                "assignment_scope": "subtree",
                "policy_ref": "pol:P4",
                "binding_effect": "add",
                "approval_status": "approved",
            },
        ]
    )
    resolved = resolve_governed(data)
    assert resolved["dams:logical/cascade/X"]["policy_refs"].value == ["pol:P3", "pol:P4"]
    assert resolved["dams:logical/cascade/X"]["policy_refs"].layer == "assignment"
    # a2 had inline P2; nearest subtree assignment on X covers a2
    assert resolved["dams:logical/cascade/X/a2"]["policy_refs"].value == ["pol:P3", "pol:P4"]


def test_policy_add_only_unions_cascade() -> None:
    data = _pkg(
        policy_bindings=[
            {
                "assignment_id": "dams:asg/pol/add-only",
                "target_element_ref": "dams:model/cascade/1",
                "assignment_scope": "subtree",
                "policy_ref": "pol:P9",
                "binding_effect": "add",
                "approval_status": "approved",
            }
        ]
    )
    resolved = resolve_governed(data)
    assert resolved["dams:logical/cascade/X"]["policy_refs"].value == ["pol:P1", "pol:P9"]


def test_ownership_assignment() -> None:
    data = _pkg(
        ownership_assignments=[
            {
                "assignment_id": "dams:asg/own/x",
                "target_element_ref": "dams:logical/cascade/X",
                "assignment_scope": "subtree",
                "data_owner_ref": "org:role/OWNER_ASG",
                "approval_status": "approved",
            }
        ]
    )
    resolved = resolve_governed(data)
    assert (
        resolved["dams:logical/cascade/X/a1"]["data_owner_ref"].value
        == "org:role/OWNER_ASG"
    )
    assert resolved["dams:logical/cascade/X/a1"]["data_owner_ref"].layer == "assignment"


def test_legacy_target_slot_accepted() -> None:
    data = _pkg(
        classification_assignments=[
            {
                "assignment_id": "dams:asg/class/legacy",
                "classified_element_ref": "dams:logical/cascade/X",
                "assignment_scope": "element",
                "governance_classification": "restricted",
                "approval_status": "approved",
            }
        ]
    )
    resolved = resolve_governed(data)
    assert (
        resolved["dams:logical/cascade/X"]["governance_classification"].value
        == "restricted"
    )
