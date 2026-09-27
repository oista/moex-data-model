"""CLI for publication projections."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from moex_publication.application.build_publication import (
    build_publication_module,
    export_slice_projection,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="moex-publication")
    sub = parser.add_subparsers(dest="command", required=True)

    export = sub.add_parser(
        "export-slice",
        help="Assess DAMS implementation and write viewer JSON projection",
    )
    export.add_argument("--schema", required=True, type=Path)
    export.add_argument("--implementation", required=True, type=Path)
    export.add_argument("--out", required=True, type=Path)
    export.add_argument("--implementation-id", default=None)

    args = parser.parse_args(argv)
    if args.command == "export-slice":
        result = export_slice_projection(
            schema_path=args.schema,
            implementation_path=args.implementation,
            out_path=args.out,
            implementation_id=args.implementation_id,
        )
        module = build_publication_module(result)
        print(
            f"wrote {args.out} module={module.module_id} "
            f"overall={result.report.overall_result.value}"
        )
        return 0 if result.report.is_conformant else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
