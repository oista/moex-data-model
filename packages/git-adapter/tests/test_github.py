"""GitHubGitProvider tests with mocked httpx transport."""

from __future__ import annotations

import base64
import json

import httpx
import pytest

from moex_git.factory import make_git_provider
from moex_git.github import GitHubGitProvider
from moex_git.ports import FileChange


def _handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    method = request.method.upper()

    if path.endswith("/contents/README.md"):
        body = {
            "encoding": "base64",
            "content": base64.b64encode(b"# MOEX\n").decode("ascii"),
        }
        return httpx.Response(200, json=body)
    if method == "GET" and "/git/ref/heads/" in path:
        return httpx.Response(
            200, json={"object": {"sha": "basecommitsha0001"}}
        )
    if method == "GET" and "/git/commits/" in path:
        return httpx.Response(
            200,
            json={"sha": "basecommitsha0001", "tree": {"sha": "basetreesha0001"}},
        )
    if method == "GET" and "/commits/" in path and not path.endswith("/commits"):
        return httpx.Response(200, json={"sha": "abc123def456"})
    if method == "GET" and path.endswith("/commits"):
        return httpx.Response(
            200,
            json=[{"sha": "aaa111"}, {"sha": "bbb222"}],
        )
    if method == "POST" and path.endswith("/git/refs"):
        return httpx.Response(201, json={"ref": "refs/heads/feat/x"})
    if method == "POST" and path.endswith("/git/blobs"):
        return httpx.Response(201, json={"sha": "blobsha0001"})
    if method == "POST" and path.endswith("/git/trees"):
        return httpx.Response(201, json={"sha": "newtreesha0001"})
    if method == "POST" and path.endswith("/git/commits"):
        return httpx.Response(201, json={"sha": "newcommitsha0001"})
    if method == "PATCH" and "/git/refs/heads/" in path:
        return httpx.Response(200, json={"object": {"sha": "newcommitsha0001"}})
    if method == "POST" and path.endswith("/pulls"):
        body = json.loads(request.content.decode("utf-8")) if request.content else {}
        return httpx.Response(
            201,
            json={
                "html_url": "https://github.com/moex/data-model/pull/42",
                "number": 42,
                "title": body.get("title"),
            },
        )
    return httpx.Response(404, json={"message": f"not found {method} {path}"})


@pytest.fixture()
def github() -> GitHubGitProvider:
    transport = httpx.MockTransport(_handler)
    client = httpx.Client(
        transport=transport,
        base_url="https://api.github.com",
        headers={"Accept": "application/vnd.github+json"},
    )
    return GitHubGitProvider(
        token="fake",
        repo="moex/data-model",
        client=client,
        base_branch="main",
    )


def test_get_file(github: GitHubGitProvider) -> None:
    data = github.get_file("main", "README.md")
    assert b"MOEX" in data


def test_resolve_and_list(github: GitHubGitProvider) -> None:
    assert github.resolve_revision("main") == "abc123def456"
    assert github.list_revisions(limit=2) == ("aaa111", "bbb222")


def test_write_branch_commit_pr(github: GitHubGitProvider) -> None:
    github.create_branch("main", "feat/x")
    sha = github.commit_files(
        "feat/x",
        [FileChange(path="model.yaml", content=b"name: x\n")],
    )
    assert sha == "newcommitsha0001"
    review = github.create_review("feat/x", "Publish trading")
    assert review.url.endswith("/pull/42")
    assert review.identifier == "42"


def test_factory_github(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MOEX_GIT_PROVIDER", "github")
    monkeypatch.setenv("MOEX_GITHUB_REPO", "moex/data-model")
    monkeypatch.setenv("MOEX_GITHUB_TOKEN", "t")
    provider = make_git_provider(provider="github")
    assert isinstance(provider, GitHubGitProvider)
