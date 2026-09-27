"""Load architecture-catalog.yaml from the repository root."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_publication_viewer.models.catalog_models import ArchitectureCatalog

CATALOG_RELATIVE = (
    Path("model-assets")
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "architecture-catalog.yaml"
)


def catalog_path(root: Path) -> Path:
    return root.resolve() / CATALOG_RELATIVE


def load_architecture_catalog(root: Path) -> ArchitectureCatalog | None:
    """Return catalog when present; missing file is allowed (flat module nav)."""
    path = catalog_path(root)
    if not path.is_file():
        return None
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if raw is None:
        return ArchitectureCatalog(nodes=[])
    return ArchitectureCatalog.model_validate(raw)
