"""Markdown normalizer."""

from __future__ import annotations

from pathlib import Path

import markdown

from moex_publication_viewer.models.manifest_models import ManifestSection
from moex_publication_viewer.models.publication_models import PublicationSection
from moex_publication_viewer.normalizers.base import NormalizeError
from moex_publication_viewer.normalizers.helpers import section_meta


class MarkdownNormalizer:
    def normalize(self, section: ManifestSection, source_path: Path) -> PublicationSection:
        try:
            raw = source_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise NormalizeError(f"cannot read markdown {source_path}: {exc}") from exc

        body = raw
        if raw.startswith("---"):
            parts = raw.split("---", 2)
            if len(parts) >= 3:
                body = parts[2].lstrip("\n")

        html = markdown.markdown(body, extensions=["fenced_code", "tables"])
        return PublicationSection(**section_meta(section), items=[], content=html)
