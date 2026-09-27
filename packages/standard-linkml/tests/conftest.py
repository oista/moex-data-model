from __future__ import annotations

from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "er-dictionary"
REPO_ROOT = Path(__file__).resolve().parents[3]
DAMS_SCHEMA = REPO_ROOT / "model_src" / "schemas" / "moex-dams.yaml"


@pytest.fixture
def fixture_dir() -> Path:
    return FIXTURE_DIR


@pytest.fixture
def fixture_profile_path() -> Path:
    return FIXTURE_DIR / "profile.yaml"


@pytest.fixture
def dams_schema() -> Path:
    assert DAMS_SCHEMA.is_file(), f"Missing DAMS schema: {DAMS_SCHEMA}"
    return DAMS_SCHEMA
