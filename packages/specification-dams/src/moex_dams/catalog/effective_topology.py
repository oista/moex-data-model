"""Dual-read helper: TopologyView facts with fallback to deprecated DataFlow slots."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from moex_dams.catalog.materialize import topology_view_path

TOPOLOGY_KEYS = (
    "source_solution_ref",
    "target_solution_ref",
    "source_system_ref",
    "target_system_ref",
    "source_platform_ref",
    "target_platform_ref",
    "integration_level",
    "integration_class",
    "integration_channel",
    "integration_spec_ref",
)


def load_topology_view(
    repo_root: Path | str,
    catalog_revision: str | None = None,
    *,
    view_path: Path | str | None = None,
) -> dict[str, Any] | None:
    """Load a committed TopologyView YAML, or None if missing."""
    if view_path is not None:
        path = Path(view_path)
    elif catalog_revision:
        path = topology_view_path(repo_root, catalog_revision)
    else:
        root = Path(repo_root) / "generated" / "topology"
        if not root.is_dir():
            return None
        candidates = sorted(root.glob("topology-view-*.yaml"))
        if not candidates:
            return None
        path = candidates[-1]
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else None


def _fact_for_flow(view: dict[str, Any] | None, flow_ref: str | None) -> dict[str, Any] | None:
    if not view or not flow_ref:
        return None
    for fact in view.get("facts") or []:
        if isinstance(fact, dict) and str(fact.get("flow_ref")) == str(flow_ref):
            return fact
    return None


def effective_topology(
    flow: dict[str, Any],
    view: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return effective topology fields for a DataFlow.

    Prefer TopologyView fact when present; otherwise fall back to deprecated
    authored slots on the flow (ADR-048 dual-read window).
    """
    fact = _fact_for_flow(view, flow.get("element_id"))
    out: dict[str, Any] = {
        "flow_ref": flow.get("element_id"),
        "integration_ref": flow.get("integration_ref"),
        "source": "topology_view" if fact else "authored_deprecated",
    }
    if fact:
        out["binding_status"] = fact.get("binding_status")
        for key in TOPOLOGY_KEYS:
            if key in fact and fact[key] is not None:
                out[key] = fact[key]
        return out

    for key in TOPOLOGY_KEYS:
        if key in flow and flow[key] is not None:
            out[key] = flow[key]
    return out


def authored_vs_effective_mismatches(
    flow: dict[str, Any],
    view: dict[str, Any] | None,
) -> list[str]:
    """List topology slots where authored deprecated values disagree with the view."""
    fact = _fact_for_flow(view, flow.get("element_id"))
    if not fact:
        return []
    mismatches: list[str] = []
    for key in TOPOLOGY_KEYS:
        authored = flow.get(key)
        derived = fact.get(key)
        if authored is None or authored == "" or derived is None:
            continue
        if str(authored) != str(derived):
            mismatches.append(key)
    return mismatches
