from __future__ import annotations

from pathlib import Path

from architecture_check.model_element_roles import (
    DESCRIPTION_SLOT_USAGE_ALLOWLIST,
    check_description_declarations,
    check_identified_vs_embedded,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_description_allowlist_passes_on_repo():
    assert check_description_declarations(REPO_ROOT) == []


def test_identified_vs_embedded_passes_on_repo():
    assert check_identified_vs_embedded(REPO_ROOT) == []


def test_allowlist_contains_has_definition_not_relationship():
    assert "HasDefinition" in DESCRIPTION_SLOT_USAGE_ALLOWLIST
    assert "Relationship" not in DESCRIPTION_SLOT_USAGE_ALLOWLIST
    assert "Mapping" not in DESCRIPTION_SLOT_USAGE_ALLOWLIST
