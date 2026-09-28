"""Git / filesystem artifact SpecificationSource (OpenAPI, AsyncAPI, ODCM, …)."""

from __future__ import annotations

import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from moex_external_sources.hashing import sha256_file, sha256_paths
from moex_external_sources.registry import SourceRegistry
from moex_modeling.external_sources.public import (
    LocalArtifact,
    LockEntry,
    MaterializationPolicy,
    RawArtifactBundle,
    SourceKind,
    SourceVersionRef,
    SpecDiff,
    SpecDiffChange,
)

_GIT_KINDS = {
    SourceKind.API_SPEC,
    SourceKind.SCHEMA,
    SourceKind.DATA_CONTRACT_STANDARD,
}


class GitArtifactSource:
    """Pin a git ref (or local directory) and copy selected text artifacts."""

    def __init__(
        self,
        registry: SourceRegistry,
        *,
        source_root: Path,
        work_dir: Path | None = None,
    ) -> None:
        if registry.kind not in _GIT_KINDS:
            raise ValueError(
                f"GitArtifactSource requires api_spec/schema/data_contract_standard, "
                f"got {registry.kind}"
            )
        self._registry = registry
        self._source_root = Path(source_root)
        self._work_dir = Path(work_dir) if work_dir else None

    @property
    def source_id(self) -> str:
        return self._registry.source_id

    @property
    def kind(self) -> SourceKind:
        return self._registry.kind

    def resolve_latest(self) -> SourceVersionRef:
        ref = self._registry.default_ref or "HEAD"
        upstream = self._registry.upstream_url
        resolved = ref
        repo = self._repo_path()
        if repo is not None and (repo / ".git").exists():
            try:
                resolved = self._git(repo, "rev-parse", ref).stdout.strip()
            except subprocess.CalledProcessError:
                resolved = ref
        return SourceVersionRef(
            source_id=self.source_id,
            upstream_ref=ref,
            resolved_uri=upstream,
            label=resolved,
        )

    def fetch(self, version_ref: SourceVersionRef) -> RawArtifactBundle:
        repo = self._repo_path()
        if repo is None:
            raise FileNotFoundError(
                f"upstream_url is not a local git/dir path: {self._registry.upstream_url}"
            )

        dest = self._work_dir or (
            self._source_root / ".cache" / "fetch" / version_ref.upstream_ref.replace("/", "_")
        )
        if dest.exists():
            shutil.rmtree(dest)
        dest.mkdir(parents=True, exist_ok=True)

        pattern = self._registry.artifact_glob or "**/*"
        if (repo / ".git").exists():
            # Export files at ref via git archive or checkout into dest
            self._export_git_tree(repo, version_ref.upstream_ref, dest)
        else:
            shutil.copytree(repo, dest, dirs_exist_ok=True)

        files = [p for p in dest.glob(pattern) if p.is_file()]
        if not files and pattern != "**/*":
            files = [p for p in dest.rglob("*") if p.is_file()]
        digest = sha256_paths(files) if files else sha256_file(dest) if dest.is_file() else "sha256:"
        if digest == "sha256:":
            # empty tree
            digest = "sha256:" + ("0" * 64)

        return RawArtifactBundle(
            source_id=self.source_id,
            version=version_ref,
            root_path=str(dest),
            artifact_paths=tuple(
                p.relative_to(dest).as_posix() for p in sorted(files, key=lambda x: x.as_posix())
            ),
            content_digest=digest if files else "sha256:" + ("0" * 64),
        )

    def materialize(
        self,
        bundle: RawArtifactBundle,
        policy: MaterializationPolicy,
    ) -> LocalArtifact:
        out_dir = Path(policy.out_dir)
        if not out_dir.is_absolute():
            out_dir = self._source_root / out_dir
        out_dir.mkdir(parents=True, exist_ok=True)

        src_root = Path(bundle.root_path)
        copied: list[Path] = []
        for rel in bundle.artifact_paths:
            src = src_root / rel
            if not src.is_file():
                continue
            # Flatten into spec/ keeping basename for single-file; keep relative for trees
            dest = out_dir / Path(rel).name if len(bundle.artifact_paths) == 1 else out_dir / rel
            if policy.dry_run:
                copied.append(dest)
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            copied.append(dest)

        if policy.dry_run:
            digest = "sha256:dry-run"
        elif not copied:
            raise FileNotFoundError("no artifacts to materialize")
        else:
            digest = sha256_paths([p for p in copied if p.is_file()])

        primary = copied[0] if copied else out_dir
        rel = (
            primary.relative_to(self._source_root).as_posix()
            if primary.is_relative_to(self._source_root)
            else str(primary)
        )
        return LocalArtifact(
            source_id=self.source_id,
            kind=self.kind,
            path=rel,
            content_digest=digest,
            version=bundle.version,
        )

    def diff(self, old: LocalArtifact, new: LocalArtifact) -> SpecDiff:
        breaking = old.content_digest != new.content_digest
        changes: tuple[SpecDiffChange, ...] = ()
        if breaking:
            changes = (
                SpecDiffChange(
                    path=new.path,
                    change_kind="modified",
                    summary="artifact content digest changed",
                ),
            )
        return SpecDiff(
            source_id=self.source_id,
            old_digest=old.content_digest,
            new_digest=new.content_digest,
            breaking=breaking,
            changes=changes,
        )

    def lock(self, artifact: LocalArtifact) -> LockEntry:
        return LockEntry(
            source_id=artifact.source_id,
            kind=artifact.kind,
            upstream_ref=artifact.version.upstream_ref,
            content_hash=artifact.content_digest,
            synced_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            artifact_path=artifact.path,
            tool_versions={},
        )

    def _repo_path(self) -> Path | None:
        url = self._registry.upstream_url
        if url.startswith("file:"):
            return Path(url.removeprefix("file://").removeprefix("file:"))
        path = Path(url)
        if path.is_absolute() and path.exists():
            return path
        candidate = (self._source_root / url).resolve()
        if candidate.exists():
            return candidate
        if path.exists():
            return path.resolve()
        return None

    def _export_git_tree(self, repo: Path, ref: str, dest: Path) -> None:
        # Prefer git archive | tar extract when available
        proc = subprocess.run(
            ["git", "archive", "--format=tar", ref],
            cwd=repo,
            check=False,
            capture_output=True,
        )
        if proc.returncode != 0:
            # Fallback: copy working tree (ref ignored)
            shutil.copytree(repo, dest, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git"))
            return
        import io
        import tarfile

        with tarfile.open(fileobj=io.BytesIO(proc.stdout), mode="r:") as tar:
            tar.extractall(dest)

    def _git(self, repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
