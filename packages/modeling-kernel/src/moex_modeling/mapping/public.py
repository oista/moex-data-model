"""MappingProvider port — transformations behind an interface (ADR-008)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

from moex_modeling.conformance.domain import Diagnostic
from moex_modeling.shared.enums import TransformationKind


class TransformSpecMeta(BaseModel):
    """Metadata required on every transformation specification."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    spec_id: str
    source_schema_revision: str
    target_schema_revision: str
    transformation_kind: TransformationKind = TransformationKind.PARTIAL
    description: str | None = None
    allow_unrestricted_eval: bool = False


class MappingPreview(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    spec: TransformSpecMeta
    preserved_semantics: tuple[str, ...] = ()
    lost_semantics: tuple[str, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = ()
    preview_payload: dict[str, Any] = Field(default_factory=dict)


class MappingResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    spec: TransformSpecMeta
    output: dict[str, Any] = Field(default_factory=dict)
    preserved_semantics: tuple[str, ...] = ()
    lost_semantics: tuple[str, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = ()
    round_trip_ok: bool | None = None


@runtime_checkable
class MappingProvider(Protocol):
    """
    Application depends on this port, not on linkml-map directly.

    Implementations wrap ObjectTransformer (or a stub) with expression allowlisting.
    """

    def load_spec_meta(self, spec_path: Path) -> TransformSpecMeta: ...

    def validate_spec(self, spec_path: Path) -> list[Diagnostic]: ...

    def preview(self, spec_path: Path, sample_path: Path) -> MappingPreview: ...

    def transform_sample(self, spec_path: Path, sample_path: Path) -> MappingResult: ...


__all__ = [
    "MappingPreview",
    "MappingProvider",
    "MappingResult",
    "TransformSpecMeta",
]
