"""Normalize a single authored YAML path into a source_file publication card."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from moex_publication_viewer.models.manifest_models import ManifestSection
from moex_publication_viewer.models.publication_models import (
    PublicationItem,
    PublicationSection,
)
from moex_publication_viewer.normalizers.base import NormalizeError
from moex_publication_viewer.normalizers.helpers import section_meta


def _yaml_meta(path: Path) -> tuple[str | None, str | None]:
    """Best-effort (version, description) from YAML mapping root."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None, None
    if not isinstance(data, dict):
        return None, None
    version = data.get("version")
    if version is not None:
        version = str(version)
    description = data.get("description")
    if description is not None:
        description = str(description)
    return version, description


class SourceFileNormalizer:
    """Load one YAML file as a DAMS-style ``source_file`` card item."""

    def normalize(self, section: ManifestSection, source_path: Path) -> PublicationSection:
        if not source_path.is_file():
            raise NormalizeError(f"source file not found: {source_path}")
        try:
            text = source_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise NormalizeError(f"cannot read source file {source_path}: {exc}") from exc
        if not text.strip():
            raise NormalizeError(f"source file is empty: {source_path}")

        version, yaml_description = _yaml_meta(source_path)
        file_name = source_path.name
        # Prefer section description (functional); fall back to YAML description.
        description = section.description or yaml_description or None
        rel_path = section.source.path.replace("\\", "/")
        item_id = f"file:{rel_path}"
        attrs: dict[str, Any] = {
            "kind": "source_file",
            "path": rel_path,
            "file_name": file_name,
            "text": text,
            "refs_out": [],
            "refs_in": [],
        }
        if version:
            attrs["version"] = version
        if description:
            attrs["description"] = description

        item = PublicationItem(
            id=item_id,
            title=section.title,
            description=description,
            attributes=attrs,
        )
        return PublicationSection(**section_meta(section), items=[item])
