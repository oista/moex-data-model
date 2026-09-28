"""API tests for Stage 7b import_draft jobs."""

from __future__ import annotations

from fastapi.testclient import TestClient

from moex_model_cli.bootstrap import find_repo_root
from moex_model_cli.gates.publish_gate import refuse_generated_draft


def test_import_draft_json_schema(client: TestClient) -> None:
    root = find_repo_root()
    fixture = (
        root
        / "packages"
        / "linkml-tooling"
        / "tests"
        / "fixtures"
        / "mini.schema.json"
    )
    headers = {"X-Moex-Actor": "importer"}
    client.post(
        "/workspaces",
        json={"id": "ws-import", "name": "Import WS"},
        headers=headers,
    )
    with fixture.open("rb") as fh:
        r = client.post(
            "/workspaces/ws-import/imports",
            data={"source_type": "json_schema", "name": "MiniPerson"},
            files={"file": ("mini.schema.json", fh, "application/json")},
            headers=headers,
        )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["kind"] == "import_draft"
    assert body["status"] == "succeeded"
    job_id = body["id"]
    arts = client.get(f"/jobs/{job_id}/artifacts", headers=headers)
    assert arts.status_code == 200
    kinds = {a["kind"] for a in arts.json()}
    assert "import-inferred-schema" in kinds
    assert "import-job-json" in kinds
    inferred = next(a for a in arts.json() if a["kind"] == "import-inferred-schema")
    content = client.get(
        f"/jobs/{job_id}/artifacts/{inferred['id']}/content",
        headers=headers,
    )
    assert content.status_code == 200
    assert "name" in content.text.lower() or "MiniPerson" in content.text
    job_path = root / inferred["path_or_uri"]
    errors = refuse_generated_draft(root=root, candidate=job_path.parent)
    assert errors


def test_import_draft_rejects_oversized(client: TestClient) -> None:
    headers = {"X-Moex-Actor": "importer"}
    client.post(
        "/workspaces",
        json={"id": "ws-import-big", "name": "Big"},
        headers=headers,
    )
    big = b"x" * (2 * 1024 * 1024 + 1)
    r = client.post(
        "/workspaces/ws-import-big/imports",
        data={"source_type": "json_schema"},
        files={"file": ("big.json", big, "application/json")},
        headers=headers,
    )
    assert r.status_code == 413
