"""Pydantic models for publish.yaml manifests."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


SectionType = Literal[
    "entity-table",
    "enum-table",
    "glossary",
    "tree",
    "markdown-doc",
    "key-value",
]

SourceFormat = Literal["yaml", "json", "csv", "markdown", "linkml-yaml"]


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
    columns: list[str] = Field(default_factory=list)
    filterable: list[str] = Field(default_factory=list)
    groupby: str | None = None
    sort: SortSpec | None = None
    key_column: str | None = None
    default_collapsed: bool = False
    tags: list[str] = Field(default_factory=list)


class PublicationManifest(BaseModel):
    module_id: str
    kind: Literal["publication_module"] = "publication_module"
    version: str = "1"
    order: int = 1000
    icon: str | None = None
    title: str
    description: str | None = None
    sections: list[ManifestSection] = Field(default_factory=list)

    @field_validator("version", mode="before")
    @classmethod
    def coerce_version(cls, value: Any) -> str:
        return str(value)
