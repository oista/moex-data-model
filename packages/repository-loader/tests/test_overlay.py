from __future__ import annotations

from pathlib import Path

from moex_repository_loader.fs import FilesystemDocumentStore
from moex_repository_loader.overlay import OverlayDocumentStore


def test_overlay_replaces_listed_texts_and_keeps_the_rest(tmp_path: Path) -> None:
    root = tmp_path / "implementations"
    root.mkdir()
    (root / "kept.txt").write_text("from-base", encoding="utf-8")
    (root / "replaced.txt").write_text("old", encoding="utf-8")
    base = FilesystemDocumentStore(root)
    store = OverlayDocumentStore(
        base,
        {"replaced.txt": "new", "added.txt": "extra"},
    )

    assert store.read_text("replaced.txt") == "new"
    assert store.read_text("kept.txt") == "from-base"
    assert store.read_text("added.txt") == "extra"
    assert store.exists("replaced.txt") is True
    assert store.exists("kept.txt") is True
    assert store.exists("added.txt") is True
    assert store.exists("missing.txt") is False
