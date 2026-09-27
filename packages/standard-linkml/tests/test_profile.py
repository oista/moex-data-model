from __future__ import annotations

from pathlib import Path

from moex_standard_linkml.ingest.profile import load_profile

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PROFILE = PACKAGE_ROOT / "templates" / "er-dictionary.profile.yaml"


def test_load_fixture_profile(fixture_profile_path: Path) -> None:
    profile = load_profile(fixture_profile_path)
    assert profile.solution_slug == "pilot"
    assert profile.sheets.entities.sheet == "Entities"
    assert profile.map_type("VARCHAR") == "string"
    assert profile.map_type("uuid") == "identifier"
    assert profile.map_type("UNKNOWN") == "string"
    assert profile.map_type(None, is_pk=True) == "identifier"


def test_load_template_profile() -> None:
    profile = load_profile(TEMPLATE_PROFILE)
    assert profile.name == "er-dictionary"
    assert "VARCHAR" in profile.type_map
