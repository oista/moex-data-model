from __future__ import annotations

import sys
from pathlib import Path

import pytest

if sys.version_info < (3, 11):
    pytest.exit(
        "moex-standard-linkml requires Python 3.11+. "
        "On this machine use: py -3.14 -m venv packages/standard-linkml/.venv "
        "then packages/standard-linkml/.venv/Scripts/python -m pytest … "
        "or: powershell -File packages/standard-linkml/scripts/check.ps1",
        returncode=2,
    )

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
