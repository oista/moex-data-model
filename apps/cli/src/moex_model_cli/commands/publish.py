"""publish command — calls publication export_slice_projection."""

from __future__ import annotations

from pathlib import Path

from moex_publication.application.build_publication import (
    build_publication_module,
    export_slice_projection,
)
from moex_model_cli.bootstrap import DEFAULT_SLICE_JSON, SlicePaths


def run_publish(
    paths: SlicePaths,
    *,
    out: Path | None = None,
    implementation_id: str | None = None,
) -> tuple[int, str]:
    out_path = out if out is not None else paths.root / DEFAULT_SLICE_JSON
    if not out_path.is_absolute():
        out_path = (paths.root / out_path).resolve()
    result = export_slice_projection(
        schema_path=paths.schema,
        implementation_path=paths.implementation,
        out_path=out_path,
        implementation_id=implementation_id,
    )
    module = build_publication_module(result)
    text = (
        f"wrote {out_path} module={module.module_id} "
        f"overall={result.report.overall_result.value}\n"
    )
    return (0 if result.report.is_conformant else 1, text)
