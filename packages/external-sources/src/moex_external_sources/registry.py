"""registry.yaml / lockfile.yaml load and validate."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

from moex_modeling.external_sources.public import LockEntry, SourceKind


class SourceRegistry(BaseModel):
    """Declarative metadata for one external source tree."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_default=True,
    )

    source_id: str
    kind: SourceKind
    adapter: str
    title: str | None = None
    description: str | None = None
    upstream_url: str
    release_cadence: str | None = None
    license: str | None = None
    default_ref: str | None = None
    default_seed: str | None = None
    extraction_method: str | None = None
    artifact_glob: str | None = None
    robot_version: str | None = None
    extra: dict[str, str] = Field(default_factory=dict)


class SourceLockfile(BaseModel):
    """On-disk lockfile wrapping a LockEntry plus optional notes."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_default=True,
    )

    lock: LockEntry
    notes: str | None = None


def _load_yaml(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"expected mapping in {path}")
    return raw


def _coerce_kind(data: dict[str, Any]) -> dict[str, Any]:
    kind = data.get("kind")
    if isinstance(kind, str):
        return {**data, "kind": SourceKind(kind)}
    return data


def load_registry(path: Path) -> SourceRegistry:
    return SourceRegistry.model_validate(_coerce_kind(_load_yaml(path)))


def load_lockfile(path: Path) -> SourceLockfile:
    data = _load_yaml(path)
    lock = data.get("lock")
    if isinstance(lock, dict):
        data = {**data, "lock": _coerce_kind(lock)}
    return SourceLockfile.model_validate(data)


def write_lockfile(path: Path, lockfile: SourceLockfile) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = lockfile.model_dump(mode="json", exclude_none=True)
    path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def list_source_dirs(roots: Path) -> list[Path]:
    """Return child dirs that contain registry.yaml."""
    if not roots.is_dir():
        return []
    out: list[Path] = []
    for child in sorted(roots.iterdir()):
        if child.is_dir() and (child / "registry.yaml").is_file():
            out.append(child)
    return out
