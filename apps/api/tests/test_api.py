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


def test_list_implementations(client: TestClient) -> None:
    r = client.get("/implementations")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert body[0]["slug"] == "trading"
    assert body[0]["id"] == "moex:implementation:trading:1.0.0"
    assert "trading" in body[0]["implementation_path"]


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


def test_workspace_create_and_list(client: TestClient) -> None:
    headers = {"X-Moex-Actor": "alice"}
    r = client.post(
        "/workspaces",
        json={"id": "ws-alice", "name": "Alice WS"},
        headers=headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == "ws-alice"
    assert any(m["user_id"] == "alice" for m in body["members"])

    listed = client.get("/workspaces", headers=headers)
    assert listed.status_code == 200
    assert any(w["id"] == "ws-alice" for w in listed.json())

    one = client.get("/workspaces/ws-alice", headers=headers)
    assert one.status_code == 200
    assert one.json()["name"] == "Alice WS"


def test_job_validate_idempotent(client: TestClient) -> None:
    headers = {
        "X-Moex-Actor": "bob",
        "Idempotency-Key": "idem-validate-1",
    }
    payload = {
        "kind": "validate",
        "workspace_id": "ws-bob",
        "implementation_id": "moex:implementation:trading:1.0.0",
    }
    r1 = client.post("/jobs", json=payload, headers=headers)
    assert r1.status_code == 200
    assert r1.json()["status"] == "succeeded"
    job_id = r1.json()["id"]

    r2 = client.post("/jobs", json=payload, headers=headers)
    assert r2.status_code == 200
    assert r2.json()["id"] == job_id

    conflict = client.post(
        "/jobs",
        json={**payload, "kind": "compile"},
        headers=headers,
    )
    assert conflict.status_code == 409

    got = client.get(f"/jobs/{job_id}", headers={"X-Moex-Actor": "bob"})
    assert got.status_code == 200
    assert got.json()["status"] == "succeeded"


def test_model_index_rebuild_and_search(client: TestClient) -> None:
    headers = {"X-Moex-Actor": "carol"}
    r = client.post("/model-index/rebuild", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["element_count"] > 0

    search = client.get("/model-index/search", params={"q": "Client"}, headers=headers)
    assert search.status_code == 200
    hits = search.json()
    assert hits
    assert any("Client" in h["element_id"] or "Client" in h["name"] for h in hits)
