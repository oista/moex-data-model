"""GitHub GitProvider stub — enabled later via env token (P4/follow-up)."""

from __future__ import annotations

import os

from moex_git.ports import FileChange, ReviewRef


class GitHubGitProviderStub:
    """Raises until MOEX_GITHUB_TOKEN is wired to a real client."""

    def __init__(self, *, token: str | None = None, repo: str | None = None) -> None:
        self.token = token or os.environ.get("MOEX_GITHUB_TOKEN")
        self.repo = repo or os.environ.get("MOEX_GITHUB_REPO")

    def _unsupported(self, method: str) -> None:
        raise NotImplementedError(
            f"GitHubGitProviderStub.{method}: set real GitHub client "
            f"(token={'set' if self.token else 'missing'}, repo={self.repo!r})"
        )

    def get_file(self, revision: str, path: str) -> bytes:
        self._unsupported("get_file")

    def resolve_revision(self, ref: str) -> str:
        self._unsupported("resolve_revision")

    def list_revisions(self, *, limit: int = 20) -> tuple[str, ...]:
        self._unsupported("list_revisions")

    def create_branch(self, base_revision: str, branch_name: str) -> None:
        self._unsupported("create_branch")

    def commit_files(self, branch_name: str, files: list[FileChange]) -> str:
        self._unsupported("commit_files")

    def create_review(self, branch_name: str, title: str) -> ReviewRef:
        self._unsupported("create_review")
