"""Local edit server for the publication viewer (127.0.0.1 only)."""

from __future__ import annotations

import json
import secrets
import threading
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from moex_publication_viewer.assets import assemble_css, assemble_js
from moex_publication_viewer.build import (
    VIEWER_ROOT,
    build,
    build_dsp_documentation_sidebar_siblings,
    build_search_index,
    compile_catalog,
    compile_modules,
    enrich_dams_explorer_implementations,
    enrich_fibo_explorer_classes,
    enrich_fibo_explorer_implementations,
    enrich_linkml_glossary_sections,
)
from moex_publication_viewer.edits import (
    EditError,
    EditTarget,
    apply_edit,
    collect_edit_registry,
)
from moex_publication_viewer.renderers.html_renderer import (
    modules_payload,
    render_viewer,
)


class ViewerServeState:
    def __init__(self, root: Path, dist_dir: Path, port: int) -> None:
        self.root = root.resolve()
        self.dist_dir = dist_dir.resolve()
        self.port = port
        self.token = secrets.token_urlsafe(32)
        self.lock = threading.RLock()
        self.modules: list[Any] = []
        self.registry: dict[tuple[str, str, str], EditTarget] = {}
        self.search_index: list[dict] = []
        self.catalog = None
        self.sidebar_siblings: list[dict] = []

    def refresh_from_disk(self, *, write_html: bool = True) -> Path:
        """Recompile modules, refresh registry, optionally rewrite index.html."""
        with self.lock:
            modules = compile_modules(
                self.root, enforce_publication_contract=False, dist_dir=self.dist_dir
            )
            catalog = compile_catalog(self.root, modules)
            enrich_dams_explorer_implementations(modules, catalog)
            enrich_fibo_explorer_classes(modules)
            enrich_fibo_explorer_implementations(modules, catalog)
            enrich_linkml_glossary_sections(modules)
            self.sidebar_siblings = build_dsp_documentation_sidebar_siblings(modules)
            self.modules = modules
            self.catalog = catalog
            self.search_index = build_search_index(modules)
            self.registry = collect_edit_registry(modules)
            index_path = self.dist_dir / "index.html"
            if write_html:
                css_text = assemble_css()
                js_text = assemble_js()
                html = render_viewer(
                    modules,
                    self.search_index,
                    VIEWER_ROOT,
                    catalog=catalog,
                    inline_css=css_text,
                    inline_js=js_text,
                    sidebar_siblings=self.sidebar_siblings,
                )
                self.dist_dir.mkdir(parents=True, exist_ok=True)
                index_path.write_text(html, encoding="utf-8")
                (self.dist_dir / "viewer.css").write_text(css_text, encoding="utf-8")
                (self.dist_dir / "viewer.js").write_text(js_text, encoding="utf-8")
            return index_path

    def rebuild(self, *, write_html: bool = True) -> Path:
        """Initial / full rebuild (publication contract gate via ``build``)."""
        with self.lock:
            index = build(self.root, self.dist_dir)
            self.refresh_from_disk(write_html=write_html)
            return index

    def allowed_origin(self, origin: str | None) -> bool:
        if not origin:
            return True  # same-origin / no Origin header (file won't hit us)
        expected = f"http://127.0.0.1:{self.port}"
        expected_localhost = f"http://localhost:{self.port}"
        return origin in (expected, expected_localhost)


def _optional_formal_diagnostics(root: Path, edited_file: Path) -> list[dict[str, Any]]:
    try:
        from moex_dams.rules.formal_checks import check_formal_requirements
        from moex_standard_linkml.domain.body import LinkMLImplementationBody
    except ImportError:
        return []
    try:
        text = edited_file.read_text(encoding="utf-8")
        import yaml

        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            return []
        # Only ModelPackage-like bodies
        if "logical_entities" not in data and "conceptual_entities" not in data:
            return []
        body = LinkMLImplementationBody(
            data=data,
            source_path=str(edited_file),
        )
        diags = check_formal_requirements(body)
        out: list[dict[str, Any]] = []
        for d in diags:
            out.append(
                {
                    "severity": getattr(getattr(d, "severity", None), "value", str(getattr(d, "severity", ""))),
                    "code": getattr(d, "code", None) or getattr(d, "rule_id", None),
                    "message": getattr(d, "message", str(d)),
                }
            )
        return out
    except Exception as exc:
        return [{"severity": "warning", "code": "formal_checks", "message": str(exc)}]


def _find_item(modules: list[Any], file: str, yaml_path: str, field: str) -> dict | None:
    from moex_publication_viewer.renderers.html_renderer import _item_to_dict

    def walk(item: Any) -> dict | None:
        targets = getattr(item, "edit_targets", None) or {}
        for et in targets.values():
            if (
                isinstance(et, dict)
                and et.get("file") == file
                and et.get("yaml_path") == yaml_path
                and et.get("field") == field
            ):
                return _item_to_dict(item)
        for child in item.children or []:
            hit = walk(child)
            if hit is not None:
                return hit
        return None

    for mod in modules:
        for sec in mod.sections:
            for item in sec.items or []:
                hit = walk(item)
                if hit is not None:
                    return hit
    return None


