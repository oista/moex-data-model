"""Text/JSON presenters for CLI (transport only)."""

from __future__ import annotations

import json

from moex_modeling import diagnostic_to_wire

from moex_dams.application.assess import SliceResult


def format_validate_text(result: SliceResult) -> str:
    report = result.report
    lines = [
        f"overall={report.overall_result.value}",
        f"package={result.graph.package_id}",
        f"nodes={len(result.graph.nodes)} edges={len(result.graph.edges)}",
    ]
    for assessment in report.assessments:
        lines.append(
            f"  {assessment.id}: {assessment.conformance_result.value} "
            f"({len(assessment.diagnostics)} diagnostics)"
        )
        for diag in assessment.diagnostics:
            lines.append(
                f"    [{diag.severity.value}] {diag.diagnostic_code}: "
                f"{diag.diagnostic_message}"
            )
    return "\n".join(lines) + "\n"


def format_validate_json(result: SliceResult) -> str:
    """Report JSON with diagnostics remapped to IMPLEMENTATION_PLAN wire shape."""
    payload = json.loads(result.report.model_dump_json())
    for i, assessment in enumerate(result.report.assessments):
        payload["assessments"][i]["diagnostics"] = [
            diagnostic_to_wire(d) for d in assessment.diagnostics
        ]
    payload["package_id"] = result.graph.package_id
    payload["implementation_id"] = result.implementation.id
    return json.dumps(payload, indent=2) + "\n"
