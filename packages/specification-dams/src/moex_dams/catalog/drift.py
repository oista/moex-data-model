"""Resolve DataFlow refs against a CatalogSnapshot and emit drift (ADR-048)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from moex_dams.catalog.refs import parse_catalog_ref
from moex_dams.catalog.snapshot import CatalogSnapshot

# Authored topology slots still present during the deprecation window.
TOPOLOGY_SLOT_MAP = {
    "source_solution_ref": ("source", "solution_ref"),
    "target_solution_ref": ("target", "solution_ref"),
    "source_system_ref": ("source", "system_ref"),
    "target_system_ref": ("target", "system_ref"),
    "source_platform_ref": ("source", "platform_ref"),
    "target_platform_ref": ("target", "platform_ref"),
}


@dataclass(frozen=True, slots=True)
class DriftFinding:
    code: str
    severity: str
    subject_ref: str | None
    message: str
    catalog_revision: str


def _participant_by_role(obj: dict[str, Any], role: str) -> dict[str, Any] | None:
    for part in obj.get("participants") or []:
        if not isinstance(part, dict):
            continue
        r = part.get("role")
        if r == role or r == "both":
            return part
    return None


def derived_topology(obj: dict[str, Any]) -> dict[str, str | None]:
    """Map snapshot integration object → DataFlow topology field values."""
    source = _participant_by_role(obj, "producer") or {}
    target = _participant_by_role(obj, "consumer") or {}
    return {
        "source_solution_ref": source.get("solution_ref"),
        "target_solution_ref": target.get("solution_ref"),
        "source_system_ref": source.get("system_ref"),
        "target_system_ref": target.get("system_ref"),
        "source_platform_ref": source.get("platform_ref"),
        "target_platform_ref": target.get("platform_ref"),
        "integration_level": obj.get("integration_level"),
        "integration_class": obj.get("integration_class"),
        "integration_channel": obj.get("channel"),
        "integration_spec_ref": obj.get("spec_uri"),
    }


def binding_status_for(
    findings: list[DriftFinding],
    *,
    bound_revision: str | None,
    snapshot_revision: str,
) -> str:
    codes = {f.code for f in findings}
    if "orphan_ref" in codes or "unknown_catalog" in codes:
        return "broken"
    if "stale_revision" in codes or (
        bound_revision and bound_revision != snapshot_revision
    ):
        return "stale"
    if "unmapped_exchange" in codes:
        return "unmapped"
    return "resolved"


def collect_drift(
    flow: dict[str, Any],
    snapshot: CatalogSnapshot,
) -> tuple[list[DriftFinding], dict[str, Any] | None]:
    """Return (findings, resolved_integration_object_or_None)."""
    findings: list[DriftFinding] = []
    rev = snapshot.catalog_revision
    flow_id = str(flow.get("element_id") or flow.get("name") or "<flow>")
    iref_raw = flow.get("integration_ref")
    iref = parse_catalog_ref(str(iref_raw) if iref_raw is not None else None)

    if iref is None:
        findings.append(
            DriftFinding(
                code="orphan_ref",
                severity="error",
                subject_ref=flow_id,
                message=f"integration_ref is missing or not a catalog CURIE: {iref_raw!r}",
                catalog_revision=rev,
            )
        )
        return findings, None

    if iref.catalog not in snapshot.catalogs_set:
        findings.append(
            DriftFinding(
                code="unknown_catalog",
                severity="error",
                subject_ref=flow_id,
                message=f"catalog {iref.catalog!r} is not present in the snapshot",
                catalog_revision=rev,
            )
        )
        return findings, None

    obj = snapshot.get(iref.catalog, iref.kind, iref.external_id)
    if obj is None:
        findings.append(
            DriftFinding(
                code="orphan_ref",
                severity="error",
                subject_ref=str(iref_raw),
                message=(
                    f"object {iref.curie} not found in snapshot "
                    f"(revision {rev})"
                ),
                catalog_revision=rev,
            )
        )
        return findings, None

    bound = flow.get("bound_catalog_revision")
    if bound is not None and str(bound) and str(bound) != rev:
        findings.append(
            DriftFinding(
                code="stale_revision",
                severity="warning",
                subject_ref=flow_id,
                message=(
                    f"bound_catalog_revision={bound!r} differs from "
                    f"snapshot catalog_revision={rev!r}"
                ),
                catalog_revision=rev,
            )
        )

    derived = derived_topology(obj)
    for slot, expected in derived.items():
        authored = flow.get(slot)
        if authored is None or authored == "" or expected is None:
            continue
        if str(authored) != str(expected):
            findings.append(
                DriftFinding(
                    code="topology_changed",
                    severity="warning",
                    subject_ref=flow_id,
                    message=(
                        f"{slot} authored={authored!r} differs from "
                        f"snapshot={expected!r}"
                    ),
                    catalog_revision=rev,
                )
            )

    ops = {
        str(op.get("operation_id"))
        for op in (obj.get("operations") or [])
        if isinstance(op, dict) and op.get("operation_id")
    }
    bindings = [b for b in (flow.get("entity_bindings") or []) if isinstance(b, dict)]
    bound_ops: set[str] = set()
    for b in bindings:
        op_ref = b.get("catalog_operation_ref")
        bid = str(b.get("element_id") or b.get("name") or "<binding>")
        if not op_ref:
            findings.append(
                DriftFinding(
                    code="unmapped_exchange",
                    severity="warning",
                    subject_ref=bid,
                    message="entity_binding has no catalog_operation_ref",
                    catalog_revision=rev,
                )
            )
            continue
        op_s = str(op_ref)
        bound_ops.add(op_s)
        if ops and op_s not in ops:
            findings.append(
                DriftFinding(
                    code="unmapped_exchange",
                    severity="warning",
                    subject_ref=bid,
                    message=(
                        f"catalog_operation_ref={op_s!r} not in snapshot "
                        f"operations for {iref.curie}"
                    ),
                    catalog_revision=rev,
                )
            )

    for op_id in sorted(ops - bound_ops):
        findings.append(
            DriftFinding(
                code="unmapped_exchange",
                severity="warning",
                subject_ref=flow_id,
                message=(
                    f"snapshot operation {op_id!r} has no entity_binding "
                    f"on {flow_id}"
                ),
                catalog_revision=rev,
            )
        )

    return findings, obj


def has_blocking_errors(findings: list[DriftFinding]) -> bool:
    return any(f.severity == "error" for f in findings)
