"""ADR-051: aggregate schema version must appear in SCHEMA-VERSION-TIMELINE.md."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
SCHEMA = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "schemas"
    / "moex-dams.yaml"
)
TIMELINE = REPO / "docs" / "migration" / "SCHEMA-VERSION-TIMELINE.md"

_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def _aggregate_version() -> str:
    data = yaml.safe_load(SCHEMA.read_text(encoding="utf-8")) or {}
    version = data.get("version")
    assert isinstance(version, str) and _SEMVER.match(version), version
    return version


def _timeline_versions() -> set[str]:
    text = TIMELINE.read_text(encoding="utf-8")
    # Table rows: | 5.1.0 | ... |
    found = set(re.findall(r"^\|\s*(\d+\.\d+\.\d+)\s*\|", text, flags=re.MULTILINE))
    assert found, "no aggregate versions found in timeline table"
    return found


def test_current_aggregate_version_has_timeline_row() -> None:
    version = _aggregate_version()
    versions = _timeline_versions()
    assert version in versions, (
        f"aggregate moex-dams.yaml version {version} missing from "
        f"{TIMELINE.relative_to(REPO)}; add a row per ADR-051 D6"
    )


def test_timeline_lists_source_of_truth_path() -> None:
    text = TIMELINE.read_text(encoding="utf-8")
    assert "moex-dams.yaml" in text
    assert "ADR-051" in text
