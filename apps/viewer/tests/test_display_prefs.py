"""Display prefs helpers and contracts (ADR-015 UI settings)."""

from __future__ import annotations

import re
from pathlib import Path

from moex_publication_viewer.build import VIEWER_ROOT

JS = (VIEWER_ROOT / "static" / "viewer.js").read_text(encoding="utf-8")

# Mirrors apps/viewer/static/viewer.js stripAdrRefs (keep in sync).
_PAREN = re.compile(
    r"\s*[\(（]\s*ADR[-–]?\s*\d{3}(?:\s*[/,]\s*(?:ADR[-–]?)?\d{3})*\s*[\)）]",
    re.I,
)
_BARE = re.compile(r"\bADR[-–]?\d{3}(?:\s*[/,]\s*(?:ADR[-–]?)?\d{3})*", re.I)


def strip_adr_refs(s: str) -> str:
    text = _PAREN.sub("", s)
    text = _BARE.sub("", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"\s+([.,;:])", r"\1", text)
    return text.strip()


def test_viewer_js_prefs_store_contract():
    for needle in (
        "moex-viewer-prefs",
        "LEGACY_THEME_KEY",
        "stripAdrRefs",
        "displayText",
        "filterExplorerItemsForPrefs",
        "applyDisplayPrefs",
        "openSettingsDialog",
        "glossary.show_relation_blocks",
        "text.hide_adr_refs",
        "navigation.hidden_roots",
    ):
        assert needle in JS, needle


def test_strip_adr_refs_real_strings():
    samples = [
        (
            "Навигация по классам и enum (renderer data-structure, ADR-016 linkml-specification).",
            "Навигация по классам и enum (renderer data-structure, linkml-specification).",
        ),
        (
            "с формальными проверками (ADR-021).",
            "с формальными проверками.",
        ),
        (
            "Glossary view: definition-site folders + flat A–Z (ADR-024/027).",
            "Glossary view: definition-site folders + flat A–Z.",
        ),
        (
            "PublicationRequirement из publication-requirements.yaml (ADR-019).",
            "PublicationRequirement из publication-requirements.yaml.",
        ),
        (
            "ADR-016/019: orphans fold into Overview",
            ": orphans fold into Overview",
        ),
        (
            "No ADR here about addresses",
            "No ADR here about addresses",
        ),
    ]
    for src, expected in samples:
        assert strip_adr_refs(src) == expected, (src, strip_adr_refs(src), expected)


def test_settings_dialog_template_exists():
    path = VIEWER_ROOT / "templates" / "components" / "settings-dialog.html.j2"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert 'id="settings-dialog"' in text
    assert "settings-reset" in text
    assert "settings-export" in text


def test_topbar_has_settings_entry():
    topbar = (VIEWER_ROOT / "templates" / "topbar.html.j2").read_text(encoding="utf-8")
    assert 'id="btn-settings"' in topbar


def test_tokens_define_palette_and_density():
    tokens = (VIEWER_ROOT / "static" / "css" / "10-tokens.css").read_text(encoding="utf-8")
    assert '[data-palette="default"]' in tokens
    assert "--class-color-plain" in tokens
    assert '[data-density="compact"]' in tokens


def test_base_html_palette_attr():
    base = (VIEWER_ROOT / "templates" / "base.html.j2").read_text(encoding="utf-8")
    assert 'data-palette="default"' in base
    assert "settings-dialog.html.j2" in base
