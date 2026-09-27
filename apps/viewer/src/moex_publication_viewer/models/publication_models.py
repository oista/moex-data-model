"""Normalized publication model consumed by the HTML renderer."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PublicationItem(BaseModel):
    id: str
    title: str | None = None
    description: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    children: list[PublicationItem] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    source_ref: str | None = None


class PublicationSection(BaseModel):
    id: str
    title: str
    description: str | None = None
    type: str
    columns: list[str] = Field(default_factory=list)
    filterable: list[str] = Field(default_factory=list)
    groupby: str | None = None
    sort_by: str | None = None
    sort_order: str = "asc"
    items: list[PublicationItem] = Field(default_factory=list)
    content: str | None = None  # markdown / html body for markdown-doc
    tags: list[str] = Field(default_factory=list)
    default_collapsed: bool = False


class PublicationModule(BaseModel):
    module_id: str
    title: str
    description: str | None = None
    icon: str | None = None
    version: str | None = None
    order: int = 1000
    sections: list[PublicationSection] = Field(default_factory=list)
    manifest_path: str | None = None


PublicationItem.model_rebuild()
