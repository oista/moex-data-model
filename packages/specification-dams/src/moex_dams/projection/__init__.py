"""Derived projections from DAMS ModelPackage instances (ADR-006)."""

from __future__ import annotations

from moex_dams.projection.dbml import (
    DbmlManifest,
    project_model_package_to_dbml,
    write_dbml_artifact,
)
from moex_dams.projection.er_layout import (
    merge_layout,
    seed_layout,
    validate_layout,
    write_or_merge_layout,
)
from moex_dams.projection.er_scene import (
    ErSceneManifest,
    project_model_package_to_er_scene,
    write_er_scene_artifact,
)
from moex_dams.projection.mermaid_er import (
    ErDiagramManifest,
    build_er_clickmap,
    project_model_package_to_er_diagram,
    try_render_er_svg,
    write_er_diagram_artifact,
)

__all__ = [
    "DbmlManifest",
    "ErDiagramManifest",
    "ErSceneManifest",
    "build_er_clickmap",
    "merge_layout",
    "project_model_package_to_dbml",
    "project_model_package_to_er_diagram",
    "project_model_package_to_er_scene",
    "seed_layout",
    "try_render_er_svg",
    "validate_layout",
    "write_dbml_artifact",
    "write_er_diagram_artifact",
    "write_er_scene_artifact",
    "write_or_merge_layout",
]
