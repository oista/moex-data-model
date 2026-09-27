"""Architecture catalog models for specification → implementation navigation."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


CatalogRole = Literal["reference_specification", "specification_implementation"]


class CatalogNode(BaseModel):
    id: str
    role: CatalogRole
    title: str
    version: str | None = None
    expressed_in: str | None = None
    conforms_to: str | None = None
    module_id: str | None = None
    order: int = 1000
    description: str | None = None

    @field_validator("version", mode="before")
    @classmethod
    def coerce_version(cls, value: Any) -> str | None:
        if value is None:
            return None
        return str(value)


class ArchitectureCatalog(BaseModel):
    kind: Literal["architecture_catalog"] = "architecture_catalog"
    version: str = "1"
    nodes: list[CatalogNode] = Field(default_factory=list)

    @field_validator("version", mode="before")
    @classmethod
    def coerce_version(cls, value: Any) -> str:
        return str(value)
