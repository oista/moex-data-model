"""Guard: solution relationships keep relationship_kind (ADR-056 D7 / F4-3)."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SOLUTIONS = REPO_ROOT / "model-assets" / "implementations" / "solutions"
SOLUTION_MODELS = (
    SOLUTIONS / "crm" / "crm-solution-model.yaml",
    SOLUTIONS / "esed" / "esed-solution-model.yaml",
    SOLUTIONS / "mdm" / "mdm-solution-model.yaml",
    SOLUTIONS / "ucd" / "ucd-solution-model.yaml",
)


def test_all_solution_relationships_have_relationship_kind() -> None:
    missing: list[str] = []
    total = 0
    for path in SOLUTION_MODELS:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict), path
        for rel in data.get("relationships") or []:
            assert isinstance(rel, dict), path
            total += 1
            eid = rel.get("element_id") or rel.get("name") or "?"
            if not str(rel.get("relationship_kind") or "").strip():
                missing.append(f"{path.name}:{eid}")
    assert total == 31, f"expected 31 solution relationships, got {total}"
    assert not missing, "relationships missing relationship_kind:\n" + "\n".join(missing)


def test_solution_relationships_remain_draft_after_kind_fill() -> None:
    """F4-3 fills kinds without promoting links to active (LDM-07 stays silent)."""
    for path in SOLUTION_MODELS:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for rel in data.get("relationships") or []:
            assert rel.get("lifecycle_status") == "draft", (
                f"{path.name}:{rel.get('element_id')} expected draft"
            )
            assert "relation_term_ref" not in rel, (
                f"{path.name}:{rel.get('element_id')} must not gain relation_term_ref"
            )
