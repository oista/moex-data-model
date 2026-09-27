"""CLI: moex-linkml ingest — ER dictionary → ModelPackage + envelope."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import yaml

from moex_standard_linkml.ingest.envelope import build_envelope
from moex_standard_linkml.ingest.mapper import MappingFailed, map_er_dictionary
from moex_standard_linkml.ingest.profile import load_profile
from moex_standard_linkml.ingest.validate import validate_model_package
from moex_standard_linkml.ingest.workbook import WorkbookError, load_workbook_tables


def _configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
        force=True,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="moex-linkml")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser(
        "ingest",
        help="Ingest ER-dictionary XLS/CSV into DAMS ModelPackage YAML",
    )
    ingest.add_argument(
        "--workbook",
        type=Path,
        required=True,
        help="Path to .xlsx or directory of CSV sheets",
    )
    ingest.add_argument(
        "--profile",
        type=Path,
        required=True,
        help="Ingest profile YAML (sheet/column mapping + defaults)",
    )
    ingest.add_argument(
        "--schema",
        type=Path,
        required=True,
        help="Path to moex-dams.yaml (or other DAMS root schema)",
    )
    ingest.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output directory for package/envelope/validation artifacts",
    )
    ingest.add_argument(
        "--name",
        default=None,
        help="Artifact basename (default: profile.package_name)",
    )
    ingest.add_argument(
        "--skip-validate",
        action="store_true",
        help="Write artifacts without running linkml-validate",
    )
    ingest.add_argument("-v", "--verbose", action="store_true")
    return parser


def cmd_ingest(args: argparse.Namespace) -> int:
    profile = load_profile(args.profile)
    basename = args.name or profile.package_name
    out_dir: Path = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        tables = load_workbook_tables(args.workbook, profile)
    except WorkbookError as exc:
        print(f"Workbook error: {exc}", file=sys.stderr)
        return 2

    for warning in tables.warnings:
        logging.warning(warning)

    try:
        result = map_er_dictionary(tables, profile)
    except MappingFailed as exc:
        for err in exc.errors:
            print(f"Mapping error: {err}", file=sys.stderr)
        return 2

    package_path = out_dir / f"{basename}.package.yaml"
    envelope_path = out_dir / f"{basename}.envelope.yaml"
    validation_path = out_dir / f"{basename}.validation.txt"

    package_text = yaml.safe_dump(
        result.package,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )
    package_bytes = package_text.encode("utf-8")
    package_path.write_bytes(package_bytes)

    envelope = build_envelope(
        profile=profile,
        package_path=package_path,
        source_path=Path(args.workbook),
        package_bytes=package_bytes,
    )
    envelope_path.write_text(
        yaml.safe_dump(
            envelope,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
        ),
        encoding="utf-8",
    )

    print(f"Wrote {package_path}")
    print(f"Wrote {envelope_path}")

    if args.skip_validate:
        validation_path.write_text("skipped (--skip-validate)\n", encoding="utf-8")
        print(f"Wrote {validation_path} (skipped)")
        return 0

    validation = validate_model_package(package_path, args.schema)
    validation_path.write_text(validation.report, encoding="utf-8")
    print(f"Wrote {validation_path}")
    if not validation.ok:
        print(validation.report, file=sys.stderr)
        return 1
    print("Validation OK (ModelPackage)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _configure_logging(getattr(args, "verbose", False))
    if args.command == "ingest":
        return cmd_ingest(args)
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
