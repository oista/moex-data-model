"""import — ER-dictionary → DAMS ModelPackage (ADR-009: not schema-automator)."""

from __future__ import annotations

import logging
from pathlib import Path
from types import SimpleNamespace

from moex_model_cli.bootstrap import SlicePaths
from moex_standard_linkml.ingest.cli import cmd_ingest


def run_import(
    paths: SlicePaths,
    *,
    workbook: Path,
    profile: Path,
    out: Path,
    name: str | None = None,
    skip_validate: bool = False,
    schema: Path | None = None,
) -> tuple[int, str]:
    """Facade over ``moex_standard_linkml.ingest`` (same logic as ``moex-linkml ingest``)."""
    if workbook is None or profile is None or out is None:
        return (
            2,
            "moex-model import requires --workbook, --profile, and --out "
            "(ER-dictionary → ModelPackage draft; schema-automator = Stage 7 / ADR-009)\n",
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

    # cmd_ingest prints to stdout/stderr; capture message for CLI consistency
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
