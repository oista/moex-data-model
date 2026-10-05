"""Pydantic ingest profile: sheet/column mapping, defaults, type_map."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator


class SheetColumns(BaseModel):
    """Logical column keys → header names in the workbook/CSV."""

    model_config = {"extra": "allow"}

    name: str = "name"
    title: str | None = "title"
    description: str | None = "description"
    entity: str | None = None
    type: str | None = None
    required: str | None = None
    pk: str | None = None
    source: str | None = None
    target: str | None = None
    source_role: str | None = None
    target_role: str | None = None
    source_card: str | None = None
    target_card: str | None = None
    identifying: str | None = None
    conceptual_ref: str | None = None
    object: str | None = None
    object_kind: str | None = None
    asset_kind: str | None = None
    asset_namespace: str | None = None
    qualified_name: str | None = None
    technology: str | None = None
    system_ref: str | None = None
    direction: str | None = None
    native_schema_ref: str | None = None
    structure_ref: str | None = None
    db_schema: str | None = None
    database: str | None = None
    parent_ref: str | None = None
    native_name: str | None = None
    native_type: str | None = None
    schema_path: str | None = None
    mapping_type: str | None = None
    mapping_cardinality: str | None = None


class SheetSpec(BaseModel):
    sheet: str
    required: bool = True
    columns: SheetColumns = Field(default_factory=SheetColumns)


class SheetsConfig(BaseModel):
    entities: SheetSpec
    attributes: SheetSpec
    relationships: SheetSpec | None = None
    conceptual: SheetSpec | None = None
    data_carriers: SheetSpec | None = None
    physical_fields: SheetSpec | None = None
    mappings: SheetSpec | None = None

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):  # type: ignore[override]
        if isinstance(obj, dict):
            legacy = "physical" + "_objects"
            if legacy in obj and "data_carriers" not in obj:
                obj = dict(obj)
                obj["data_carriers"] = obj.pop(legacy)
        return super().model_validate(obj, *args, **kwargs)


class IngestDefaults(BaseModel):
    lifecycle_status: str = "draft"
    solution_data_role: str = "producer"
    domain_ref: str = "eam:domain/PILOT"
    namespace: str = "https://data.moex.com/models/pilot/"
    entity_type: str = "core"
    data_class: str = "master_data"
    business_importance: str = "medium"
    context_name: str = "PilotContext"
    context_title: str = "Pilot domain context"
    context_description: str = (
        "Auto-generated domain context for ingested logical entities"
    )


class ConformsTo(BaseModel):
    specification_id: str = "moex-dams"
    specification_version: str = "0.1"
    specification_revision: str = "0.1.0"


class IngestProfile(BaseModel):
    name: str = "er-dictionary"
    solution_ref: str
    solution_slug: str
    id_prefix: str = "dams"
    package_name: str
    package_title: str
    package_description: str
    model_version: str = "0.1.0"
    api_version: str = "dams.moex/v0.1"
    conforms_to: ConformsTo = Field(default_factory=ConformsTo)
    sheets: SheetsConfig
    defaults: IngestDefaults = Field(default_factory=IngestDefaults)
    type_map: dict[str, str] = Field(default_factory=dict)

    @field_validator("type_map", mode="before")
    @classmethod
    def _normalize_type_map(cls, value: Any) -> dict[str, str]:
        if not value:
            return {}
        return {str(k).strip().upper(): str(v).strip() for k, v in dict(value).items()}

    def map_type(self, raw: str | None, *, is_pk: bool = False) -> str:
        if is_pk:
            return "identifier"
        if not raw or not str(raw).strip():
            return "string"
        key = str(raw).strip().upper()
        return self.type_map.get(key, "string")


def load_profile(path: Path | str) -> IngestProfile:
    path = Path(path)
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Ingest profile must be a mapping: {path}")
    return IngestProfile.model_validate(data)
