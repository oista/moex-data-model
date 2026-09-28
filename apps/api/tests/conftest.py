"""Shared API test fixtures."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from moex_model_api.app import create_app


@pytest.fixture()
def client() -> TestClient:
    with TestClient(create_app(database_url="sqlite:///:memory:")) as c:
        yield c
