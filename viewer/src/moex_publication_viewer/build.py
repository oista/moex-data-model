"""Compile manifests into PublicationModule list and render HTML."""

from __future__ import annotations

import json
from pathlib import Path

from moex_publication_viewer.discovery import discover_manifest_paths
from moex_publication_viewer.manifest_loader import load_manifest, resolve_source_path
from moex_publication_viewer.models.publication_models import PublicationModule
from moex_publication_viewer.normalizers import get_normalizer
from moex_publication_viewer.normalizers.base import NormalizeError
from moex_publication_viewer.normalizers.linkml_normalizer import clear_schema_view_cache
from moex_publication_viewer.renderers.html_renderer import render_viewer
from moex_publication_viewer.validators import ValidationError, validate_manifests

PACKAGE_DIR = Path(__file__).resolve().parent
VIEWER_ROOT = PACKAGE_DIR.parent.parent  # viewer/


def compile_modules(root: Path) -> list[PublicationModule]:
    clear_schema_view_cache()
    paths = discover_manifest_paths(root)
    pairs = []
    for path in paths:
        manifest = load_manifest(path)
        if manifest is None:
            continue
        pairs.append((path, manifest))

    validate_manifests(pairs)

    modules: list[PublicationModule] = []
    errors: list[str] = []

    for path, manifest in pairs:
        sections = []
        for section in manifest.sections:
            source_path = resolve_source_path(path, section.source.path)
            try:
                normalizer = get_normalizer(section.source.format)
            except KeyError:
                errors.append(
                    f"{path}: unsupported source.format '{section.source.format}' "
                    f"in section '{section.id}'"
                )
                continue
            try:
                pub_section = normalizer.normalize(section, source_path)
            except NormalizeError as exc:
                errors.append(f"{path}: section '{section.id}': {exc}")
                continue
            if not pub_section.items and not pub_section.content:
                errors.append(
                    f"{path}: section '{section.id}' is empty after normalize "
                    f"(source: {source_path})"
                )
                continue
            sections.append(pub_section)

        modules.append(
            PublicationModule(
                module_id=manifest.module_id,
                title=manifest.title,
                description=manifest.description,
                icon=manifest.icon,
                version=manifest.version,
                order=manifest.order,
                sections=sections,
                manifest_path=str(path),
            )
        )

    if errors:
        raise ValidationError(errors)

    modules.sort(key=lambda m: (m.order, m.title))
    return modules


def build_search_index(modules: list[PublicationModule]) -> list[dict]:
    index: list[dict] = []
    for mod in modules:
        index.append(
            {
                "kind": "module",
                "module_id": mod.module_id,
                "title": mod.title,
                "description": mod.description or "",
            }
        )
        for sec in mod.sections:
            index.append(
                {
                    "kind": "section",
                    "module_id": mod.module_id,
                    "section_id": sec.id,
                    "title": sec.title,
                    "description": sec.description or "",
                }
            )
            for item in sec.items:
                _index_item(index, mod.module_id, sec.id, item)
    return index


def _index_item(index: list[dict], module_id: str, section_id: str, item) -> None:
    # Hierarchy-only group nodes are not selectable cards — skip search hits
    attrs = item.attributes or {}
    if attrs.get("kind") != "group":
        index.append(
            {
                "kind": "item",
                "module_id": module_id,
                "section_id": section_id,
                "item_id": item.id,
                "title": item.title or item.id,
                "description": item.description or "",
            }
        )
    for child in item.children:
        _index_item(index, module_id, section_id, child)


def build(root: Path, dist_dir: Path | None = None) -> Path:
    """Build viewer into dist_dir (default viewer/dist). Returns index.html path."""
    root = root.resolve()
    if dist_dir is None:
        dist_dir = VIEWER_ROOT / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)

    modules = compile_modules(root)
    search_index = build_search_index(modules)

    registry = {
        "modules": [
            {
                "module_id": m.module_id,
                "title": m.title,
                "sections": [s.id for s in m.sections],
                "manifest_path": m.manifest_path,
            }
            for m in modules
        ]
    }
    (dist_dir / "manifest_registry.json").write_text(
        json.dumps(registry, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    html = render_viewer(modules, search_index, VIEWER_ROOT)
    index_path = dist_dir / "index.html"
    index_path.write_text(html, encoding="utf-8")

    static_src = VIEWER_ROOT / "static"
    for name in ("viewer.css", "viewer.js"):
        src = static_src / name
        if src.is_file():
            (dist_dir / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    return index_path
