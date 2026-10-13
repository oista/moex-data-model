"""Read TopologyView facts for a DataFlow (ADR-048; dual-read window closed)."""

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
    """Return effective topology fields for a DataFlow from TopologyView only.

    Authored topology slots were removed in ADR-048 PR-5; there is no
    deprecated-slot fallback. When the view has no fact for the flow,
    ``source`` is ``"missing"`` and topology keys are omitted.
    """
    fact = _fact_for_flow(view, flow.get("element_id"))
    out: dict[str, Any] = {
        "flow_ref": flow.get("element_id"),
        "integration_ref": flow.get("integration_ref"),
        "source": "topology_view" if fact else "missing",
    }
    if not fact:
        return out

    out["binding_status"] = fact.get("binding_status")
    for key in TOPOLOGY_KEYS:
        if key in fact and fact[key] is not None:
            out[key] = fact[key]
    return out
