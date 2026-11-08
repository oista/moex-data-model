"""GitLabGitProvider tests with mocked httpx transport."""

from __future__ import annotations

import base64
import json

import httpx
import pytest

from moex_git.factory import make_git_provider
from moex_git.gitlab import GitLabGitProvider
from moex_git.ports import FileChange

PROJECT = "group%2Fmodels"
COMMIT_BODIES: list[dict] = []


def _handler(request: httpx.Request) -> httpx.Response:
    path = request.url.raw_path.decode("ascii").split("?", 1)[0]
    method = request.method.upper()
    assert f"/projects/{PROJECT}/" in path

    if method == "GET" and path.endswith("/repository/files/README.md"):
        return httpx.Response(
            200,
            json={
                "encoding": "base64",
                "content": base64.b64encode(b"# MOEX\n").decode("ascii"),
            },
        )
    if method == "GET" and "/repository/files/" in path:
        return httpx.Response(404, json={"message": "404 File Not Found"})
    if method == "GET" and path.endswith("/repository/commits"):
        return httpx.Response(200, json=[{"id": "aaa111"}, {"id": "bbb222"}])
    if method == "GET" and "/repository/commits/" in path:
        return httpx.Response(200, json={"id": "abc123def456"})
    if method == "POST" and path.endswith("/repository/branches"):
        body = json.loads(request.content.decode("utf-8"))
        assert body["branch"] == "feat/x"
        assert body["ref"] == "main"
        return httpx.Response(201, json={"name": body["branch"]})
    if method == "POST" and path.endswith("/repository/commits"):
        body = json.loads(request.content.decode("utf-8"))
        COMMIT_BODIES.append(body)
        return httpx.Response(201, json={"id": "newcommitsha0001"})
    if method == "POST" and path.endswith("/merge_requests"):
        body = json.loads(request.content.decode("utf-8"))
        return httpx.Response(
            201,
            json={
                "web_url": "https://gitlab.example/group/models/-/merge_requests/7",
                "iid": 7,
                "title": body.get("title"),
                "source_branch": body.get("source_branch"),
                "target_branch": body.get("target_branch"),
            },
        )
    return httpx.Response(404, json={"message": f"not found {method} {path}"})


@pytest.fixture()
def gitlab() -> GitLabGitProvider:
    COMMIT_BODIES.clear()
    transport = httpx.MockTransport(_handler)
    client = httpx.Client(
        transport=transport,
        base_url="https://gitlab.example/api/v4",
        headers={"PRIVATE-TOKEN": "fake"},
    )
    return GitLabGitProvider(
        url="https://gitlab.example",
        token="fake",
        project="group/models",
        client=client,
        base_branch="main",
    )


def test_get_file(gitlab: GitLabGitProvider) -> None:
    data = gitlab.get_file("main", "README.md")
    assert b"MOEX" in data


def test_resolve_and_list(gitlab: GitLabGitProvider) -> None:
    assert gitlab.resolve_revision("main") == "abc123def456"
    assert gitlab.list_revisions(limit=2) == ("aaa111", "bbb222")


def test_write_branch_commit_merge_request(gitlab: GitLabGitProvider) -> None:
    gitlab.create_branch("main", "feat/x")
    sha = gitlab.commit_files(
        "feat/x",
        [
            FileChange(path="README.md", content=b"# updated\n"),
            FileChange(path="model.yaml", content=b"name: x\n"),
        ],
    )
    assert sha == "newcommitsha0001"
    assert len(COMMIT_BODIES) == 1
    actions = {item["file_path"]: item["action"] for item in COMMIT_BODIES[0]["actions"]}
    assert actions == {"README.md": "update", "model.yaml": "create"}
    assert COMMIT_BODIES[0]["branch"] == "feat/x"
    review = gitlab.create_review("feat/x", "Publish trading")
    assert review.url.endswith("/merge_requests/7")
    assert review.identifier == "7"


def test_commit_files_requires_a_file(gitlab: GitLabGitProvider) -> None:
    with pytest.raises(ValueError):
        gitlab.commit_files("feat/x", [])


def test_factory_gitlab(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MOEX_GIT_PROVIDER", "gitlab")
    monkeypatch.setenv("MOEX_GITLAB_URL", "https://gitlab.example")
    monkeypatch.setenv("MOEX_GITLAB_PROJECT", "group/models")
    monkeypatch.setenv("MOEX_GITLAB_TOKEN", "t")
    monkeypatch.setenv("MOEX_GITLAB_BASE", "develop")
    monkeypatch.setenv("MOEX_GITLAB_CA_BUNDLE", "C:/ca.pem")
    provider = make_git_provider(provider="gitlab")
    assert isinstance(provider, GitLabGitProvider)
    assert provider.project == "group/models"
    assert provider.base_branch == "develop"
    assert provider.ca_bundle == "C:/ca.pem"
    provider.close()


def test_factory_gitlab_requires_project(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MOEX_GITLAB_PROJECT", raising=False)
    monkeypatch.setenv("MOEX_GITLAB_URL", "https://gitlab.example")
    with pytest.raises(ValueError):
        make_git_provider(provider="gitlab")
