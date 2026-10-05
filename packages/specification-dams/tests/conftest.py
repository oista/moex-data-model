from __future__ import annotations

import sys
from pathlib import Path

import pytest

if sys.version_info < (3, 11):
    pytest.exit(
        "moex-specification-dams requires Python 3.11+.",
        returncode=2,
    )

REPO_ROOT = Path(__file__).resolve().parents[3]
DAMS_SCHEMA = (
    REPO_ROOT
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "schemas"
    / "moex-dams.yaml"
)
MDM = (
    REPO_ROOT
    / "model-assets"
    / "implementations"
    / "solutions"
    / "mdm"
    / "mdm-solution-model.yaml"
)


@pytest.fixture
def dams_schema() -> Path:
    assert DAMS_SCHEMA.is_file()
    return DAMS_SCHEMA


@pytest.fixture
def mdm_solution() -> Path:
    assert MDM.is_file()
    return MDM
