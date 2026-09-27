"""Typed LinkML bodies: specification = schema view; implementation = instance."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr


class LinkMLSpecificationBody(BaseModel):
    """Normative LinkML schema body (TSpecBody). Wraps SchemaView path + metadata."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
        arbitrary_types_allowed=True,
    )

    schema_path: str
    schema_id: str | None = None
    schema_name: str | None = None
    root_class: str | None = None
    class_names: tuple[str, ...] = ()
    slot_names: tuple[str, ...] = ()
    enum_names: tuple[str, ...] = ()

    _schema_view: Any = PrivateAttr(default=None)

    def bind_schema_view(self, schema_view: Any) -> None:
        """Attach runtime SchemaView (not part of frozen equality)."""
        object.__setattr__(self, "_schema_view", schema_view)

    @property
    def schema_view(self) -> Any:
        return self._schema_view

    @property
    def path(self) -> Path:
        return Path(self.schema_path)


class LinkMLImplementationBody(BaseModel):
    """Instance body (TImplBody) — typically a DAMS ModelPackage dict."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    source_path: str
    target_class: str = "ModelPackage"
    data: dict[str, Any] = Field(default_factory=dict)

    @property
    def path(self) -> Path:
        return Path(self.source_path)

    @property
    def element_id(self) -> str | None:
        return self.data.get("element_id") or self.data.get("id")

    @property
    def name(self) -> str | None:
        return self.data.get("name")
