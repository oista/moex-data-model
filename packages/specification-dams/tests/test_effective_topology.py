"""Tests for TopologyView-only effective_topology (ADR-048 post dual-read)."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_dams.catalog.effective_topology import (
    effective_topology,
    load_topology_view,
)

REPO = Path(__file__).resolve().parents[3]
FLOW = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "examples"
    / "client-data-flow.yaml"
)


def test_effective_prefers_topology_view() -> None:
    flow = yaml.safe_load(FLOW.read_text(encoding="utf-8"))
    view = load_topology_view(REPO, "2026-10-12.fixture.1")
    assert view is not None
    eff = effective_topology(flow, view)
    assert eff["source"] == "topology_view"
    assert eff["source_system_ref"] == "eam:system/TRADING_CORE"
    assert eff["binding_status"] in {"resolved", "unmapped", "stale", "broken"}


def test_missing_when_no_view() -> None:
    flow = {
        "element_id": "dams:flow/x",
        "integration_ref": "clinkr:integration/INT-00421",
        # Legacy authored keys must be ignored after PR-5.
        "source_system_ref": "eam:system/TRADING_CORE",
    }
    eff = effective_topology(flow, None)
    assert eff["source"] == "missing"
    assert "source_system_ref" not in eff
    assert eff["integration_ref"] == "clinkr:integration/INT-00421"


def test_missing_when_view_has_no_fact() -> None:
    flow = yaml.safe_load(FLOW.read_text(encoding="utf-8"))
    view = {"facts": [{"flow_ref": "dams:flow/other", "source_system_ref": "eam:system/X"}]}
    eff = effective_topology(flow, view)
    assert eff["source"] == "missing"
    assert "source_system_ref" not in eff
