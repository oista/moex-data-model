"""Catalog and path-safe resolve for model-assets/transformations (Stage 7 Workbench)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


TRANSFORMS_REL = Path("model-assets") / "transformations"


@dataclass(frozen=True)
class SpecCatalogEntry:
    rel_path: str
    spec_id: str
    source_schema_revision: str
    target_schema_revision: str
    transformation_kind: str
    description: str | None


@dataclass(frozen=True)
class SampleCatalogEntry:
    rel_path: str
    name: str


@dataclass(frozen=True)
class CatalogWarning:
    rel_path: str
    message: str


def transforms_root(repo_root: Path) -> Path:
    return (repo_root / TRANSFORMS_REL).resolve()


def list_specs(repo_root: Path) -> tuple[list[SpecCatalogEntry], list[CatalogWarning]]:
    root = transforms_root(repo_root)
    specs: list[SpecCatalogEntry] = []
    warnings: list[CatalogWarning] = []
    if not root.is_dir():
        return specs, warnings

    try:
        from moex_linkml_tooling.map_provider import LinkmlMapProvider
    except ImportError:
        warnings.append(
            CatalogWarning(
                rel_path="",
                message="moex-linkml-tooling[map] is required to load transform specs",
            )
        )
        return specs, warnings

    provider = LinkmlMapProvider()
    for path in sorted(root.glob("*.yaml")):
        if not path.is_file():
            continue
        rel = path.name
        try:
            meta = provider.load_spec_meta(path)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            warnings.append(CatalogWarning(rel_path=rel, message=str(exc)))
            continue
        specs.append(
            SpecCatalogEntry(
                rel_path=rel,
                spec_id=meta.spec_id,
                source_schema_revision=meta.source_schema_revision,
                target_schema_revision=meta.target_schema_revision,
                transformation_kind=meta.transformation_kind.value
                if hasattr(meta.transformation_kind, "value")
                else str(meta.transformation_kind),
                description=meta.description,
            )
        )
    return specs, warnings


def list_samples(repo_root: Path) -> list[SampleCatalogEntry]:
    samples_dir = transforms_root(repo_root) / "samples"
    out: list[SampleCatalogEntry] = []
    if not samples_dir.is_dir():
        return out
    for path in sorted(samples_dir.iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".json", ".yaml", ".yml"}:
            continue
        out.append(
            SampleCatalogEntry(
                rel_path=f"samples/{path.name}",
                name=path.name,
            )
        )
    return out


def resolve_under_transforms(repo_root: Path, rel: str) -> Path:
    """
    Resolve a relative path under transformations/.

    Rejects absolute paths, empty, and any escape via .. or symlink outside root.
    """
    if not rel or rel.startswith("/") or rel.startswith("\\"):
        raise ValueError(f"invalid transform path: {rel!r}")
    raw = Path(rel)
    if raw.is_absolute() or ".." in raw.parts:
        raise ValueError(f"path escape rejected: {rel!r}")
    # Disallow nested dirs other than samples/ for samples; specs are top-level only
    # but resolve_under_transforms is shared — caller validates role.
    root = transforms_root(repo_root)
    candidate = (root / raw).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"path escape rejected: {rel!r}") from exc
    return candidate


def resolve_spec_path(repo_root: Path, rel: str) -> Path:
    path = resolve_under_transforms(repo_root, rel)
    # Specs must be top-level yaml in transformations/
    if path.parent != transforms_root(repo_root):
        raise ValueError(f"spec must be top-level under transformations/: {rel!r}")
    if path.suffix.lower() not in {".yaml", ".yml"}:
        raise ValueError(f"spec must be a YAML file: {rel!r}")
    if not path.is_file():
        raise FileNotFoundError(f"transform spec not found: {rel}")
    return path


def resolve_sample_path(repo_root: Path, rel: str) -> Path:
    path = resolve_under_transforms(repo_root, rel)
    samples_dir = transforms_root(repo_root) / "samples"
    try:
        path.relative_to(samples_dir.resolve())
    except ValueError as exc:
        raise ValueError(f"sample must be under transformations/samples/: {rel!r}") from exc
    if not path.is_file():
        raise FileNotFoundError(f"sample not found: {rel}")
    return path


__all__ = [
    "CatalogWarning",
    "SampleCatalogEntry",
    "SpecCatalogEntry",
    "TRANSFORMS_REL",
    "list_samples",
    "list_specs",
    "resolve_sample_path",
    "resolve_spec_path",
    "transforms_root",
]
