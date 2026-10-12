"""RepositoryLoader: manifest index + lazy document load + assemble."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from moex_repository_loader.canonical import document_content_hash
from moex_repository_loader.fs import FilesystemDocumentStore
from moex_repository_loader.lock import LockError, read_lock
from moex_repository_loader.models import DocumentRef, LoadedDocument, RepositoryManifest
from moex_repository_loader.ports import DocumentStore

IMPLEMENTATIONS_REL = Path("model-assets") / "implementations"
MANIFEST_NAME = "manifest.yaml"
LOCK_NAME = "manifest.lock"

_SKIP_DESCRIPTOR = frozenset({"content_digest", "revision"})


class HashMismatchError(RuntimeError):
    """Document content_hash does not match manifest.lock."""


class RepositoryLoader:
    def __init__(
        self,
        repo_root: Path,
        *,
        store: DocumentStore | None = None,
        verify_hashes: bool = True,
    ) -> None:
        self._repo_root = repo_root.resolve()
        self._impl_root = self._repo_root / IMPLEMENTATIONS_REL
        self._store = store or FilesystemDocumentStore(self._impl_root)
        self._verify_hashes = verify_hashes
        self._manifest: RepositoryManifest | None = None
        self._lock_hashes: dict[str, str] | None = None
        self._cache: dict[str, LoadedDocument] = {}

    @property
    def repo_root(self) -> Path:
        return self._repo_root

    @property
    def implementations_root(self) -> Path:
        return self._impl_root

    def manifest_path(self) -> Path:
        return self._impl_root / MANIFEST_NAME

    def lock_path(self) -> Path:
        return self._impl_root / LOCK_NAME

    def load_manifest(self) -> RepositoryManifest:
        if self._manifest is not None:
            return self._manifest
        raw = yaml.safe_load(self._store.read_text(MANIFEST_NAME))
        if not isinstance(raw, dict):
            raise ValueError("manifest.yaml must be a mapping")
        docs = []
        for item in raw.get("documents") or []:
            if not isinstance(item, dict):
                raise ValueError("documents entries must be mappings")
            deps = item.get("depends_on") or []
            docs.append(
                DocumentRef(
                    id=str(item["id"]),
                    kind=item["kind"],
                    path=str(item["path"]).replace("\\", "/"),
                    version=str(item["version"]),
                    owner=str(item["owner"]),
                    depends_on=tuple(str(d) for d in deps),
                )
            )
        # Deterministic order by id (code point), independent of YAML order.
        docs_sorted = tuple(sorted(docs, key=lambda d: d.id))
        self._manifest = RepositoryManifest(
            manifest_schema_version=str(raw["manifest_schema_version"]),
            repository_id=str(raw["repository_id"]),
            documents=docs_sorted,
        )
        return self._manifest

    def _ensure_lock(self) -> dict[str, str]:
        if self._lock_hashes is not None:
            return self._lock_hashes
        _header, entries = read_lock(self.lock_path())
        self._lock_hashes = {e.id: e.content_hash for e in entries.values()}
        return self._lock_hashes

    def resolve(self, document_id: str) -> DocumentRef:
        manifest = self.load_manifest()
        for ref in manifest.documents:
            if ref.id == document_id:
                return ref
        raise KeyError(f"unknown document id: {document_id}")

    def document_ids(self) -> tuple[str, ...]:
        return tuple(ref.id for ref in self.load_manifest().documents)

    def compute_hash(self, ref: DocumentRef) -> str:
        descriptor, body = self._read_pair(ref)
        return document_content_hash(descriptor, body)

    def compute_all_hashes(self) -> dict[str, str]:
        return {ref.id: self.compute_hash(ref) for ref in self.load_manifest().documents}

    def load_package(self, document_id: str) -> LoadedDocument:
        if document_id in self._cache:
            return self._cache[document_id]
        ref = self.resolve(document_id)
        descriptor, body = self._read_pair(ref)
        digest = document_content_hash(descriptor, body)
        if self._verify_hashes:
            try:
                expected = self._ensure_lock().get(document_id)
            except LockError:
                raise
            if expected is None:
                raise HashMismatchError(f"no lock entry for {document_id}")
            if expected != digest:
                raise HashMismatchError(
                    f"hash mismatch for {document_id}: "
                    f"lock={expected} actual={digest}"
                )
        loaded = LoadedDocument(
            ref=ref,
            descriptor=descriptor,
            body=body,
            content_hash=digest,
        )
        self._cache[document_id] = loaded
        return loaded

    def assemble(self) -> dict[str, Any]:
        """In-memory MOEXModelRepository-shaped mapping (packages only today)."""
        manifest = self.load_manifest()
        packages: list[dict[str, Any]] = []
        for ref in manifest.documents:
            if ref.kind != "package":
                continue
            packages.append(self.load_package(ref.id).body)
        return {
            "repository_id": manifest.repository_id,
            "model_packages": packages,
        }

    def _read_pair(self, ref: DocumentRef) -> tuple[dict[str, Any], dict[str, Any]]:
        env_text = self._store.read_text(ref.path)
        descriptor = yaml.safe_load(env_text)
        if not isinstance(descriptor, dict):
            raise ValueError(f"{ref.path}: expected mapping")
        body_name = descriptor.get("body_ref") or descriptor.get("implementation_body")
        if not body_name:
            raise ValueError(f"{ref.path}: missing body_ref")
        body_rel = (Path(ref.path).parent / str(body_name)).as_posix()
        body_raw = yaml.safe_load(self._store.read_text(body_rel))
        if not isinstance(body_raw, dict):
            raise ValueError(f"{body_rel}: expected mapping")
        return descriptor, body_raw
