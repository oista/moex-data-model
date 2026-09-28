"""moex-model entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from moex_model_cli.bootstrap import SlicePaths
from moex_model_cli.commands.compile import run_compile
from moex_model_cli.commands.diagram import run_diagram
from moex_model_cli.commands.diff import run_diff
from moex_model_cli.commands.import_ import run_import
from moex_model_cli.commands.lint import run_lint
from moex_model_cli.commands.map_cmd import run_map
from moex_model_cli.commands.publish import run_publish
from moex_model_cli.commands.semantic_diff import run_semantic_diff
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
    compile_p.add_argument(
        "--artifacts",
        action="store_true",
        help="Also regenerate OWL/SHACL/DBML/Mermaid under generated/artifacts",
    )

    diagram = sub.add_parser(
        "diagram",
        help="Project ModelPackage to DBML (logical/physical; ADR-006)",
    )
    _add_slice_args(diagram)
    diagram.add_argument("--out", type=Path, default=None)
    diagram.add_argument(
        "--profile",
        default="logical",
        help="Projection profile: logical (default) or physical",
    )
    diagram.add_argument(
        "--format",
        dest="fmt",
        default="dbml",
        help="Output format (only dbml)",
    )

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

    import_p = sub.add_parser(
        "import",
        help=(
            "ER-dictionary → ModelPackage draft "
            "(schema-automator = Stage 7 / ADR-009)"
        ),
    )
    _add_slice_args(import_p)
    import_p.add_argument(
        "--workbook",
        type=Path,
        required=True,
        help="Path to .xlsx or directory of CSV sheets",
    )
    import_p.add_argument(
        "--profile",
        type=Path,
        required=True,
        dest="ingest_profile",
        help="Ingest profile YAML",
    )
    import_p.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output directory for package/envelope/validation artifacts",
    )
    import_p.add_argument("--name", default=None, help="Artifact basename")
    import_p.add_argument(
        "--skip-validate",
        action="store_true",
        help="Write artifacts without linkml-validate",
    )

    map_p = sub.add_parser(
        "map",
        help=(
            "SSSOM load or LinkML binding extract "
            "(linkml-map engine = Stage 7 / ADR-008)"
        ),
    )
    _add_slice_args(map_p)
    map_p.add_argument(
        "--sssom",
        type=Path,
        default=None,
        help="Load and summarize an SSSOM YAML mapping set",
    )
    map_p.add_argument(
        "--extract-schema",
        type=Path,
        default=None,
        help="Extract class_uri / slot_uri / mappings from a LinkML schema",
    )
    map_p.add_argument("--json", action="store_true", help="Print bindings as JSON")

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
        code, text = run_compile(
            paths,
            with_json_schema=args.json_schema,
            with_artifacts=args.artifacts,
        )
    elif args.command == "diagram":
        code, text = run_diagram(
            paths,
            out=args.out,
            profile=args.profile,
            fmt=args.fmt,
        )
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
    elif args.command == "import":
        code, text = run_import(
            paths,
            workbook=args.workbook,
            profile=args.ingest_profile,
            out=args.out,
            name=args.name,
            skip_validate=args.skip_validate,
            schema=args.schema,
        )
    elif args.command == "map":
        code, text = run_map(
            paths,
            sssom=args.sssom,
            extract_schema=args.extract_schema,
            as_json=args.json,
        )
    else:
        return 2

    sys.stdout.write(text)
    return code


if __name__ == "__main__":
    sys.exit(main())
