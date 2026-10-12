"""Filesystem DocumentStore under model-assets/implementations/."""

from __future__ import annotations

from pathlib import Path


class FilesystemDocumentStore:
    def __init__(self, implementations_root: Path) -> None:
        self._root = implementations_root.resolve()

    @property
    def root(self) -> Path:
        return self._root

    def _resolve(self, relative_path: str) -> Path:
        rel = relative_path.replace("\\", "/").lstrip("/")
        if ".." in Path(rel).parts:
            raise ValueError(f"path escapes implementations root: {relative_path}")
        path = (self._root / rel).resolve()
        try:
            path.relative_to(self._root)
        except ValueError as exc:
            raise ValueError(
                f"path escapes implementations root: {relative_path}"
            ) from exc
        return path

    def read_text(self, relative_path: str) -> str:
        path = self._resolve(relative_path)
        return path.read_text(encoding="utf-8")

    def exists(self, relative_path: str) -> bool:
        return self._resolve(relative_path).is_file()
