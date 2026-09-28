"""External specification source sync — port and DTOs (ADR-017)."""

from __future__ import annotations

from enum import Enum
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field


class SourceKind(str, Enum):
    ONTOLOGY = "ontology"
    API_SPEC = "api_spec"
    SCHEMA = "schema"
    DATA_CONTRACT_STANDARD = "data_contract_standard"


class SourceVersionRef(BaseModel):
    """Immutable pointer to an upstream release, tag, or commit."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    source_id: str
    upstream_ref: str
    resolved_uri: str | None = None
    label: str | None = None


class RawArtifactBundle(BaseModel):
    """Fetched upstream bytes/paths before kind-specific materialize."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    source_id: str
    version: SourceVersionRef
    root_path: str
    artifact_paths: tuple[str, ...] = ()
    content_digest: str | None = None


class LocalArtifact(BaseModel):
    """Materialized, git-friendly local artifact under external-sources/."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    source_id: str
    kind: SourceKind
    path: str
    content_digest: str
    version: SourceVersionRef
    extraction_method: str | None = None
    seed_digest: str | None = None


class SpecDiffChange(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    path: str
    change_kind: str
    summary: str | None = None


class SpecDiff(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    source_id: str
    old_digest: str | None = None
    new_digest: str | None = None
    breaking: bool = False
    changes: tuple[SpecDiffChange, ...] = ()


class LockEntry(BaseModel):
    """Pinned sync record — poetry.lock analogue for external specs."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    source_id: str
    kind: SourceKind
    upstream_ref: str
    content_hash: str
    synced_at: str | None = None
    extraction_method: str | None = None
    seed_hash: str | None = None
    tool_versions: dict[str, str] = Field(default_factory=dict)
    artifact_path: str | None = None


class MaterializationPolicy(BaseModel):
    """How to place materialized artifacts on disk."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    out_dir: str
    seed_path: str | None = None
    extraction_method: str | None = None
    run_reason: bool = False
    dry_run: bool = False
    extra: dict[str, str] = Field(default_factory=dict)


@runtime_checkable
class SpecificationSource(Protocol):
    """
    Application depends on this port for external spec sync (ADR-017).

    fetch looks the same for all kinds; materialize is kind-specific.
    """

    @property
    def source_id(self) -> str: ...

    @property
    def kind(self) -> SourceKind: ...

    def resolve_latest(self) -> SourceVersionRef: ...

    def fetch(self, version_ref: SourceVersionRef) -> RawArtifactBundle: ...

    def materialize(
        self,
        bundle: RawArtifactBundle,
        policy: MaterializationPolicy,
    ) -> LocalArtifact: ...

    def diff(self, old: LocalArtifact, new: LocalArtifact) -> SpecDiff: ...

    def lock(self, artifact: LocalArtifact) -> LockEntry: ...


__all__ = [
    "LocalArtifact",
    "LockEntry",
    "MaterializationPolicy",
    "RawArtifactBundle",
    "SourceKind",
    "SourceVersionRef",
    "SpecDiff",
    "SpecDiffChange",
    "SpecificationSource",
]
