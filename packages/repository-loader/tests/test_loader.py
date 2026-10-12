from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from moex_repository_loader.fs import FilesystemDocumentStore
from moex_repository_loader.loader import HashMismatchError, RepositoryLoader
from moex_repository_loader.lock import write_lock

REPO = Path(__file__).resolve().parents[3]


class CountingStore(FilesystemDocumentStore):
    def __init__(self, root: Path) -> None:
        super().__init__(root)
        self.reads: list[str] = []

    def read_text(self, relative_path: str) -> str:
        self.reads.append(relative_path.replace("\\", "/"))
        return super().read_text(relative_path)


def test_load_manifest_sorts_by_id() -> None:
    loader = RepositoryLoader(REPO, verify_hashes=False)
    ids = [d.id for d in loader.load_manifest().documents]
    assert ids == sorted(ids)
    assert len(ids) == 8


def test_shuffled_manifest_same_document_id_order() -> None:
    """YAML document order must not affect loader order (sorted by id)."""
    impl = REPO / "model-assets" / "implementations"
    raw = yaml.safe_load((impl / "manifest.yaml").read_text(encoding="utf-8"))
    forward = RepositoryLoader(REPO, verify_hashes=False).document_ids()

    class ReverseManifestStore(FilesystemDocumentStore):
        def read_text(self, relative_path: str) -> str:
            if relative_path.replace("\\", "/") == "manifest.yaml":
                shuffled = dict(raw)
                shuffled["documents"] = list(reversed(list(raw["documents"])))
                return yaml.dump(shuffled, allow_unicode=True, sort_keys=False)
            return super().read_text(relative_path)

    reverse = RepositoryLoader(
        REPO,
        store=ReverseManifestStore(impl),
        verify_hashes=False,
    ).document_ids()
    assert forward == reverse
    assert forward == tuple(sorted(forward))


def test_lazy_load_package_does_not_read_other_bodies() -> None:
    store = CountingStore(REPO / "model-assets" / "implementations")
    loader = RepositoryLoader(REPO, store=store, verify_hashes=False)
    loader.load_manifest()
    store.reads.clear()
    crm_id = "moex:implementation:crm:0.1.0"
    loader.load_package(crm_id)
    body_reads = [r for r in store.reads if r.endswith(".yaml") and "manifest" not in r]
    assert any("crm" in r for r in body_reads)
    assert not any("esed" in r for r in body_reads)
    assert not any("mdm" in r for r in body_reads)
    assert not any("ucd" in r for r in body_reads)


def test_hash_mismatch_raises(tmp_path: Path) -> None:
    # Use real repo but fake lock with wrong hash.
    lock_path = REPO / "model-assets" / "implementations" / "manifest.lock"
    if not lock_path.is_file():
        pytest.skip("manifest.lock not generated yet")
    loader = RepositoryLoader(REPO, verify_hashes=True)
    # Corrupt cache path: write temp lock elsewhere by monkeypatching lock_path
    bad = {doc_id: "sha256:" + ("0" * 64) for doc_id in loader.document_ids()}
    write_lock(tmp_path / "manifest.lock", bad)

    class BadLockLoader(RepositoryLoader):
        def lock_path(self) -> Path:  # type: ignore[override]
            return tmp_path / "manifest.lock"

    bad_loader = BadLockLoader(REPO, verify_hashes=True)
    with pytest.raises(HashMismatchError):
        bad_loader.load_package("moex:implementation:crm:0.1.0")
