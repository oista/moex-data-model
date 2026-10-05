"""Normalize Mermaid erDiagram markdown (+ sibling SVG / DBML) for viewer."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from moex_publication_viewer.models.manifest_models import ManifestSection
from moex_publication_viewer.models.publication_models import PublicationSection
from moex_publication_viewer.normalizers.base import NormalizeError
from moex_publication_viewer.normalizers.helpers import section_meta

_SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
_MERMAID_FENCE_RE = re.compile(r"```mermaid\s*(.*?)```", re.IGNORECASE | re.DOTALL)


def _extract_mermaid_source(raw: str) -> str:
    m = _MERMAID_FENCE_RE.search(raw)
    if m:
        return m.group(1).strip() + "\n"
    stripped = raw.lstrip()
    if stripped.startswith("erDiagram"):
        return stripped if stripped.endswith("\n") else stripped + "\n"
    return raw.strip() + "\n"


def _sanitize_svg(svg: str) -> str:
    cleaned = _SCRIPT_RE.sub("", svg)
    # Keep only from first <svg to last </svg>
    start = cleaned.lower().find("<svg")
    end = cleaned.lower().rfind("</svg>")
    if start >= 0 and end > start:
        return cleaned[start : end + len("</svg>")].strip()
    return cleaned.strip()


def _sibling_dbml_path(source_path: Path) -> Path:
    """``logical.erd.md`` → ``logical.dbml``; otherwise ``{stem}.dbml``."""
    name = source_path.name
    if name.endswith(".erd.md"):
        return source_path.parent / f"{name[: -len('.erd.md')]}.dbml"
    return source_path.with_suffix(".dbml")


def _load_dbml_source(source_path: Path) -> tuple[str, bool]:
    dbml_path = _sibling_dbml_path(source_path)
    if not dbml_path.is_file():
        return "", True
    try:
        text = dbml_path.read_text(encoding="utf-8")
    except OSError:
        return "", True
    if not text.strip():
        return "", True
    return text if text.endswith("\n") else text + "\n", False


def _load_clickmap(source_path: Path) -> dict[str, Any] | None:
    """Load sibling ``*.erd.clickmap.json`` when present (conceptual diagrams)."""
    clickmap_path = source_path.parent / (source_path.stem + ".clickmap.json")
    if not clickmap_path.is_file():
        return None
    try:
        raw = json.loads(clickmap_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return raw if isinstance(raw, dict) else None


def _profile_base(source_path: Path) -> str:
    """``logical.erd.md`` → ``logical``; otherwise stem."""
    name = source_path.name
    if name.endswith(".erd.md"):
        return name[: -len(".erd.md")]
    return source_path.stem


def _load_json_sibling(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return raw if isinstance(raw, dict) else None


def _repo_relative_path(path: Path) -> str:
    """Prefer path under ``model-assets/…``; else basename."""
    resolved = path.resolve()
    parts = resolved.parts
    if "model-assets" in parts:
        i = parts.index("model-assets")
        return "/".join(parts[i:])
    return resolved.name


class MermaidDiagramNormalizer:
    """Load ``*.erd.md``; embed sibling SVG / DBML / scene / layout when present."""

    def normalize(self, section: ManifestSection, source_path: Path) -> PublicationSection:
        try:
            raw = source_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise NormalizeError(f"cannot read mermaid diagram {source_path}: {exc}") from exc

        mermaid_source = _extract_mermaid_source(raw)
        svg_path = source_path.with_suffix(".svg")
        content = ""
        svg_missing = True
        if svg_path.is_file():
            try:
                content = _sanitize_svg(svg_path.read_text(encoding="utf-8"))
                svg_missing = not bool(content)
            except OSError:
                content = ""
                svg_missing = True

        dbml_source, dbml_missing = _load_dbml_source(source_path)
        base = _profile_base(source_path)
        scene_path = source_path.parent / f"{base}.scene.json"
        layout_path = source_path.parent / f"{base}.layout.json"
        scene = _load_json_sibling(scene_path)
        layout = _load_json_sibling(layout_path)

        attrs: dict[str, Any] = {
            "mermaid_source": mermaid_source,
            "svg_missing": svg_missing,
            "dbml_source": dbml_source,
            "dbml_missing": dbml_missing,
        }
        clickmap = _load_clickmap(source_path)
        if clickmap is not None:
            attrs["erd_clickmap"] = clickmap
        if scene is not None:
            attrs["erd_scene"] = scene
        if layout is not None:
            from moex_publication_viewer.edits import value_hash

            attrs["erd_layout"] = layout
            attrs["erd_layout_path"] = _repo_relative_path(layout_path)
            attrs["erd_layout_hash"] = value_hash(layout)

        meta = section_meta(section)
        return PublicationSection(
            **meta,
            items=[],
            content=content,
            attributes=attrs,
        )
