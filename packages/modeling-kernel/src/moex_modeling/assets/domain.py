"""Domain types for implementation asset discovery (Workbench catalog)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ImplementationAsset:
    """Resolved on-disk SpecificationImplementation package."""

    id: str
    slug: str
    title: str
    version: str
    implementation_kind: str
    implementation_profile: str | None
    dams_model_level: str | None
    envelope_path: Path
    body_path: Path
    specification_envelope_path: Path | None
    publication_manifest_path: Path | None


@dataclass(frozen=True, slots=True)
class PublicationTarget:
    """Git commit path for an implementation body (relative to repo root)."""

    repo_path: str
    manifest_path: Path | None


class ImplementationNotFound(LookupError):
    """No asset matches the given coordinate or presentation slug."""


class AssetResolutionError(RuntimeError):
    """Body/schema path missing, invalid, or escapes the repository root."""


def slug_and_version_from_id(implementation_id: str) -> tuple[str, str]:
    """
    Derive presentation slug and version from a canonical coordinate.

    Expected shape: ``moex:implementation:{slug}:{version}``.
    """
    prefix = "moex:implementation:"
    if not implementation_id.startswith(prefix):
        raise ValueError(
            f"implementation id must start with {prefix!r}: {implementation_id}"
        )
    rest = implementation_id[len(prefix) :]
    slug, sep, version = rest.rpartition(":")
    if not sep or not slug or not version:
        raise ValueError(
            f"implementation id must be moex:implementation:{{slug}}:{{version}}: "
            f"{implementation_id}"
        )
    return slug, version


__all__ = [
    "AssetResolutionError",
    "ImplementationAsset",
    "ImplementationNotFound",
    "PublicationTarget",
    "slug_and_version_from_id",
]
