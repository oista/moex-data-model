"""Read-only GitHub GitProvider via REST (writes remain unsupported)."""

from __future__ import annotations

import base64
import os
from typing import Any

import httpx

from moex_git.ports import FileChange, ReviewRef


class GitHubGitProvider:
    """GitProvider backed by GitHub Contents/Commits API (read methods only)."""

    def __init__(
        self,
        *,
        token: str | None = None,
        repo: str | None = None,
        api_base: str = "https://api.github.com",
        client: httpx.Client | None = None,
    ) -> None:
        self.token = token or os.environ.get("MOEX_GITHUB_TOKEN")
        self.repo = repo or os.environ.get("MOEX_GITHUB_REPO")
        if not self.repo or "/" not in self.repo:
            raise ValueError(
                "MOEX_GITHUB_REPO must be set as owner/name "
                f"(got {self.repo!r})"
            )
        self.api_base = api_base.rstrip("/")
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        self._client = client or httpx.Client(
            base_url=self.api_base, headers=headers, timeout=30.0
        )
        self._owns_client = client is None

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def _get(self, path: str, **params: Any) -> Any:
        resp = self._client.get(path, params=params or None)
        resp.raise_for_status()
        return resp.json()

    def get_file(self, revision: str, path: str) -> bytes:
        data = self._get(
            f"/repos/{self.repo}/contents/{path.lstrip('/')}",
            ref=revision,
        )
        if isinstance(data, list):
            raise IsADirectoryError(path)
        encoding = data.get("encoding")
        content = data.get("content")
        if encoding == "base64" and isinstance(content, str):
            return base64.b64decode(content)
        raise ValueError(f"unexpected contents payload for {path}")

    def resolve_revision(self, ref: str) -> str:
        data = self._get(f"/repos/{self.repo}/commits/{ref}")
        sha = data.get("sha")
        if not isinstance(sha, str) or not sha:
            raise LookupError(f"cannot resolve ref {ref!r}")
        return sha

    def list_revisions(self, *, limit: int = 20) -> tuple[str, ...]:
        data = self._get(
            f"/repos/{self.repo}/commits",
            per_page=min(max(limit, 1), 100),
        )
        if not isinstance(data, list):
            return ()
        return tuple(str(item["sha"]) for item in data if item.get("sha"))

    def create_branch(self, base_revision: str, branch_name: str) -> None:
        raise NotImplementedError(
            "GitHubGitProvider.create_branch: write path not implemented"
        )

    def commit_files(self, branch_name: str, files: list[FileChange]) -> str:
        raise NotImplementedError(
            "GitHubGitProvider.commit_files: write path not implemented"
        )

    def create_review(self, branch_name: str, title: str) -> ReviewRef:
        raise NotImplementedError(
            "GitHubGitProvider.create_review: write path not implemented"
        )


# Back-compat alias used by earlier roadmap slice.
GitHubGitProviderStub = GitHubGitProvider