class ViewerHandler(BaseHTTPRequestHandler):
    state: ViewerServeState  # set via partial

    def log_message(self, fmt: str, *args: Any) -> None:
        # quieter default
        print(f"[viewer-serve] {self.address_string()} {fmt % args}")

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _check_host(self) -> bool:
        host = self.headers.get("Host", "")
        ok_hosts = {
            f"127.0.0.1:{self.state.port}",
            f"localhost:{self.state.port}",
        }
        if host not in ok_hosts:
            self._send_json(403, {"ok": False, "error": f"refused host: {host}"})
            return False
        return True

    def do_GET(self) -> None:  # noqa: N802
        if not self._check_host():
            return
        parsed = urlparse(self.path)
        if parsed.path == "/api/capabilities":
            self._send_json(
                200,
                {"edit": True, "token": self.state.token},
            )
            return
        if parsed.path in ("/", "/index.html"):
            index = self.state.dist_dir / "index.html"
            if not index.is_file():
                self.send_error(404, "index.html missing; rebuild")
                return
            data = index.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        # static siblings in dist
        rel = parsed.path.lstrip("/")
        if ".." in Path(rel).parts:
            self.send_error(403)
            return
        candidate = (self.state.dist_dir / rel).resolve()
        try:
            candidate.relative_to(self.state.dist_dir.resolve())
        except ValueError:
            self.send_error(403)
            return
        if candidate.is_file():
            data = candidate.read_bytes()
            ctype = "application/octet-stream"
            if candidate.suffix == ".js":
                ctype = "application/javascript"
            elif candidate.suffix == ".css":
                ctype = "text/css"
            elif candidate.suffix == ".json":
                ctype = "application/json"
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        self.send_error(404)

    def do_POST(self) -> None:  # noqa: N802
        if not self._check_host():
            return
        parsed = urlparse(self.path)
        if parsed.path != "/api/edit":
            self.send_error(404)
            return
        origin = self.headers.get("Origin")
        if not self.state.allowed_origin(origin):
            self._send_json(403, {"ok": False, "error": "bad origin"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json(422, {"ok": False, "error": "invalid JSON"})
            return
        if body.get("token") != self.state.token:
            self._send_json(403, {"ok": False, "error": "bad token"})
            return
        et_raw = body.get("edit_target")
        if not isinstance(et_raw, dict):
            self._send_json(422, {"ok": False, "error": "missing edit_target"})
            return
        new_value = body.get("new_value")

        with self.state.lock:
            try:

                def _verify() -> None:
                    compile_modules(
                        self.state.root,
                        enforce_publication_contract=False,
                        dist_dir=self.state.dist_dir,
                    )

                result = apply_edit(
                    self.state.root,
                    et_raw,
                    new_value,
                    self.state.registry,
                    rebuild=_verify,
                )
            except EditError as exc:
                self._send_json(
                    exc.status,
                    {"ok": False, "error": exc.message},
                )
                return
            except Exception as exc:
                self._send_json(422, {"ok": False, "error": str(exc)})
                return

            # Refresh modules / HTML / registry after successful edit
            self.state.refresh_from_disk(write_html=True)
            diagnostics = _optional_formal_diagnostics(self.state.root, result.path)
            item = _find_item(
                self.state.modules,
                str(et_raw.get("file")),
                str(et_raw.get("yaml_path")),
                str(et_raw.get("field")),
            )
            if item is None:
                from moex_publication_viewer.renderers.html_renderer import _item_to_dict

                def deep(i: Any) -> dict | None:
                    t = getattr(i, "edit_targets", None) or {}
                    for et in t.values():
                        if (
                            isinstance(et, dict)
                            and et.get("yaml_path") == et_raw.get("yaml_path")
                        ):
                            return _item_to_dict(i)
                    for c in i.children or []:
                        hit = deep(c)
                        if hit:
                            return hit
                    return None

                for mod in self.state.modules:
                    for sec in mod.sections:
                        for it in sec.items or []:
                            found = deep(it)
                            if found:
                                item = found
                                break

            self._send_json(
                200,
                {
                    "ok": True,
                    "diagnostics": diagnostics,
                    "item": item,
                    "modules": modules_payload(self.state.modules),
                    "search_index": self.state.search_index,
                    "new_hash": result.new_hash,
                },
            )


def serve(
    root: Path,
    *,
    dist_dir: Path | None = None,
    port: int = 8765,
    open_browser: bool = False,
) -> None:
    root = root.resolve()
    if dist_dir is None:
        dist_dir = VIEWER_ROOT / "dist"
    state = ViewerServeState(root, dist_dir, port)
    print(f"Building viewer from {root} …")
    index = state.rebuild(write_html=True)
    print(f"Serving {index} on http://127.0.0.1:{port}/")

    handler = partial(ViewerHandler)
    # attach state
    ViewerHandler.state = state  # type: ignore[attr-defined]
    httpd = ThreadingHTTPServer(("127.0.0.1", port), ViewerHandler)
    if open_browser:
        import webbrowser

        webbrowser.open(f"http://127.0.0.1:{port}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        httpd.server_close()


def make_server(
    root: Path,
    *,
    dist_dir: Path | None = None,
    port: int = 0,
) -> tuple[ThreadingHTTPServer, ViewerServeState]:
    """Test helper: bind port 0, return (server, state) after initial build."""
    root = root.resolve()
    if dist_dir is None:
        dist_dir = root / "dist"
    # temporary state with port 0; update after bind
    state = ViewerServeState(root, dist_dir, port=0)
    state.rebuild(write_html=True)

    class BoundHandler(ViewerHandler):
        pass

    httpd = ThreadingHTTPServer(("127.0.0.1", port), BoundHandler)
    state.port = httpd.server_address[1]
    BoundHandler.state = state  # type: ignore[attr-defined]
    return httpd, state
