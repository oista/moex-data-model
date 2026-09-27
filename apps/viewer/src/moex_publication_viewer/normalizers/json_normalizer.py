"""JSON normalizer."""

from __future__ import annotations

import json
from pathlib import Path

from moex_publication_viewer.models.manifest_models import ManifestSection
from moex_publication_viewer.models.publication_models import PublicationItem, PublicationSection
from moex_publication_viewer.normalizers.base import NormalizeError
from moex_publication_viewer.normalizers.helpers import records_to_items, section_meta, select_path


class JsonNormalizer:
    def normalize(self, section: ManifestSection, source_path: Path) -> PublicationSection:
        try:
            data = json.loads(source_path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise NormalizeError(f"cannot parse JSON {source_path}: {exc}") from exc
        try:
            selected = select_path(data, section.source.select)
        except KeyError as exc:
            raise NormalizeError(str(exc)) from exc

        if section.type == "key-value" and isinstance(selected, dict):
            items = [
                PublicationItem(id=str(k), title=str(k), attributes={"value": v})
                for k, v in selected.items()
                if not isinstance(v, (list, dict))
            ]
        else:
            items = records_to_items(selected, key_column=section.key_column)

        return PublicationSection(**section_meta(section), items=items)
