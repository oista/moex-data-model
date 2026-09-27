from __future__ import annotations

import sys
from pathlib import Path

import pytest

if sys.version_info < (3, 11):
    pytest.exit("moex-publication requires Python 3.11+.", returncode=2)

REPO_ROOT = Path(__file__).resolve().parents[3]
DAMS_SCHEMA = REPO_ROOT / "model_src" / "schemas" / "moex-dams.yaml"
TRADING = REPO_ROOT / "model_src" / "examples" / "trading-solution-model.yaml"


@pytest.fixture
def dams_schema() -> Path:
    return DAMS_SCHEMA


@pytest.fixture
def trading_solution() -> Path:
    return TRADING
