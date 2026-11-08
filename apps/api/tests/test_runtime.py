"""Runtime settings for a deployed API: listen address, auth mode, models preflight."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from moex_model_api.__main__ import listen_address
from moex_model_api.app import create_app
from moex_model_api.auth import TrustedHeaderAuthMiddleware
from moex_model_api.preflight import CONTRACTS_MANIFEST_REL, check_models

MARKER_REL = Path("model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml")


def _manifest(**overrides: str) -> dict[str, str]:
    body = {
        "schema_digest": "sha256:same",
        "schema_version": "5.5.0",
        "content_digest": "sha256:contracts",
    }
    body.update(overrides)
    return body


def _write_models(root: Path, manifest: dict[str, str], *, marker: bool = True) -> None:
    if marker:
        marker_path = root / MARKER_REL
        marker_path.parent.mkdir(parents=True, exist_ok=True)
        marker_path.write_text("id: dams\n", encoding="utf-8")
    manifest_path = root / CONTRACTS_MANIFEST_REL
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")


def test_listen_address_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MOEX_API_HOST", raising=False)
    monkeypatch.delenv("MOEX_API_PORT", raising=False)
    assert listen_address() == ("127.0.0.1", 8000)


def test_listen_address_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MOEX_API_HOST", "0.0.0.0")
    monkeypatch.setenv("MOEX_API_PORT", "8100")
    assert listen_address() == ("0.0.0.0", 8100)


def test_listen_address_rejects_bad_port(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MOEX_API_PORT", "nope")
    with pytest.raises(SystemExit):
        listen_address()


def test_dev_auth_still_uses_actor_header(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MOEX_AUTH_MODE", raising=False)
    with TestClient(create_app(database_url="sqlite:///:memory:")) as client:
        response = client.get("/health", headers={"X-Moex-Actor": "alice"})
    assert response.status_code == 200


def test_trusted_header_sets_actor(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MOEX_AUTH_MODE", "trusted-header")
    app = FastAPI()
    app.add_middleware(TrustedHeaderAuthMiddleware)

    @app.get("/who")
    def who(request: Request) -> dict[str, str]:
        return {"actor": request.state.actor}

    with TestClient(app) as client:
        ok = client.get("/who", headers={"X-Remote-User": "nina"})
        missing = client.get("/who")
        forged = client.get(
            "/who",
            headers={"X-Moex-Actor": "dev", "X-Remote-User": ""},
        )
    assert ok.status_code == 200
    assert ok.json() == {"actor": "nina"}
    assert missing.status_code == 401
    assert forged.status_code == 401


def test_create_app_trusted_header_rejects_unsigned(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MOEX_AUTH_MODE", "trusted-header")
    with TestClient(create_app(database_url="sqlite:///:memory:")) as client:
        probe = client.get("/health")
        denied = client.get("/implementations")
        allowed = client.get("/implementations", headers={"X-Remote-User": "ops"})
    assert probe.status_code == 200
    assert denied.status_code == 401
    assert allowed.status_code == 200


def test_preflight_ready_when_digests_match(tmp_path: Path) -> None:
    models = tmp_path / "models"
    image = tmp_path / "image" / CONTRACTS_MANIFEST_REL
    body = _manifest()
    _write_models(models, body)
    image.parent.mkdir(parents=True)
    image.write_text(json.dumps(body), encoding="utf-8")

    report = check_models(models, image)
    assert report.status == "ready"
    assert report.marker_present is True
    assert report.contracts_match is True
    assert report.schema_version == "5.5.0"
    assert report.problems == []


def test_preflight_not_ready_without_marker(tmp_path: Path) -> None:
    models = tmp_path / "models"
    image = tmp_path / "image-manifest.json"
    body = _manifest()
    _write_models(models, body, marker=False)
    image.write_text(json.dumps(body), encoding="utf-8")

    report = check_models(models, image)
    assert report.status == "not_ready"
    assert report.marker_present is False
    assert any("marker" in problem for problem in report.problems)


def test_preflight_not_ready_when_schema_differs(tmp_path: Path) -> None:
    models = tmp_path / "models"
    image = tmp_path / "image-manifest.json"
    _write_models(models, _manifest(schema_digest="sha256:clone"))
    image.write_text(
        json.dumps(_manifest(schema_digest="sha256:image")),
        encoding="utf-8",
    )

    report = check_models(models, image)
    assert report.status == "not_ready"
    assert report.contracts_match is False
    assert any("schema_digest" in problem for problem in report.problems)


def test_ready_endpoint_uses_models_root(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    models = tmp_path / "models"
    image = tmp_path / "image" / CONTRACTS_MANIFEST_REL
    body = _manifest()
    _write_models(models, body)
    image.parent.mkdir(parents=True)
    image.write_text(json.dumps(body), encoding="utf-8")
    monkeypatch.setenv("MOEX_MODELS_ROOT", str(models))
    monkeypatch.setenv("MOEX_IMAGE_CONTRACTS_MANIFEST", str(image))
    monkeypatch.delenv("MOEX_AUTH_MODE", raising=False)

    with TestClient(create_app(database_url="sqlite:///:memory:")) as client:
        response = client.get("/ready")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["schema_version"] == "5.5.0"


def _gate(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, *, ready: bool) -> TestClient:
    models = tmp_path / "models"
    image = tmp_path / "image" / CONTRACTS_MANIFEST_REL
    if ready:
        body = _manifest()
        _write_models(models, body)
    else:
        models.mkdir()
        body = _manifest()
    image.parent.mkdir(parents=True, exist_ok=True)
    image.write_text(json.dumps(body), encoding="utf-8")
    monkeypatch.setenv("MOEX_REQUIRE_MODELS_READY", "1")
    monkeypatch.setenv("MOEX_MODELS_READY_TTL", "0")
    monkeypatch.setenv("MOEX_MODELS_ROOT", str(models))
    monkeypatch.setenv("MOEX_IMAGE_CONTRACTS_MANIFEST", str(image))
    monkeypatch.delenv("MOEX_AUTH_MODE", raising=False)
    return TestClient(create_app(database_url="sqlite:///:memory:"))


def test_ready_gate_503_when_models_empty(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    with _gate(monkeypatch, tmp_path, ready=False) as client:
        blocked = client.get("/implementations")
        health = client.get("/health")
        ready = client.get("/ready")
    assert blocked.status_code == 503
    assert blocked.json()["status"] == "not_ready"
    assert health.status_code == 200
    assert ready.status_code == 503


def test_ready_gate_503_when_schema_differs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    models = tmp_path / "models"
    image = tmp_path / "image" / CONTRACTS_MANIFEST_REL
    _write_models(models, _manifest(schema_digest="sha256:clone"))
    image.parent.mkdir(parents=True)
    image.write_text(
        json.dumps(_manifest(schema_digest="sha256:image")),
        encoding="utf-8",
    )
    monkeypatch.setenv("MOEX_REQUIRE_MODELS_READY", "1")
    monkeypatch.setenv("MOEX_MODELS_READY_TTL", "0")
    monkeypatch.setenv("MOEX_MODELS_ROOT", str(models))
    monkeypatch.setenv("MOEX_IMAGE_CONTRACTS_MANIFEST", str(image))
    monkeypatch.delenv("MOEX_AUTH_MODE", raising=False)
    with TestClient(create_app(database_url="sqlite:///:memory:")) as client:
        response = client.get("/implementations")
    assert response.status_code == 503
    assert response.json()["contracts_match"] is False


def test_ready_gate_opens_after_models_match(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    with _gate(monkeypatch, tmp_path, ready=True) as client:
        response = client.get("/implementations")
    assert response.status_code == 200


def test_ready_gate_off_by_default(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    models = tmp_path / "models"
    models.mkdir()
    monkeypatch.delenv("MOEX_REQUIRE_MODELS_READY", raising=False)
    monkeypatch.setenv("MOEX_MODELS_ROOT", str(models))
    monkeypatch.delenv("MOEX_AUTH_MODE", raising=False)
    with TestClient(create_app(database_url="sqlite:///:memory:")) as client:
        response = client.get("/implementations")
    assert response.status_code != 503
