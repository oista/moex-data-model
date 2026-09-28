"""External sources package — SpecificationSource port (ADR-017)."""

from moex_modeling.external_sources.public import (
    LocalArtifact,
    LockEntry,
    MaterializationPolicy,
    RawArtifactBundle,
    SourceKind,
    SourceVersionRef,
    SpecDiff,
    SpecDiffChange,
    SpecificationSource,
)

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
