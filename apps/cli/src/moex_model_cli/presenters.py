"""Text/JSON presenters for CLI (transport only)."""

from __future__ import annotations

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
    return result.report.model_dump_json(indent=2) + "\n"
