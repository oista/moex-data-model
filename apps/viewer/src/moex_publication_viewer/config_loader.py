"""Load viewer UI config (colors, etc.) from apps/viewer/config/."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

DEFAULT_CLASS_KIND_COLORS: dict[str, Any] = {
    "roles": {
        "plain": "#3d8f6e",
        "mixin": "#3d6eb5",
        "abstract": "#2e8fad",
        "enum": "#b8922e",
    },
    "corner": {
        "has_mixins": "#3d6eb5",
    },
}


def load_class_kind_colors(viewer_root: Path) -> dict[str, Any]:
    path = viewer_root / "config" / "class-kind-colors.yaml"
    if not path.is_file():
        return dict(DEFAULT_CLASS_KIND_COLORS)
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    roles = {**(DEFAULT_CLASS_KIND_COLORS["roles"]), **(data.get("roles") or {})}
    corner = {**(DEFAULT_CLASS_KIND_COLORS["corner"]), **(data.get("corner") or {})}
    return {"roles": roles, "corner": corner}


def load_viewer_config(viewer_root: Path) -> dict[str, Any]:
    return {"class_kind_colors": load_class_kind_colors(viewer_root)}
