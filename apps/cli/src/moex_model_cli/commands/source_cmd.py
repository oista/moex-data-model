"""moex-model source — list / sync / diff external specification sources (ADR-017)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from moex_model_cli.bootstrap import SlicePaths

DEFAULT_SOURCES_DIR = Path("model-assets") / "external-sources"


def _sources_root(paths: SlicePaths, sources_dir: Path | None) -> Path:
    if sources_dir is not None:
        return sources_dir if sources_dir.is_absolute() else paths.root / sources_dir
    return paths.root / DEFAULT_SOURCES_DIR


def run_source(
    paths: SlicePaths,
    *,
    action: str,
    source_id: str | None = None,
    seed: Path | None = None,
    dry_run: bool = False,
    as_json: bool = False,
    sources_dir: Path | None = None,
    from_ref: str | None = None,
    to_ref: str | None = None,
) -> tuple[int, str]:
    try:
        from moex_external_sources.factory import build_source, sync_source
        from moex_external_sources.registry import list_source_dirs, load_lockfile, load_registry
    except ImportError:
        return (
            2,
            "moex-model source requires moex-external-sources "
            "(pip install -e packages/external-sources)\n",
        )

    root = _sources_root(paths, sources_dir)

    if action == "list":
        dirs = list_source_dirs(root)
        rows: list[dict[str, Any]] = []
        for d in dirs:
            reg = load_registry(d / "registry.yaml")
            lock_path = d / "lockfile.yaml"
            pinned = None
            if lock_path.is_file():
                pinned = load_lockfile(lock_path).lock.upstream_ref
            rows.append(
                {
                    "source_id": reg.source_id,
                    "kind": reg.kind.value,
                    "adapter": reg.adapter,
                    "title": reg.title,
                    "pinned_ref": pinned,
                    "path": str(d.relative_to(paths.root))
                    if d.is_relative_to(paths.root)
                    else str(d),
                }
            )
        if as_json:
            return 0, json.dumps(rows, indent=2) + "\n"
        if not rows:
            return 0, f"(no sources under {root})\n"
        lines = [
            f"{r['source_id']}\t{r['kind']}\t{r['adapter']}\t"
            f"pin={r['pinned_ref'] or '-'}\t{r['path']}"
            for r in rows
        ]
        return 0, "\n".join(lines) + "\n"

    if action == "sync":
        if not source_id:
            return 2, "moex-model source sync requires <source_id>\n"
        source_dir = root / source_id
        if not (source_dir / "registry.yaml").is_file():
            return 2, f"unknown source {source_id!r} (no registry.yaml under {source_dir})\n"
        seed_path = seed
        if seed_path is not None and not seed_path.is_absolute():
            seed_path = (paths.root / seed_path).resolve()
        try:
            artifact, entry, diff = sync_source(
                source_dir,
                seed=seed_path,
                dry_run=dry_run,
                write_lock=not dry_run,
            )
        except Exception as exc:  # noqa: BLE001 — surface to CLI
            return 1, f"source sync failed: {exc}\n"

        payload = {
            "artifact": artifact.model_dump(mode="json"),
            "lock": entry.model_dump(mode="json"),
            "diff": diff.model_dump(mode="json") if diff else None,
            "dry_run": dry_run,
        }
        if as_json:
            return 0, json.dumps(payload, indent=2) + "\n"
        lines = [
            f"synced {entry.source_id}",
            f"  upstream_ref: {entry.upstream_ref}",
            f"  content_hash: {entry.content_hash}",
            f"  artifact:     {entry.artifact_path}",
        ]
        if diff is not None:
            lines.append(f"  diff:         breaking={diff.breaking} changes={len(diff.changes)}")
        if dry_run:
            lines.append("  (dry-run: lockfile not written)")
        return 0, "\n".join(lines) + "\n"

    if action == "diff":
        if not source_id:
            return 2, "moex-model source diff requires <source_id>\n"
        source_dir = root / source_id
        if not (source_dir / "registry.yaml").is_file():
            return 2, f"unknown source {source_id!r}\n"
        lock_path = source_dir / "lockfile.yaml"
        if not lock_path.is_file():
            return 1, f"no lockfile for {source_id}; run source sync first\n"

        # MVP: re-sync dry-run and compare digests; --from/--to reserved for git pins
        _ = from_ref, to_ref
        try:
            _registry, source = build_source(source_dir)
            old_lock = load_lockfile(lock_path).lock
            artifact, _entry, diff = sync_source(
                source_dir,
                seed=seed,
                dry_run=True,
                write_lock=False,
            )
        except Exception as exc:  # noqa: BLE001
            return 1, f"source diff failed: {exc}\n"

        if diff is None:
            # fabricate from old lock vs dry-run artifact
            from moex_modeling.external_sources.public import LocalArtifact

            version = source.resolve_latest()
            old_art = LocalArtifact(
                source_id=old_lock.source_id,
                kind=old_lock.kind,
                path=old_lock.artifact_path or "",
                content_digest=old_lock.content_hash,
                version=version.model_copy(update={"upstream_ref": old_lock.upstream_ref}),
                extraction_method=old_lock.extraction_method,
                seed_digest=old_lock.seed_hash,
            )
            diff = source.diff(old_art, artifact)

        if as_json:
            return (1 if diff.breaking else 0), json.dumps(
                diff.model_dump(mode="json"), indent=2
            ) + "\n"
        lines = [
            f"diff {diff.source_id}",
            f"  old: {diff.old_digest}",
            f"  new: {diff.new_digest}",
            f"  breaking: {diff.breaking}",
        ]
        for ch in diff.changes:
            lines.append(f"  - {ch.change_kind} {ch.path}: {ch.summary or ''}")
        return (1 if diff.breaking else 0), "\n".join(lines) + "\n"

    return 2, f"unknown source action {action!r}\n"
