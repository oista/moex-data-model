"""moex-model selection — validate ExternalTermSelection packages (ADR-020)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from moex_model_cli.bootstrap import SlicePaths

DEFAULT_SELECTIONS_DIR = Path("model-assets") / "external-selections"
DEFAULT_SCOPES_DIR = Path("model-assets") / "external-scopes"


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected mapping at root")
    return data


def _resolve_selection_path(paths: SlicePaths, target: str | Path) -> Path:
    p = Path(target)
    if p.is_file():
        return p if p.is_absolute() else paths.root / p
    # id or id/version under external-selections
    base = paths.root / DEFAULT_SELECTIONS_DIR / str(target)
    if (base / "selection.yaml").is_file():
        return base / "selection.yaml"
    # try */0.1/selection.yaml
    matches = sorted(base.glob("*/selection.yaml"))
    if matches:
        return matches[0]
    # direct path relative to root
    cand = paths.root / str(target)
    if cand.is_file():
        return cand
    raise FileNotFoundError(
        f"selection not found: {target} (expected selection.yaml under "
        f"{DEFAULT_SELECTIONS_DIR}/<id>/)"
    )


def _load_scope_for_ref(paths: SlicePaths, scope_ref: str) -> dict[str, Any] | None:
    scopes_root = paths.root / DEFAULT_SCOPES_DIR
    if not scopes_root.is_dir():
        return None
    for path in scopes_root.rglob("specification-scope.yaml"):
        data = _load_yaml(path)
        if data.get("id") == scope_ref:
            return data
    return None


def run_selection_validate(
    paths: SlicePaths,
    *,
    target: str,
    as_json: bool = False,
) -> tuple[int, str]:
    try:
        from moex_modeling.external_alignment.public import (
            scope_from_dict,
            selection_from_dict,
            validate_selection,
        )
    except ImportError:
        return (
            2,
            "moex-model selection requires moex-modeling-kernel "
            "(pip install -e packages/modeling-kernel)\n",
        )

    try:
        sel_path = _resolve_selection_path(paths, target)
    except FileNotFoundError as exc:
        return 2, f"{exc}\n"

    try:
        sel_data = _load_yaml(sel_path)
        selection = selection_from_dict(sel_data)
    except Exception as exc:
        return 1, f"failed to load selection {sel_path}: {exc}\n"

    scope = None
    known: set[str] | None = None
    scope_data = _load_scope_for_ref(paths, selection.scope_ref)
    if scope_data is not None:
        scope = scope_from_dict(scope_data)
        known = {scope.id}
    else:
        # still validate scope_ref against discovered scope ids if any
        scopes_root = paths.root / DEFAULT_SCOPES_DIR
        known = set()
        if scopes_root.is_dir():
            for path in scopes_root.rglob("specification-scope.yaml"):
                try:
                    known.add(str(_load_yaml(path).get("id") or ""))
                except Exception:
                    continue
            known.discard("")
        if not known:
            known = None

    report = validate_selection(selection, scope=scope, known_scope_ids=known)

    payload = {
        "selection_id": selection.id,
        "path": str(sel_path),
        "ok": report.ok,
        "draft_only": selection.draft_only,
        "issues": [
            {"severity": i.severity, "code": i.code, "message": i.message}
            for i in report.issues
        ],
    }

    if as_json:
        return (0 if report.ok else 1), json.dumps(payload, indent=2) + "\n"

    lines = [
        f"selection: {selection.id}",
        f"path: {sel_path}",
        f"status: {'OK' if report.ok else 'FAILED'}",
    ]
    for i in report.issues:
        lines.append(f"  [{i.severity}] {i.code}: {i.message}")
    if not report.issues:
        lines.append("  (no issues)")
    return (0 if report.ok else 1), "\n".join(lines) + "\n"
