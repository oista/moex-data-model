"""CLI for FIBO definition export: ``python -m moex_standard_owl.fibo``."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from moex_standard_owl.constants import (
    DEFAULT_ENTITY_TYPES,
    DEFAULT_OUTPUT_FORMATS,
    TYPE_INDIVIDUAL,
)
from moex_standard_owl.fibo.aggregation import aggregate_entities, filter_for_main_mart
from moex_standard_owl.fibo.constants import ALL_DOMAINS, DEFAULT_DOMAINS, DEFAULT_RELEASE
from moex_standard_owl.fibo.discovery import discover_rdf_files
from moex_standard_owl.fibo.exporter import run_export
from moex_standard_owl.models import EntityOccurrence, ParseError
from moex_standard_owl.rdf_parser import parse_rdf_file
from moex_standard_owl.validation import (
    ValidationError,
    parse_csv_list,
    validate_domains,
    validate_entity_types,
    validate_formats,
    validate_output_path,
    validate_source_path,
)

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m moex_standard_owl.fibo",
        description=(
            "Export FIBO ontology entity definitions to CSV / Excel / JSON "
            "from a local edmcouncil/fibo checkout (offline)."
        ),
    )
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Local path to cloned/unpacked FIBO repository.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Directory for export results.",
    )
    parser.add_argument(
        "--release",
        default=DEFAULT_RELEASE,
        help=f"FIBO release identifier (default: {DEFAULT_RELEASE}).",
    )
    parser.add_argument(
        "--domains",
        default=None,
        help=(
            "Comma-separated domain list. "
            f"Default: {','.join(DEFAULT_DOMAINS)}."
        ),
    )
    parser.add_argument(
        "--include-examples",
        action="store_true",
        help="Include EXMP example ontologies.",
    )
    parser.add_argument(
        "--include-individuals",
        action="store_true",
        help="Include owl:NamedIndividual in primary CSV marts.",
    )
    parser.add_argument(
        "--include-deprecated",
        action="store_true",
        help="Include deprecated entities in primary CSV marts.",
    )
    parser.add_argument(
        "--types",
        default=None,
        help=(
            "Comma-separated entity type codes: "
            "class,object_property,datatype_property,annotation_property,individual. "
            f"Default: {','.join(DEFAULT_ENTITY_TYPES)}."
        ),
    )
    parser.add_argument(
        "--format",
        dest="formats",
        default=None,
        help="Comma-separated output formats: csv,xlsx,json. Default: csv,xlsx.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose logging (per-file progress).",
    )
    parser.add_argument(
        "--fail-on-parse-error",
        action="store_true",
        help="Exit with non-zero status on the first RDF parse failure.",
    )
    return parser


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    # Log to stdout so PowerShell ($ErrorActionPreference=Stop) does not
    # treat recoverable parse warnings as terminating NativeCommandError.
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
        force=True,
    )
    # FIBO occasionally ships non-canonical xsd:dateTime literals; rdflib
    # still parses the graph but spams WARNING tracebacks — hide by default.
    if not verbose:
        logging.getLogger("rdflib.term").setLevel(logging.ERROR)


def process_files(
    files,
    *,
    source_release: str,
    extract_type_codes: set[str],
    fail_on_parse_error: bool,
    verbose: bool,
) -> tuple[list[EntityOccurrence], list[ParseError], int, int]:
    occurrences: list[EntityOccurrence] = []
    errors: list[ParseError] = []
    successful = 0
    processed = 0

    for discovered in files:
        processed += 1
        if verbose:
            logger.info("Parsing %s", discovered.module_path)
        occs, err = parse_rdf_file(
            discovered.path,
            module_path=discovered.module_path,
            source_release=source_release,
            source_domain=discovered.domain,
            entity_type_codes=extract_type_codes,
        )
        if err is not None:
            errors.append(err)
            if fail_on_parse_error:
                logger.error("Aborting due to --fail-on-parse-error")
                return occurrences, errors, processed, successful
            continue
        successful += 1
        occurrences.extend(occs)
        if verbose:
            logger.info(
                "  %s: %d entit(y/ies)", discovered.module_path, len(occs)
            )

    return occurrences, errors, processed, successful


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.verbose)

    try:
        source = validate_source_path(args.source)
        output = validate_output_path(args.output)
        domains = validate_domains(
            parse_csv_list(args.domains, default=DEFAULT_DOMAINS),
            allowed=ALL_DOMAINS,
        )
        type_codes = validate_entity_types(
            parse_csv_list(args.types, default=DEFAULT_ENTITY_TYPES)
        )
        formats = validate_formats(
            parse_csv_list(args.formats, default=DEFAULT_OUTPUT_FORMATS)
        )
    except ValidationError as exc:
        logger.error("%s", exc)
        return 2

    # Individuals: extract for Individuals sheet always; include in main mart
    # when flag set or when explicitly listed in --types.
    extract_codes = set(type_codes) | {TYPE_INDIVIDUAL}
    include_individuals = args.include_individuals or (
        TYPE_INDIVIDUAL in type_codes
    )
    if include_individuals and TYPE_INDIVIDUAL not in type_codes:
        type_codes = list(type_codes) + [TYPE_INDIVIDUAL]

    logger.info("Starting FIBO export")
    logger.info("source=%s", source)
    logger.info("output=%s", output)
    logger.info("release=%s", args.release)
    logger.info("domains=%s", ",".join(domains))
    logger.info("types=%s", ",".join(type_codes))
    logger.info("formats=%s", ",".join(formats))
    logger.info(
        "include_examples=%s include_individuals=%s include_deprecated=%s",
        args.include_examples,
        include_individuals,
        args.include_deprecated,
    )

    files = discover_rdf_files(
        source,
        domains,
        include_examples=args.include_examples,
    )
    logger.info("Discovered %d RDF file(s)", len(files))

    occurrences, errors, processed, successful = process_files(
        files,
        source_release=args.release,
        extract_type_codes=extract_codes,
        fail_on_parse_error=args.fail_on_parse_error,
        verbose=args.verbose,
    )

    if args.fail_on_parse_error and errors:
        # Still write error CSV for diagnostics before exit
        from moex_standard_owl.fibo.exporter import parse_errors_to_dataframe, write_csv

        write_csv(parse_errors_to_dataframe(errors), output / "fibo_parse_errors.csv")
        return 1

    aggregated = aggregate_entities(occurrences)

    # Counts by type
    type_counts: dict[str, int] = {}
    for ent in aggregated:
        type_counts[ent.entity_type] = type_counts.get(ent.entity_type, 0) + 1
    for owl_type, count in sorted(type_counts.items()):
        logger.info("Entities %s: %d", owl_type, count)

    deprecated_count = sum(1 for e in aggregated if e.is_deprecated)
    active_count = sum(1 for e in aggregated if not e.is_deprecated)
    logger.info("Active (pre-filter): %d; deprecated: %d", active_count, deprecated_count)

    main_type_set = set(type_codes)
    main_entities = filter_for_main_mart(
        aggregated,
        type_codes=main_type_set,
        include_individuals=include_individuals,
        include_deprecated=args.include_deprecated,
    )

    manifest = run_export(
        output_dir=output,
        source_path=source,
        source_release=args.release,
        domains=domains,
        type_codes=type_codes,
        include_examples=args.include_examples,
        include_individuals=include_individuals,
        include_deprecated=args.include_deprecated,
        formats=formats,
        main_entities=main_entities,
        all_aggregated=aggregated,
        parse_errors=errors,
        processed_files=processed,
        successful_files=successful,
    )

    logger.info(
        "Export complete: %d main entities, %d parse errors",
        manifest.entities_total,
        manifest.failed_files,
    )
    for name in manifest.output_files:
        logger.info("Output: %s", output / name)

    return 0 if not (args.fail_on_parse_error and errors) else 1


if __name__ == "__main__":
    sys.exit(main())
