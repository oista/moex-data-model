"""GitLab GitProvider via REST API v4 (read + branch, commit, merge request)."""

from __future__ import annotations

import base64
import os
import ssl
from typing import Any
from urllib.parse import quote

import httpx

from moex_git.ports import FileChange, ReviewRef


class GitLabGitProvider:
    """GitProvider backed by a GitLab instance (including a local one)."""

    def __init__(
        self,
        *,
        url: str | None = None,
        token: str | None = None,
        project: str | None = None,
        api_base: str | None = None,
        client: httpx.Client | None = None,
        base_branch: str | None = None,
        ca_bundle: str | None = None,
    ) -> None:
        self.url = (url or os.environ.get("MOEX_GITLAB_URL") or "").rstrip("/")
        self.token = token if token is not None else os.environ.get("MOEX_GITLAB_TOKEN")
        self.project = project or os.environ.get("MOEX_GITLAB_PROJECT")
        self.base_branch = (
            base_branch or os.environ.get("MOEX_GITLAB_BASE") or "main"
        )
        if ca_bundle is None and "MOEX_GITLAB_CA_BUNDLE" in os.environ:
            ca_bundle = os.environ.get("MOEX_GITLAB_CA_BUNDLE") or None
        self.ca_bundle = ca_bundle or None
        if not self.url:
            raise ValueError("MOEX_GITLAB_URL must be set (e.g. https://gitlab.local)")
        if not self.project:
            raise ValueError(
                "MOEX_GITLAB_PROJECT must be set as group/name or a numeric id "
                f"(got {self.project!r})"
            )
        self._project = quote(str(self.project), safe="")
        self._api_base = (api_base or f"{self.url}/api/v4").rstrip("/")
        self._client = client
        self._owns_client = False

    def _http(self) -> httpx.Client:
        if self._client is not None:
            return self._client
        headers: dict[str, str] = {}
        if self.token:
            headers["PRIVATE-TOKEN"] = self.token
        verify: ssl.SSLContext | bool = True
        if self.ca_bundle:
            verify = ssl.create_default_context(cafile=self.ca_bundle)
        self._client = httpx.Client(
            base_url=self._api_base,
            headers=headers,
            timeout=30.0,
            verify=verify,
        )
        self._owns_client = True
        return self._client

    def close(self) -> None:
        if self._owns_client and self._client is not None:
            self._client.close()

    def _get(self, path: str, **params: Any) -> Any:
        resp = self._http().get(path, params=params or None)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, payload: dict[str, Any]) -> Any:
        resp = self._http().post(path, json=payload)
        resp.raise_for_status()
        return resp.json()

    def _file_url(self, path: str) -> str:
        encoded = quote(path.lstrip("/"), safe="")
        return f"/projects/{self._project}/repository/files/{encoded}"

    def get_file(self, revision: str, path: str) -> bytes:
        data = self._get(self._file_url(path), ref=revision)
        if isinstance(data, list):
            raise IsADirectoryError(path)
        encoding = data.get("encoding")
        content = data.get("content")
        if encoding == "base64" and isinstance(content, str):
            return base64.b64decode("".join(content.split()))
        raise ValueError(f"unexpected file payload for {path}")

    def resolve_revision(self, ref: str) -> str:
        encoded = quote(ref, safe="")
        data = self._get(f"/projects/{self._project}/repository/commits/{encoded}")
        sha = data.get("id")
        if not isinstance(sha, str) or not sha:
            raise LookupError(f"cannot resolve ref {ref!r}")
        return sha

    def list_revisions(self, *, limit: int = 20) -> tuple[str, ...]:
        data = self._get(
            f"/projects/{self._project}/repository/commits",
            per_page=min(max(limit, 1), 100),
        )
        if not isinstance(data, list):
            return ()
        return tuple(str(item["id"]) for item in data if item.get("id"))

    def create_branch(self, base_revision: str, branch_name: str) -> None:
        self._post(
            f"/projects/{self._project}/repository/branches",
            {"branch": branch_name, "ref": base_revision},
        )

    def _file_exists(self, revision: str, path: str) -> bool:
        resp = self._http().get(self._file_url(path), params={"ref": revision})
        if resp.status_code == 404:
            return False
        resp.raise_for_status()
        return True

    def commit_files(self, branch_name: str, files: list[FileChange]) -> str:
        if not files:
            raise ValueError("commit_files requires at least one file")
        actions: list[dict[str, str]] = []
        for change in files:
            try:
                content = change.content.decode("utf-8")
                encoding = "text"
            except UnicodeDecodeError:
                content = base64.b64encode(change.content).decode("ascii")
                encoding = "base64"
            actions.append(
                {
                    "action": "update" if self._file_exists(branch_name, change.path) else "create",
                    "file_path": change.path,
                    "content": content,
                    "encoding": encoding,
                }
            )
        commit = self._post(
            f"/projects/{self._project}/repository/commits",
            {
                "branch": branch_name,
                "commit_message": f"moex-git: update {len(files)} file(s)",
                "actions": actions,
            },
        )
        sha = commit.get("id")
        if not isinstance(sha, str) or not sha:
            raise LookupError("GitLab commit response has no id")
        return sha

    def create_review(self, branch_name: str, title: str) -> ReviewRef:
        mr = self._post(
            f"/projects/{self._project}/merge_requests",
            {
                "title": title,
                "source_branch": branch_name,
                "target_branch": self.base_branch,
                "description": "Created by MOEX Workbench publication.",
            },
        )
        return ReviewRef(
            url=str(mr.get("web_url") or ""),
            identifier=str(mr.get("iid") or mr.get("id") or ""),
        )
