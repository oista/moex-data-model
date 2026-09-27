"""Normalizer protocol and registry."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from moex_publication_viewer.models.manifest_models import ManifestSection
from moex_publication_viewer.models.publication_models import PublicationSection


class Normalizer(Protocol):
    def normalize(
        self,
        section: ManifestSection,
        source_path: Path,
    ) -> PublicationSection: ...


class NormalizeError(Exception):
    def __init__(self, message: str, *, manifest_hint: str | None = None) -> None:
        prefix = f"{manifest_hint}: " if manifest_hint else ""
        super().__init__(f"{prefix}{message}")
