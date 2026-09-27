"""Load and lightly filter publish.yaml files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from moex_publication_viewer.models.manifest_models import PublicationManifest


class ManifestLoadError(Exception):
    def __init__(self, path: Path, message: str) -> None:
        self.path = path
        super().__init__(f"{path}: {message}")


def load_raw_yaml(path: Path) -> dict[str, Any] | None:
    """Load YAML. Returns None if kind is missing/other (skip silently)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ManifestLoadError(path, f"cannot read file: {exc}") from exc
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ManifestLoadError(path, f"invalid YAML: {exc}") from exc
    if data is None:
        return None
    if not isinstance(data, dict):
        raise ManifestLoadError(path, "manifest root must be a mapping")
    kind = data.get("kind")
    if kind != "publication_module":
        return None
    return data


def load_manifest(path: Path) -> PublicationManifest | None:
    """Parse a publication_module manifest, or return None to skip."""
    data = load_raw_yaml(path)
    if data is None:
        return None
    try:
        return PublicationManifest.model_validate(data)
    except Exception as exc:  # pydantic ValidationError
        raise ManifestLoadError(path, f"validation failed: {exc}") from exc


def resolve_source_path(manifest_path: Path, relative: str) -> Path:
    """Resolve source.path relative to the manifest directory."""
    return (manifest_path.parent / relative).resolve()
