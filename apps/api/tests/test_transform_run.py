"""API tests for Workbench map/transform catalog + run."""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from moex_model_cli.bootstrap import find_repo_root


def test_list_transforms_catalog(client: TestClient) -> None:
    headers = {"X-Moex-Actor": "mapper"}
    client.post(
        "/workspaces",
        json={"id": "ws-map", "name": "Map WS"},
        headers=headers,
    )
    r = client.get("/workspaces/ws-map/transforms", headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    rels = {s["rel_path"] for s in body["specs"]}
    assert "person-identity.yaml" in rels
    assert "dams-logical-entity-rename-kind.yaml" in rels
    sample_rels = {s["rel_path"] for s in body["samples"]}
    assert "samples/dams_logical_entity_sample.json" in sample_rels


def test_preview_bundled_sample_rename_kind(client: TestClient) -> None:
    headers = {"X-Moex-Actor": "mapper"}
    client.post(
        "/workspaces",
        json={"id": "ws-map-prev", "name": "Map Prev"},
        headers=headers,
    )
    r = client.post(
        "/workspaces/ws-map-prev/transforms/run",
        data={
            "spec_rel": "dams-logical-entity-rename-kind.yaml",
            "mode": "preview",
            "backend": "object",
            "sample_rel": "samples/dams_logical_entity_sample.json",
        },
        headers=headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["mode"] == "preview"
    assert body["backend"] == "object"
    payload = body["preview_payload"] or {}
    assert payload.get("name") == "TradeOrder"
    assert payload.get("logical_entity_kind") == "core"
    assert "entity_type" not in payload
    assert any("entity_type" in s or "logical_type" in s for s in body["lost_semantics"]) or (
        "LogicalEntity.entity_type" in body["lost_semantics"]
    )


def test_sample_upload_person_identity(client: TestClient) -> None:
    headers = {"X-Moex-Actor": "mapper"}
    client.post(
        "/workspaces",
        json={"id": "ws-map-up", "name": "Map Up"},
        headers=headers,
    )
    root = find_repo_root()
    sample = (
        root
        / "packages"
        / "linkml-tooling"
        / "tests"
        / "fixtures"
        / "person_sample.json"
    )
    with sample.open("rb") as fh:
        r = client.post(
            "/workspaces/ws-map-up/transforms/run",
            data={
                "spec_rel": "person-identity.yaml",
                "mode": "sample",
                "backend": "object",
            },
            files={"file": ("person_sample.json", fh, "application/json")},
            headers=headers,
        )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["mode"] == "sample"
    assert body["output"] is not None
    assert body["output"].get("name") == "Ada"
    assert body["preview_payload"] is None


def test_path_traversal_rejected(client: TestClient) -> None:
    headers = {"X-Moex-Actor": "mapper"}
    client.post(
        "/workspaces",
        json={"id": "ws-map-trav", "name": "Map Trav"},
        headers=headers,
    )
    r = client.post(
        "/workspaces/ws-map-trav/transforms/run",
        data={
            "spec_rel": "../schemas/moex-dams.yaml",
            "mode": "preview",
            "backend": "object",
            "sample_rel": "samples/dams_logical_entity_sample.json",
        },
        headers=headers,
    )
    assert r.status_code == 400, r.text

    r2 = client.post(
        "/workspaces/ws-map-trav/transforms/run",
        data={
            "spec_rel": "person-identity.yaml",
            "mode": "preview",
            "backend": "object",
            "sample_rel": "samples/../../README.md",
        },
        headers=headers,
    )
    assert r2.status_code == 400, r2.text


def test_sql_backend_identity(client: TestClient) -> None:
    headers = {"X-Moex-Actor": "mapper"}
    client.post(
        "/workspaces",
        json={"id": "ws-map-sql", "name": "Map SQL"},
        headers=headers,
    )
    r = client.post(
        "/workspaces/ws-map-sql/transforms/run",
        data={
            "spec_rel": "dams-logical-entity-identity.yaml",
            "mode": "sample",
            "backend": "sql",
            "sample_rel": "samples/dams_logical_entity_sample.json",
        },
        headers=headers,
    )
    if r.status_code == 503:
        return
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["backend"] == "sql"
    assert body["output"] is not None
    assert body["output"].get("name") == "TradeOrder"


def test_rejects_both_or_neither_sample(client: TestClient) -> None:
    headers = {"X-Moex-Actor": "mapper"}
    client.post(
        "/workspaces",
        json={"id": "ws-map-xor", "name": "Map Xor"},
        headers=headers,
    )
    r = client.post(
        "/workspaces/ws-map-xor/transforms/run",
        data={
            "spec_rel": "person-identity.yaml",
            "mode": "preview",
            "backend": "object",
        },
        headers=headers,
    )
    assert r.status_code == 400, r.text

    sample = json.dumps({"name": "Ada", "legacy_code": "L1"}).encode()
    r2 = client.post(
        "/workspaces/ws-map-xor/transforms/run",
        data={
            "spec_rel": "person-identity.yaml",
            "mode": "preview",
            "backend": "object",
            "sample_rel": "samples/dams_logical_entity_sample.json",
        },
        files={"file": ("x.json", sample, "application/json")},
        headers=headers,
    )
    assert r2.status_code == 400, r2.text
