"""Normalized publication model consumed by the HTML renderer."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

# Explorer nav node kinds (stored in PublicationItem.attributes["kind"]).
# Breadcrumb trail uses these via moex_publication_viewer.nav_crumb.
ExplorerItemKind = Literal[
    "group",
    "class",
    "enum",
    "enum_value",
    "slot",
    "source_file",
    "requirement",
    "section_ref",
    "implementation_ref",
    "hierarchy_entity",
    "entity",
    "relation-term",
    "owl-class",
    "doc_page",
]


class PublicationItem(BaseModel):
    id: str
    title: str | None = None
    description: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    children: list[PublicationItem] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    source_ref: str | None = None
    # field name -> EditTarget dict (description / title / aliases)
    edit_targets: dict[str, dict[str, str]] | None = None


class PublicationSection(BaseModel):
    id: str
    title: str
    description: str | None = None
    type: str
    kind: str | None = None
    renderer_mode: str | None = None
    satisfies: list[str] = Field(default_factory=list)
    columns: list[str] = Field(default_factory=list)
    filterable: list[str] = Field(default_factory=list)
    groupby: str | None = None
    sort_by: str | None = None
    sort_order: str = "asc"
    items: list[PublicationItem] = Field(default_factory=list)
    content: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    default_collapsed: bool = False
    instance_of: str | None = None


class PublicationModule(BaseModel):
    module_id: str
    title: str
    description: str | None = None
    icon: str | None = None
    version: str | None = None
    order: int = 1000
    profile: str | None = None
    implements: list[dict[str, Any]] = Field(default_factory=list)
    conformance_status: str | None = None
    implementation_profile: str | None = None
    dams_model_level: str | None = None
    sections: list[PublicationSection] = Field(default_factory=list)
    manifest_path: str | None = None


PublicationItem.model_rebuild()
