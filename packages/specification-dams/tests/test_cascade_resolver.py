"""ADR-023 containment cascade: ownership, classification, policies."""

from __future__ import annotations

from moex_dams.rules.cascade import (
    DATA_OWNER_PLACEHOLDER,
    find_redundant_overrides,
    resolve_governed,
)


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


def test_inherit_package_to_entity_to_attribute() -> None:
    resolved = resolve_governed(_pkg())
    a1 = resolved["dams:logical/cascade/X/a1"]
    assert a1["data_owner_ref"].value == "org:role/OWNER_A"
    assert a1["data_owner_ref"].source_element_id == "dams:model/cascade/1"
    assert a1["data_steward_ref"].value == "org:role/STEWARD_S"
    assert a1["governance_classification"].value == "internal"
    assert a1["policy_refs"].value == ["pol:P1"]


def test_entity_owner_override() -> None:
    resolved = resolve_governed(_pkg())
    y = resolved["dams:logical/cascade/Y"]
    assert y["data_owner_ref"].value == "org:role/OWNER_B"
    assert y["data_owner_ref"].source_element_id == "dams:logical/cascade/Y"
    assert y["data_steward_ref"].value == "org:role/STEWARD_S"
    assert y["data_steward_ref"].source_element_id == "dams:model/cascade/1"
    assert y["governance_classification"].value == "confidential"
    y1 = resolved["dams:logical/cascade/Y/y1"]
    assert y1["data_owner_ref"].value == "org:role/OWNER_B"
    assert y1["governance_classification"].value == "confidential"
    assert y1["policy_refs"].value == ["pol:P1"]


def test_attribute_steward_and_policy_override() -> None:
    resolved = resolve_governed(_pkg())
    a2 = resolved["dams:logical/cascade/X/a2"]
    assert a2["data_owner_ref"].value == "org:role/OWNER_A"
    assert a2["data_steward_ref"].value == "org:role/STEWARD_T"
    assert a2["data_steward_ref"].source_element_id == "dams:logical/cascade/X/a2"
    assert a2["policy_refs"].value == ["pol:P2"]
    assert a2["governance_classification"].value == "internal"


def test_empty_policy_list_is_override_not_inherit() -> None:
    data = _pkg()
    data["logical_entities"][0]["policy_refs"] = []
    resolved = resolve_governed(data)
    x = resolved["dams:logical/cascade/X"]
    assert x["policy_refs"].value == []
    assert x["policy_refs"].source_element_id == "dams:logical/cascade/X"
    a1 = resolved["dams:logical/cascade/X/a1"]
    assert a1["policy_refs"].value == []


def test_absent_policy_inherits() -> None:
    data = _pkg()
    # entity X has no policy_refs key → inherit P1; a2 overrides to P2
    resolved = resolve_governed(data)
    assert resolved["dams:logical/cascade/X"]["policy_refs"].value == ["pol:P1"]
    assert "policy_refs" not in data["logical_entities"][0]


def test_physical_field_inherits_from_object_and_package() -> None:
    data = _pkg(
        data_carriers=[
            {
                "element_id": "dams:physical/cascade/T",
                "name": "T",
                "description": "table",
                "lifecycle_status": "draft",
                "system_ref": "eam:system/S",
                "asset_kind": "relational_table",
                "asset_namespace": "postgres://S",
                "qualified_name": "public.t",
                "technology": "postgres",
                "structure_ref": "urn:schema:t",
                "direction": "internal",
                "data_owner_ref": "org:role/PHYS_OWNER",
                "physical_fields": [
                    {
                        "element_id": "dams:physical/cascade/T/c1",
                        "name": "c1",
                        "description": "col",
                        "lifecycle_status": "draft",
                        "carrier_ref": "dams:physical/cascade/T",
                        "native_name": "c1",
                        "native_type": "text",
                        "required": True,
                    }
                ],
            }
        ]
    )
    resolved = resolve_governed(data)
    c1 = resolved["dams:physical/cascade/T/c1"]
    assert c1["data_owner_ref"].value == "org:role/PHYS_OWNER"
    assert c1["governance_classification"].value == "internal"
    assert c1["policy_refs"].value == ["pol:P1"]


def test_redundant_override_detected() -> None:
    data = _pkg()
    data["logical_entities"][0]["data_owner_ref"] = "org:role/OWNER_A"
    findings = find_redundant_overrides(data)
    assert any(
        eid == "dams:logical/cascade/X" and slot == "data_owner_ref"
        for eid, slot, _v, _p in findings
    )


def test_placeholder_constant() -> None:
    assert DATA_OWNER_PLACEHOLDER == "org:role/DATA_OWNER_PENDING"
