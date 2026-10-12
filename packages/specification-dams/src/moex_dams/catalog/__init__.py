"""Catalog snapshot resolve / drift / TopologyView materialize (ADR-048)."""

from __future__ import annotations

from moex_dams.catalog.drift import DriftFinding, collect_drift
from moex_dams.catalog.effective_topology import (
    authored_vs_effective_mismatches,
    effective_topology,
    load_topology_view,
)
from moex_dams.catalog.materialize import materialize_topology_view, topology_view_path
from moex_dams.catalog.refs import CatalogRef, parse_catalog_ref
from moex_dams.catalog.snapshot import CatalogSnapshot, load_snapshot

__all__ = [
    "CatalogRef",
    "CatalogSnapshot",
    "DriftFinding",
    "authored_vs_effective_mismatches",
    "collect_drift",
    "effective_topology",
    "load_snapshot",
    "load_topology_view",
    "materialize_topology_view",
    "parse_catalog_ref",
    "topology_view_path",
]
