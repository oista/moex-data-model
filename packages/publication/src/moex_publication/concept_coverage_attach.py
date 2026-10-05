"""Attach concept-coverage summary into publication vertical slice (informational)."""

from __future__ import annotations

from typing import Any

from moex_dams.application.concept_coverage import compute_concept_coverage


def attach_concept_coverage(slice_doc: dict[str, Any], packages: list[dict[str, Any]]) -> dict[str, Any]:
    """Mutate/return slice with ``concept_coverage`` key (never fails)."""
    try:
        report = compute_concept_coverage(packages)
    except Exception as exc:  # noqa: BLE001 — informational only
        report = {"error": str(exc)}
    out = dict(slice_doc)
    out["concept_coverage"] = report
    return out
