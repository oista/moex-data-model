"""Load EffectiveGovernanceView for display (ADR-049)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

DEFAULT_AS_OF = "2026-10-12"


def governance_view_path(repo_root: Path | str, as_of: str = DEFAULT_AS_OF) -> Path:
    safe = as_of.replace("/", "_").replace("\\", "_")
    return Path(repo_root) / "generated" / "governance" / f"effective-governance-view-{safe}.yaml"


def load_effective_governance_view(
    repo_root: Path | str,
    *,
    as_of: str = DEFAULT_AS_OF,
) -> dict[str, Any] | None:
    """Return EffectiveGovernanceView mapping, or None if not materialized."""
    path = governance_view_path(repo_root, as_of)
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else None


def effective_slots_for(
    view: dict[str, Any],
    element_ref: str,
) -> list[dict[str, Any]]:
    """Return EffectiveSlot rows for one element_ref."""
    for el in view.get("elements") or []:
        if isinstance(el, dict) and el.get("element_ref") == element_ref:
            slots = el.get("slots") or []
            return [s for s in slots if isinstance(s, dict)]
    return []
