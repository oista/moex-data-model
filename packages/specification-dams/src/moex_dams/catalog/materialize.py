"""Materialize TopologyView YAML under generated/topology/ (ADR-048)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from moex_dams.catalog.drift import (
    binding_status_for,
    collect_drift,
    derived_topology,
    has_blocking_errors,
)
from moex_dams.catalog.snapshot import CatalogSnapshot, default_snapshot_path, load_snapshot


def topology_view_path(repo_root: Path | str, catalog_revision: str) -> Path:
    safe = catalog_revision.replace("/", "_").replace("\\", "_")
    return Path(repo_root) / "generated" / "topology" / f"topology-view-{safe}.yaml"


def discover_flow_paths(repo_root: Path) -> list[Path]:
    """Example DataFlow + ``*.data-flow.yaml`` under implementations."""
    paths: list[Path] = []
    example = (
        repo_root
        / "model-assets"
        / "specifications"
        / "moex-dams"
        / "0.1"
        / "examples"
        / "client-data-flow.yaml"
    )
    if example.is_file():
        paths.append(example)
    impl = repo_root / "model-assets" / "implementations"
    if impl.is_dir():
        paths.extend(sorted(impl.rglob("*.data-flow.yaml")))
    # Stable unique by resolve()
    seen: set[Path] = set()
    out: list[Path] = []
    for p in paths:
        key = p.resolve()
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


def _load_flow(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: DataFlow root must be a mapping")
    return data


def build_topology_view(
    flows: list[dict[str, Any]],
    snapshot: CatalogSnapshot,
    *,
    built_at: str | None = None,
) -> tuple[dict[str, Any], list[Any]]:
    """Build TopologyView dict and aggregate drift findings."""
    all_findings: list[Any] = []
    facts: list[dict[str, Any]] = []
    when = built_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    for flow in flows:
        findings, obj = collect_drift(flow, snapshot)
        all_findings.extend(findings)
        status = binding_status_for(
            findings,
            bound_revision=(
                str(flow["bound_catalog_revision"])
                if flow.get("bound_catalog_revision") is not None
                else None
            ),
            snapshot_revision=snapshot.catalog_revision,
        )
        derived = derived_topology(obj) if obj else {}
        fact: dict[str, Any] = {
            "flow_ref": flow.get("element_id"),
            "integration_ref": flow.get("integration_ref"),
            "binding_status": status,
        }
        for key in (
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
        ):
            val = derived.get(key)
            if val is not None:
                fact[key] = val
        facts.append(fact)

    view = {
        "catalog_revision": snapshot.catalog_revision,
        "built_at": when,
        "snapshot_digest": snapshot.digest,
        "facts": facts,
    }
    return view, all_findings


def dump_topology_view(view: dict[str, Any]) -> str:
    header = (
        "# Generated TopologyView (ADR-048). Do not edit by hand.\n"
        "# Regenerate: python -m moex_dams.catalog.cli materialize --root .\n"
    )
    body = yaml.safe_dump(view, sort_keys=False, allow_unicode=True)
    if not body.endswith("\n"):
        body += "\n"
    return header + body


def materialize_topology_view(
    repo_root: Path | str,
    *,
    snapshot_path: Path | str | None = None,
    flow_paths: list[Path] | None = None,
    write: bool = True,
) -> tuple[Path, dict[str, Any], list[Any]]:
    """Load snapshot + flows, build view, optionally write generated/topology/."""
    root = Path(repo_root)
    snap_path = Path(snapshot_path) if snapshot_path else default_snapshot_path(root)
    snapshot = load_snapshot(snap_path)
    paths = flow_paths if flow_paths is not None else discover_flow_paths(root)
    flows = [_load_flow(p) for p in paths]
    view, findings = build_topology_view(flows, snapshot)
    out = topology_view_path(root, snapshot.catalog_revision)
    if write:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(dump_topology_view(view), encoding="utf-8")
    return out, view, findings


def check_topology_view(
    repo_root: Path | str,
    *,
    snapshot_path: Path | str | None = None,
    flow_paths: list[Path] | None = None,
) -> list[str]:
    """Regenerate in a temp dir and diff against committed TopologyView.

    Also fails when drift has severity=error.
    """
    root = Path(repo_root)
    errors: list[str] = []
    out, view, findings = materialize_topology_view(
        root,
        snapshot_path=snapshot_path,
        flow_paths=flow_paths,
        write=False,
    )
    if has_blocking_errors(findings):
        for f in findings:
            if f.severity == "error":
                errors.append(f"{f.code}: {f.message}")
    expected_text = dump_topology_view(view)
    if not out.is_file():
        errors.append(f"missing generated TopologyView: {out}")
        return errors
    # Compare ignoring built_at (non-deterministic wall clock).
    committed = yaml.safe_load(out.read_text(encoding="utf-8"))
    regenerated = yaml.safe_load(expected_text)
    if isinstance(committed, dict):
        committed.pop("built_at", None)
    if isinstance(regenerated, dict):
        regenerated.pop("built_at", None)
    if committed != regenerated:
        errors.append(
            f"TopologyView drift (hand-edit or stale): {out}. "
            "Run: python -m moex_dams.catalog.cli materialize --root ."
        )
    return errors
