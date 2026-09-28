"""YAML normalizer."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_publication_viewer.models.manifest_models import ManifestSection
from moex_publication_viewer.models.publication_models import PublicationItem, PublicationSection
from moex_publication_viewer.normalizers.base import NormalizeError
from moex_publication_viewer.normalizers.helpers import (
    flatten_publication_requirements,
    records_to_items,
    section_meta,
    select_path,
)

FLATTENED_REQUIREMENTS_SELECT = "flattened_requirements"


class YamlNormalizer:
    def normalize(self, section: ManifestSection, source_path: Path) -> PublicationSection:
        try:
            data = yaml.safe_load(source_path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise NormalizeError(f"cannot parse YAML {source_path}: {exc}") from exc

        select = section.source.select
        if select == FLATTENED_REQUIREMENTS_SELECT:
            selected = flatten_publication_requirements(data)
        else:
            try:
                selected = select_path(data, select)
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
