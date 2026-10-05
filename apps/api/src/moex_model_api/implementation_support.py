"""Workbench helpers over ImplementationCatalog (no FastAPI imports)."""

from __future__ import annotations

from moex_modeling import ImplementationAsset
from moex_model_cli.bootstrap import SlicePaths


def is_workbench_editable(asset: ImplementationAsset) -> bool:
    return (
        asset.implementation_kind == "linkml"
        and asset.implementation_profile == "dams-data-model"
    )


def paths_for_asset(
    *,
    root,
    catalog,
    asset: ImplementationAsset,
) -> SlicePaths:
    return SlicePaths.resolve(
        root=root,
        schema=catalog.resolve_schema(asset.id),
        implementation=asset.body_path,
    )


def relative_body_path(root, asset: ImplementationAsset) -> str:
    try:
        return asset.body_path.relative_to(root).as_posix()
    except ValueError:
        return asset.body_path.as_posix()


__all__ = [
    "is_workbench_editable",
    "paths_for_asset",
    "relative_body_path",
]
