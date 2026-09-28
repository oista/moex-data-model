"""Assemble and optionally inline viewer static assets (CSS/JS/fonts/icons)."""

from __future__ import annotations

import base64
import re
from pathlib import Path

VIEWER_ROOT = Path(__file__).resolve().parent.parent.parent
STATIC = VIEWER_ROOT / "static"
CSS_DIR = STATIC / "css"
JS_DIR = STATIC / "js"
FONTS_DIR = STATIC / "fonts"
ICONS_DIR = STATIC / "icons"

CSS_ORDER = [
    "00-reset.css",
    "10-tokens.css",
    "15-fonts.css",  # generated or static placeholder; may be injected
    "20-base.css",
    "30-layout.css",
    "40-components.css",
    "50-renderers.css",
    "60-utilities.css",
    "70-responsive.css",
    "80-print.css",
]

JS_ORDER = [
    "state.js",
    "navigation.js",
    "tree.js",
    "search.js",
    "theme.js",
    "clipboard.js",
    "tables.js",
    "dialogs.js",
    "accessibility.js",
    "app.js",
]

# Font files → @font-face families
FONT_FACES = [
    ("inter-latin.woff2", "MOEX UI", "100 900", "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD"),
    ("inter-latin-ext.woff2", "MOEX UI", "100 900", "U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF"),
    ("inter-cyrillic.woff2", "MOEX UI", "100 900", "U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116"),
    ("jetbrains-mono-400.woff2", "JetBrains Mono", "400", "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD"),
    ("jetbrains-mono-500.woff2", "JetBrains Mono", "500", "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD"),
    ("jetbrains-mono-cyr-400.woff2", "JetBrains Mono", "400", "U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116"),
    ("jetbrains-mono-cyr-500.woff2", "JetBrains Mono", "500", "U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116"),
]


def _data_uri_woff2(path: Path) -> str:
    raw = path.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:font/woff2;base64,{b64}"


def build_fonts_css() -> str:
    chunks: list[str] = ["/* Embedded fonts (generated at build) */\n"]
    for filename, family, weight, unicode_range in FONT_FACES:
        path = FONTS_DIR / filename
        if not path.is_file():
            continue
        uri = _data_uri_woff2(path)
        chunks.append(
            f"""@font-face {{
  font-family: "{family}";
  src: url("{uri}") format("woff2");
  font-weight: {weight};
  font-style: normal;
  font-display: swap;
  unicode-range: {unicode_range};
}}
"""
        )
    return "\n".join(chunks)


def assemble_css() -> str:
    parts: list[str] = []
    fonts_css = build_fonts_css()
    for name in CSS_ORDER:
        if name == "15-fonts.css":
            parts.append(fonts_css)
            continue
        path = CSS_DIR / name
        if path.is_file():
            parts.append(f"/* === {name} === */\n{path.read_text(encoding='utf-8')}")
    # Fallback: legacy monolith if layered CSS incomplete
    if len(parts) <= 2:
        legacy = STATIC / "viewer.css"
        if legacy.is_file():
            parts.append(legacy.read_text(encoding="utf-8"))
    return "\n\n".join(parts)


def assemble_js() -> str:
    parts: list[str] = []
    for name in JS_ORDER:
        path = JS_DIR / name
        if path.is_file():
            parts.append(f"/* === {name} === */\n{path.read_text(encoding='utf-8')}")
    if not parts:
        legacy = STATIC / "viewer.js"
        if legacy.is_file():
            return legacy.read_text(encoding="utf-8")
    return "\n\n".join(parts)


def write_dev_bundles() -> tuple[str, str]:
    """Write assembled CSS/JS to static/viewer.css and static/viewer.js for tooling."""
    css = assemble_css()
    js = assemble_js()
    (STATIC / "viewer.css").write_text(css, encoding="utf-8")
    # Do not overwrite viewer.js source — it is the canonical app script until split.
    return css, js


def load_icon_svg(name: str) -> str:
    path = ICONS_DIR / f"{name}.svg"
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8").strip()


_EXTERNAL_URL_RE = re.compile(
    r"""(?i)(?:src|href)\s*=\s*["']https?://[^"']+["']|url\(\s*["']?https?://"""
)


def assert_no_required_cdn(html: str) -> None:
    """Raise if HTML appears to require external network assets for UI."""
    # Allow comments mentioning https; flag real src/href/url usage
    if _EXTERNAL_URL_RE.search(html):
        raise ValueError("Viewer HTML must not require external CDN assets")
