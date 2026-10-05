"""Data-driven Workbench contract suite over all editable catalog assets."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from moex_dams.application.assess import assess_implementation
from moex_git import LocalGitProvider
from moex_model_api.app import create_app
from moex_model_api.implementation_support import (
    is_workbench_editable,
    paths_for_asset,
)
from moex_model_cli.asset_registry import FilesystemImplementationCatalog
from moex_model_cli.bootstrap import find_repo_root
from moex_modeling import ImplementationAsset

REQUIRED_SOLUTION_SLUGS = frozenset({"trading", "mdm", "ucd", "crm", "esed"})


@pytest.fixture(scope="module")
def catalog() -> FilesystemImplementationCatalog:
    return FilesystemImplementationCatalog(find_repo_root())


def _solution_assets() -> list[ImplementationAsset]:
    catalog = FilesystemImplementationCatalog(find_repo_root())
    return [
        a
        for a in catalog.list()
        if is_workbench_editable(a) and a.dams_model_level == "solution"
    ]


@pytest.fixture(scope="module")
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


def test_required_solution_slugs_present(
    catalog: FilesystemImplementationCatalog,
) -> None:
    slugs = {a.slug for a in catalog.list()}
    assert REQUIRED_SOLUTION_SLUGS <= slugs


def test_unknown_implementation_404(client: TestClient) -> None:
    r = client.get("/implementations/no-such-impl/body")
    assert r.status_code == 404


def test_job_requires_implementation_id(client: TestClient) -> None:
    r = client.post(
        "/jobs",
        json={"kind": "validate", "workspace_id": "ws-x"},
        headers={"X-Moex-Actor": "t"},
    )
    assert r.status_code == 422


@pytest.mark.parametrize(
    "asset",
    [pytest.param(a, id=a.slug) for a in _solution_assets()],
)
class TestEditableImplementationContract:
    def test_list_and_detail_resolve(
        self, client: TestClient, asset: ImplementationAsset
    ) -> None:
        listed = client.get("/implementations")
        assert listed.status_code == 200
        by_id = {row["id"]: row for row in listed.json()}
        assert asset.id in by_id
        assert by_id[asset.id]["slug"] == asset.slug

        by_slug = client.get(f"/implementations/{asset.slug}")
        by_coord = client.get(f"/implementations/{asset.id}")
        assert by_slug.status_code == 200
        assert by_coord.status_code == 200
        assert by_slug.json()["id"] == by_coord.json()["id"] == asset.id

    def test_body_matches_disk(
        self,
        client: TestClient,
        catalog: FilesystemImplementationCatalog,
        asset: ImplementationAsset,
    ) -> None:
        r = client.get(f"/implementations/{asset.slug}/body")
        assert r.status_code == 200
        body = r.json()
        expected = catalog.load_body(asset.id)
        assert body["content"] == expected
        rel = asset.body_path.relative_to(catalog.root).as_posix()
        assert body["path"] == rel
        assert body["content_digest"].startswith("sha256:")

    def test_conformance_matches_oracle(
        self,
        client: TestClient,
        catalog: FilesystemImplementationCatalog,
        asset: ImplementationAsset,
    ) -> None:
        paths = paths_for_asset(root=catalog.root, catalog=catalog, asset=asset)
        oracle = assess_implementation(
            schema_path=paths.schema,
            implementation_path=paths.implementation,
            implementation_id=asset.id,
        )
        r = client.get(f"/implementations/{asset.slug}/conformance")
        assert r.status_code == 200
        body = r.json()
        assert body["overall_result"] == oracle.report.overall_result.value
        assert body["is_conformant"] is oracle.report.is_conformant
        assert body["implementation_id"] == asset.id

    def test_document_round_trip(
        self, client: TestClient, asset: ImplementationAsset
    ) -> None:
        headers = {"X-Moex-Actor": f"u-{asset.slug}"}
        ws = f"ws-contract-{asset.slug}"
        published = client.get(f"/implementations/{asset.slug}/body").json()
        put = client.put(
            f"/workspaces/{ws}/documents/{asset.slug}",
            json={
                "content": published["content"],
                "base_digest": published["content_digest"],
            },
            headers=headers,
        )
        assert put.status_code == 200
        assert put.json()["doc_key"] == asset.id

        got = client.get(
            f"/workspaces/{ws}/documents/{asset.id}",
            headers=headers,
        )
        assert got.status_code == 200
        assert got.json()["doc_key"] == asset.id
        assert got.json()["content"] == published["content"]

    def test_mutation_add_logical_entity(
        self, client: TestClient, asset: ImplementationAsset
    ) -> None:
        headers = {"X-Moex-Actor": f"mut-{asset.slug}"}
        ws = f"ws-mut-{asset.slug}"
        eid = f"dams:logical/{asset.slug}/ContractSpikeEntity"
        r = client.post(
            f"/workspaces/{ws}/documents/{asset.slug}/mutations",
            json={
                "op": "add_logical_entity",
                "entity": {"element_id": eid, "name": "ContractSpikeEntity"},
            },
            headers=headers,
        )
        assert r.status_code == 200, r.text
        assert eid in r.json()["content"]
        assert r.json()["doc_key"] == asset.id

    def test_semantic_diff_unmodified_not_breaking(
        self, client: TestClient, asset: ImplementationAsset
    ) -> None:
        headers = {"X-Moex-Actor": f"diff-{asset.slug}"}
        ws = f"ws-diff-{asset.slug}"
        published = client.get(f"/implementations/{asset.slug}/body").json()
        client.put(
            f"/workspaces/{ws}/documents/{asset.slug}",
            json={
                "content": published["content"],
                "base_digest": published["content_digest"],
            },
            headers=headers,
        )
        r = client.post(
            f"/workspaces/{ws}/documents/{asset.slug}/semantic-diff",
            headers=headers,
        )
        assert r.status_code == 200
        assert r.json()["has_breaking"] is False

    def test_validate_job_canonical_id(
        self, client: TestClient, asset: ImplementationAsset
    ) -> None:
        headers = {"X-Moex-Actor": f"job-{asset.slug}"}
        ws = f"ws-job-{asset.slug}"
        published = client.get(f"/implementations/{asset.slug}/body").json()
        client.put(
            f"/workspaces/{ws}/documents/{asset.slug}",
            json={
                "content": published["content"],
                "base_digest": published["content_digest"],
            },
            headers=headers,
        )
        job = client.post(
            "/jobs",
            json={
                "kind": "validate",
                "workspace_id": ws,
                "implementation_id": asset.slug,
                "source": "draft",
            },
            headers=headers,
        )
        assert job.status_code == 200, job.text
        assert job.json()["implementation_id"] == asset.id
        assert job.json()["status"] == "succeeded"

    def test_model_index_filter(
        self, client: TestClient, asset: ImplementationAsset
    ) -> None:
        headers = {"X-Moex-Actor": f"idx-{asset.slug}"}
        rebuild = client.post(
            "/model-index/rebuild",
            params={"implementation_id": asset.id},
            headers=headers,
        )
        assert rebuild.status_code == 200
        assert rebuild.json()["implementation_id"] == asset.id
        search = client.get(
            "/model-index/search",
            params={"q": "a", "implementation_id": asset.id},
            headers=headers,
        )
        assert search.status_code == 200
        for hit in search.json():
            assert hit["implementation_id"] == asset.id

    def test_diagram_layout_isolated_per_implementation(
        self, client: TestClient, asset: ImplementationAsset
    ) -> None:
        headers = {"X-Moex-Actor": f"diag-{asset.slug}"}
        ws = "ws-shared-diagram"
        published = client.get(f"/implementations/{asset.slug}/body").json()
        client.put(
            f"/workspaces/{ws}/documents/{asset.slug}",
            json={
                "content": published["content"],
                "base_digest": published["content_digest"],
            },
            headers=headers,
        )
        opened = client.post(
            f"/workspaces/{ws}/diagrams",
            json={"implementation_id": asset.id, "profile": "logical"},
            headers=headers,
        )
        assert opened.status_code == 200, opened.text
        sid = opened.json()["session_id"]
        layout = client.put(
            f"/workspaces/{ws}/diagrams/{sid}/layout",
            json={
                "nodes": {f"node-{asset.slug}": {"x": 1, "y": 2}},
                "model_revision": "draft",
            },
            headers=headers,
        )
        assert layout.status_code == 200
        assert asset.id in layout.json()["diagram_id"]
        assert f"node-{asset.slug}" in layout.json()["nodes"]

    def test_publish_oracle_gate(
        self,
        publish_client: TestClient,
        catalog: FilesystemImplementationCatalog,
        asset: ImplementationAsset,
    ) -> None:
        headers = {"X-Moex-Actor": f"pub-{asset.slug}"}
        ws = f"ws-pub-{asset.slug}"
        paths = paths_for_asset(root=catalog.root, catalog=catalog, asset=asset)
        oracle = assess_implementation(
            schema_path=paths.schema,
            implementation_path=paths.implementation,
            implementation_id=asset.id,
        )
        published = publish_client.get(
            f"/implementations/{asset.slug}/body"
        ).json()
        publish_client.put(
            f"/workspaces/{ws}/documents/{asset.slug}",
            json={
                "content": published["content"],
                "base_digest": published["content_digest"],
            },
            headers=headers,
        )
        r = publish_client.post(
            "/publications",
            json={
                "workspace_id": ws,
                "implementation_id": asset.id,
                "title": f"Publish {asset.slug}",
            },
            headers={**headers, "Idempotency-Key": f"pub-{asset.slug}-1"},
        )
        if oracle.report.is_conformant:
            assert r.status_code == 200, r.text
            assert r.json()["implementation_id"] == asset.id
            assert r.json()["status"] == "submitted"
        else:
            assert r.status_code == 422
