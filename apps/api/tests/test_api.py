"""API smoke tests (SQLite in-memory)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from moex_model_api.app import create_app


@pytest.fixture()
def client() -> TestClient:
    with TestClient(create_app(database_url="sqlite:///:memory:")) as c:
        yield c


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_trading_conformance(client: TestClient) -> None:
    r = client.get("/implementations/trading/conformance")
    assert r.status_code == 200
    body = r.json()
    assert body["is_conformant"] is True
    assert body["overall_result"] == "conformant"


def test_validation_run_persisted(client: TestClient) -> None:
    r = client.post(
        "/validation-runs",
        json={"implementation_id": "moex:implementation:trading:1.0.0"},
        headers={"X-Moex-Actor": "tester"},
    )
    assert r.status_code == 200
    run_id = r.json()["id"]
    g = client.get(f"/validation-runs/{run_id}")
    assert g.status_code == 200
    assert g.json()["overall_result"] == "conformant"
