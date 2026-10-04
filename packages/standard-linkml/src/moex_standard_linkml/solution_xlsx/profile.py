"""Pydantic profile for Object/ObjectAttribute → DAMS solution import."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, field_validator


class SheetColumns(BaseModel):
    """Logical column keys → header names in the workbook."""

    model_config = {"extra": "forbid"}

    # Object sheet
    src_system: str = "SrcSystem"
    object_code: str = "ObjectCode"
    object_name: str = "ObjectName"
    src_object_code: str = "SrcObjectCode"
    src_object_name: str = "SrcObjectName"
    src_description: str = "SrcDescription"

    # ObjectAttribute sheet
    sort_order: str = "SortOrder"
    attribute_code: str = "AttributeCode"
    attribute_description: str = "AttributeDescription"
    data_type: str = "DataType"
    mandatory: str = "Mandatory"
    pk: str = "PK"
    ak: str = "AK"
    fk: str = "FK"
    src_attribute_code: str = "SrcAttributeCode"
    src_attribute_description: str = "SrcAttributeDescription"
    src_data_type: str = "SrcDataType"
    comments: str = "Comments"
    base_src_scode: str = "BaseSrcSCode"
    base_src_sname: str = "BaseSrcSName"
    base_src_object_code: str = "BaseSrcObjectCode"


class SheetSpec(BaseModel):
    sheet: str
    required: bool = True
    # When set, header row is found by matching these names (case-sensitive strip).
    # When None, use first non-empty row as header.
    required_headers: list[str] = Field(default_factory=list)


class SheetsConfig(BaseModel):
    objects: SheetSpec = Field(
        default_factory=lambda: SheetSpec(
            sheet="Object",
            required=True,
            required_headers=["SrcSystem", "ObjectCode", "ObjectName"],
        )
    )
    object_attributes: SheetSpec = Field(
        default_factory=lambda: SheetSpec(
            sheet="ObjectAttribute",
            required=True,
            required_headers=[
                "ObjectCode",
                "AttributeCode",
                "SrcSystem",
                "SrcAttributeCode",
            ],
        )
    )


class SystemDefaults(BaseModel):
    """Per-SrcSystem settings used when building ModelPackage / physical layer."""

    src_system: str
    slug: str
    solution_ref: str
    system_ref: str
    package_name: str
    package_title: str
    package_description: str
    model_version: str = "0.1.0"
    object_kind: str = "table"
    technology: str = "relational"
    direction: str = "internal"
    native_schema_ref_template: str = "urn:moex:{slug}:schema/{object}"
    type_map: dict[str, str] = Field(default_factory=dict)
    domain_ref: str = "eam:domain/PARTY"
    namespace: str | None = None
    context_name: str | None = None
    context_title: str | None = None
    context_description: str | None = None

    @field_validator("type_map", mode="before")
    @classmethod
    def _normalize_type_map(cls, value: Any) -> dict[str, str]:
        if not value:
            return {}
        return {str(k).strip().upper(): str(v).strip() for k, v in dict(value).items()}

    def resolved_namespace(self) -> str:
        if self.namespace:
            return self.namespace
        return f"https://data.moex.com/models/{self.slug}/"

    def resolved_context_name(self) -> str:
        return self.context_name or f"{self.slug.title()}Context"

    def resolved_context_title(self) -> str:
        return self.context_title or f"Контекст {self.src_system}"

    def resolved_context_description(self) -> str:
        return (
            self.context_description
            or f"Доменный контекст модели решения {self.src_system}"
        )

    def map_type(self, raw: str | None, *, is_pk: bool = False) -> str:
        if is_pk:
            return "identifier"
        if not raw or not str(raw).strip():
            return "string"
        key = str(raw).strip().upper()
        # Strip length specs: VARCHAR(500) → VARCHAR
        base = key.split("(", 1)[0].strip()
        return self.type_map.get(key) or self.type_map.get(base) or "string"

    def native_schema_ref(self, object_name: str) -> str:
        return self.native_schema_ref_template.format(
            slug=self.slug,
            object=object_name,
            system=self.src_system,
        )


class PackageDefaults(BaseModel):
    """Defaults for it-solution required slots not present in xlsx."""

    lifecycle_status: str = "draft"
    api_version: str = "dams.moex/v0.1"
    implementation_scope: str = "solution"
    solution_data_role: str = "producer"
    entity_type: str = "core"
    data_class: str = "master_data"
    business_importance: str = "medium"
    data_owner_ref: str = "org:role/DATA_OWNER_PENDING"
    ownership_inheritance_rule: str = (
        "Ответственность за данные наследуется от ИТ-решения "
        "при отсутствии локального override на сущности."
    )
    governance_classification: str = "internal"
    business_key_kind: str = "surrogate"
    identity_rule: str = (
        "Идентичность определяется первичным ключом сущности "
        "в контуре ИТ-решения (требует уточнения владельцем данных)."
    )
    conceptual_alignment_status: str = "pending"
    alignment_rationale: str = (
        "Локальный stub из импорта xlsx; выверка с enterprise conceptual — follow-up."
    )
    mapping_coverage_status_mapped: str = "mapped"
    mapping_coverage_status_planned: str = "planned"
    mapping_rationale_planned: str = (
        "Физическое соответствие не выведено из ObjectAttribute; "
        "заполните mapping вручную или повторите импорт после доработки источника."
    )


class ConformsTo(BaseModel):
    specification_id: str = "moex:specification:moex-dams:0.1"
    specification_version: str = "0.1.0"
    specification_revision: str = "0.1.0"


class SolutionXlsxProfile(BaseModel):
    name: str = "solution-xlsx"
    id_prefix: str = "dams"
    sheets: SheetsConfig = Field(default_factory=SheetsConfig)
    columns: SheetColumns = Field(default_factory=SheetColumns)
    systems: list[SystemDefaults]
    defaults: PackageDefaults = Field(default_factory=PackageDefaults)
    conforms_to: ConformsTo = Field(default_factory=ConformsTo)
    src_only: Literal["ignore", "physical"] = "ignore"
    severity_overrides: dict[str, str] = Field(default_factory=dict)
    ignored_sheets: list[str] = Field(
        default_factory=lambda: ["1", "2", "Блок api"]
    )
    specification_envelope: str = (
        "../../../specifications/moex-dams/0.1/specification.yaml"
    )
    conceptual_implementation_ref: str = (
        "moex:implementation:moex-enterprise-conceptual-model:0.1"
    )

    def system_for(self, src_system: str) -> SystemDefaults | None:
        key = src_system.strip().casefold()
        for sys in self.systems:
            if sys.src_system.strip().casefold() == key:
                return sys
        return None

    def known_systems(self) -> set[str]:
        return {s.src_system.strip().casefold() for s in self.systems}


def load_solution_profile(path: Path | str) -> SolutionXlsxProfile:
    path = Path(path)
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"SolutionXlsxProfile must be a mapping: {path}")
    return SolutionXlsxProfile.model_validate(data)


def system_to_ingest_profile(system: SystemDefaults, profile: SolutionXlsxProfile):
    """Build a minimal IngestProfile for map_er_dictionary."""
    from moex_standard_linkml.ingest.profile import (
        ConformsTo as IngestConformsTo,
        IngestDefaults,
        IngestProfile,
        SheetColumns as IngestSheetColumns,
        SheetSpec as IngestSheetSpec,
        SheetsConfig as IngestSheetsConfig,
    )

    defaults = profile.defaults
    return IngestProfile(
        name=f"solution-xlsx-{system.slug}",
        solution_ref=system.solution_ref,
        solution_slug=system.slug,
        id_prefix=profile.id_prefix,
        package_name=system.package_name,
        package_title=system.package_title,
        package_description=system.package_description,
        model_version=system.model_version,
        api_version=defaults.api_version,
        conforms_to=IngestConformsTo(
            specification_id="moex-dams",
            specification_version="0.1",
            specification_revision=profile.conforms_to.specification_revision,
        ),
        sheets=IngestSheetsConfig(
            entities=IngestSheetSpec(
                sheet="Entities",
                required=True,
                columns=IngestSheetColumns(
                    name="name",
                    title="title",
                    description="description",
                    conceptual_ref="conceptual_ref",
                ),
            ),
            attributes=IngestSheetSpec(
                sheet="Attributes",
                required=True,
                columns=IngestSheetColumns(
                    entity="entity",
                    name="name",
                    title="title",
                    description="description",
                    type="type",
                    required="required",
                    pk="pk",
                ),
            ),
            relationships=IngestSheetSpec(
                sheet="Relationships",
                required=False,
                columns=IngestSheetColumns(
                    name="name",
                    source="source",
                    target="target",
                    source_role="source_role",
                    target_role="target_role",
                    source_card="source_card",
                    target_card="target_card",
                    identifying="identifying",
                ),
            ),
            physical_objects=IngestSheetSpec(
                sheet="PhysicalObjects",
                required=False,
                columns=IngestSheetColumns(
                    name="name",
                    title="title",
                    description="description",
                    object_kind="object_kind",
                    qualified_name="qualified_name",
                    technology="technology",
                    system_ref="system_ref",
                    direction="direction",
                    native_schema_ref="native_schema_ref",
                ),
            ),
            physical_fields=IngestSheetSpec(
                sheet="PhysicalFields",
                required=False,
                columns=IngestSheetColumns(
                    object="object",
                    name="name",
                    description="description",
                    native_name="native_name",
                    native_type="native_type",
                    required="required",
                ),
            ),
            mappings=IngestSheetSpec(
                sheet="Mappings",
                required=False,
                columns=IngestSheetColumns(
                    name="name",
                    source="source",
                    target="target",
                    mapping_type="mapping_type",
                    mapping_cardinality="mapping_cardinality",
                ),
            ),
        ),
        defaults=IngestDefaults(
            lifecycle_status=defaults.lifecycle_status,
            solution_data_role=defaults.solution_data_role,
            domain_ref=system.domain_ref,
            namespace=system.resolved_namespace(),
            entity_type=defaults.entity_type,
            data_class=defaults.data_class,
            business_importance=defaults.business_importance,
            context_name=system.resolved_context_name(),
            context_title=system.resolved_context_title(),
            context_description=system.resolved_context_description(),
        ),
        type_map=dict(system.type_map),
    )
