"""One-way RequirementCatalog YAML → CSV projection (ADR-013)."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import yaml

CSV_COLUMNS: tuple[str, ...] = (
    "catalog_id",
    "catalog_name",
    "source_path",
    "element_id",
    "code",
    "name",
    "title",
    "description",
    "statement",
    "requirement_level",
    "requirement_section",
    "lifecycle_status",
    "applies_target_class",
    "applies_target_kinds",
    "applies_implementation_scope",
    "applies_dams_model_level",
    "applies_implementation_profile",
    "check_count",
    "check_ids",
    "check_kinds",
    "severities",
    "diagnostic_codes",
)

_JOIN = "; "


def _s(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return _JOIN.join(_s(v) for v in value)
    text = str(value).replace("\r\n", "\n").replace("\r", "\n")
    return text.strip()


def _rel(path: Path, root: Path | None) -> str:
    if root is not None:
        try:
            return path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            pass
    return path.resolve().as_posix()


def requirement_row(
    req: dict[str, Any],
    *,
    catalog_id: str,
    catalog_name: str,
    source_path: str,
) -> dict[str, str]:
    applies = req.get("applies_to") if isinstance(req.get("applies_to"), dict) else {}
    checks = [c for c in (req.get("formal_checks") or []) if isinstance(c, dict)]
    row = {
        "catalog_id": catalog_id,
        "catalog_name": catalog_name,
        "source_path": source_path,
        "element_id": _s(req.get("element_id")),
        "code": _s(req.get("code")),
        "name": _s(req.get("name")),
        "title": _s(req.get("title")),
        "description": _s(req.get("description")),
        "statement": _s(req.get("statement")),
        "requirement_level": _s(req.get("requirement_level")),
        "requirement_section": _s(req.get("requirement_section")),
        "lifecycle_status": _s(req.get("lifecycle_status")),
        "applies_target_class": _s(applies.get("applies_target_class")),
        "applies_target_kinds": _s(applies.get("applies_target_kinds") or []),
        "applies_implementation_scope": _s(applies.get("applies_implementation_scope")),
        "applies_dams_model_level": _s(applies.get("applies_dams_model_level")),
        "applies_implementation_profile": _s(
            applies.get("applies_implementation_profile")
        ),
        "check_count": str(len(checks)),
        "check_ids": _s([c.get("check_id") for c in checks]),
        "check_kinds": _s([c.get("kind") for c in checks]),
        "severities": _s([c.get("severity") for c in checks]),
        "diagnostic_codes": _s([c.get("diagnostic_code") for c in checks]),
    }
    return {k: row[k] for k in CSV_COLUMNS}


def iter_catalog_rows(path: Path, *, source_path: str) -> list[dict[str, str]]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path} is not a YAML mapping")
    reqs = raw.get("requirements") or []
    if not isinstance(reqs, list):
        raise ValueError(f"{path} requirements is not a list")
    catalog_id = _s(raw.get("catalog_id"))
    catalog_name = _s(raw.get("name"))
    rows = [
        requirement_row(
            req,
            catalog_id=catalog_id,
            catalog_name=catalog_name,
            source_path=source_path,
        )
        for req in reqs
        if isinstance(req, dict)
    ]
    return sorted(
        rows,
        key=lambda r: (
            r["requirement_level"],
            r["requirement_section"],
            r["code"],
            r["element_id"],
        ),
    )


def default_catalog_paths(root: Path) -> list[Path]:
    folder = root / "model-assets/specifications/moex-dams/0.1/requirements"
    return sorted(p for p in folder.glob("*.yaml") if p.is_file())


def collect_requirement_rows(
    paths: list[Path],
    *,
    root: Path | None = None,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in paths:
        rows.extend(iter_catalog_rows(path, source_path=_rel(path, root)))
    return sorted(
        rows,
        key=lambda r: (
            r["requirement_level"],
            r["requirement_section"],
            r["code"],
            r["element_id"],
        ),
    )


def write_requirements_csv(rows: list[dict[str, str]], out: Path) -> int:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(CSV_COLUMNS), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)
