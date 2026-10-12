"""moex-model lock update|verify (ADR-047)."""

from __future__ import annotations

from pathlib import Path

from moex_repository_loader.loader import RepositoryLoader
from moex_repository_loader.lock import lock_update_hint, verify_lock, write_lock


def run_lock_update(repo_root: Path) -> tuple[int, str]:
    loader = RepositoryLoader(repo_root, verify_hashes=False)
    hashes = loader.compute_all_hashes()
    write_lock(loader.lock_path(), hashes)
    return 0, f"wrote {loader.lock_path().relative_to(repo_root).as_posix()} entries={len(hashes)}\n"


def run_lock_verify(repo_root: Path) -> tuple[int, str]:
    loader = RepositoryLoader(repo_root, verify_hashes=False)
    expected = loader.compute_all_hashes()
    problems = verify_lock(loader.lock_path(), expected)
    if not problems:
        return 0, f"lock OK entries={len(expected)}\n"
    lines = ["lock verify FAILED:"]
    lines.extend(f"  - {p}" for p in problems)
    lines.append(lock_update_hint())
    return 1, "\n".join(lines) + "\n"
