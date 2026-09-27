"""CLI for DAMS vertical-slice assessment."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from moex_dams.application.assess import assess_implementation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="moex-dams-assess")
    sub = parser.add_subparsers(dest="command", required=True)

    assess = sub.add_parser("assess", help="Run LinkML + DAMS conformance on a package")
    assess.add_argument("--schema", required=True, type=Path)
    assess.add_argument("--implementation", required=True, type=Path)
    assess.add_argument("--json", action="store_true", help="Print report as JSON")

    args = parser.parse_args(argv)
    if args.command == "assess":
        result = assess_implementation(
            schema_path=args.schema,
            implementation_path=args.implementation,
        )
        if args.json:
            print(result.report.model_dump_json(indent=2))
        else:
            print(f"overall={result.report.overall_result.value}")
            print(f"package={result.graph.package_id}")
            print(f"nodes={len(result.graph.nodes)} edges={len(result.graph.edges)}")
            for assessment in result.report.assessments:
                print(
                    f"  {assessment.id}: {assessment.conformance_result.value} "
                    f"({len(assessment.diagnostics)} diagnostics)"
                )
            for diag in (
                d
                for a in result.report.assessments
                for d in a.diagnostics
            ):
                print(
                    f"    [{diag.severity.value}] {diag.diagnostic_code}: "
                    f"{diag.diagnostic_message}"
                )
        return 0 if result.report.is_conformant else 1

    return 2


if __name__ == "__main__":
    sys.exit(main())
