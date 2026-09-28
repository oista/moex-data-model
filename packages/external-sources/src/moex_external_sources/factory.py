"""Adapter factory and sync orchestration."""

from __future__ import annotations

from pathlib import Path

from moex_external_sources.fibo_adapter import FiboOntologySource
from moex_external_sources.git_adapter import GitArtifactSource
from moex_external_sources.registry import (
    SourceLockfile,
    SourceRegistry,
    load_lockfile,
    load_registry,
    write_lockfile,
)
from moex_modeling.external_sources.public import (
    LocalArtifact,
    LockEntry,
    MaterializationPolicy,
    SpecDiff,
    SpecificationSource,
)


def build_source(
    source_dir: Path,
    *,
    mirror_root: Path | None = None,
    work_dir: Path | None = None,
    robot_jar: Path | None = None,
    robot_cache: Path | None = None,
) -> tuple[SourceRegistry, SpecificationSource]:
    registry = load_registry(source_dir / "registry.yaml")
    adapter = registry.adapter
    if adapter in {"fibo", "ontology", "robot"}:
        source: SpecificationSource = FiboOntologySource(
            registry,
            source_root=source_dir,
            mirror_root=mirror_root,
            robot_jar=robot_jar,
            robot_cache=robot_cache,
        )
    elif adapter in {"git", "git_artifact", "openapi", "asyncapi", "odcm"}:
        source = GitArtifactSource(
            registry,
            source_root=source_dir,
            work_dir=work_dir,
        )
    else:
        raise ValueError(f"unknown adapter {adapter!r} for source {registry.source_id}")
    return registry, source


def sync_source(
    source_dir: Path,
    *,
    seed: Path | None = None,
    dry_run: bool = False,
    write_lock: bool = True,
    mirror_root: Path | None = None,
    work_dir: Path | None = None,
    robot_jar: Path | None = None,
    robot_cache: Path | None = None,
) -> tuple[LocalArtifact, LockEntry, SpecDiff | None]:
    """
    resolve_latest → fetch → materialize → lock; optional diff vs previous lock.
    """
    registry, source = build_source(
        source_dir,
        mirror_root=mirror_root,
        work_dir=work_dir,
        robot_jar=robot_jar,
        robot_cache=robot_cache,
    )
    version = source.resolve_latest()
    bundle = source.fetch(version)

    if registry.kind.value == "ontology":
        out_dir = "modules"
        seed_path = str(seed) if seed else registry.default_seed
    else:
        out_dir = "spec"
        seed_path = None

    policy = MaterializationPolicy(
        out_dir=out_dir,
        seed_path=seed_path,
        extraction_method=registry.extraction_method,
        dry_run=dry_run,
    )
    artifact = source.materialize(bundle, policy)
    entry = source.lock(artifact)

    previous: SpecDiff | None = None
    lock_path = source_dir / "lockfile.yaml"
    if lock_path.is_file():
        old = load_lockfile(lock_path)
        old_artifact = LocalArtifact(
            source_id=old.lock.source_id,
            kind=old.lock.kind,
            path=old.lock.artifact_path or "",
            content_digest=old.lock.content_hash,
            version=version.model_copy(
                update={"upstream_ref": old.lock.upstream_ref}
            ),
            extraction_method=old.lock.extraction_method,
            seed_digest=old.lock.seed_hash,
        )
        previous = source.diff(old_artifact, artifact)

    if write_lock and not dry_run:
        write_lockfile(lock_path, SourceLockfile(lock=entry))

    return artifact, entry, previous
