"""GitProvider port — hosting-agnostic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class FileChange:
    path: str
    content: bytes
    mode: str = "100644"


@dataclass(frozen=True, slots=True)
class ReviewRef:
    url: str
    identifier: str


@runtime_checkable
class GitProvider(Protocol):
    def get_file(self, revision: str, path: str) -> bytes: ...

    def resolve_revision(self, ref: str) -> str: ...

    def list_revisions(self, *, limit: int = 20) -> tuple[str, ...]: ...

    def create_branch(self, base_revision: str, branch_name: str) -> None: ...

    def commit_files(self, branch_name: str, files: list[FileChange]) -> str: ...

    def create_review(self, branch_name: str, title: str) -> ReviewRef: ...
