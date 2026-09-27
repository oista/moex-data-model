from __future__ import annotations

import sys
from pathlib import Path

import pytest

if sys.version_info < (3, 11):
    pytest.exit("moex-model-cli requires Python 3.11+.", returncode=2)

REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT
