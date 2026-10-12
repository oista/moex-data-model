"""manifest.lock read / write / verify (JSON Lines)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from moex_repository_loader.models import RepositoryLockEntry, RepositoryLockHeader

LOCK_SCHEMA_VERSION = "0.1.0"


class LockError(RuntimeError):
    """Lock file missing, malformed, or out of date."""


def read_lock(path: Path) -> tuple[RepositoryLockHeader, dict[str, RepositoryLockEntry]]:
    if not path.is_file():
        raise LockError(f"lock file missing: {path}")
    lines = [
        ln.strip()
        for ln in path.read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]
    if not lines:
        raise LockError(f"lock file empty: {path}")
    header_raw = json.loads(lines[0])
    header = RepositoryLockHeader.model_validate(header_raw)
    entries: dict[str, RepositoryLockEntry] = {}
    for line in lines[1:]:
        entry = RepositoryLockEntry.model_validate(json.loads(line))
        if entry.id in entries:
            raise LockError(f"duplicate lock id: {entry.id}")
        entries[entry.id] = entry
    return header, entries


def format_lock(
    entries: dict[str, str],
    *,
    lock_schema_version: str = LOCK_SCHEMA_VERSION,
) -> str:
    """Build lock file text from id -> content_hash map."""
    lines = [json.dumps({"lock_schema_version": lock_schema_version}, sort_keys=True)]
    for doc_id in sorted(entries):
        lines.append(
            json.dumps(
                {"id": doc_id, "content_hash": entries[doc_id]},
                sort_keys=True,
            )
        )
    return "\n".join(lines) + "\n"


def write_lock(path: Path, entries: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(format_lock(entries), encoding="utf-8", newline="\n")


def verify_lock(
    path: Path,
    expected: dict[str, str],
) -> list[str]:
    """Return human-readable problems; empty list means OK."""
    problems: list[str] = []
    try:
        _header, entries = read_lock(path)
    except (LockError, json.JSONDecodeError, ValueError) as exc:
        return [str(exc)]

    expected_ids = set(expected)
    actual_ids = set(entries)
    for missing in sorted(expected_ids - actual_ids):
        problems.append(f"missing lock entry: {missing}")
    for extra in sorted(actual_ids - expected_ids):
        problems.append(f"extra lock entry: {extra}")
    for doc_id in sorted(expected_ids & actual_ids):
        if entries[doc_id].content_hash != expected[doc_id]:
            problems.append(
                f"hash mismatch: {doc_id} "
                f"(lock={entries[doc_id].content_hash} actual={expected[doc_id]})"
            )
    return problems


def lock_update_hint() -> str:
    return "Run: moex-model lock update --root <repo>"


def expected_hashes_from_dicts(rows: list[dict[str, Any]]) -> dict[str, str]:
    """Helper for tests: [{id, content_hash}, ...] -> map."""
    return {str(r["id"]): str(r["content_hash"]) for r in rows}
