"""Pydantic models for publish.yaml manifests."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


SectionType = Literal[
    "entity-table",
    "enum-table",
    "glossary",
    "tree",
    "markdown-doc",
    "key-value",
    "explorer",
]

SourceFormat = Literal["yaml", "json", "csv", "markdown", "linkml-yaml"]

PublicationProfileId = Literal[
    "linkml-specification",
    "ontology",
    "implementation",
]

PublicationSectionKind = Literal[
    "overview",
    "classes",
    "slots",
    "enumerations",
    "schema-files",
    "taxonomy",
    "glossary",
    "identity",
    "bindings",
    "data-flows",
    "conformance",
    "model-assessment",
    "source",
    "external-specification-scope",
    "competency-questions",
    "term-selection",
    "mapping-table",
    "dependency-list",
    "extraction-provenance",
]


class SourceSpec(BaseModel):
    format: SourceFormat
    path: str
    select: str | None = None


class SortSpec(BaseModel):
    by: str
    order: Literal["asc", "desc"] = "asc"


class ManifestSection(BaseModel):
    id: str
    title: str
    description: str | None = None
    type: SectionType
    source: SourceSpec
    kind: PublicationSectionKind | None = None
    satisfies: list[str] = Field(default_factory=list)
    columns: list[str] = Field(default_factory=list)
    filterable: list[str] = Field(default_factory=list)
    groupby: str | None = None
    sort: SortSpec | None = None
    key_column: str | None = None
    default_collapsed: bool = False
    tags: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def legacy_role_to_kind(cls, data: Any) -> Any:
        """Accept legacy ``role`` as alias for ``kind`` (pre-ADR-016 drafts)."""
        if isinstance(data, dict) and data.get("kind") is None and data.get("role"):
            data = {**data, "kind": data["role"]}
        return data


class ImplementsRef(BaseModel):
    """Reference Spec / conformance profile this module claims (ADR-019)."""

    specification_ref: str
    profile_ref: str | None = None
    conformance_target: str | None = None


class PublicationManifest(BaseModel):
    module_id: str
    kind: Literal["publication_module"] = "publication_module"
    version: str = "1"
    order: int = 1000
    icon: str | None = None
    title: str
    description: str | None = None
    profile: PublicationProfileId | None = None
    implements: list[ImplementsRef] = Field(default_factory=list)
    conformance_status: str | None = None
    semantic_assertion_status: str | None = None
    approval_status: str | None = None
    implementation_profile: str | None = None
    dams_model_level: str | None = None
    sections: list[ManifestSection] = Field(default_factory=list)

    @field_validator("version", mode="before")
    @classmethod
    def coerce_version(cls, value: Any) -> str:
        return str(value)

    @model_validator(mode="before")
    @classmethod
    def legacy_modeling_standard(cls, data: Any) -> Any:
        """Map draft modeling_standard → profile when profile absent."""
        if not isinstance(data, dict) or data.get("profile"):
            return data
        ms = data.get("modeling_standard")
        if ms == "linkml":
            data = {**data, "profile": "linkml-specification"}
        elif ms == "owl":
            data = {**data, "profile": "ontology"}
        return data
