"""import — ER-dictionary ingest or schema-automator draft (ADR-009)."""

from __future__ import annotations

import logging
from pathlib import Path
from types import SimpleNamespace

from moex_model_cli.bootstrap import SlicePaths
from moex_modeling.import_draft.public import ImportSourceType
from moex_modeling.shared.enums import DiagnosticSeverity
from moex_standard_linkml.ingest.cli import cmd_ingest


def run_import(
    paths: SlicePaths,
    *,
    out: Path | None = None,
    workbook: Path | None = None,
    profile: Path | None = None,
    name: str | None = None,
    skip_validate: bool = False,
    schema: Path | None = None,
    source_type: str | None = None,
    source: Path | None = None,
) -> tuple[int, str]:
    if source_type is not None:
        return _run_automator_import(
            paths,
            source_type=source_type,
            source=source,
            out=out,
            name=name,
        )

    if workbook is None or profile is None or out is None:
        return (
            2,
            "moex-model import requires either "
            "(--workbook --profile --out) for ER-dictionary, or "
            "(--source-type --source --out) for schema-automator draft (ADR-009)\n",
        )

    wb = workbook if workbook.is_absolute() else (paths.root / workbook).resolve()
    prof = profile if profile.is_absolute() else (paths.root / profile).resolve()
    out_dir = out if out.is_absolute() else (paths.root / out).resolve()
    schema_path = schema if schema is not None else paths.schema
    if schema_path is not None and not schema_path.is_absolute():
        schema_path = (paths.root / schema_path).resolve()

    if not wb.exists():
        return 2, f"workbook not found: {wb}\n"
    if not prof.is_file():
        return 2, f"ingest profile not found: {prof}\n"
    if schema_path is None or not schema_path.is_file():
        return 2, f"DAMS schema not found: {schema_path}\n"

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
        force=True,
    )
    args = SimpleNamespace(
        workbook=wb,
        profile=prof,
        schema=schema_path,
        out=out_dir,
        name=name,
        skip_validate=skip_validate,
        verbose=False,
    )
    code = cmd_ingest(args)
    basename_hint = name or prof.stem
    if code == 0:
        return (
            0,
            f"import OK workbook={wb} out={out_dir} "
            f"(package/envelope under basename≈{basename_hint})\n",
        )
    if code == 1:
        return 1, f"import validation failed (see artifacts under {out_dir})\n"
    return code, f"import failed (exit {code})\n"


def _run_automator_import(
    paths: SlicePaths,
    *,
    source_type: str,
    source: Path | None,
    out: Path | None,
    name: str | None,
) -> tuple[int, str]:
    if source is None or out is None:
        return (
            2,
            "moex-model import --source-type requires --source and --out\n",
        )
    try:
        ImportSourceType(source_type)
    except ValueError:
        allowed = ", ".join(t.value for t in ImportSourceType)
        return 2, f"unknown --source-type {source_type!r}; expected one of: {allowed}\n"

    try:
        from moex_linkml_tooling.import_engine import SchemaAutomatorImportEngine
    except ImportError:
        return (
            1,
            "moex-model import --source-type requires moex-linkml-tooling[automator]\n",
        )

    src = source if source.is_absolute() else (paths.root / source).resolve()
    out_dir = out if out.is_absolute() else (paths.root / out).resolve()
    if not src.is_file():
        return 2, f"import source not found: {src}\n"

    engine = SchemaAutomatorImportEngine()
    try:
        manifest = engine.run_import(
            src,
            source_type,
            out_dir,
            options={"name": name} if name else None,
        )
    except (OSError, ValueError, TypeError) as exc:
        return 1, f"import draft failed: {exc}\n"

    fatal = any(
        d.severity in {DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL}
        for d in manifest.diagnostics
    )
    job_dir = out_dir / manifest.job_id
    msg = (
        f"import draft OK status={manifest.status} job={manifest.job_id} "
        f"digest={manifest.source_digest} out={job_dir} "
        f"diagnostics={len(manifest.diagnostics)}\n"
    )
    if fatal:
        return 1, f"import draft failed status={manifest.status} job={manifest.job_id}\n"
    # Surface warnings on stderr via return text (stdout)
    warns = [
        d.diagnostic_message
        for d in manifest.diagnostics
        if d.severity == DiagnosticSeverity.WARNING
    ]
    if warns:
        msg += "warnings:\n" + "\n".join(f"  - {w}" for w in warns) + "\n"
    return 0, msg
