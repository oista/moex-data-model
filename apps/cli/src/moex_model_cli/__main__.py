"""moex-model entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from moex_model_cli.bootstrap import SlicePaths


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
        help=(
            "Also regenerate OWL/SHACL/DBML/Mermaid/Python/Doc/RDF "
            "under generated/artifacts"
        ),
    )
    compile_p.add_argument(
        "--bundle",
        action="store_true",
        help="Also rebuild the DAMS release bundle index (+ staged tree)",
    )

    diagram = sub.add_parser(
        "diagram",
        help="Project ModelPackage to DBML or Mermaid erDiagram (ADR-006)",
    )
    _add_slice_args(diagram)
    diagram.add_argument("--out", type=Path, default=None)
    diagram.add_argument(
        "--profile",
        default="logical",
        help="Projection profile: logical (default), physical, or conceptual",
    )
    diagram.add_argument(
        "--format",
        dest="fmt",
        default="dbml",
        help="Output format: dbml (default) or mermaid",
    )
    diagram.add_argument(
        "--no-svg",
        action="store_true",
        help="Skip SVG render for --format mermaid (md only)",
    )
    diagram.add_argument(
        "--reset-layout",
        action="store_true",
        help="Regenerate {profile}.layout.json from scratch (discard saved positions)",
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

    coverage = sub.add_parser(
        "concept-coverage",
        help="Informational ConceptualProperty coverage report (does not fail CI)",
    )
    _add_slice_args(coverage)
    coverage.add_argument("--json", action="store_true", help="Print JSON report")

    schema_diff = sub.add_parser(
        "schema-diff",
        help="Classify DAMS LinkML schema changes (breaking / additive / …)",
    )
    _add_slice_args(schema_diff)
    schema_diff.add_argument("--from", dest="from_ref", default=None)
    schema_diff.add_argument("--to", dest="to_ref", default=None)
    schema_diff.add_argument("--left", type=Path, default=None, help="Base schema YAML")
    schema_diff.add_argument("--right", type=Path, default=None, help="Target schema YAML")
    schema_diff.add_argument(
        "--changelog",
        type=Path,
        default=None,
        help="Changelog path covering breaking changes (default: docs/migration/CHANGELOG-technical-asset.md)",
    )
    schema_diff.add_argument(
        "--compatibility-baseline-ref",
        action="store_true",
        help="Mark that the target revision declares compatibility_baseline_ref",
    )
    schema_diff.add_argument(
        "--fail-on-breaking",
        action="store_true",
        help="Exit 1 when breaking changes are not covered by changelog/baseline",
    )
    schema_diff.add_argument("--json", action="store_true", help="Print JSON report")
    schema_diff.add_argument(
        "--out-json",
        type=Path,
        default=None,
        help="Write JSON report to path",
    )
    schema_diff.add_argument(
        "--out-text",
        type=Path,
        default=None,
        help="Write text summary to path",
    )

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
            "solutions/mdm/publications/vertical_slice.json)"
        ),
    )

    import_p = sub.add_parser(
        "import",
        help=(
            "ER-dictionary → ModelPackage, or schema-automator → generated-draft "
            "(ADR-009)"
        ),
    )
    _add_slice_args(import_p)
    import_p.add_argument(
        "--workbook",
        type=Path,
        default=None,
        help="Path to .xlsx or directory of CSV sheets (ER-dictionary mode)",
    )
    import_p.add_argument(
        "--profile",
        type=Path,
        default=None,
        dest="ingest_profile",
        help="Ingest profile YAML (ER-dictionary mode)",
    )
    import_p.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output directory (ER package or generated/imports parent)",
    )
    import_p.add_argument("--name", default=None, help="Artifact basename")
    import_p.add_argument(
        "--skip-validate",
        action="store_true",
        help="ER mode: write artifacts without linkml-validate",
    )
    import_p.add_argument(
        "--source-type",
        default=None,
        choices=["json_schema", "sql", "csv", "rdf"],
        help="schema-automator draft import (ADR-009)",
    )
    import_p.add_argument(
        "--source",
        type=Path,
        default=None,
        help="Source file for --source-type draft import",
    )

    import_sol = sub.add_parser(
        "import-solution",
        help="Object/ObjectAttribute xlsx → DAMS solution YAML (ADR-022)",
    )
    _add_slice_args(import_sol)
    import_sol.add_argument(
        "--xlsx",
        type=Path,
        required=True,
        help="Path to src_soluitions_model.xlsx (or fixture)",
    )
    import_sol.add_argument(
        "--system",
        required=True,
        help="SrcSystem value: MDM | UCD | CRM | ЕСЭД",
    )
    import_sol.add_argument(
        "--profile",
        type=Path,
        default=None,
        help=(
            "SolutionXlsxProfile YAML "
            "(default: model-assets/implementations/solutions/"
            "solution-xlsx.profile.yaml)"
        ),
    )
    import_sol.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Solution directory (default: model-assets/implementations/solutions/<slug>)",
    )
    import_sol.add_argument(
        "--report-dir",
        type=Path,
        default=None,
        help="Import report directory (default: tmp/solution-import/<slug>)",
    )
    import_sol.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing solution YAML",
    )
    import_sol.add_argument(
        "--strict",
        action="store_true",
        help="Promote SXI warnings to errors",
    )
    import_sol.add_argument(
        "--skip-validate",
        action="store_true",
        help="Skip LinkML ModelPackage validation",
    )
    import_sol.add_argument(
        "--skip-assess",
        action="store_true",
        help="Skip moex_dams assess",
    )
    import_sol.add_argument(
        "--skip-export",
        action="store_true",
        help="Skip vertical_slice.json export",
    )

    map_p = sub.add_parser(
        "map",
        help="SSSOM load, LinkML binding extract, or linkml-map transform (ADR-008)",
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
    map_p.add_argument(
        "--transform",
        type=Path,
        default=None,
        help="linkml-map transformation specification (MOEX envelope + body)",
    )
    map_p.add_argument(
        "--preview",
        type=Path,
        default=None,
        help="With --transform: sample path for preview",
    )
    map_p.add_argument(
        "--sample",
        type=Path,
        default=None,
        help="With --transform: sample path for transform_sample",
    )
    map_p.add_argument(
        "--backend",
        default="object",
        choices=["object", "sql"],
        help="With --transform: object (default ObjectTransformer) or sql (SQLCompiler)",
    )
    map_p.add_argument("--json", action="store_true", help="Print bindings/result as JSON")

    source = sub.add_parser(
        "source",
        help="List / sync / diff external specification sources (ADR-017)",
    )
    source_sub = source.add_subparsers(dest="source_action", required=True)

    source_list = source_sub.add_parser("list", help="List registered external sources")
    _add_slice_args(source_list)
    source_list.add_argument(
        "--sources-dir",
        type=Path,
        default=None,
        help="Override model-assets/external-sources",
    )
    source_list.add_argument("--json", action="store_true")

    source_sync = source_sub.add_parser("sync", help="Fetch + materialize + lock a source")
    _add_slice_args(source_sync)
    source_sync.add_argument("source_id", help="Directory name under external-sources/")
    source_sync.add_argument(
        "--seed",
        type=Path,
        default=None,
        help="Override seed term-file (ontology sources)",
    )
    source_sync.add_argument(
        "--dry-run",
        action="store_true",
        help="Materialize without writing lockfile",
    )
    source_sync.add_argument(
        "--sources-dir",
        type=Path,
        default=None,
        help="Override model-assets/external-sources",
    )
    source_sync.add_argument("--json", action="store_true")

    source_diff = source_sub.add_parser(
        "diff",
        help="Compare locked artifact to a fresh dry-run materialize",
    )
    _add_slice_args(source_diff)
    source_diff.add_argument("source_id")
    source_diff.add_argument("--from", dest="from_ref", default=None)
    source_diff.add_argument("--to", dest="to_ref", default=None)
    source_diff.add_argument("--seed", type=Path, default=None)
    source_diff.add_argument("--sources-dir", type=Path, default=None)
    source_diff.add_argument("--json", action="store_true")

    selection = sub.add_parser(
        "selection",
        help="Validate ExternalTermSelection packages (ADR-020)",
    )
    selection_sub = selection.add_subparsers(dest="selection_action", required=True)
    selection_validate = selection_sub.add_parser(
        "validate",
        help="Validate a selection.yaml against scope and ADR-020 invariants",
    )
    _add_slice_args(selection_validate)
    selection_validate.add_argument(
        "target",
        help="selection id under external-selections/ or path to selection.yaml",
    )
    selection_validate.add_argument("--json", action="store_true")

    export_req = sub.add_parser(
        "export-requirements",
        help="Dump DAMS RequirementCatalog YAML to XLSX (ADR-013)",
    )
    _add_slice_args(export_req)
    export_req.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output XLSX path",
    )
    export_req.add_argument(
        "--catalog",
        dest="catalogs",
        type=Path,
        action="append",
        default=None,
        help=(
            "Catalog YAML (repeatable). "
            "Default: moex-dams/0.1/requirements/*.yaml"
        ),
    )

    ontology = sub.add_parser(
        "ontology-report",
        help="DAMS schema URI profile or URI semantic diff (ADR-030)",
    )
    _add_slice_args(ontology)
    ontology.add_argument(
        "--from",
        dest="from_schema",
        type=Path,
        default=None,
        help="Old schema YAML for URI diff",
    )
    ontology.add_argument(
        "--to",
        dest="to_schema",
        type=Path,
        default=None,
        help="New schema YAML for URI diff",
    )
    ontology.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write ontology-profile JSON (also writes sibling .md)",
    )
    ontology.add_argument("--json", action="store_true", help="Print JSON")

    digest = sub.add_parser(
        "digest",
        help="Verify or rewrite DataModelBinding.integrity_digest (ADR-042)",
    )
    _add_slice_args(digest)
    digest.add_argument(
        "--model",
        default=None,
        help="Filter by element_id substring or path substring",
    )
    digest.add_argument(
        "--write",
        action="store_true",
        help="Write recomputed digests (examples/demo by default)",
    )
    digest.add_argument(
        "--allow-non-demo-write",
        action="store_true",
        help="Allow --write for non-example bindings (requires process from ADR-042)",
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
        schema=getattr(args, "schema", None),
        implementation=getattr(args, "implementation", None),
    )

    if args.command == "validate":
        from moex_model_cli.commands.validate import run_validate

        code, text = run_validate(
            paths,
            as_json=args.json,
            implementation_id=args.implementation_id,
        )
    elif args.command == "lint":
        from moex_model_cli.commands.lint import run_lint

        code, text = run_lint(paths)
    elif args.command == "compile":
        from moex_model_cli.commands.compile import run_compile

        code, text = run_compile(
            paths,
            with_json_schema=args.json_schema,
            with_artifacts=args.artifacts,
            with_bundle=args.bundle,
        )
    elif args.command == "diagram":
        from moex_model_cli.commands.diagram import run_diagram

        code, text = run_diagram(
            paths,
            out=args.out,
            profile=args.profile,
            fmt=args.fmt,
            render_svg=not getattr(args, "no_svg", False),
            reset_layout=bool(getattr(args, "reset_layout", False)),
        )
    elif args.command == "diff":
        from moex_model_cli.commands.diff import run_diff

        code, text = run_diff(
            paths,
            from_ref=args.from_ref,
            to_ref=args.to_ref,
            path=args.path,
        )
    elif args.command == "semantic-diff":
        from moex_model_cli.commands.semantic_diff import run_semantic_diff

        code, text = run_semantic_diff(
            paths,
            from_ref=args.from_ref,
            to_ref=args.to_ref,
            path=args.path,
            left=args.left,
            right=args.right,
            as_json=args.json,
        )
    elif args.command == "concept-coverage":
        from moex_model_cli.commands.concept_coverage import run_concept_coverage

        code, text = run_concept_coverage(paths, as_json=args.json)
    elif args.command == "schema-diff":
        from moex_model_cli.commands.schema_diff import run_schema_diff

        code, text = run_schema_diff(
            paths,
            from_ref=args.from_ref,
            to_ref=args.to_ref,
            left=args.left,
            right=args.right,
            changelog=args.changelog,
            has_compatibility_baseline_ref=args.compatibility_baseline_ref,
            fail_on_breaking=args.fail_on_breaking,
            as_json=args.json,
            out_json=args.out_json,
            out_text=args.out_text,
        )
    elif args.command == "publish":
        from moex_model_cli.commands.publish import run_publish

        code, text = run_publish(
            paths,
            out=args.out,
            implementation_id=args.implementation_id,
        )
    elif args.command == "import":
        from moex_model_cli.commands.import_ import run_import

        code, text = run_import(
            paths,
            workbook=args.workbook,
            profile=args.ingest_profile,
            out=args.out,
            name=args.name,
            skip_validate=args.skip_validate,
            schema=args.schema,
            source_type=args.source_type,
            source=args.source,
        )
    elif args.command == "import-solution":
        from moex_model_cli.commands.import_solution import run_import_solution

        code, text = run_import_solution(
            paths,
            xlsx=args.xlsx,
            system=args.system,
            profile=args.profile,
            out=args.out,
            report_dir=args.report_dir,
            force=args.force,
            strict=args.strict,
            skip_validate=args.skip_validate,
            skip_assess=args.skip_assess,
            skip_export=args.skip_export,
        )
    elif args.command == "map":
        from moex_model_cli.commands.map_cmd import run_map

        code, text = run_map(
            paths,
            sssom=args.sssom,
            extract_schema=args.extract_schema,
            transform=args.transform,
            preview=args.preview,
            sample=args.sample,
            as_json=args.json,
            backend=getattr(args, "backend", "object"),
        )
    elif args.command == "source":
        from moex_model_cli.commands.source_cmd import run_source

        code, text = run_source(
            paths,
            action=args.source_action,
            source_id=getattr(args, "source_id", None),
            seed=getattr(args, "seed", None),
            dry_run=getattr(args, "dry_run", False),
            as_json=getattr(args, "json", False),
            sources_dir=getattr(args, "sources_dir", None),
            from_ref=getattr(args, "from_ref", None),
            to_ref=getattr(args, "to_ref", None),
        )
    elif args.command == "selection":
        from moex_model_cli.commands.selection_cmd import run_selection_validate

        code, text = run_selection_validate(
            paths,
            target=args.target,
            as_json=getattr(args, "json", False),
        )
    elif args.command == "export-requirements":
        from moex_model_cli.commands.export_requirements import run_export_requirements

        code, text = run_export_requirements(
            paths,
            out=args.out,
            catalogs=args.catalogs,
        )
    elif args.command == "ontology-report":
        from moex_model_cli.commands.ontology_report import run_ontology_report

        code, text = run_ontology_report(
            paths,
            schema=getattr(args, "schema", None),
            from_schema=getattr(args, "from_schema", None),
            to_schema=getattr(args, "to_schema", None),
            as_json=getattr(args, "json", False),
            out=getattr(args, "out", None),
        )
    elif args.command == "digest":
        from moex_model_cli.commands.digest import run_digest

        code, text = run_digest(
            paths,
            model=args.model,
            write=args.write,
            allow_non_demo_write=args.allow_non_demo_write,
        )
    else:
        return 2

    sys.stdout.write(text)
    return code


if __name__ == "__main__":
    sys.exit(main())
