"""Ports for reading repository documents."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class DocumentStore(Protocol):
    """Read bytes/text under a repository root (paths are posix-relative)."""

    def read_text(self, relative_path: str) -> str: ...

    def exists(self, relative_path: str) -> bool: ...
