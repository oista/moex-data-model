"""GitHubGitProvider read-path tests with mocked httpx transport."""

from __future__ import annotations

import base64

import httpx
import pytest

from moex_git.factory import make_git_provider
from moex_git.github import GitHubGitProvider


def _handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path.endswith("/contents/README.md"):
        body = {
            "encoding": "base64",
            "content": base64.b64encode(b"# MOEX\n").decode("ascii"),
        }
        return httpx.Response(200, json=body)
    if "/commits/" in path and not path.endswith("/commits"):
        return httpx.Response(200, json={"sha": "abc123def456"})
    if path.endswith("/commits"):
        return httpx.Response(
            200,
            json=[{"sha": "aaa111"}, {"sha": "bbb222"}],
        )
    return httpx.Response(404, json={"message": "not found"})


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
    )


def test_get_file(github: GitHubGitProvider) -> None:
    data = github.get_file("main", "README.md")
    assert b"MOEX" in data


def test_resolve_and_list(github: GitHubGitProvider) -> None:
    assert github.resolve_revision("main") == "abc123def456"
    assert github.list_revisions(limit=2) == ("aaa111", "bbb222")


def test_writes_not_implemented(github: GitHubGitProvider) -> None:
    with pytest.raises(NotImplementedError):
        github.create_branch("main", "feat/x")


def test_factory_github(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MOEX_GIT_PROVIDER", "github")
    monkeypatch.setenv("MOEX_GITHUB_REPO", "moex/data-model")
    monkeypatch.setenv("MOEX_GITHUB_TOKEN", "t")
    provider = make_git_provider(provider="github")
    assert isinstance(provider, GitHubGitProvider)
