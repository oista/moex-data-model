"""moex-model entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from moex_model_cli.bootstrap import SlicePaths
from moex_model_cli.commands.publish import run_publish
from moex_model_cli.commands.validate import run_validate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="moex-model",
        description="CLI adapter for the MOEX modeling vertical slice",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser(
        "validate",
        help="LinkML native validation + DAMS semantic rules",
    )
    _add_slice_args(validate)
    validate.add_argument("--json", action="store_true", help="Print ConformanceReport JSON")

    publish = sub.add_parser(
        "publish",
        help="Assess implementation and write viewer JSON projection",
    )
    _add_slice_args(publish)
    publish.add_argument(
        "--out",
        type=Path,
        default=None,
        help=(
            "Output JSON path (default: model-assets/implementations/"
            "solutions/trading-platform/publications/vertical_slice.json)"
        ),
    )
    return parser


def _add_slice_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root (default: discover from cwd)",
    )
    parser.add_argument("--schema", type=Path, default=None)
    parser.add_argument("--implementation", type=Path, default=None)
    parser.add_argument("--implementation-id", default=None)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    paths = SlicePaths.resolve(
        root=args.root,
        schema=args.schema,
        implementation=args.implementation,
    )
    if args.command == "validate":
        code, text = run_validate(
            paths,
            as_json=args.json,
            implementation_id=args.implementation_id,
        )
        sys.stdout.write(text)
        return code
    if args.command == "publish":
        code, text = run_publish(
            paths,
            out=args.out,
            implementation_id=args.implementation_id,
        )
        sys.stdout.write(text)
        return code
    return 2


if __name__ == "__main__":
    sys.exit(main())
