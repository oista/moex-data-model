"""ontology-report — DAMS schema URI profile and URI semantic diff."""

from __future__ import annotations

import json
from pathlib import Path

from moex_dams.application.ontology_report import (
    build_ontology_profile,
    diff_schema_element_uris,
    ontology_profile_markdown,
)
from moex_model_cli.bootstrap import SlicePaths


def run_ontology_report(
    paths: SlicePaths,
    *,
    schema: Path | None = None,
    from_schema: Path | None = None,
    to_schema: Path | None = None,
    as_json: bool = False,
    out: Path | None = None,
) -> tuple[int, str]:
    if from_schema is not None or to_schema is not None:
        if from_schema is None or to_schema is None:
            return 2, "ontology-report --from/--to require both schema paths\n"
        left = from_schema if from_schema.is_absolute() else paths.root / from_schema
        right = to_schema if to_schema.is_absolute() else paths.root / to_schema
        try:
            report = diff_schema_element_uris(
                left,
                right,
                base_label=str(from_schema),
                target_label=str(to_schema),
            )
        except Exception as exc:
            return 2, f"ontology-report diff failed: {exc}\n"
        if as_json:
            return (
                1 if report.has_breaking else 0,
                report.model_dump_json(indent=2) + "\n",
            )
        counts = report.counts_by_category()
        lines = [
            f"ontology-report base={report.base_label} "
            f"target={report.target_label} changes={len(report.changes)} "
            f"breaking={counts.get('breaking', 0)} "
            f"non_breaking={counts.get('non_breaking', 0)}\n"
        ]
        for change in report.changes:
            subject = change.subject_ref or "-"
            lines.append(
                f"{change.category.value.upper()} {change.change_code} "
                f"{subject}: {change.message}\n"
            )
        return (1 if report.has_breaking else 0, "".join(lines))

    target = schema or paths.schema
    target = target if target.is_absolute() else paths.root / target
    try:
        profile = build_ontology_profile(target)
    except Exception as exc:
        return 2, f"ontology-report failed: {exc}\n"

    if out is not None:
        out_path = out if out.is_absolute() else paths.root / out
        out_path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(profile, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        out_path.write_text(text, encoding="utf-8", newline="\n")
        md_path = out_path.with_suffix(".md")
        md_path.write_text(
            ontology_profile_markdown(profile), encoding="utf-8", newline="\n"
        )
        return 0, (
            f"ontology-report schema={target} "
            f"classes={len(profile['classes'])} slots={len(profile['slots'])} "
            f"enums={len(profile['enums'])} issues={len(profile['issues'])} "
            f"→ {out_path}\n"
        )

    if as_json:
        return (
            0,
            json.dumps(profile, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        )

    return 0, ontology_profile_markdown(profile)
