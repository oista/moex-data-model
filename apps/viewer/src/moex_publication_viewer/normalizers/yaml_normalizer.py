"""YAML normalizer."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_publication_viewer.models.manifest_models import ManifestSection
from moex_publication_viewer.models.publication_models import PublicationItem, PublicationSection
from moex_publication_viewer.normalizers.base import NormalizeError
from moex_publication_viewer.normalizers.edit_targets import attach_yaml_list_edit_targets
from moex_publication_viewer.normalizers.helpers import (
    flatten_publication_requirements,
    records_to_items,
    section_meta,
    select_path,
)
from moex_publication_viewer.normalizers.conceptual_entity_links_projection import (
    project_conceptual_entity_links,
)
from moex_publication_viewer.normalizers.model_glossary_projection import (
    project_model_glossary,
)

FLATTENED_REQUIREMENTS_SELECT = "flattened_requirements"
MODEL_GLOSSARY_SELECT = "model_glossary"
CONCEPTUAL_ENTITY_LINKS_SELECT = "conceptual_entity_links"


class YamlNormalizer:
    def normalize(self, section: ManifestSection, source_path: Path) -> PublicationSection:
        try:
            data = yaml.safe_load(source_path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise NormalizeError(f"cannot parse YAML {source_path}: {exc}") from exc

        select = section.source.select
        skip_edit = select in (
            FLATTENED_REQUIREMENTS_SELECT,
            MODEL_GLOSSARY_SELECT,
            CONCEPTUAL_ENTITY_LINKS_SELECT,
        )
        if select == FLATTENED_REQUIREMENTS_SELECT:
            selected = flatten_publication_requirements(data)
        elif select == MODEL_GLOSSARY_SELECT:
            selected = project_model_glossary(data)
        elif select == CONCEPTUAL_ENTITY_LINKS_SELECT:
            selected = project_conceptual_entity_links(data)
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
            if (
                not skip_edit
                and isinstance(selected, list)
                and select
                and "." not in select  # top-level list only for v1
            ):
                records = [r for r in selected if isinstance(r, dict)]
                items = attach_yaml_list_edit_targets(
                    items,
                    source_path=source_path,
                    select=select,
                    records=records,
                    key_column=section.key_column,
                )

        return PublicationSection(**section_meta(section), items=items)
