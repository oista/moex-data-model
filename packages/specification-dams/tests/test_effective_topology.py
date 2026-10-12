"""Tests for effective_topology dual-read (ADR-048 PR-3)."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_dams.catalog.effective_topology import (
    authored_vs_effective_mismatches,
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


def test_fallback_to_authored_when_no_view() -> None:
    flow = {
        "element_id": "dams:flow/x",
        "integration_ref": "clinkr:integration/INT-00421",
        "source_system_ref": "eam:system/TRADING_CORE",
    }
    eff = effective_topology(flow, None)
    assert eff["source"] == "authored_deprecated"
    assert eff["source_system_ref"] == "eam:system/TRADING_CORE"


def test_no_mismatches_when_aligned() -> None:
    flow = yaml.safe_load(FLOW.read_text(encoding="utf-8"))
    view = load_topology_view(REPO, "2026-10-12.fixture.1")
    assert authored_vs_effective_mismatches(flow, view) == []


def test_mismatch_detected() -> None:
    flow = yaml.safe_load(FLOW.read_text(encoding="utf-8"))
    flow["source_system_ref"] = "eam:system/OTHER"
    view = load_topology_view(REPO, "2026-10-12.fixture.1")
    assert "source_system_ref" in authored_vs_effective_mismatches(flow, view)
