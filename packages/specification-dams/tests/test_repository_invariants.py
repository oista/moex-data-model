"""INV-058 repository element_id uniqueness and walker consistency with INV-050."""

from __future__ import annotations

from moex_dams.rules.package_invariants import check_package_element_id_uniqueness
from moex_dams.rules.repository_invariants import (
    check_repository_element_id_uniqueness,
    collect_element_ids,
    iter_element_id_locations,
)


def test_repository_collision_emits_inv058() -> None:
    composite = {
        "repository_id": "moex:repository:t",
        "model_packages": [
            {
                "element_id": "dams:model/a",
                "conceptual_entities": [{"element_id": "dams:concept/X"}],
            },
            {
                "element_id": "dams:model/b",
                "conceptual_entities": [{"element_id": "dams:concept/X"}],
            },
        ],
    }
    diags = check_repository_element_id_uniqueness(
        composite,
        package_ids=["moex:implementation:a:0.1", "moex:implementation:b:0.1"],
    )
    assert any(d.diagnostic_code == "DAMS-INV-058" for d in diags)
    assert all(
        any(
            det.detail_key == "invariant_id" and det.detail_value == "INV-058"
            for det in d.diagnostic_details
        )
        for d in diags
        if d.diagnostic_code == "DAMS-INV-058"
    )
    msg = next(d.diagnostic_message for d in diags if d.diagnostic_code == "DAMS-INV-058")
    assert "moex:implementation:a:0.1" in msg
    assert "moex:implementation:b:0.1" in msg


def test_repository_unique_ids_ok() -> None:
    composite = {
        "repository_id": "moex:repository:t",
        "model_packages": [
            {
                "element_id": "dams:model/a",
                "conceptual_entities": [{"element_id": "dams:concept/A"}],
            },
            {
                "element_id": "dams:model/b",
                "conceptual_entities": [{"element_id": "dams:concept/B"}],
            },
        ],
    }
    assert check_repository_element_id_uniqueness(composite) == []


def test_duplicate_within_one_package_is_not_inv058() -> None:
    """Within-package dups are INV-050; INV-058 requires ≥2 packages."""
    composite = {
        "repository_id": "moex:repository:t",
        "model_packages": [
            {
                "element_id": "dams:model/a",
                "conceptual_entities": [
                    {"element_id": "dams:concept/X"},
                    {"element_id": "dams:concept/X"},
                ],
            }
        ],
    }
    assert check_repository_element_id_uniqueness(composite) == []
    assert any(
        d.diagnostic_code == "DAMS-INV-050"
        for d in check_package_element_id_uniqueness(composite["model_packages"][0])
    )


def test_walker_ids_match_inv050_and_collect() -> None:
    data = {
        "element_id": "dams:model/p",
        "conceptual_entities": [
            {"element_id": "dams:concept/A"},
            {"element_id": "dams:concept/B"},
        ],
        "logical_entities": [
            {
                "element_id": "dams:logical/E",
                "attributes": [{"element_id": "dams:logical/E/a"}],
            }
        ],
    }
    from_iter = {eid for eid, _ in iter_element_id_locations(data)}
    from_collect = set(collect_element_ids(data))
    assert from_iter == from_collect
    assert from_iter == {
        "dams:model/p",
        "dams:concept/A",
        "dams:concept/B",
        "dams:logical/E",
        "dams:logical/E/a",
    }
    # INV-050 uses the same collect_element_ids walk.
    assert check_package_element_id_uniqueness(data) == []
    data["conceptual_entities"].append({"element_id": "dams:concept/A"})
    assert any(
        d.diagnostic_code == "DAMS-INV-050"
        for d in check_package_element_id_uniqueness(data)
    )
