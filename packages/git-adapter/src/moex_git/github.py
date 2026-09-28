"""GitHub GitProvider via REST (read + write for Stage 3 narrow-v3)."""

from __future__ import annotations

import base64
import os
from typing import Any

import httpx

from moex_git.ports import FileChange, ReviewRef


class GitHubGitProvider:
    """GitProvider backed by GitHub Contents / Git Data / Pulls APIs."""

    def __init__(
        self,
        *,
        token: str | None = None,
        repo: str | None = None,
        api_base: str = "https://api.github.com",
        client: httpx.Client | None = None,
        base_branch: str | None = None,
    ) -> None:
        self.token = token or os.environ.get("MOEX_GITHUB_TOKEN")
        self.repo = repo or os.environ.get("MOEX_GITHUB_REPO")
        self.base_branch = (
            base_branch
            or os.environ.get("MOEX_GITHUB_BASE")
            or "main"
        )
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

    def _post(self, path: str, json: dict[str, Any]) -> Any:
        resp = self._client.post(path, json=json)
        resp.raise_for_status()
        return resp.json()

    def _patch(self, path: str, json: dict[str, Any]) -> Any:
        resp = self._client.patch(path, json=json)
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
        sha = self.resolve_revision(base_revision)
        self._post(
            f"/repos/{self.repo}/git/refs",
            {"ref": f"refs/heads/{branch_name}", "sha": sha},
        )

    def commit_files(self, branch_name: str, files: list[FileChange]) -> str:
        if not files:
            raise ValueError("commit_files requires at least one file")
        ref = self._get(f"/repos/{self.repo}/git/ref/heads/{branch_name}")
        base_commit_sha = ref["object"]["sha"]
        base_commit = self._get(f"/repos/{self.repo}/git/commits/{base_commit_sha}")
        base_tree_sha = base_commit["tree"]["sha"]

        tree_items: list[dict[str, str]] = []
        for change in files:
            blob = self._post(
                f"/repos/{self.repo}/git/blobs",
                {
                    "content": base64.b64encode(change.content).decode("ascii"),
                    "encoding": "base64",
                },
            )
            tree_items.append(
                {
                    "path": change.path,
                    "mode": change.mode or "100644",
                    "type": "blob",
                    "sha": blob["sha"],
                }
            )
        tree = self._post(
            f"/repos/{self.repo}/git/trees",
            {"base_tree": base_tree_sha, "tree": tree_items},
        )
        commit = self._post(
            f"/repos/{self.repo}/git/commits",
            {
                "message": f"moex-git: update {len(files)} file(s)",
                "tree": tree["sha"],
                "parents": [base_commit_sha],
            },
        )
        new_sha = str(commit["sha"])
        self._patch(
            f"/repos/{self.repo}/git/refs/heads/{branch_name}",
            {"sha": new_sha, "force": False},
        )
        return new_sha

    def create_review(self, branch_name: str, title: str) -> ReviewRef:
        pr = self._post(
            f"/repos/{self.repo}/pulls",
            {
                "title": title,
                "head": branch_name,
                "base": self.base_branch,
                "body": "Created by MOEX Workbench publication.",
            },
        )
        return ReviewRef(
            url=str(pr.get("html_url") or ""),
            identifier=str(pr.get("number") or pr.get("id") or ""),
        )


# Back-compat alias used by earlier roadmap slice.
GitHubGitProviderStub = GitHubGitProvider
