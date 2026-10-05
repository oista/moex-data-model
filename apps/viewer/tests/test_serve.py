"""HTTP serve + /api/edit integration tests."""

from __future__ import annotations

import json
import threading
from http.client import HTTPConnection
from pathlib import Path

import yaml

from moex_publication_viewer.serve import make_server


def _mini_repo(tmp_path: Path) -> Path:
    mod = tmp_path / "mod"
    mod.mkdir()
    (mod / "model.yaml").write_text(
        yaml.dump(
            {
                "logical_entities": [
                    {
                        "element_id": "dams:logical/A",
                        "name": "A",
                        "title": "Alpha",
                        "description": "First entity",
                        "aliases": ["aka"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (mod / "publish.yaml").write_text(
        """
module_id: moex:module:tmp-edit
kind: publication_module
title: Tmp Edit
sections:
  - id: logical
    title: Logical
    type: entity-table
    key_column: element_id
    source:
      format: yaml
      path: model.yaml
      select: logical_entities
    columns: [element_id, name, title, description]
""",
        encoding="utf-8",
    )
    return tmp_path


def test_capabilities_and_edit_roundtrip(tmp_path: Path):
    root = _mini_repo(tmp_path)
    dist = tmp_path / "dist"
    httpd, state = make_server(root, dist_dir=dist, port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        port = state.port
        conn = HTTPConnection("127.0.0.1", port, timeout=10)
        conn.request("GET", "/api/capabilities")
        resp = conn.getresponse()
        assert resp.status == 200
        caps = json.loads(resp.read().decode("utf-8"))
        assert caps["edit"] is True
        token = caps["token"]
        assert token

        # Find an edit target from registry
        assert state.registry
        target = next(iter(state.registry.values()))
        assert target.field in ("description", "title", "aliases")
        # Prefer description
        for t in state.registry.values():
            if t.field == "description":
                target = t
                break

        body = json.dumps(
            {
                "token": token,
                "edit_target": target.to_dict(),
                "new_value": "Edited from API",
            }
        )
        conn.request(
            "POST",
            "/api/edit",
            body=body,
            headers={
                "Content-Type": "application/json",
                "Origin": f"http://127.0.0.1:{port}",
                "Host": f"127.0.0.1:{port}",
            },
        )
        resp = conn.getresponse()
        raw = resp.read().decode("utf-8")
        assert resp.status == 200, raw
        payload = json.loads(raw)
        assert payload["ok"] is True
        assert payload["modules"]
        text = (root / "mod" / "model.yaml").read_text(encoding="utf-8")
        assert "Edited from API" in text
        conn.close()
    finally:
        httpd.shutdown()


def test_layout_api_roundtrip_and_guards(tmp_path: Path):
    root = _mini_repo(tmp_path)
    pub = root / "mod" / "publications"
    pub.mkdir()
    layout_path = pub / "logical.layout.json"
    layout = {
        "version": 1,
        "profile": "logical",
        "nodes": {"dams:logical/A": {"x": 1, "y": 2, "color": "#4285F4"}},
        "edges": {},
    }
    layout_path.write_text(json.dumps(layout), encoding="utf-8")
    from moex_publication_viewer.edits import value_hash

    base_hash = value_hash(layout)
    httpd, state = make_server(root, dist_dir=tmp_path / "dist", port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        port = state.port
        conn = HTTPConnection("127.0.0.1", port, timeout=10)
        conn.request("GET", "/api/capabilities")
        caps = json.loads(conn.getresponse().read().decode("utf-8"))
        assert caps["layout_edit"] is True
        token = caps["token"]

        updated = {
            **layout,
            "nodes": {"dams:logical/A": {"x": 40, "y": 60, "color": "#0F9D58"}},
        }
        rel = "mod/publications/logical.layout.json"
        conn.request(
            "POST",
            "/api/layout",
            body=json.dumps(
                {
                    "token": token,
                    "path": rel,
                    "layout": updated,
                    "base_hash": base_hash,
                }
            ),
            headers={
                "Content-Type": "application/json",
                "Origin": f"http://127.0.0.1:{port}",
                "Host": f"127.0.0.1:{port}",
            },
        )
        resp = conn.getresponse()
        raw = resp.read().decode("utf-8")
        assert resp.status == 200, raw
        payload = json.loads(raw)
        assert payload["ok"] is True
        on_disk = json.loads(layout_path.read_text(encoding="utf-8"))
        assert on_disk["nodes"]["dams:logical/A"]["x"] == 40

        # Conflict when base_hash is stale
        conn.request(
            "POST",
            "/api/layout",
            body=json.dumps(
                {
                    "token": token,
                    "path": rel,
                    "layout": updated,
                    "base_hash": "deadbeef",
                }
            ),
            headers={
                "Content-Type": "application/json",
                "Origin": f"http://127.0.0.1:{port}",
                "Host": f"127.0.0.1:{port}",
            },
        )
        resp = conn.getresponse()
        assert resp.status == 409
        resp.read()

        # Escape root
        conn.request(
            "POST",
            "/api/layout",
            body=json.dumps(
                {
                    "token": token,
                    "path": "../outside.layout.json",
                    "layout": updated,
                    "base_hash": payload["new_hash"],
                }
            ),
            headers={
                "Content-Type": "application/json",
                "Origin": f"http://127.0.0.1:{port}",
                "Host": f"127.0.0.1:{port}",
            },
        )
        resp = conn.getresponse()
        assert resp.status == 403
        resp.read()
        conn.close()
    finally:
        httpd.shutdown()


def test_bad_token_forbidden(tmp_path: Path):
    root = _mini_repo(tmp_path)
    httpd, state = make_server(root, dist_dir=tmp_path / "dist", port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        port = state.port
        target = next(iter(state.registry.values()))
        conn = HTTPConnection("127.0.0.1", port, timeout=10)
        conn.request(
            "POST",
            "/api/edit",
            body=json.dumps(
                {
                    "token": "wrong",
                    "edit_target": target.to_dict(),
                    "new_value": "x",
                }
            ),
            headers={
                "Content-Type": "application/json",
                "Origin": f"http://127.0.0.1:{port}",
                "Host": f"127.0.0.1:{port}",
            },
        )
        resp = conn.getresponse()
        assert resp.status == 403
        conn.close()
    finally:
        httpd.shutdown()
