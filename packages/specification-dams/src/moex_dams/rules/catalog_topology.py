"""L2 catalog topology invariants against the file snapshot (ADR-048)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from moex_modeling import (
    ConformancePhase,
    Diagnostic,
    DiagnosticDetail,
    DiagnosticSeverity,
)

from moex_dams.catalog.drift import collect_drift
from moex_dams.catalog.snapshot import default_snapshot_path, load_snapshot


def _diag(
    *,
    code: str,
    message: str,
    subject: str | None,
    invariant_id: str,
    severity: DiagnosticSeverity,
    requirement_code: str | None = None,
) -> Diagnostic:
    details = [
        DiagnosticDetail(detail_key="finding", detail_value=message),
        DiagnosticDetail(detail_key="invariant_id", detail_value=invariant_id),
    ]
    if requirement_code:
        details.append(
            DiagnosticDetail(
                detail_key="requirement_code",
                detail_value=requirement_code,
            )
        )
    return Diagnostic(
        diagnostic_code=code,
        severity=severity,
        diagnostic_message=message,
        conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
        subject_ref=subject,
        diagnostic_details=tuple(details),
    )


def iter_data_flows(data: dict[str, Any]) -> list[dict[str, Any]]:
    flows = data.get("data_flows")
    if isinstance(flows, list):
        return [f for f in flows if isinstance(f, dict)]
    # Standalone DataFlow document (examples / fixtures).
    if data.get("integration_ref") is not None and (
        "entity_bindings" in data or str(data.get("element_id", "")).startswith("dams:flow")
    ):
        return [data]
    return []


def iter_data_model_bindings(data: dict[str, Any]) -> list[dict[str, Any]]:
    bindings = data.get("data_model_bindings")
    if isinstance(bindings, list):
        return [b for b in bindings if isinstance(b, dict)]
    if data.get("integrity_digest") is not None and data.get("integration_ref") is not None:
        return [data]
    return []


def _repo_root() -> Path:
    # …/packages/specification-dams/src/moex_dams/rules/catalog_topology.py
    return Path(__file__).resolve().parents[5]


def check_catalog_topology(
    data: dict[str, Any],
    *,
    snapshot_path: Path | None = None,
    repo_root: Path | None = None,
) -> list[Diagnostic]:
    """Emit INV-038…INV-041 diagnostics for flows/bindings vs catalog snapshot."""
    root = repo_root or _repo_root()
    path = snapshot_path or default_snapshot_path(root)
    if not path.is_file():
        return []

    try:
        snapshot = load_snapshot(path)
    except Exception as exc:  # noqa: BLE001 — surface as diagnostic
        return [
            _diag(
                code="DAMS-INV-038",
                message=f"catalog snapshot load failed: {exc}",
                subject=str(path),
                invariant_id="INV-038",
                severity=DiagnosticSeverity.ERROR,
                requirement_code="FLW-002",
            )
        ]

    out: list[Diagnostic] = []
    for flow in iter_data_flows(data):
        findings, obj = collect_drift(flow, snapshot)
        flow_id = str(flow.get("element_id") or "<flow>")
        for f in findings:
            if f.code in {"orphan_ref", "unknown_catalog"}:
                out.append(
                    _diag(
                        code="DAMS-INV-038",
                        message=f.message,
                        subject=f.subject_ref or flow_id,
                        invariant_id="INV-038",
                        severity=DiagnosticSeverity.ERROR,
                        requirement_code="FLW-002",
                    )
                )
            elif f.code == "stale_revision":
                out.append(
                    _diag(
                        code="DAMS-INV-040",
                        message=f.message,
                        subject=f.subject_ref or flow_id,
                        invariant_id="INV-040",
                        severity=DiagnosticSeverity.WARNING,
                        requirement_code="FLW-004",
                    )
                )
            elif f.code == "unmapped_exchange" and "catalog_operation_ref" in f.message:
                # Only operation-ref presence / membership → INV-039
                out.append(
                    _diag(
                        code="DAMS-INV-039",
                        message=f.message,
                        subject=f.subject_ref or flow_id,
                        invariant_id="INV-039",
                        severity=DiagnosticSeverity.WARNING,
                        requirement_code="FLW-003",
                    )
                )

        # Stronger INV-039: if binding declares catalog_operation_ref not in ops
        if obj is not None:
            ops = {
                str(op.get("operation_id"))
                for op in (obj.get("operations") or [])
                if isinstance(op, dict) and op.get("operation_id")
            }
            for b in flow.get("entity_bindings") or []:
                if not isinstance(b, dict):
                    continue
                op_ref = b.get("catalog_operation_ref")
                if op_ref and ops and str(op_ref) not in ops:
                    bid = str(b.get("element_id") or "<binding>")
                    # already emitted via unmapped_exchange; ensure INV-039
                    if not any(
                        d.diagnostic_code == "DAMS-INV-039"
                        and d.subject_ref == bid
                        for d in out
                    ):
                        out.append(
                            _diag(
                                code="DAMS-INV-039",
                                message=(
                                    f"catalog_operation_ref={op_ref!r} not in "
                                    f"snapshot operations"
                                ),
                                subject=bid,
                                invariant_id="INV-039",
                                severity=DiagnosticSeverity.WARNING,
                                requirement_code="FLW-003",
                            )
                        )

    for binding in iter_data_model_bindings(data):
        crev = binding.get("catalog_revision")
        if crev is None or crev == "":
            continue
        if str(crev) != snapshot.catalog_revision:
            bid = str(binding.get("element_id") or "<binding>")
            out.append(
                _diag(
                    code="DAMS-INV-041",
                    message=(
                        f"DataModelBinding.catalog_revision={crev!r} differs from "
                        f"snapshot catalog_revision={snapshot.catalog_revision!r}"
                    ),
                    subject=bid,
                    invariant_id="INV-041",
                    severity=DiagnosticSeverity.WARNING,
                    requirement_code="FLW-005",
                )
            )

    return out
