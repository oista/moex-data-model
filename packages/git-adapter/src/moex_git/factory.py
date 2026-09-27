"""Select Local vs GitHub GitProvider from environment."""

from __future__ import annotations

import os
from pathlib import Path

from moex_git.github import GitHubGitProvider
from moex_git.local import LocalGitProvider
from moex_git.ports import GitProvider


def make_git_provider(
    *,
    repo_root: Path | str | None = None,
    provider: str | None = None,
) -> GitProvider:
    """Return GitProvider for ``MOEX_GIT_PROVIDER`` (``local``|``github``)."""
    name = (provider or os.environ.get("MOEX_GIT_PROVIDER") or "local").lower()
    if name == "github":
        return GitHubGitProvider()
    if name == "local":
        root = repo_root or os.environ.get("MOEX_GIT_ROOT") or Path.cwd()
        return LocalGitProvider(root)
    raise ValueError(f"unknown MOEX_GIT_PROVIDER={name!r} (use local|github)")
