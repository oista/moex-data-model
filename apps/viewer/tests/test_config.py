"""Viewer config loader tests."""

from pathlib import Path

import yaml

from moex_publication_viewer.config_loader import (
    DEFAULT_CLASS_KIND_COLORS,
    DEFAULT_DISPLAY_SETTINGS,
    load_class_kind_colors,
    load_display_config,
    load_viewer_config,
)
from moex_publication_viewer.build import VIEWER_ROOT, build


def _hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.strip().lstrip("#")
    if len(h) != 6:
        raise ValueError(hex_color)
    return tuple(int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))  # type: ignore[return-value]


def _rel_luminance(rgb: tuple[float, float, float]) -> float:
    def chan(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (chan(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg: str, bg: str) -> float:
    l1 = _rel_luminance(_hex_to_rgb(fg))
    l2 = _rel_luminance(_hex_to_rgb(bg))
    lighter, darker = (l1, l2) if l1 >= l2 else (l2, l1)
    return (lighter + 0.05) / (darker + 0.05)


def test_class_kind_colors_config_exists():
    path = VIEWER_ROOT / "config" / "class-kind-colors.yaml"
    assert path.is_file()
    data = load_class_kind_colors(VIEWER_ROOT)
    assert data["roles"]["plain"]
    assert data["roles"]["mixin"]
    assert data["roles"]["abstract"]
    assert data["roles"]["enum"]
    assert data["corner"]["has_mixins"]


def test_display_config_catalog():
    path = VIEWER_ROOT / "config" / "display.yaml"
    assert path.is_file()
    cfg = load_display_config(VIEWER_ROOT)
    assert cfg["version"] == 1
    keys = {s["key"] for s in cfg["settings"]}
    expected = {s["key"] for s in DEFAULT_DISPLAY_SETTINGS}
    assert expected <= keys
    assert cfg["defaults"]["appearance.theme"] == "light"
    assert cfg["defaults"]["glossary.show_relation_blocks"] is True
    theme = next(s for s in cfg["settings"] if s["key"] == "appearance.theme")
    assert "system" in theme["options"]


def test_load_viewer_config_shape():
    cfg = load_viewer_config(VIEWER_ROOT)
    assert "class_kind_colors" in cfg
    assert "display" in cfg
    assert set(cfg["class_kind_colors"]["roles"]) >= {
        "plain",
        "mixin",
        "abstract",
        "enum",
    }
    assert "defaults" in cfg["display"]
    assert "settings" in cfg["display"]


def test_missing_config_falls_back(tmp_path: Path):
    data = load_class_kind_colors(tmp_path)
    assert data["roles"] == DEFAULT_CLASS_KIND_COLORS["roles"]
    display = load_display_config(tmp_path)
    assert display["defaults"]["appearance.theme"] == "light"
    assert len(display["settings"]) == len(DEFAULT_DISPLAY_SETTINGS)


def test_display_yaml_partial_override(tmp_path: Path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "display.yaml").write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "settings": [
                    {
                        "key": "appearance.theme",
                        "type": "choice",
                        "options": ["light", "dark", "system"],
                        "default": "dark",
                        "label": "Theme",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    cfg = load_display_config(tmp_path)
    assert cfg["defaults"]["appearance.theme"] == "dark"
    assert "glossary.view" in cfg["defaults"]


def test_class_kind_palette_contrast_aa():
    """UI component contrast ≥ 3:1 (WCAG AA) on light and dark surfaces."""
    colors = load_class_kind_colors(VIEWER_ROOT)
    light_bg = "#ffffff"
    dark_bg = "#171a20"
    for name, hex_color in colors["roles"].items():
        assert contrast_ratio(hex_color, light_bg) >= 3.0, (name, hex_color, "light")
        assert contrast_ratio(hex_color, dark_bg) >= 3.0, (name, hex_color, "dark")
    corner = colors["corner"]["has_mixins"]
    assert contrast_ratio(corner, light_bg) >= 3.0
    assert contrast_ratio(corner, dark_bg) >= 3.0


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
    assert "#9a7a18" in html
    assert "appearance.theme" in html
    assert "text.hide_adr_refs" in html
    assert "glossary.show_relation_blocks" in html
