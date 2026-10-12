"""Catalog snapshot resolve / drift / TopologyView materialize (ADR-048)."""

from __future__ import annotations

from moex_dams.catalog.drift import DriftFinding, collect_drift
from moex_dams.catalog.materialize import materialize_topology_view, topology_view_path
from moex_dams.catalog.refs import CatalogRef, parse_catalog_ref
from moex_dams.catalog.snapshot import CatalogSnapshot, load_snapshot

__all__ = [
    "CatalogRef",
    "CatalogSnapshot",
    "DriftFinding",
    "collect_drift",
    "load_snapshot",
    "materialize_topology_view",
    "parse_catalog_ref",
    "topology_view_path",
]
