"""API smoke tests (SQLite in-memory)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from moex_git import LocalGitProvider
from moex_model_api.app import create_app

MDM_ID = "moex:implementation:mdm:0.1.0"
MDM_SLUG = "mdm"


@pytest.fixture()
def client() -> TestClient:
    with TestClient(create_app(database_url="sqlite:///:memory:")) as c:
        yield c


@pytest.fixture()
def temp_git_repo(tmp_path: Path) -> Path:
    root = tmp_path / "gitrepo"
    root.mkdir()
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    (root / "README.md").write_text("init\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return root


@pytest.fixture()
def publish_client(temp_git_repo: Path) -> TestClient:
    git = LocalGitProvider(temp_git_repo)
    with TestClient(
        create_app(database_url="sqlite:///:memory:", git_provider=git)
    ) as c:
        yield c


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_list_implementations(client: TestClient) -> None:
    r = client.get("/implementations")
    assert r.status_code == 200
    body = r.json()
    assert len(body) >= 5
    by_slug = {row["slug"]: row for row in body}
    assert "mdm" in by_slug
    assert by_slug["mdm"]["id"] == MDM_ID
    assert "mdm" in by_slug["mdm"]["implementation_path"]
    assert by_slug["mdm"]["workbench_editable"] is True


def test_mdm_conformance(client: TestClient) -> None:
    r = client.get("/implementations/mdm/conformance")
    assert r.status_code == 200
    body = r.json()
    assert body["is_conformant"] is True
    assert body["overall_result"] == "conformant_with_warnings"


def test_validation_run_persisted(client: TestClient) -> None:
    r = client.post(
        "/validation-runs",
        json={"implementation_id": "moex:implementation:mdm:0.1.0"},
        headers={"X-Moex-Actor": "tester"},
    )
    assert r.status_code == 200
    run_id = r.json()["id"]
    g = client.get(f"/validation-runs/{run_id}")
    assert g.status_code == 200
    assert g.json()["overall_result"] == "conformant_with_warnings"


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
        "implementation_id": "moex:implementation:mdm:0.1.0",
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


def test_compile_job_lists_and_previews_artifacts(client: TestClient) -> None:
    headers = {
        "X-Moex-Actor": "compiler",
        "Idempotency-Key": "idem-compile-art-1",
    }
    r = client.post(
        "/jobs",
        json={
            "kind": "compile",
            "workspace_id": "ws-compile",
            "implementation_id": "moex:implementation:mdm:0.1.0",
            "source": "published",
        },
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["status"] == "succeeded"
    job_id = r.json()["id"]

    arts = client.get(
        f"/jobs/{job_id}/artifacts",
        headers={"X-Moex-Actor": "compiler"},
    )
    assert arts.status_code == 200
    items = arts.json()
    assert len(items) >= 1
    assert items[0]["kind"] == "pydantic-contracts"
    art_id = items[0]["id"]

    content = client.get(
        f"/jobs/{job_id}/artifacts/{art_id}/content",
        headers={"X-Moex-Actor": "compiler"},
    )
    assert content.status_code == 200
    assert "directory:" in content.text or "class " in content.text


def test_mdm_body(client: TestClient) -> None:
    r = client.get("/implementations/mdm/body")
    assert r.status_code == 200
    body = r.json()
    assert "element_id:" in body["content"]
    assert body["content_digest"].startswith("sha256:")
    assert "mdm" in body["path"]


def test_document_mutations_seed_and_conflict(client: TestClient) -> None:
    headers = {"X-Moex-Actor": "mutator"}
    published_path = client.get("/implementations/mdm/body").json()["path"]
    from moex_model_cli.bootstrap import find_repo_root

    pub_file = find_repo_root() / published_path
    before = pub_file.read_text(encoding="utf-8")

    r = client.post(
        "/workspaces/ws-mut/documents/mdm/mutations",
        json={
            "op": "add_logical_entity",
            "entity": {
                "element_id": "dams:logical/mdm/OrderBook",
                "name": "OrderBook",
                "title": "Order book",
            },
        },
        headers=headers,
    )
    assert r.status_code == 200
    assert "dams:logical/mdm/OrderBook" in r.json()["content"]

    attr = client.post(
        "/workspaces/ws-mut/documents/mdm/mutations",
        json={
            "op": "add_logical_attribute",
            "owner_element_id": "dams:logical/mdm/ENTERPRISE",
            "attribute": {
                "element_id": "dams:logical/mdm/ENTERPRISE/nickname",
                "name": "nickname",
                "data_type_ref": "dams:datatype/string",
                "required": False,
            },
        },
        headers=headers,
    )
    assert attr.status_code == 200
    assert "dams:logical/mdm/ENTERPRISE/nickname" in attr.json()["content"]

    dup = client.post(
        "/workspaces/ws-mut/documents/mdm/mutations",
        json={
            "op": "add_logical_entity",
            "entity": {
                "element_id": "dams:logical/mdm/OrderBook",
                "name": "OrderBook2",
            },
        },
        headers=headers,
    )
    assert dup.status_code == 409

    after = pub_file.read_text(encoding="utf-8")
    assert after == before

    job = client.post(
        "/jobs",
        json={
            "kind": "validate",
            "workspace_id": "ws-mut",
            "implementation_id": "moex:implementation:mdm:0.1.0",
            "source": "draft",
        },
        headers={**headers, "Idempotency-Key": "idem-mut-validate"},
    )
    assert job.status_code == 200
    assert job.json()["status"] == "succeeded"


def test_document_mutations_update_and_delete(client: TestClient) -> None:
    headers = {"X-Moex-Actor": "mutator-edit"}
    upd = client.post(
        "/workspaces/ws-mut-edit/documents/mdm/mutations",
        json={
            "op": "update_logical_entity",
            "element_id": "dams:logical/mdm/ENTERPRISE",
            "patch": {"title": "Client (edited)"},
        },
        headers=headers,
    )
    assert upd.status_code == 200
    assert "Client (edited)" in upd.json()["content"]

    del_attr = client.post(
        "/workspaces/ws-mut-edit/documents/mdm/mutations",
        json={
            "op": "delete_logical_attribute",
            "element_id": "dams:logical/mdm/ENTERPRISE/SHORT_NAME",
        },
        headers=headers,
    )
    assert del_attr.status_code == 200
    # Attribute body gone; mapping rows may still mention the id as a ref.
    assert (
        "element_id: dams:logical/mdm/ENTERPRISE/SHORT_NAME\n"
        not in del_attr.json()["content"]
    )

    del_ent = client.post(
        "/workspaces/ws-mut-edit/documents/mdm/mutations",
        json={
            "op": "delete_logical_entity",
            "element_id": "dams:logical/mdm/ENTERPRISE",
        },
        headers=headers,
    )
    assert del_ent.status_code == 200
    assert "element_id: dams:logical/mdm/ENTERPRISE\n" not in del_ent.json()["content"]

    missing = client.post(
        "/workspaces/ws-mut-edit/documents/mdm/mutations",
        json={
            "op": "update_logical_entity",
            "element_id": "dams:logical/mdm/Missing",
            "patch": {"name": "X"},
        },
        headers=headers,
    )
    assert missing.status_code == 400


def test_document_mutations_relationship_and_mapping(client: TestClient) -> None:
    headers = {"X-Moex-Actor": "mutator-rel"}
    rel = client.post(
        "/workspaces/ws-mut-rel/documents/mdm/mutations",
        json={
            "op": "add_relationship",
            "relationship": {
                "element_id": "dams:rel/mdm/ENTERPRISE-Self",
                "name": "client_self",
                "description": "Self ref for test",
                "lifecycle_status": "draft",
                "source_entity_ref": "dams:logical/mdm/ENTERPRISE",
                "target_entity_ref": "dams:logical/mdm/ENTERPRISE",
            },
        },
        headers=headers,
    )
    assert rel.status_code == 200
    assert "dams:rel/mdm/ENTERPRISE-Self" in rel.json()["content"]

    upd_rel = client.post(
        "/workspaces/ws-mut-rel/documents/mdm/mutations",
        json={
            "op": "update_relationship",
            "element_id": "dams:rel/mdm/ENTERPRISE-Self",
            "patch": {"title": "Self"},
        },
        headers=headers,
    )
    assert upd_rel.status_code == 200
    assert "title: Self" in upd_rel.json()["content"]

    mapping = client.post(
        "/workspaces/ws-mut-rel/documents/mdm/mutations",
        json={
            "op": "add_mapping",
            "mapping": {
                "element_id": "dams:mapping/mdm/wb-test",
                "name": "map_wb_test",
                "description": "Workbench test mapping",
                "lifecycle_status": "draft",
                "source_refs": ["dams:logical/mdm/ENTERPRISE/ENTERPRISE_ID"],
                "target_refs": ["dams:physical/mdm/client-topic/client_id"],
                "mapping_type": "field_mapping",
                "mapping_cardinality": "one_to_one",
            },
        },
        headers=headers,
    )
    assert mapping.status_code == 200
    assert "dams:mapping/mdm/wb-test" in mapping.json()["content"]

    del_map = client.post(
        "/workspaces/ws-mut-rel/documents/mdm/mutations",
        json={
            "op": "delete_mapping",
            "element_id": "dams:mapping/mdm/wb-test",
        },
        headers=headers,
    )
    assert del_map.status_code == 200
    assert "dams:mapping/mdm/wb-test" not in del_map.json()["content"]

    del_rel = client.post(
        "/workspaces/ws-mut-rel/documents/mdm/mutations",
        json={
            "op": "delete_relationship",
            "element_id": "dams:rel/mdm/ENTERPRISE-Self",
        },
        headers=headers,
    )
    assert del_rel.status_code == 200
    assert "dams:rel/mdm/ENTERPRISE-Self" not in del_rel.json()["content"]


def test_document_mutations_physical_object_and_field(client: TestClient) -> None:
    headers = {"X-Moex-Actor": "editor"}
    add_obj = client.post(
        "/workspaces/ws-mut-phys/documents/mdm/mutations",
        json={
            "op": "add_physical_object",
            "physical_object": {
                "element_id": "dams:physical/mdm/wb-orders",
                "name": "wb_orders",
                "object_kind": "table",
            },
        },
        headers=headers,
    )
    assert add_obj.status_code == 200
    assert "dams:physical/mdm/wb-orders" in add_obj.json()["content"]

    add_field = client.post(
        "/workspaces/ws-mut-phys/documents/mdm/mutations",
        json={
            "op": "add_physical_field",
            "owner_element_id": "dams:physical/mdm/wb-orders",
            "physical_field": {
                "element_id": "dams:physical/mdm/wb-orders/id",
                "name": "id",
                "native_type": "uuid",
            },
        },
        headers=headers,
    )
    assert add_field.status_code == 200
    assert "dams:physical/mdm/wb-orders/id" in add_field.json()["content"]

    upd = client.post(
        "/workspaces/ws-mut-phys/documents/mdm/mutations",
        json={
            "op": "update_physical_object",
            "element_id": "dams:physical/mdm/wb-orders",
            "patch": {"title": "WB Orders"},
        },
        headers=headers,
    )
    assert upd.status_code == 200
    assert "WB Orders" in upd.json()["content"]

    del_field = client.post(
        "/workspaces/ws-mut-phys/documents/mdm/mutations",
        json={
            "op": "delete_physical_field",
            "element_id": "dams:physical/mdm/wb-orders/id",
        },
        headers=headers,
    )
    assert del_field.status_code == 200
    assert "dams:physical/mdm/wb-orders/id" not in del_field.json()["content"]

    del_obj = client.post(
        "/workspaces/ws-mut-phys/documents/mdm/mutations",
        json={
            "op": "delete_physical_object",
            "element_id": "dams:physical/mdm/wb-orders",
        },
        headers=headers,
    )
    assert del_obj.status_code == 200
    assert "dams:physical/mdm/wb-orders" not in del_obj.json()["content"]


def test_workspace_document_put_get_and_validate_draft(client: TestClient) -> None:
    headers = {"X-Moex-Actor": "editor"}
    published = client.get("/implementations/mdm/body").json()
    content = published["content"].replace(
        "Черновой пример модели одного ИТ-решения.",
        "Черновой пример модели одного ИТ-решения (draft).",
        1,
    )
    put = client.put(
        "/workspaces/ws-edit/documents/mdm",
        json={"content": content, "base_digest": published["content_digest"]},
        headers=headers,
    )
    assert put.status_code == 200
    assert "draft" in put.json()["content"]

    got = client.get(
        "/workspaces/ws-edit/documents/mdm",
        headers=headers,
    )
    assert got.status_code == 200
    assert got.json()["content"] == content

    missing = client.get(
        "/workspaces/ws-missing/documents/mdm",
        headers=headers,
    )
    assert missing.status_code == 404

    job = client.post(
        "/jobs",
        json={
            "kind": "validate",
            "workspace_id": "ws-edit",
            "implementation_id": "moex:implementation:mdm:0.1.0",
            "source": "draft",
        },
        headers={**headers, "Idempotency-Key": "idem-draft-1"},
    )
    assert job.status_code == 200
    assert job.json()["status"] == "succeeded"
    assert "source=draft" in job.json()["result_summary"]


def test_semantic_diff_preview_identical_and_breaking(client: TestClient) -> None:
    headers = {"X-Moex-Actor": "diff-user"}
    missing = client.post(
        "/workspaces/ws-diff-missing/documents/mdm/semantic-diff",
        headers=headers,
    )
    assert missing.status_code == 400
    assert "draft" in missing.json()["detail"]

    published = client.get("/implementations/mdm/body").json()
    put = client.put(
        "/workspaces/ws-diff/documents/mdm",
        json={
            "content": published["content"],
            "base_digest": published["content_digest"],
        },
        headers=headers,
    )
    assert put.status_code == 200

    identical = client.post(
        "/workspaces/ws-diff/documents/mdm/semantic-diff",
        headers=headers,
    )
    assert identical.status_code == 200
    body = identical.json()
    assert body["base_label"] == "published"
    assert body["target_label"] == "draft:ws-diff"
    assert body["has_breaking"] is False
    assert body["changes"] == []
    assert body["counts"]["breaking"] == 0

    deleted = client.post(
        "/workspaces/ws-diff/documents/mdm/mutations",
        json={
            "op": "delete_logical_attribute",
            "element_id": "dams:logical/mdm/ENTERPRISE/SHORT_NAME",
        },
        headers=headers,
    )
    assert deleted.status_code == 200

    breaking = client.post(
        "/workspaces/ws-diff/documents/mdm/semantic-diff",
        headers=headers,
    )
    assert breaking.status_code == 200
    report = breaking.json()
    assert report["has_breaking"] is True
    assert report["counts"]["breaking"] >= 1
    codes = {c["change_code"] for c in report["changes"]}
    assert "DAMS-DIFF-REMOVE" in codes
    subjects = {c["subject_ref"] for c in report["changes"]}
    assert "dams:logical/mdm/ENTERPRISE/SHORT_NAME" in subjects


def test_publication_from_draft_idempotent(
    publish_client: TestClient, temp_git_repo: Path
) -> None:
    headers = {"X-Moex-Actor": "publisher"}
    published = publish_client.get("/implementations/mdm/body").json()
    put = publish_client.put(
        "/workspaces/ws-pub/documents/mdm",
        json={
            "content": published["content"],
            "base_digest": published["content_digest"],
        },
        headers=headers,
    )
    assert put.status_code == 200

    payload = {
        "workspace_id": "ws-pub",
        "implementation_id": "moex:implementation:mdm:0.1.0",
        "title": "Publish MDM",
        "base_ref": "HEAD",
    }
    r1 = publish_client.post(
        "/publications",
        json=payload,
        headers={**headers, "Idempotency-Key": "idem-pub-1"},
    )
    assert r1.status_code == 200, r1.text
    body = r1.json()
    assert body["status"] == "submitted"
    assert body["commit_sha"]
    assert body["review_url"].startswith("local://review/")
    assert body["branch_name"].startswith("workbench/publish-")

    # File written only in temp repo, not necessarily under real model-assets path
    written = list(temp_git_repo.rglob("*.yaml"))
    assert written

    r2 = publish_client.post(
        "/publications",
        json=payload,
        headers={**headers, "Idempotency-Key": "idem-pub-1"},
    )
    assert r2.status_code == 200
    assert r2.json()["id"] == body["id"]

    got = publish_client.get(
        f"/publications/{body['id']}",
        headers=headers,
    )
    assert got.status_code == 200
    assert got.json()["commit_sha"] == body["commit_sha"]


def test_publication_gate_rejects_bad_digest(
    publish_client: TestClient,
) -> None:
    """Broken golden digest must fail-closed before Git publish."""
    from moex_model_cli.bootstrap import find_repo_root
    from moex_model_cli.gates.digests import artifact_paths

    headers = {"X-Moex-Actor": "publisher"}
    published = publish_client.get("/implementations/mdm/body").json()
    put = publish_client.put(
        "/workspaces/ws-gate/documents/mdm",
        json={
            "content": published["content"],
            "base_digest": published["content_digest"],
        },
        headers=headers,
    )
    assert put.status_code == 200

    paths = artifact_paths(find_repo_root())
    manifest = paths["python_manifest"]
    orig = manifest.read_text(encoding="utf-8")
    data = json.loads(orig)
    data["content_digest"] = "sha256:" + ("0" * 64)
    manifest.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    try:
        r = publish_client.post(
            "/publications",
            json={
                "workspace_id": "ws-gate",
                "implementation_id": "moex:implementation:mdm:0.1.0",
                "title": "Should fail gate",
                "base_ref": "HEAD",
            },
            headers={**headers, "Idempotency-Key": "idem-gate-fail"},
        )
        assert r.status_code == 422, r.text
        detail = r.json()["detail"]
        assert detail["message"] == "publish-gate failed"
        assert any("digest mismatch" in e for e in detail["errors"])
    finally:
        manifest.write_text(orig, encoding="utf-8")


def test_model_index_rebuild_and_search(client: TestClient) -> None:
    headers = {"X-Moex-Actor": "carol"}
    r = client.post(
        "/model-index/rebuild",
        params={"implementation_id": MDM_ID},
        headers=headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["element_count"] > 0
    assert body["implementation_id"] == MDM_ID

    search = client.get(
        "/model-index/search",
        params={"q": "ENTERPRISE", "implementation_id": MDM_ID},
        headers=headers,
    )
    assert search.status_code == 200
    hits = search.json()
    assert hits
    assert any(
        "ENTERPRISE" in h["element_id"] or "ENTERPRISE" in h["name"] for h in hits
    )
    assert all(h["implementation_id"] == MDM_ID for h in hits)


def test_diagram_open_submit_apply(client: TestClient) -> None:
    headers = {"X-Moex-Actor": "diagrammer"}
    client.post(
        "/workspaces",
        json={"id": "ws-diagram", "name": "Diagram WS"},
        headers=headers,
    )
    pub = client.get("/implementations/mdm/body", headers=headers)
    assert pub.status_code == 200
    content = pub.json()["content"]
    client.put(
        "/workspaces/ws-diagram/documents/mdm",
        json={"content": content, "base_digest": pub.json()["content_digest"]},
        headers=headers,
    )

    opened = client.post(
        "/workspaces/ws-diagram/diagrams",
        json={"implementation_id": MDM_ID, "profile": "logical"},
        headers=headers,
    )
    assert opened.status_code == 200, opened.text
    session_id = opened.json()["session_id"]
    dbml = opened.json()["dbml"]
    assert "Table" in dbml

    marker = None
    for line in dbml.splitlines():
        stripped = line.strip()
        # column line with note setting (not Table/Project Note:)
        if (
            "note:" in stripped.lower()
            and not stripped.lower().startswith("note:")
            and " " in stripped
        ):
            marker = line
            break
    assert marker is not None
    dbml2 = dbml.replace(marker, marker + "\n  diagramExtra string", 1)

    submitted = client.post(
        f"/workspaces/ws-diagram/diagrams/{session_id}/submit",
        json={"dbml": dbml2},
        headers=headers,
    )
    assert submitted.status_code == 200, submitted.text
    body = submitted.json()
    assert body["op_count"] >= 1
    assert body["rejected"] == []

    applied = client.post(
        f"/workspaces/ws-diagram/diagrams/{session_id}/apply",
        headers=headers,
    )
    assert applied.status_code == 200, applied.text
    assert "diagramExtra" in applied.json()["content"]

    layout = client.put(
        f"/workspaces/ws-diagram/diagrams/{session_id}/layout",
        json={
            "nodes": {"dams:logical/x": {"x": 1, "y": 2}},
            "model_revision": "draft",
        },
        headers=headers,
    )
    assert layout.status_code == 200
    assert layout.json()["nodes"]["dams:logical/x"]["x"] == 1


def test_diagram_reject_element_id_strip(client: TestClient) -> None:
    import re

    headers = {"X-Moex-Actor": "diagrammer2"}
    client.post(
        "/workspaces",
        json={"id": "ws-diagram2", "name": "Diagram WS2"},
        headers=headers,
    )
    pub = client.get("/implementations/mdm/body", headers=headers)
    content = pub.json()["content"]
    client.put(
        "/workspaces/ws-diagram2/documents/mdm",
        json={"content": content, "base_digest": pub.json()["content_digest"]},
        headers=headers,
    )
    opened = client.post(
        "/workspaces/ws-diagram2/diagrams",
        json={"implementation_id": MDM_ID, "profile": "logical"},
        headers=headers,
    )
    dbml = opened.json()["dbml"]
    session_id = opened.json()["session_id"]
    bad = re.sub(r"element_id=[^;'\s]+;?\s*", "", dbml, count=1)
    submitted = client.post(
        f"/workspaces/ws-diagram2/diagrams/{session_id}/submit",
        json={"dbml": bad},
        headers=headers,
    )
    assert submitted.status_code == 200
    if submitted.json()["rejected"]:
        applied = client.post(
            f"/workspaces/ws-diagram2/diagrams/{session_id}/apply",
            headers=headers,
        )
        assert applied.status_code == 400
