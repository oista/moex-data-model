"""Local git working-tree adapter via subprocess."""

from __future__ import annotations

import subprocess
from pathlib import Path

from moex_git.ports import FileChange, ReviewRef


class LocalGitProvider:
    """GitProvider backed by ``git`` CLI in ``repo_root``."""

    def __init__(self, repo_root: Path | str) -> None:
        self.root = Path(repo_root).resolve()

    def _run(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self.root,
            check=check,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def get_file(self, revision: str, path: str) -> bytes:
        proc = subprocess.run(
            ["git", "show", f"{revision}:{path}"],
            cwd=self.root,
            check=True,
            capture_output=True,
        )
        return proc.stdout

    def resolve_revision(self, ref: str) -> str:
        proc = self._run("rev-parse", ref)
        return proc.stdout.strip()

    def list_revisions(self, *, limit: int = 20) -> tuple[str, ...]:
        proc = self._run("log", f"-{limit}", "--format=%H")
        lines = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
        return tuple(lines)

    def create_branch(self, base_revision: str, branch_name: str) -> None:
        self._run("branch", branch_name, base_revision)

    def commit_files(self, branch_name: str, files: list[FileChange]) -> str:
        self._run("checkout", branch_name)
        for change in files:
            target = self.root / change.path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(change.content)
            self._run("add", change.path)
        self._run("commit", "-m", f"moex-git: update {len(files)} file(s)")
        return self.resolve_revision("HEAD")

    def create_review(self, branch_name: str, title: str) -> ReviewRef:
        # Local backend cannot open a hosting PR — return a stub ref.
        tip = self.resolve_revision(branch_name)
        return ReviewRef(
            url=f"local://review/{branch_name}",
            identifier=f"{branch_name}@{tip[:12]}:{title}",
        )
