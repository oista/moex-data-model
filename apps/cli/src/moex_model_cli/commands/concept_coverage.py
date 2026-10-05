"""CLI: conceptual property coverage report (informational)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from moex_dams.application.concept_coverage import compute_concept_coverage


def run_concept_coverage(
    paths: list[Path],
    *,
    as_json: bool = False,
) -> tuple[int, str]:
    packages: list[dict[str, Any]] = []
    for path in paths:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            packages.append(data)
    report = compute_concept_coverage(packages)
    if as_json:
        return 0, json.dumps(report, ensure_ascii=False, indent=2)
    lines = [
        f"attributes: {report['attribute_count']}",
        f"with concept_ref: {report['with_concept_ref']} ({report['concept_ref_ratio']:.1%})",
        f"critical without concept_ref: {len(report['critical_without_concept_ref'])}",
        f"orphan ConceptualProperty: {len(report['orphan_conceptual_properties'])}",
        f"cross-solution candidates: {len(report['cross_solution_candidates'])}",
    ]
    return 0, "\n".join(lines) + "\n"
