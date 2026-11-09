"""DocumentStore that layers in-memory texts over another store."""

from __future__ import annotations

from moex_repository_loader.ports import DocumentStore


def _key(relative_path: str) -> str:
    return relative_path.replace("\\", "/").lstrip("/")


class OverlayDocumentStore:
    """Read ``overrides`` first; everything else comes from ``base``."""

    def __init__(self, base: DocumentStore, overrides: dict[str, str]) -> None:
        self._base = base
        self._overrides = {_key(path): text for path, text in overrides.items()}

    def read_text(self, relative_path: str) -> str:
        key = _key(relative_path)
        if key in self._overrides:
            return self._overrides[key]
        return self._base.read_text(relative_path)

    def exists(self, relative_path: str) -> bool:
        key = _key(relative_path)
        if key in self._overrides:
            return True
        return self._base.exists(relative_path)
