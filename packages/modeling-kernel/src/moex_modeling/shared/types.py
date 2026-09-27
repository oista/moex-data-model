"""Small immutable value objects."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class _Frozen(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )


class AnnotationPair(_Frozen):
    annotation_key: str
    annotation_value: str | None = None


class DiagnosticDetail(_Frozen):
    detail_key: str
    detail_value: str | None = None


class SourceLocation(_Frozen):
    source_uri: str | None = None
    line: int | None = None
    column: int | None = None
    json_pointer: str | None = None


class StandardRef(_Frozen):
    standard_id: str
    version_constraint: str
    standard_revision: str | None = None
    dialect_uri: str | None = None


class SpecificationRef(_Frozen):
    specification_id: str
    specification_version: str
    specification_revision: str


class ImplementationRef(_Frozen):
    implementation_id: str
    implementation_revision: str


class SourceDescriptor(_Frozen):
    source_uri: str
    media_type: str | None = None
    source_root_type: str | None = None
    authoritative: bool = True


class ProvenanceRecord(_Frozen):
    generated_from: str | None = None
    created_by: str | None = None
    created_at: str | None = None
    generator_id: str | None = None
    generator_version: str | None = None
    configuration_digest: str | None = None
