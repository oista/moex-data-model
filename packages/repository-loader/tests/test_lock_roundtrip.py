from __future__ import annotations

from pathlib import Path

from moex_repository_loader.loader import RepositoryLoader
from moex_repository_loader.lock import format_lock, read_lock, verify_lock, write_lock

REPO = Path(__file__).resolve().parents[3]


def test_format_lock_sorted_no_aggregate() -> None:
    text = format_lock({"b": "sha256:" + ("b" * 64), "a": "sha256:" + ("a" * 64)})
    lines = text.strip().splitlines()
    assert "lock_schema_version" in lines[0]
    assert '"id": "a"' in lines[1]
    assert '"id": "b"' in lines[2]
    assert "timestamp" not in text
    assert text.count("sha256:") == 2  # only per-entry hashes


def test_write_verify_roundtrip(tmp_path: Path) -> None:
    loader = RepositoryLoader(REPO, verify_hashes=False)
    hashes = loader.compute_all_hashes()
    lock = tmp_path / "manifest.lock"
    write_lock(lock, hashes)
    assert verify_lock(lock, hashes) == []
    header, entries = read_lock(lock)
    assert header.lock_schema_version == "0.1.0"
    assert set(entries) == set(hashes)
