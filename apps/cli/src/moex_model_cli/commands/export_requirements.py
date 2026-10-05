"""export-requirements — dump DAMS RequirementCatalog YAML to XLSX."""

from __future__ import annotations

from pathlib import Path

from moex_dams.application.export_requirements import (
    collect_requirement_rows,
    default_catalog_paths,
    write_requirements_xlsx,
)
from moex_model_cli.bootstrap import SlicePaths


def run_export_requirements(
    paths: SlicePaths,
    *,
    out: Path,
    catalogs: list[Path] | None = None,
) -> tuple[int, str]:
    catalog_paths = catalogs or default_catalog_paths(paths.root)
    catalog_paths = [
        p if p.is_absolute() else paths.root / p for p in catalog_paths
    ]
    missing = [p for p in catalog_paths if not p.is_file()]
    if missing:
        names = ", ".join(str(p) for p in missing)
        return 2, f"export-requirements: catalog not found: {names}\n"
    try:
        rows = collect_requirement_rows(catalog_paths, root=paths.root)
        n = write_requirements_xlsx(rows, out)
    except Exception as exc:
        return 2, f"export-requirements failed: {exc}\n"
    return 0, (
        f"export-requirements out={out} rows={n} catalogs={len(catalog_paths)}\n"
    )
