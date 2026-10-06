"""Legacy kind tokens → TechnicalAsset collection/asset_kind (Variant B, ADR-031/033)."""

from __future__ import annotations

from typing import Any

# Legacy object_kind / already-migrated asset_kind → (collection_key, asset_kind)
KIND_MAP: dict[str, tuple[str, str]] = {
    "database": ("data_containers", "database"),
    "schema": ("data_containers", "schema"),
    "table": ("data_carriers", "relational_table"),
    "view": ("data_carriers", "relational_view"),
    "relational_table": ("data_carriers", "relational_table"),
    "relational_view": ("data_carriers", "relational_view"),
    "api": ("access_points", "interface"),
    "endpoint": ("access_points", "operation"),
    "interface": ("access_points", "interface"),
    "operation": ("access_points", "operation"),
    "channel": ("access_points", "channel"),
    "topic": ("data_carriers", "stream_topic"),
    "queue": ("data_carriers", "stream_queue"),
    "stream_topic": ("data_carriers", "stream_topic"),
    "stream_queue": ("data_carriers", "stream_queue"),
    "file": ("data_carriers", "file"),
    "dataset": ("data_carriers", "dataset"),
    "in_memory": ("data_carriers", "in_memory"),
    "api_resource": ("data_carriers", "api_resource"),
    "other": ("data_carriers", "other"),
    "pipeline": ("execution_assets", "pipeline"),
    "job": ("execution_assets", "job"),
    "bucket": ("data_containers", "bucket"),
    "broker": ("data_containers", "broker"),
    "directory": ("data_containers", "directory"),
    "cluster": ("data_containers", "cluster"),
}

# Legacy carrier kinds superseded by Message (ADR-040) — resolve_kind returns None.
_REMOVED_CARRIER_KINDS = frozenset({"payload", "message", "message" + "_type"})
TRANSITIONAL_KINDS = frozenset()  # emptied; Message is not a TechnicalAsset
COLLECTION_KEYS = (
    "data_carriers",
    "access_points",
    "data_containers",
    "execution_assets",
)
CARRIER_COLLECTIONS = frozenset({"data_carriers"})


def resolve_kind(raw: str | None) -> tuple[str, str] | None:
    """Return (collection_key, asset_kind) or None if unknown / removed."""
    if not raw:
        return None
    key = str(raw).strip()
    if key in _REMOVED_CARRIER_KINDS:
        return None
    return KIND_MAP.get(key)


def heuristic_namespace(technology: str | None, system_ref: str | None) -> str:
    tech = (technology or "").strip().lower() or "unknown"
    sys_id = _system_id(system_ref)
    return f"{tech}://{sys_id}"


def _system_id(system_ref: str | None) -> str:
    s = str(system_ref or "")
    if "/" in s:
        return s.rsplit("/", 1)[-1]
    if ":" in s:
        return s.rsplit(":", 1)[-1]
    return s or "unknown"


def infer_parent_names(
    *,
    qualified_name: str | None,
    native_schema_ref: str | None,
    schema: str | None = None,
    database: str | None = None,
) -> tuple[str | None, str | None]:
    """Infer (database_name, schema_name) from source columns / refs (ADR-033)."""
    db = (database or "").strip() or None
    sch = (schema or "").strip() or None
    if sch and db:
        return db, sch
    if sch:
        return db, sch
    if db:
        return db, sch

    # postgres:ucd.OBJECT / oracle:SCHEMA.TABLE
    native = (native_schema_ref or "").strip()
    if native and ":" in native:
        after = native.split(":", 1)[1]
        if "." in after:
            left, _right = after.rsplit(".", 1)
            if left and not left.startswith("//") and "/" not in left:
                return db, left

    # qualified_name SCHEMA.TABLE (single dot, no URI)
    qn = (qualified_name or "").strip()
    if qn and "." in qn and "://" not in qn and "/" not in qn:
        left, _right = qn.rsplit(".", 1)
        if left:
            return db, left

    return db, sch


def ensure_container(
    containers: list[dict[str, Any]],
    by_name: dict[str, dict[str, Any]],
    *,
    name: str,
    asset_kind: str,
    prefix: str,
    slug: str,
    technology: str,
    system_ref: str,
    solution_ref: str,
    lifecycle_status: str,
    parent_ref: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Get or create a DataContainer; keyed by name within the package."""
    existing = by_name.get(name)
    if existing is not None:
        return existing
    from moex_standard_linkml.ingest import ids

    curie = ids.physical_object_id(prefix, slug, name)
    obj: dict[str, Any] = {
        "element_id": curie,
        "name": name,
        "title": name,
        "description": description or f"Data container {name}",
        "lifecycle_status": lifecycle_status,
        "solution_ref": solution_ref,
        "system_ref": system_ref,
        "qualified_name": name,
        "technology": technology,
        "asset_namespace": heuristic_namespace(technology, system_ref),
        "asset_kind": asset_kind,
    }
    if parent_ref:
        obj["parent_ref"] = parent_ref
    containers.append(obj)
    by_name[name] = obj
    return obj
