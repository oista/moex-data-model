"""moex-model entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from moex_model_cli.bootstrap import SlicePaths
from moex_model_cli.commands.compile import run_compile
from moex_model_cli.commands.diagram import run_diagram
from moex_model_cli.commands.diff import run_diff
from moex_model_cli.commands.lint import run_lint
from moex_model_cli.commands.publish import run_publish
from moex_model_cli.commands.semantic_diff import run_semantic_diff
from moex_model_cli.commands.stubs import run_not_implemented
from moex_model_cli.commands.validate import run_validate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="moex-model",
        description="CLI adapter for the MOEX modeling platform",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser(
        "validate",
        help="LinkML native validation + DAMS semantic rules",
    )
    _add_slice_args(validate)
    validate.add_argument("--json", action="store_true", help="Print ConformanceReport JSON")

    lint = sub.add_parser("lint", help="LinkML validate + DAMS structural/reference rules")
    _add_slice_args(lint)

    compile_p = sub.add_parser("compile", help="Regenerate DAMS Pydantic contracts")
    _add_slice_args(compile_p)
    compile_p.add_argument(
        "--json-schema",
        action="store_true",
        help="Also emit JSON Schema under generated/artifacts",
    )

    diagram = sub.add_parser("diagram", help="Export DBML golden sample for drawDB")
    _add_slice_args(diagram)
    diagram.add_argument("--out", type=Path, default=None)
    diagram.add_argument("--profile", default="physical")

    diff = sub.add_parser("diff", help="Unified diff of an asset between two git revisions")
    _add_slice_args(diff)
    diff.add_argument("--from", dest="from_ref", required=True)
    diff.add_argument("--to", dest="to_ref", required=True)
    diff.add_argument(
        "--path",
        default=None,
        help="Repo-relative path (default: implementation YAML)",
    )

    semantic = sub.add_parser(
        "semantic-diff",
        help="Classify DAMS ModelPackage changes (breaking / compatible / …)",
    )
    _add_slice_args(semantic)
    semantic.add_argument("--from", dest="from_ref", default=None)
    semantic.add_argument("--to", dest="to_ref", default=None)
    semantic.add_argument(
        "--path",
        default=None,
        help="Repo-relative path for Git mode (default: implementation YAML)",
    )
    semantic.add_argument("--left", type=Path, default=None, help="Base YAML file")
    semantic.add_argument("--right", type=Path, default=None, help="Target YAML file")
    semantic.add_argument("--json", action="store_true", help="Print SemanticDiffReport JSON")

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

    for name in ("import", "map"):
        stub = sub.add_parser(name, help=f"Not implemented ({name})")
        _add_slice_args(stub)

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
        schema=getattr(args, "schema", None),
        implementation=getattr(args, "implementation", None),
    )

    if args.command == "validate":
        code, text = run_validate(
            paths,
            as_json=args.json,
            implementation_id=args.implementation_id,
        )
    elif args.command == "lint":
        code, text = run_lint(paths)
    elif args.command == "compile":
        code, text = run_compile(paths, with_json_schema=args.json_schema)
    elif args.command == "diagram":
        code, text = run_diagram(paths, out=args.out, profile=args.profile)
    elif args.command == "diff":
        code, text = run_diff(
            paths,
            from_ref=args.from_ref,
            to_ref=args.to_ref,
            path=args.path,
        )
    elif args.command == "semantic-diff":
        code, text = run_semantic_diff(
            paths,
            from_ref=args.from_ref,
            to_ref=args.to_ref,
            path=args.path,
            left=args.left,
            right=args.right,
            as_json=args.json,
        )
    elif args.command == "publish":
        code, text = run_publish(
            paths,
            out=args.out,
            implementation_id=args.implementation_id,
        )
    elif args.command in {"import", "map"}:
        code, text = run_not_implemented(args.command)
    else:
        return 2

    sys.stdout.write(text)
    return code


if __name__ == "__main__":
    sys.exit(main())
