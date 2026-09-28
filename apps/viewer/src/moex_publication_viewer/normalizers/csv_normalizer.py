"""CSV normalizer."""

from __future__ import annotations

import csv
from pathlib import Path

from moex_publication_viewer.models.manifest_models import ManifestSection
from moex_publication_viewer.models.publication_models import PublicationSection
from moex_publication_viewer.normalizers.base import NormalizeError
from moex_publication_viewer.normalizers.helpers import (
    items_to_domain_explorer,
    items_to_tree,
    records_to_items,
    section_meta,
)


class CsvNormalizer:
    def normalize(self, section: ManifestSection, source_path: Path) -> PublicationSection:
        try:
            with source_path.open(encoding="utf-8-sig", newline="") as fh:
                reader = csv.DictReader(fh)
                rows = list(reader)
                headers = list(reader.fieldnames or [])
        except Exception as exc:
            raise NormalizeError(f"cannot parse CSV {source_path}: {exc}") from exc

        items = records_to_items(rows, key_column=section.key_column)
        if section.type == "tree":
            items = items_to_tree(items)
        elif section.type == "explorer":
            items = items_to_domain_explorer(items)
        meta = section_meta(section)
        meta["columns"] = section.columns or headers
        return PublicationSection(**meta, items=items)
