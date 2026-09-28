"""Publication read models (compatible with root viewer Publication*)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PublicationItem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    id: str
    title: str | None = None
    description: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    children: tuple[PublicationItem, ...] = ()
    tags: tuple[str, ...] = ()
    source_ref: str | None = None


class PublicationSection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    id: str
    title: str
    description: str | None = None
    type: str
    role: str | None = None
    columns: tuple[str, ...] = ()
    filterable: tuple[str, ...] = ()
    items: tuple[PublicationItem, ...] = ()
    content: str | None = None
    tags: tuple[str, ...] = ()
    default_collapsed: bool = False


class PublicationModule(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    module_id: str
    title: str
    description: str | None = None
    icon: str | None = None
    version: str | None = None
    order: int = 1000
    modeling_standard: str | None = None
    sections: tuple[PublicationSection, ...] = ()
    manifest_path: str | None = None


PublicationItem.model_rebuild()
