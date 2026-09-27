"""Discovery tests."""

from pathlib import Path

from moex_publication_viewer.discovery import discover_manifest_paths


def test_discover_finds_publish_yaml(tmp_path: Path):
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "publish.yaml").write_text("kind: publication_module\n", encoding="utf-8")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "publish.yaml").write_text("kind: publication_module\n", encoding="utf-8")
    (tmp_path / "dist").mkdir()
    (tmp_path / "dist" / "publish.yaml").write_text("kind: publication_module\n", encoding="utf-8")

    found = discover_manifest_paths(tmp_path)
    assert len(found) == 1
    assert found[0].name == "publish.yaml"
    assert ".venv" not in found[0].parts
