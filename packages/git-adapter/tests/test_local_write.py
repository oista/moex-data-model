"""LocalGitProvider write path against an isolated temp repository."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from moex_git import LocalGitProvider
from moex_git.ports import FileChange


@pytest.fixture()
def temp_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    (root / "README.md").write_text("hello\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return root


def test_branch_commit_review(temp_repo: Path) -> None:
    git = LocalGitProvider(temp_repo)
    base = git.resolve_revision("HEAD")
    git.create_branch(base, "workbench/publish-test")
    sha = git.commit_files(
        "workbench/publish-test",
        [
            FileChange(
                path="model-assets/sample.yaml",
                content=b"element_id: x\nname: x\n",
            )
        ],
    )
    assert len(sha) >= 7
    assert (temp_repo / "model-assets" / "sample.yaml").is_file()
    review = git.create_review("workbench/publish-test", "Test publish")
    assert review.url.startswith("local://review/")
    assert "workbench/publish-test" in review.identifier
