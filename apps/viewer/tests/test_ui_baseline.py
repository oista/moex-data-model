"""UI baseline contract — do not regenerate fixtures when redesigning; compare behavior."""

from pathlib import Path

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "ui-baseline"


def test_ui_baseline_fixtures_exist():
    assert (FIXTURE / "viewer.css").is_file()
    assert (FIXTURE / "viewer.js").is_file()
    assert (FIXTURE / "base.html.j2").is_file()
    assert (FIXTURE / "MANIFEST.txt").is_file()
    manifest = (FIXTURE / "MANIFEST.txt").read_text(encoding="utf-8")
    assert "HAS_SIDEBAR=True" in manifest
    assert "HAS_SEARCH=True" in manifest
    assert "HAS_THEME=True" in manifest


def test_ui_baseline_had_player_branding():
    """Pre-Atlas shell used Data Specification Player (historical fixture)."""
    base = (FIXTURE / "base.html.j2").read_text(encoding="utf-8")
    assert "Data Specification Player" in base
    assert "global-search" in base
    assert "btn-theme" in base
    assert "btn-expand" in base
    assert "btn-copy-link" in base


def test_ui_baseline_css_had_blue_accent():
    css = (FIXTURE / "viewer.css").read_text(encoding="utf-8")
    assert "--accent: #1f6feb" in css
    assert ".nav-group-children[hidden]" in css


def test_ui_baseline_js_had_core_behaviors():
    js = (FIXTURE / "viewer.js").read_text(encoding="utf-8")
    for needle in (
        "runSearch",
        "renderYamlFold",
        "navigateToNode",
        "btn-theme",
        "walkExplorerItems",
        "rootSpecifications",
    ):
        assert needle in js
