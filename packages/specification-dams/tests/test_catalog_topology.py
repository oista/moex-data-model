"""Tests for catalog snapshot / drift / TopologyView (ADR-048)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from moex_dams.catalog.drift import collect_drift, has_blocking_errors
from moex_dams.catalog.materialize import (
    build_topology_view,
    check_topology_view,
    dump_topology_view,
    materialize_topology_view,
)
from moex_dams.catalog.refs import parse_catalog_ref
from moex_dams.catalog.snapshot import SnapshotError, canonical_digest, load_snapshot

REPO = Path(__file__).resolve().parents[3]
SNAPSHOT = (
    REPO
    / "model-assets"
    / "catalog-snapshots"
    / "clinkr"
    / "catalog-snapshot.json"
)
FLOW = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "examples"
    / "client-data-flow.yaml"
)


def test_parse_catalog_ref() -> None:
    ref = parse_catalog_ref("clinkr:integration/INT-00421")
    assert ref is not None
    assert ref.catalog == "clinkr"
    assert ref.kind == "integration"
    assert ref.external_id == "INT-00421"
    assert parse_catalog_ref("not-a-curie") is None


def test_load_repo_snapshot() -> None:
    snap = load_snapshot(SNAPSHOT)
    assert snap.catalog_revision == "2026-10-12.fixture.1"
    assert snap.get("clinkr", "integration", "INT-00421") is not None


def test_duplicate_object_rejected(tmp_path: Path) -> None:
    data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    data["objects"].append(dict(data["objects"][0]))
    data["digest"] = canonical_digest(data)
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(SnapshotError, match="duplicate"):
        load_snapshot(path)


def test_orphan_ref_is_error() -> None:
    snap = load_snapshot(SNAPSHOT)
    flow = yaml.safe_load(FLOW.read_text(encoding="utf-8"))
    flow["integration_ref"] = "clinkr:integration/DOES-NOT-EXIST"
    findings, obj = collect_drift(flow, snap)
    assert obj is None
    assert has_blocking_errors(findings)
    assert any(f.code == "orphan_ref" for f in findings)


def test_unknown_catalog_is_error() -> None:
    snap = load_snapshot(SNAPSHOT)
    flow = yaml.safe_load(FLOW.read_text(encoding="utf-8"))
    flow["integration_ref"] = "othercat:integration/INT-00421"
    findings, _ = collect_drift(flow, snap)
    assert any(f.code == "unknown_catalog" and f.severity == "error" for f in findings)


def test_stale_revision_warning() -> None:
    snap = load_snapshot(SNAPSHOT)
    flow = yaml.safe_load(FLOW.read_text(encoding="utf-8"))
    flow["bound_catalog_revision"] = "old-rev"
    findings, obj = collect_drift(flow, snap)
    assert obj is not None
    assert any(f.code == "stale_revision" and f.severity == "warning" for f in findings)


def test_topology_changed_warning() -> None:
    snap = load_snapshot(SNAPSHOT)
    flow = yaml.safe_load(FLOW.read_text(encoding="utf-8"))
    flow["source_system_ref"] = "eam:system/OTHER"
    findings, _ = collect_drift(flow, snap)
    assert any(f.code == "topology_changed" for f in findings)


def test_unmapped_exchange_warning() -> None:
    snap = load_snapshot(SNAPSHOT)
    flow = yaml.safe_load(FLOW.read_text(encoding="utf-8"))
    findings, _ = collect_drift(flow, snap)
    assert any(f.code == "unmapped_exchange" for f in findings)


def test_materialize_and_check_roundtrip(tmp_path: Path) -> None:
    # Minimal fake repo: snapshot + flow + generated dir
    snap_dir = tmp_path / "model-assets" / "catalog-snapshots" / "clinkr"
    snap_dir.mkdir(parents=True)
    snap_path = snap_dir / "catalog-snapshot.json"
    snap_path.write_text(SNAPSHOT.read_text(encoding="utf-8"), encoding="utf-8")
    flow_dir = (
        tmp_path
        / "model-assets"
        / "specifications"
        / "moex-dams"
        / "0.1"
        / "examples"
    )
    flow_dir.mkdir(parents=True)
    flow_path = flow_dir / "client-data-flow.yaml"
    flow_path.write_text(FLOW.read_text(encoding="utf-8"), encoding="utf-8")

    out, view, findings = materialize_topology_view(tmp_path, write=True)
    assert out.is_file()
    assert view["catalog_revision"] == "2026-10-12.fixture.1"
    assert view["facts"]
    assert not has_blocking_errors(findings)

    errors = check_topology_view(tmp_path)
    assert errors == []

    # Hand-edit should fail check
    text = out.read_text(encoding="utf-8")
    out.write_text(text + "# tamper\n", encoding="utf-8")
    # yaml may ignore trailing comment — change a fact instead
    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    data["facts"][0]["binding_status"] = "broken"
    out.write_text(dump_topology_view(data), encoding="utf-8")
    errors = check_topology_view(tmp_path)
    assert errors and "TopologyView drift" in errors[0]


def test_build_view_resolved_when_aligned() -> None:
    snap = load_snapshot(SNAPSHOT)
    flow = yaml.safe_load(FLOW.read_text(encoding="utf-8"))
    flow["bound_catalog_revision"] = snap.catalog_revision
    flow["entity_bindings"][0]["catalog_operation_ref"] = "client.changed"
    view, findings = build_topology_view([flow], snap, built_at="2026-10-12T00:00:00+00:00")
    assert view["facts"][0]["binding_status"] == "resolved"
    assert not has_blocking_errors(findings)
    assert not any(f.code == "unmapped_exchange" for f in findings)
