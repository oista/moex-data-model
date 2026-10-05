"""Requirement lifecycle / implementation status data contracts."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
SCHEMA_TYPES = (
    REPO
    / "model-assets/specifications/moex-dams/0.1/schemas/moex-types.yaml"
)
REQ_DIR = REPO / "model-assets/specifications/moex-dams/0.1/requirements"
FIXTURE_DIR = Path(__file__).parent / "fixtures" / "requirements"

LIFECYCLE_VALUES = {
    "draft",
    "proposed",
    "approved",
    "rejected",
    "deprecated",
    "superseded",
}
IMPLEMENTATION_VALUES = {
    "not_started",
    "in_progress",
    "implemented",
    "verified",
}


def _enum_values(enum_name: str) -> dict[str, str]:
    data = yaml.safe_load(SCHEMA_TYPES.read_text(encoding="utf-8"))
    enum = data["enums"][enum_name]
    out: dict[str, str] = {}
    for key, meta in (enum.get("permissible_values") or {}).items():
        desc = ""
        if isinstance(meta, dict):
            desc = str(meta.get("description") or "").strip()
        out[key] = desc
    return out


def _iter_requirements(path: Path) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return []
    return [r for r in (data.get("requirements") or []) if isinstance(r, dict)]


def test_lifecycle_enum_values_and_ru_descriptions() -> None:
    values = _enum_values("RequirementLifecycleStatus")
    assert set(values) == LIFECYCLE_VALUES
    for key, desc in values.items():
        assert desc, f"missing RU description for {key}"


def test_implementation_enum_values_and_ru_descriptions() -> None:
    values = _enum_values("RequirementImplementationStatus")
    assert set(values) == IMPLEMENTATION_VALUES
    for key, desc in values.items():
        assert desc, f"missing RU description for {key}"


def test_catalog_and_fixture_statuses_in_enum() -> None:
    paths = [
        REQ_DIR / "it-solution-requirements.yaml",
        REQ_DIR / "conceptual-model-requirements.yaml",
        *sorted(FIXTURE_DIR.glob("*.yaml")),
    ]
    for path in paths:
        for req in _iter_requirements(path):
            status = req.get("lifecycle_status")
            assert status in LIFECYCLE_VALUES, f"{path.name}: {req.get('code')} -> {status}"
            impl = req.get("implementation_status")
            if impl is not None:
                assert impl in IMPLEMENTATION_VALUES, (
                    f"{path.name}: {req.get('code')} impl={impl}"
                )


def test_status_showcase_covers_all_lifecycle_values() -> None:
    path = FIXTURE_DIR / "status-showcase.yaml"
    reqs = _iter_requirements(path)
    statuses = {r["lifecycle_status"] for r in reqs}
    assert statuses == LIFECYCLE_VALUES
    by_id = {r["element_id"]: r for r in reqs}
    superseded = [r for r in reqs if r["lifecycle_status"] == "superseded"]
    assert superseded
    for r in superseded:
        target = r.get("superseded_by")
        assert target in by_id, f"superseded_by {target} not in showcase"
