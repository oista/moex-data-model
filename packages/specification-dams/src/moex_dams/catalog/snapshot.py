"""Load and index CatalogSnapshot JSON files (ADR-048)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class SnapshotError(ValueError):
    """Invalid snapshot file."""


def canonical_digest(payload: dict[str, Any]) -> str:
    """sha256 digest of payload without the digest field (canonical JSON)."""
    body = {k: v for k, v in payload.items() if k != "digest"}
    raw = json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class ObjectKey:
    catalog: str
    kind: str
    external_id: str


@dataclass
class CatalogSnapshot:
    catalog_revision: str
    digest: str
    captured_at: str | None
    catalogs: list[str]
    objects: list[dict[str, Any]]
    by_key: dict[ObjectKey, dict[str, Any]] = field(default_factory=dict)
    catalogs_set: set[str] = field(default_factory=set)
    path: Path | None = None

    def get(self, catalog: str, kind: str, external_id: str) -> dict[str, Any] | None:
        return self.by_key.get(ObjectKey(catalog, kind, external_id))


def load_snapshot(path: Path | str) -> CatalogSnapshot:
    """Load snapshot JSON; reject duplicate keys and digest mismatches."""
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SnapshotError(f"{p}: root must be an object")

    revision = data.get("catalog_revision")
    if not revision or not isinstance(revision, str):
        raise SnapshotError(f"{p}: catalog_revision is required")

    objects = data.get("objects")
    if not isinstance(objects, list) or not objects:
        raise SnapshotError(f"{p}: objects must be a non-empty list")

    by_key: dict[ObjectKey, dict[str, Any]] = {}
    for i, obj in enumerate(objects):
        if not isinstance(obj, dict):
            raise SnapshotError(f"{p}: objects[{i}] must be an object")
        catalog = obj.get("catalog")
        kind = obj.get("kind")
        external_id = obj.get("external_id")
        if not all(isinstance(x, str) and x for x in (catalog, kind, external_id)):
            raise SnapshotError(
                f"{p}: objects[{i}] needs catalog, kind, external_id strings"
            )
        key = ObjectKey(str(catalog), str(kind), str(external_id))
        if key in by_key:
            raise SnapshotError(
                f"{p}: duplicate object ({key.catalog}, {key.kind}, {key.external_id})"
            )
        by_key[key] = obj

    expected = canonical_digest(data)
    declared = data.get("digest")
    if declared != expected:
        raise SnapshotError(
            f"{p}: digest mismatch: declared={declared!r} expected={expected!r}"
        )

    catalogs = data.get("catalogs") or []
    if not isinstance(catalogs, list):
        raise SnapshotError(f"{p}: catalogs must be a list")
    catalogs_list = [str(c) for c in catalogs]
    catalogs_set = set(catalogs_list) | {k.catalog for k in by_key}

    return CatalogSnapshot(
        catalog_revision=revision,
        digest=str(declared),
        captured_at=data.get("captured_at") if isinstance(data.get("captured_at"), str) else None,
        catalogs=catalogs_list,
        objects=list(objects),
        by_key=by_key,
        catalogs_set=catalogs_set,
        path=p,
    )


def default_snapshot_path(repo_root: Path | str) -> Path:
    return (
        Path(repo_root)
        / "model-assets"
        / "catalog-snapshots"
        / "clinkr"
        / "catalog-snapshot.json"
    )
