"""Load viewer UI config (colors, display catalog) from apps/viewer/config/."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

DEFAULT_CLASS_KIND_COLORS: dict[str, Any] = {
    "roles": {
        "plain": "#3d8f6e",
        "mixin": "#3d6eb5",
        "abstract": "#2e8fad",
        "enum": "#9a7a18",
    },
    "corner": {
        "has_mixins": "#3d6eb5",
    },
}

DEFAULT_DISPLAY_SETTINGS: list[dict[str, Any]] = [
    {
        "key": "appearance.theme",
        "type": "choice",
        "options": ["light", "dark", "system"],
        "default": "light",
        "label": "Theme",
        "group": "Appearance",
    },
    {
        "key": "appearance.density",
        "type": "choice",
        "options": ["comfortable", "compact"],
        "default": "comfortable",
        "label": "Density",
        "group": "Appearance",
    },
    {
        "key": "appearance.palette",
        "type": "choice",
        "options": ["default"],
        "default": "default",
        "label": "Color palette",
        "group": "Appearance",
    },
    {
        "key": "navigation.hidden_roots",
        "type": "multi-from-data",
        "default": [],
        "label": "Hidden navigation roots",
        "description": "Hides sidebar roots only. Search and deep links still open items.",
        "group": "Navigation",
    },
    {
        "key": "text.hide_adr_refs",
        "type": "bool",
        "default": False,
        "label": "Hide ADR references in text",
        "description": "Strips mentions like (ADR-016/019) from displayed descriptions.",
        "group": "Text",
    },
    {
        "key": "glossary.show_relation_blocks",
        "type": "bool",
        "default": True,
        "label": "Show Taxonomy / See also blocks",
        "description": "ADR-027 relation blocks on glossary term cards.",
        "group": "Glossary",
    },
    {
        "key": "glossary.show_overview_folder",
        "type": "bool",
        "default": True,
        "label": "Show Overview → Glossary folder",
        "group": "Glossary",
    },
    {
        "key": "glossary.view",
        "type": "choice",
        "options": ["by-definition-site", "flat-az"],
        "default": "by-definition-site",
        "label": "Glossary folder view",
        "description": (
            "Definition-site folders vs flat A–Z section link under Overview → Glossary."
        ),
        "group": "Glossary",
    },
]

DEFAULT_DISPLAY_CONFIG: dict[str, Any] = {
    "version": 1,
    "settings": list(DEFAULT_DISPLAY_SETTINGS),
    "presets": {},
}


def load_class_kind_colors(viewer_root: Path) -> dict[str, Any]:
    path = viewer_root / "config" / "class-kind-colors.yaml"
    if not path.is_file():
        return {
            "roles": dict(DEFAULT_CLASS_KIND_COLORS["roles"]),
            "corner": dict(DEFAULT_CLASS_KIND_COLORS["corner"]),
        }
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    roles = {**(DEFAULT_CLASS_KIND_COLORS["roles"]), **(data.get("roles") or {})}
    corner = {**(DEFAULT_CLASS_KIND_COLORS["corner"]), **(data.get("corner") or {})}
    return {"roles": roles, "corner": corner}


def _normalize_setting(raw: dict[str, Any], fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    base = dict(fallback or {})
    base.update({k: v for k, v in raw.items() if v is not None})
    key = base.get("key")
    if not key:
        raise ValueError("display setting missing key")
    stype = base.get("type") or "bool"
    base["key"] = str(key)
    base["type"] = str(stype)
    if "label" not in base:
        base["label"] = str(key)
    if stype == "choice":
        options = list(base.get("options") or [])
        if not options and fallback:
            options = list(fallback.get("options") or [])
        base["options"] = [str(o) for o in options]
        default = base.get("default", options[0] if options else None)
        if default is not None and options and default not in options:
            default = options[0]
        base["default"] = default
    elif stype == "multi-from-data":
        default = base.get("default", [])
        if not isinstance(default, list):
            default = []
        base["default"] = [str(x) for x in default]
    elif stype == "bool":
        base["default"] = bool(base.get("default", False))
    return base


def load_display_config(viewer_root: Path) -> dict[str, Any]:
    """Load display settings catalog; merge YAML over built-in defaults by key."""
    path = viewer_root / "config" / "display.yaml"
    by_key = {s["key"]: dict(s) for s in DEFAULT_DISPLAY_SETTINGS}
    version = DEFAULT_DISPLAY_CONFIG["version"]
    presets: dict[str, Any] = {}
    if path.is_file():
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        version = int(data.get("version") or version)
        presets = dict(data.get("presets") or {})
        for raw in data.get("settings") or []:
            if not isinstance(raw, dict) or not raw.get("key"):
                continue
            key = str(raw["key"])
            by_key[key] = _normalize_setting(raw, by_key.get(key))
    settings = [_normalize_setting(by_key[k]) for k in by_key]
    # Stable order: Appearance, Navigation, Text, Glossary, then rest
    group_order = {"Appearance": 0, "Navigation": 1, "Text": 2, "Glossary": 3}
    settings.sort(key=lambda s: (group_order.get(s.get("group") or "", 99), s["key"]))
    defaults = {s["key"]: s["default"] for s in settings}
    return {
        "version": version,
        "settings": settings,
        "defaults": defaults,
        "presets": presets,
    }


def load_viewer_config(viewer_root: Path) -> dict[str, Any]:
    return {
        "class_kind_colors": load_class_kind_colors(viewer_root),
        "display": load_display_config(viewer_root),
    }
