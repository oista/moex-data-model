"""LocalGitProvider smoke against this repository."""

from __future__ import annotations

from pathlib import Path

import pytest

from moex_git import LocalGitProvider

REPO = Path(__file__).resolve().parents[3]


@pytest.fixture
def git() -> LocalGitProvider:
    return LocalGitProvider(REPO)


def test_resolve_and_get_readme(git: LocalGitProvider) -> None:
    tip = git.resolve_revision("HEAD")
    assert len(tip) >= 7
    data = git.get_file("HEAD", "README.md")
    assert b"MOEX" in data or b"moex" in data.lower()


def test_list_revisions(git: LocalGitProvider) -> None:
    revs = git.list_revisions(limit=3)
    assert revs
    assert all(len(r) >= 7 for r in revs)
