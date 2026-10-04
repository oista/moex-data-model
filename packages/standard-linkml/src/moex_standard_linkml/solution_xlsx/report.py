"""Import report: console + Markdown + JSON."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from moex_standard_linkml.solution_xlsx.diagnostics import Diagnostic, Severity


def summarize(diagnostics: list[Diagnostic]) -> dict[str, int]:
    counts = {"error": 0, "warning": 0, "info": 0}
    for d in diagnostics:
        counts[d.severity.value] = counts.get(d.severity.value, 0) + 1
    return counts


def render_markdown(
    *,
    title: str,
    diagnostics: list[Diagnostic],
    extras: dict[str, Any] | None = None,
) -> str:
    counts = summarize(diagnostics)
    lines = [
        f"# {title}",
        "",
        f"- errors: **{counts['error']}**",
        f"- warnings: **{counts['warning']}**",
        f"- info: **{counts['info']}**",
        "",
    ]
    if extras:
        lines.append("## Summary")
        lines.append("")
        for k, v in extras.items():
            lines.append(f"- **{k}**: {v}")
        lines.append("")
    lines.append("## Diagnostics")
    lines.append("")
    if not diagnostics:
        lines.append("_No diagnostics._")
        lines.append("")
        return "\n".join(lines)

    for d in diagnostics:
        loc = d.source_ref.label() if d.source_ref else "—"
        lines.append(f"### `{d.code}` ({d.severity.value}) @ `{loc}`")
        lines.append("")
        lines.append(d.message_ru)
        lines.append("")
        lines.append(f"**Что сделать:** {d.remediation}")
        if d.element_ref:
            lines.append("")
            lines.append(f"**element:** `{d.element_ref}`")
        lines.append("")
    return "\n".join(lines)


def write_report(
    report_dir: Path,
    *,
    title: str,
    diagnostics: list[Diagnostic],
    extras: dict[str, Any] | None = None,
) -> tuple[Path, Path]:
    report_dir.mkdir(parents=True, exist_ok=True)
    md_path = report_dir / "import-report.md"
    json_path = report_dir / "import-report.json"
    md_path.write_text(
        render_markdown(title=title, diagnostics=diagnostics, extras=extras),
        encoding="utf-8",
    )
    payload = {
        "title": title,
        "counts": summarize(diagnostics),
        "extras": extras or {},
        "diagnostics": [d.to_dict() for d in diagnostics],
    }
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return md_path, json_path


def format_console(diagnostics: list[Diagnostic], *, limit: int = 40) -> str:
    counts = summarize(diagnostics)
    lines = [
        f"SXI diagnostics: error={counts['error']} "
        f"warning={counts['warning']} info={counts['info']}"
    ]
    for d in diagnostics[:limit]:
        lines.append(str(d))
    if len(diagnostics) > limit:
        lines.append(f"... and {len(diagnostics) - limit} more")
    return "\n".join(lines) + "\n"


def exit_code_for(
    diagnostics: list[Diagnostic],
    *,
    io_skipped: bool = False,
) -> int:
    if any(d.severity is Severity.ERROR for d in diagnostics):
        return 1
    if io_skipped:
        return 3
    return 0
