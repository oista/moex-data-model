"""Viewer config loader tests."""

from pathlib import Path

from moex_publication_viewer.config_loader import (
    DEFAULT_CLASS_KIND_COLORS,
    load_class_kind_colors,
    load_viewer_config,
)
from moex_publication_viewer.build import VIEWER_ROOT, build


def test_class_kind_colors_config_exists():
    path = VIEWER_ROOT / "config" / "class-kind-colors.yaml"
    assert path.is_file()
    data = load_class_kind_colors(VIEWER_ROOT)
    assert data["roles"]["plain"]
    assert data["roles"]["mixin"]
    assert data["roles"]["abstract"]
    assert data["roles"]["enum"]
    assert data["corner"]["has_mixins"]


def test_load_viewer_config_shape():
    cfg = load_viewer_config(VIEWER_ROOT)
    assert "class_kind_colors" in cfg
    assert set(cfg["class_kind_colors"]["roles"]) >= {
        "plain",
        "mixin",
        "abstract",
        "enum",
    }


def test_missing_config_falls_back(tmp_path: Path):
    data = load_class_kind_colors(tmp_path)
    assert data["roles"] == DEFAULT_CLASS_KIND_COLORS["roles"]


def test_build_embeds_viewer_config():
    repo = Path(__file__).resolve().parents[3]
    dist = repo / "apps" / "viewer" / "dist"
    index = build(repo, dist)
    html = index.read_text(encoding="utf-8")
    assert 'id="viewer-config"' in html
    assert '"plain"' in html
    assert '"mixin"' in html
    assert '"abstract"' in html
    assert '"enum"' in html
    assert '"has_mixins"' in html
    assert "#b8922e" in html
