"""Requirement lifecycle status tokens and Viewer UI wiring."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_publication_viewer.assets import assemble_css
from moex_publication_viewer.normalizers.dams_explorer_roots import (
    _load_requirement_items,
)

VIEWER_ROOT = Path(__file__).resolve().parents[1]
JS = (VIEWER_ROOT / "static" / "viewer.js").read_text(encoding="utf-8")
TOKENS = (VIEWER_ROOT / "static" / "css" / "10-tokens.css").read_text(encoding="utf-8")
COMPONENTS = (VIEWER_ROOT / "static" / "css" / "40-components.css").read_text(
    encoding="utf-8"
)
REPO = VIEWER_ROOT.parents[1]
SHOWCASE = (
    REPO
    / "packages/specification-dams/tests/fixtures/requirements/status-showcase.yaml"
)
STATUS_VARS = (
    "--status-draft",
    "--status-proposed",
    "--status-approved",
    "--status-inactive",
)
RU_LABELS = (
    "Черновик",
    "На согласовании",
    "Утверждено",
    "Отклонено",
    "Устарело",
    "Заменено",
)


def test_status_tokens_defined_in_light_and_dark() -> None:
    light = TOKENS.split("[data-theme=\"dark\"]")[0]
    dark = TOKENS.split("[data-theme=\"dark\"]")[1]
    for var in STATUS_VARS:
        assert f"{var}:" in light
        assert f"{var}:" in dark
    assert "--status-outline:" in light and "--status-outline:" in dark
    assert "--status-chip-bg:" in light and "--status-chip-bg:" in dark
    assert "--nav-requirements-accent:" in light


def test_req_status_component_rules_use_vars_not_hex() -> None:
    css = assemble_css()
    chunk = css.split(".req-status--draft")[1].split(".nav-kind.kind-plain")[0]
    assert "#" not in chunk
    assert "rgb(" not in chunk
    for cls in ("draft", "proposed", "approved", "inactive"):
        assert f".req-status--{cls}" in css
    assert ".req-status-chip" in css
    assert "var(--status-chip-bg)" in css
    assert "var(--status-outline)" in COMPONENTS or "var(--status-outline)" in css


def test_js_requirement_status_table_and_mark() -> None:
    assert "const REQUIREMENT_STATUS" in JS
    assert "function requirementMarkHtml" in JS
    assert "function requirementStatusInfo" in JS
    assert 'requirement: "R"' in JS
    req_svg = JS.split("function requirementsFileSvg")[1].split(
        "function requirementsFileMarkHtml"
    )[0]
    assert "currentColor" in req_svg
    assert "#ff6641" not in req_svg
    for label in RU_LABELS:
        assert label in JS


def test_normalizer_loads_status_and_resolves_superseded(tmp_path: Path) -> None:
    spec_dir = tmp_path / "moex-dams" / "0.1"
    req_dir = spec_dir / "requirements"
    req_dir.mkdir(parents=True)
    target = req_dir / "status-showcase.yaml"
    target.write_text(SHOWCASE.read_text(encoding="utf-8"), encoding="utf-8")
    items = _load_requirement_items(spec_dir, catalog_rel="requirements/status-showcase.yaml")
    by_code = {it.attributes["code"]: it for it in items}
    assert set(by_code) >= {"GEN-801", "GEN-803", "GEN-806"}
    assert by_code["GEN-801"].attributes["lifecycle_status"] == "draft"
    assert by_code["GEN-803"].attributes["implementation_status"] == "implemented"
    superseded = by_code["GEN-806"].attributes
    assert superseded["lifecycle_status"] == "superseded"
    assert superseded["superseded_by"] == "dams:req/GEN-803"
    assert superseded["superseded_by_item"] == "req:GEN-803"
