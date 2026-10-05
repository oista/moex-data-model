#!/usr/bin/env python3
"""Migrate PhysicalObject instances to TechnicalAsset hierarchy (Variant B).

Idempotent: re-running on already-migrated YAML is a no-op (empty diff).
Preserves order/comments via ruamel.yaml when available; falls back to PyYAML.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

KIND_MAP: dict[str, tuple[str, str]] = {
    # object_kind -> (collection_key, asset_kind)
    "database": ("data_containers", "database"),
    "schema": ("data_containers", "schema"),
    "table": ("data_carriers", "relational_table"),
    "view": ("data_carriers", "relational_view"),
    "api": ("access_points", "interface"),
    "endpoint": ("access_points", "operation"),
    "payload": ("data_carriers", "message_type"),
    "topic": ("data_carriers", "stream_topic"),
    "queue": ("data_carriers", "stream_queue"),
    "message": ("data_carriers", "message_type"),
    "file": ("data_carriers", "file"),
    "dataset": ("data_carriers", "dataset"),
    "pipeline": ("execution_assets", "pipeline"),
}

TRANSITIONAL_KINDS = frozenset({"payload", "message"})
COLUMN_KIND = "column"

COLLECTION_KEYS = (
    "data_carriers",
    "access_points",
    "data_containers",
    "execution_assets",
)


def _load_yaml(path: Path) -> tuple[Any, str]:
    try:
        from ruamel.yaml import YAML

        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.default_flow_style = False
        data = yaml.load(path.read_text(encoding="utf-8"))
        return data, "ruamel"
    except Exception:
        import yaml

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data, "pyyaml"


def _dump_yaml(data: Any, path: Path, engine: str) -> None:
    if engine == "ruamel":
        from ruamel.yaml import YAML

        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.default_flow_style = False
        yaml.width = 120
        with path.open("w", encoding="utf-8") as fh:
            yaml.dump(data, fh)
    else:
        import yaml

        path.write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )


def _as_dict(obj: Any) -> dict[str, Any] | None:
    if isinstance(obj, dict):
        return obj
    return None


def _system_id(system_ref: Any) -> str:
    s = str(system_ref or "")
    if "/" in s:
        return s.rsplit("/", 1)[-1]
    if ":" in s:
        return s.rsplit(":", 1)[-1]
    return s or "unknown"


def _heuristic_namespace(obj: dict[str, Any]) -> tuple[str, bool]:
    """Return (namespace, is_heuristic)."""
    tech = str(obj.get("technology") or "").strip().lower() or "unknown"
    sys_id = _system_id(obj.get("system_ref"))
    return f"{tech}://{sys_id}", True


def _collect_element_ids(data: dict[str, Any]) -> set[str]:
    ids: set[str] = set()

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            eid = node.get("element_id")
            if eid:
                ids.add(str(eid))
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return ids


def _count_fields(data: dict[str, Any]) -> int:
    n = 0
    for key in ("physical_objects", *COLLECTION_KEYS):
        for obj in data.get(key) or []:
            if isinstance(obj, dict):
                n += len(obj.get("physical_fields") or [])
    return n


def _rewrite_ref_keys(node: Any, replacements: dict[str, str]) -> int:
    """Rename dict keys according to replacements. Returns count of renames."""
    changed = 0
    if isinstance(node, dict):
        for old, new in list(replacements.items()):
            if old in node and new not in node:
                node[new] = node.pop(old)
                changed += 1
            elif old in node and new in node:
                # prefer new; drop old
                node.pop(old)
                changed += 1
        for v in list(node.values()):
            changed += _rewrite_ref_keys(v, replacements)
    elif isinstance(node, list):
        for item in node:
            changed += _rewrite_ref_keys(item, replacements)
    return changed


def _find_interface_for_endpoint(
    endpoint: dict[str, Any],
    apis: list[dict[str, Any]],
    report: list[str],
) -> str | None:
    parent = endpoint.get("parent_ref") or endpoint.get("parent")
    if parent:
        return str(parent)
    qn = str(endpoint.get("qualified_name") or "")
    matches = []
    for api in apis:
        api_qn = str(api.get("qualified_name") or "")
        if api_qn and (qn.startswith(api_qn) or api_qn in qn):
            matches.append(api)
        elif api.get("element_id") and str(api["element_id"]) in qn:
            matches.append(api)
    if len(matches) == 1:
        return str(matches[0]["element_id"])
    if len(matches) > 1:
        report.append(
            f"ERROR: endpoint {endpoint.get('element_id')} has ambiguous api parents: "
            f"{[m.get('element_id') for m in matches]}"
        )
        return None
    report.append(
        f"ERROR: endpoint {endpoint.get('element_id')} has no resolvable interface_ref"
    )
    return None


def migrate_document(data: dict[str, Any], *, demo: bool = False) -> dict[str, Any]:
    """Migrate in-place and return report dict."""
    report_lines: list[str] = []
    transitional_ns: list[str] = []
    skipped_columns: list[str] = []
    errors: list[str] = []

    before_ids = _collect_element_ids(data)
    before_fields = _count_fields(data)

    # Already migrated?
    if not data.get("physical_objects") and any(data.get(k) for k in COLLECTION_KEYS):
        return {
            "changed": False,
            "report": ["idempotent: already migrated (no physical_objects)"],
            "before_ids": before_ids,
            "after_ids": before_ids,
            "before_fields": before_fields,
            "after_fields": before_fields,
            "transitional_namespace": [],
            "errors": [],
        }

    physical = list(data.get("physical_objects") or [])
    if not physical and not any(data.get(k) for k in COLLECTION_KEYS):
        # Still rewrite any leftover keys in nested structures
        n = _rewrite_ref_keys(
            data,
            {
                "physical_object_ref": "carrier_ref",
                "physical_object_refs": "carrier_refs",
            },
        )
        return {
            "changed": n > 0,
            "report": [f"no physical_objects; rewrote {n} legacy keys"],
            "before_ids": before_ids,
            "after_ids": _collect_element_ids(data),
            "before_fields": before_fields,
            "after_fields": _count_fields(data),
            "transitional_namespace": [],
            "errors": [],
        }

    collections: dict[str, list[dict[str, Any]]] = {k: list(data.get(k) or []) for k in COLLECTION_KEYS}
    # Index existing by element_id for idempotency
    existing_ids = {
        str(o.get("element_id"))
        for items in collections.values()
        for o in items
        if isinstance(o, dict) and o.get("element_id")
    }

    apis = [
        o
        for o in physical
        if isinstance(o, dict) and str(o.get("object_kind") or "") == "api"
    ]

    for obj in physical:
        if not isinstance(obj, dict):
            continue
        kind = str(obj.get("object_kind") or "")
        eid = str(obj.get("element_id") or "")
        if kind == COLUMN_KIND:
            skipped_columns.append(eid)
            report_lines.append(
                f"SKIP column (not a quantum): {eid} — address via carrier_ref+schema_path"
            )
            continue
        if kind not in KIND_MAP:
            errors.append(f"unknown object_kind {kind!r} on {eid}")
            continue
        coll, asset_kind = KIND_MAP[kind]
        if eid in existing_ids:
            continue

        new_obj = copy.deepcopy(dict(obj))
        # Drop legacy slots
        for drop in ("object_kind", "native_schema_ref"):
            new_obj.pop(drop, None)

        ns, heuristic = _heuristic_namespace(obj)
        new_obj["asset_namespace"] = ns
        new_obj["asset_kind"] = asset_kind

        # native_schema_ref -> structure_ref for carriers
        if coll == "data_carriers":
            native = obj.get("native_schema_ref")
            if native and "structure_ref" not in new_obj:
                new_obj["structure_ref"] = native
            # Rewrite field refs
            for field in new_obj.get("physical_fields") or []:
                if isinstance(field, dict) and "physical_object_ref" in field:
                    field["carrier_ref"] = field.pop("physical_object_ref")
            if kind in TRANSITIONAL_KINDS:
                tags = list(new_obj.get("tags") or [])
                if "transitional" not in tags:
                    tags.append("transitional")
                new_obj["tags"] = tags
        else:
            # non-carriers: drop physical_fields if any (columns shouldn't be here)
            new_obj.pop("physical_fields", None)
            new_obj.pop("mapping_coverage_status", None)
            new_obj.pop("mapping_rationale", None)
            # Containers/execution should not keep location from legacy
            if coll in ("data_containers", "execution_assets"):
                new_obj.pop("direction", None)

        if coll == "access_points" and asset_kind == "operation":
            iface = _find_interface_for_endpoint(obj, apis, errors)
            if iface:
                new_obj["interface_ref"] = iface

        if heuristic:
            tags = list(new_obj.get("tags") or [])
            for t in ("transitional", "namespace_heuristic"):
                if t not in tags:
                    tags.append(t)
            new_obj["tags"] = tags
            transitional_ns.append(eid)

        # technology optional now but keep if present
        collections[coll].append(new_obj)
        existing_ids.add(eid)
        report_lines.append(f"MIGRATE {kind} -> {coll}/{asset_kind}: {eid}")

    # Write collections
    for key, items in collections.items():
        if items:
            data[key] = items
        elif key in data and not data[key]:
            pass

    # Remove physical_objects
    if "physical_objects" in data:
        del data["physical_objects"]
        report_lines.append("REMOVED physical_objects")

    # Rewrite nested legacy keys everywhere
    n = _rewrite_ref_keys(
        data,
        {
            "physical_object_ref": "carrier_ref",
            "physical_object_refs": "carrier_refs",
        },
    )
    if n:
        report_lines.append(f"REWROTE {n} legacy ref keys")

    # integrity_digest: only for demo/fixtures
    if demo:
        for binding_key in ("data_model_bindings",):
            for b in data.get(binding_key) or []:
                if isinstance(b, dict) and "integrity_digest" in b:
                    payload = json.dumps(b.get("selections") or [], sort_keys=True)
                    digest = "sha256:" + hashlib.sha256(payload.encode()).hexdigest()
                    b["integrity_digest"] = digest
                    report_lines.append(
                        f"RECOMPUTED integrity_digest for {b.get('element_id')} (demo)"
                    )

    after_ids = _collect_element_ids(data)
    after_fields = _count_fields(data)

    # Invariants
    lost = before_ids - after_ids - set(skipped_columns)
    # column element_ids intentionally dropped
    if lost:
        errors.append(f"INVARIANT element_id lost: {sorted(lost)[:20]}")
    if before_fields != after_fields and skipped_columns:
        # columns may have been nested fields; fields count should match non-column
        pass
    if before_fields != after_fields:
        report_lines.append(
            f"NOTE field count before={before_fields} after={after_fields} "
            f"(skipped_columns={len(skipped_columns)})"
        )

    return {
        "changed": True,
        "report": report_lines,
        "before_ids": before_ids,
        "after_ids": after_ids,
        "before_fields": before_fields,
        "after_fields": after_fields,
        "transitional_namespace": transitional_ns,
        "skipped_columns": skipped_columns,
        "errors": errors,
    }


def migrate_file(
    path: Path,
    *,
    write: bool = True,
    demo: bool = False,
    report_dir: Path | None = None,
) -> dict[str, Any]:
    data, engine = _load_yaml(path)
    if not isinstance(data, dict):
        return {"path": str(path), "changed": False, "errors": ["not a mapping"]}

    # SpecImpl envelope: body may be nested
    body = data
    if "spec" in data and isinstance(data["spec"], dict) and "body" in data["spec"]:
        body = data["spec"]["body"]
    elif "body" in data and isinstance(data["body"], dict):
        body = data["body"]

    # Detect ModelPackage-like root
    target = body if isinstance(body, dict) else data
    # If physical_objects at top level of data (solution model style)
    if "physical_objects" in data or any(k in data for k in COLLECTION_KEYS):
        target = data
    elif "physical_objects" in (body or {}) or any(
        k in (body or {}) for k in COLLECTION_KEYS
    ):
        target = body

    result = migrate_document(target, demo=demo)
    result["path"] = str(path)
    result["engine"] = engine

    if write and result.get("changed"):
        _dump_yaml(data, path, engine)

    if report_dir:
        report_dir.mkdir(parents=True, exist_ok=True)
        md = report_dir / f"{path.stem}-migration-report.md"
        lines = [
            f"# Migration report: `{path}`\n",
            f"- changed: {result.get('changed')}\n",
            f"- fields: {result.get('before_fields')} → {result.get('after_fields')}\n",
            f"- element_ids: {len(result.get('before_ids') or [])} → "
            f"{len(result.get('after_ids') or [])}\n",
            "\n## Log\n",
        ]
        for line in result.get("report") or []:
            lines.append(f"- {line}\n")
        if result.get("transitional_namespace"):
            lines.append("\n## Transitional namespace assets\n")
            for eid in result["transitional_namespace"]:
                lines.append(f"- `{eid}`\n")
        if result.get("errors"):
            lines.append("\n## Errors\n")
            for e in result["errors"]:
                lines.append(f"- {e}\n")
        md.write_text("".join(lines), encoding="utf-8")
        result["report_path"] = str(md)

    return result


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("paths", nargs="+", type=Path, help="YAML model files")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--demo", action="store_true", help="Allow integrity_digest recompute")
    p.add_argument(
        "--report-dir",
        type=Path,
        default=Path("docs/migration/reports"),
    )
    args = p.parse_args(argv)

    rc = 0
    for path in args.paths:
        if not path.is_file():
            print(f"MISSING {path}", file=sys.stderr)
            rc = 1
            continue
        result = migrate_file(
            path,
            write=not args.dry_run,
            demo=args.demo,
            report_dir=args.report_dir,
        )
        status = "CHANGED" if result.get("changed") else "OK"
        print(f"{status} {path}")
        for e in result.get("errors") or []:
            print(f"  ERROR: {e}", file=sys.stderr)
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
