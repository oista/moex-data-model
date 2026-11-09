"""Recompute manifest.lock from a git revision plus one new body."""

from __future__ import annotations

import subprocess

from moex_git.ports import FileChange, GitProvider
from moex_model_cli.bootstrap import find_repo_root
from moex_repository_loader import OverlayDocumentStore, RepositoryLoader
from moex_repository_loader.lock import format_lock

IMPLEMENTATIONS_PREFIX = "model-assets/implementations"
MANIFEST_PATH = f"{IMPLEMENTATIONS_PREFIX}/manifest.yaml"
LOCK_PATH = f"{IMPLEMENTATIONS_PREFIX}/manifest.lock"


def _normalize(text: str) -> str:
    return text.replace("\r\n", "\n")


def _read_or_missing(git: GitProvider, revision: str, path: str) -> bytes | None:
    """Return file bytes, or None when that path is not a file at revision."""
    try:
        return git.get_file(revision, path)
    except (IsADirectoryError, subprocess.CalledProcessError):
        return None
    except Exception as exc:
        response = getattr(exc, "response", None)
        if getattr(response, "status_code", None) == 404:
            return None
        raise


class GitRevisionDocumentStore:
    """DocumentStore over one git revision, under the implementations tree."""

    def __init__(
        self,
        git: GitProvider,
        revision: str,
        prefix: str = IMPLEMENTATIONS_PREFIX,
    ) -> None:
        self._git = git
        self._revision = revision
        self._prefix = prefix.strip("/")

    def _full(self, relative_path: str) -> str:
        rel = relative_path.replace("\\", "/").lstrip("/")
        return f"{self._prefix}/{rel}"

    def read_text(self, relative_path: str) -> str:
        data = self._git.get_file(self._revision, self._full(relative_path))
        return data.decode("utf-8")

    def exists(self, relative_path: str) -> bool:
        return (
            _read_or_missing(self._git, self._revision, self._full(relative_path))
            is not None
        )


def relock_change(
    git: GitProvider,
    base_revision: str,
    rel: str,
    content: str,
) -> FileChange | None:
    """Lock file for base_revision with ``rel`` replaced by ``content``.

    Returns None when the implementations manifest is absent (nothing to lock)
    or when the recomputed lock text already matches the base revision.
    """
    if _read_or_missing(git, base_revision, MANIFEST_PATH) is None:
        return None
    rel_posix = rel.replace("\\", "/")
    prefix = f"{IMPLEMENTATIONS_PREFIX}/"
    if not rel_posix.startswith(prefix):
        raise ValueError(f"publication path is outside implementations: {rel}")
    rel_under = rel_posix[len(prefix) :]
    store = OverlayDocumentStore(
        GitRevisionDocumentStore(git, base_revision),
        {rel_under: content},
    )
    hashes = RepositoryLoader(
        find_repo_root(),
        store=store,
        verify_hashes=False,
    ).compute_all_hashes()
    text = format_lock(hashes)
    current = _read_or_missing(git, base_revision, LOCK_PATH)
    if current is not None and _normalize(current.decode("utf-8")) == text:
        return None
    return FileChange(path=LOCK_PATH, content=text.encode("utf-8"))
