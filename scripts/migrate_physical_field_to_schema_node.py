#!/usr/bin/env python3
"""Migrate DataCarrier.physical_fields to DataStructure / SchemaNode (ADR-038/039).

Idempotent: re-running on already-migrated YAML is a no-op (empty local_key set
change). Preserves order/comments via ruamel.yaml when available; falls back to
PyYAML.

CLI:
  python scripts/migrate_physical_field_to_schema_node.py PATH [PATH ...]
      [--apply] [--report PATH] [--demo]
"""

from __future__ import annotations

import argparse
import copy
import re
import sys
from pathlib import Path
from typing import Any

_SRC = Path(__file__).resolve().parents[1] / "packages" / "specification-dams" / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from moex_dams.application.binding_revision import (  # noqa: E402
    apply_binding_revision_policy,
)

ROOT_KEY = "root"
LOCAL_KEY_RE = re.compile(r"^[a-z0-9_.-]+$")
HTTP_URI_RE = re.compile(r"^https?://", re.IGNORECASE)

# Slots moved from PhysicalField onto SchemaNode
FIELD_NODE_SLOTS = (
    "native_name",
    "native_type",
    "required",
    "ordinal_position",
    "mapping_coverage_status",
    "mapping_rationale",
    "description",
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


def _last_segment(ref: Any) -> str:
    s = str(ref or "").strip()
    if not s:
        return "unknown"
    if "#" in s:
        s = s.split("#", 1)[0]
    if "/" in s:
        return s.rsplit("/", 1)[-1]
    if ":" in s:
        return s.rsplit(":", 1)[-1]
    return s


def _package_slug(carrier: dict[str, Any], data: dict[str, Any]) -> str:
    """Derive namespace slug for dams:structure/{slug}/{name}."""
    eid = str(carrier.get("element_id") or "")
    # dams:physical/{slug}/{name} or dams:carrier/{slug}/{name}
    parts = eid.split("/")
    if len(parts) >= 3 and parts[0].startswith("dams:"):
        return _slug_token(parts[1]) or "unknown"
    sys_ref = str(carrier.get("system_ref") or data.get("system_ref") or "")
    if sys_ref:
        return _slug_token(_last_segment(sys_ref)) or "unknown"
    sol = str(carrier.get("solution_ref") or data.get("solution_ref") or "")
    if sol:
        return _slug_token(_last_segment(sol)) or "unknown"
    return "unknown"


def _slug_token(text: str) -> str:
    """Lowercase slug; alphabet [a-z0-9_.-]; other chars → _."""
    s = str(text or "").strip().lower()
    out: list[str] = []
    for ch in s:
        if ("a" <= ch <= "z") or ("0" <= ch <= "9") or ch in "_.-":
            out.append(ch)
        else:
            out.append("_")
    token = "".join(out)
    token = re.sub(r"_+", "_", token).strip("_.-")
    return token or "_"


def _path_segments(field: dict[str, Any]) -> list[str]:
    raw = field.get("schema_path")
    if raw is None or str(raw).strip() == "":
        raw = field.get("native_name") or field.get("name") or "field"
    parts = [p for p in str(raw).split(".") if p != ""]
    if not parts:
        parts = ["field"]
    return [_slug_token(p) for p in parts]


def _allocate_key(
    preferred: str,
    used: set[str],
    collisions: list[str],
    *,
    context: str,
) -> str:
    key = preferred if LOCAL_KEY_RE.match(preferred) else _slug_token(preferred)
    if key not in used:
        used.add(key)
        return key
    n = 2
    while f"{key}-{n}" in used:
        n += 1
    alt = f"{key}-{n}"
    used.add(alt)
    collisions.append(
        f"COLLISION local_key {preferred!r} → {alt!r} ({context})"
    )
    return alt


def _ensure_object_node(
    nodes: dict[str, dict[str, Any]],
    key: str,
    parent_key: str,
) -> None:
    if key not in nodes:
        nodes[key] = {
            "local_key": key,
            "node_kind": "object",
            "children": [],
        }
    parent = nodes[parent_key]
    children = list(parent.get("children") or [])
    if key not in children:
        children.append(key)
        parent["children"] = children


def _scalar_from_field(field: dict[str, Any], local_key: str) -> dict[str, Any]:
    node: dict[str, Any] = {
        "local_key": local_key,
        "node_kind": "scalar",
    }
    for slot in FIELD_NODE_SLOTS:
        if slot in field and field[slot] is not None:
            node[slot] = copy.deepcopy(field[slot])
    # ordinal_position → also column_position for relational structures
    if "ordinal_position" in node and "column_position" not in node:
        node["column_position"] = node["ordinal_position"]
    elif field.get("ordinal_position") is not None and "column_position" not in node:
        node["column_position"] = field["ordinal_position"]
        node["ordinal_position"] = field["ordinal_position"]
    return node


def build_nodes_from_fields(
    fields: list[dict[str, Any]],
    *,
    structure_id: str,
    carrier_id: str,
) -> tuple[list[dict[str, Any]], dict[str, str], list[str], list[str]]:
    """Build flat SchemaNode list from PhysicalField list.

    Returns (nodes, field_eid→structure#local_key, collisions, errors).
    """
    collisions: list[str] = []
    errors: list[str] = []
    used: set[str] = {ROOT_KEY}
    nodes: dict[str, dict[str, Any]] = {
        ROOT_KEY: {
            "local_key": ROOT_KEY,
            "node_kind": "object",
            "children": [],
        }
    }
    field_map: dict[str, str] = {}

    for field in fields:
        if not isinstance(field, dict):
            continue
        field_eid = str(field.get("element_id") or "")
        segments = _path_segments(field)
        preferred_leaf = ".".join(segments)
        context = field_eid or preferred_leaf

        # Intermediate object nodes for dotted paths
        parent_key = ROOT_KEY
        for i, _seg in enumerate(segments[:-1]):
            obj_key = ".".join(segments[: i + 1])
            if obj_key in nodes and nodes[obj_key].get("node_kind") != "object":
                errors.append(
                    f"ERROR: path conflict — {obj_key!r} already non-object "
                    f"while building {context}"
                )
                continue
            if obj_key not in used:
                used.add(obj_key)
            _ensure_object_node(nodes, obj_key, parent_key)
            parent_key = obj_key

        leaf_key = _allocate_key(
            preferred_leaf,
            used,
            collisions,
            context=context,
        )
        if leaf_key in nodes and nodes[leaf_key].get("node_kind") == "object":
            errors.append(
                f"ERROR: path conflict — leaf {leaf_key!r} collides with object "
                f"node ({context})"
            )
            continue

        nodes[leaf_key] = _scalar_from_field(field, leaf_key)
        parent = nodes[parent_key]
        children = list(parent.get("children") or [])
        if leaf_key not in children:
            children.append(leaf_key)
            parent["children"] = children

        if field_eid:
            field_map[field_eid] = f"{structure_id}#{leaf_key}"

    # Stable order: root first, then by local_key
    ordered = [nodes[ROOT_KEY]] + [
        nodes[k] for k in sorted(nodes.keys()) if k != ROOT_KEY
    ]
    return ordered, field_map, collisions, errors


def _structure_element_id(carrier: dict[str, Any], data: dict[str, Any]) -> str:
    slug = _package_slug(carrier, data)
    name = str(carrier.get("name") or "").strip() or _last_segment(
        carrier.get("element_id")
    )
    return f"dams:structure/{slug}/{name}"


def _message_element_id(carrier: dict[str, Any], data: dict[str, Any]) -> str:
    slug = _package_slug(carrier, data)
    name = str(carrier.get("name") or "").strip() or _last_segment(
        carrier.get("element_id")
    )
    return f"dams:message/{slug}/{name}"


def _is_http_uri(value: Any) -> bool:
    return bool(HTTP_URI_RE.match(str(value or "").strip()))


def _count_physical_fields(data: dict[str, Any]) -> int:
    n = 0
    for carrier in data.get("data_carriers") or []:
        if isinstance(carrier, dict):
            n += len(carrier.get("physical_fields") or [])
    return n


def _count_field_mappings(data: dict[str, Any]) -> int:
    n = 0
    for m in data.get("mappings") or []:
        if isinstance(m, dict) and str(m.get("mapping_type") or "") == "field_mapping":
            n += 1
    return n


def _collect_local_keys(data: dict[str, Any]) -> set[str]:
    keys: set[str] = set()
    for st in data.get("data_structures") or []:
        if not isinstance(st, dict):
            continue
        for node in st.get("nodes") or []:
            if isinstance(node, dict) and node.get("local_key"):
                keys.add(str(node["local_key"]))
    return keys


def _count_scalar_nodes(data: dict[str, Any]) -> int:
    n = 0
    for st in data.get("data_structures") or []:
        if not isinstance(st, dict):
            continue
        for node in st.get("nodes") or []:
            if isinstance(node, dict) and str(node.get("node_kind") or "") == "scalar":
                n += 1
    return n


def _carriers_needing_migration(data: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for carrier in data.get("data_carriers") or []:
        if isinstance(carrier, dict) and (carrier.get("physical_fields") or []):
            out.append(carrier)
    return out


def _rewrite_ref_value(value: Any, field_map: dict[str, str]) -> Any:
    if isinstance(value, str) and value in field_map:
        return field_map[value]
    return value


def _rewrite_mapping_refs(data: dict[str, Any], field_map: dict[str, str]) -> int:
    """Rewrite field_mapping source/target refs. Returns number of replaced values."""
    changed = 0
    for mapping in data.get("mappings") or []:
        if not isinstance(mapping, dict):
            continue
        if str(mapping.get("mapping_type") or "") != "field_mapping":
            continue
        for slot in ("source_refs", "target_refs"):
            refs = mapping.get(slot)
            if not isinstance(refs, list):
                continue
            new_refs: list[Any] = []
            for ref in refs:
                new = _rewrite_ref_value(ref, field_map)
                if new != ref:
                    changed += 1
                new_refs.append(new)
            mapping[slot] = new_refs
    return changed


def _rewrite_physical_field_refs_everywhere(
    node: Any,
    field_map: dict[str, str],
) -> int:
    """Rename physical_field_refs → schema_node_refs and rewrite CURIE values."""
    changed = 0
    if isinstance(node, dict):
        if "physical_field_refs" in node:
            old = node.pop("physical_field_refs")
            new_list: list[Any] = []
            if isinstance(old, list):
                for ref in old:
                    new = _rewrite_ref_value(ref, field_map)
                    if new != ref:
                        changed += 1
                    new_list.append(new)
            else:
                new_list = old
            existing = list(node.get("schema_node_refs") or [])
            # merge unique
            for item in new_list if isinstance(new_list, list) else []:
                if item not in existing:
                    existing.append(item)
            node["schema_node_refs"] = existing
            changed += 1
        for v in list(node.values()):
            changed += _rewrite_physical_field_refs_everywhere(v, field_map)
    elif isinstance(node, list):
        for item in node:
            changed += _rewrite_physical_field_refs_everywhere(item, field_map)
    return changed


def _find_parent_channel(
    carrier_id: str,
    access_points: list[dict[str, Any]],
    errors: list[str],
) -> dict[str, Any] | None:
    matches: list[dict[str, Any]] = []
    for ap in access_points:
        if not isinstance(ap, dict):
            continue
        serves = {str(x) for x in (ap.get("serves_refs") or [])}
        if carrier_id not in serves:
            continue
        kind = str(ap.get("asset_kind") or "")
        if kind in ("channel", "operation"):
            matches.append(ap)
    channels = [m for m in matches if str(m.get("asset_kind")) == "channel"]
    pool = channels if channels else matches
    if len(pool) == 1:
        return pool[0]
    if len(pool) > 1:
        errors.append(
            f"ERROR: message_type carrier {carrier_id} has ambiguous parent "
            f"channel/operation: {[m.get('element_id') for m in pool]}"
        )
        return None
    errors.append(
        f"ERROR: message_type carrier {carrier_id} has no unambiguous parent "
        f"AccessPoint (channel|operation) via serves_refs"
    )
    return None


def _make_structure(
    *,
    structure_id: str,
    carrier: dict[str, Any],
    nodes: list[dict[str, Any]],
    old_structure_ref: Any,
    report_lines: list[str],
) -> dict[str, Any]:
    name = str(carrier.get("name") or "").strip() or _last_segment(
        carrier.get("element_id")
    )
    structure: dict[str, Any] = {
        "element_id": structure_id,
        "name": name,
        "description": carrier.get("description")
        or f"Structure migrated from {carrier.get('element_id')}",
        "lifecycle_status": carrier.get("lifecycle_status") or "draft",
        "schema_format": "relational",
        "structure_version": "1.0.0",
        "root_local_key": ROOT_KEY,
        "nodes": nodes,
    }
    if _is_http_uri(old_structure_ref):
        structure["source_artifact_ref"] = str(old_structure_ref)
        report_lines.append(
            f"MOVED structure_ref → source_artifact_ref: {old_structure_ref} "
            f"({carrier.get('element_id')})"
        )
    elif old_structure_ref:
        report_lines.append(
            f"NOTE opaque structure_ref not copied to source_artifact_ref: "
            f"{old_structure_ref!r} on {carrier.get('element_id')}"
        )
    return structure


def migrate_document(data: dict[str, Any], *, demo: bool = False) -> dict[str, Any]:
    """Migrate physical_fields → DataStructure/SchemaNode in place."""
    report_lines: list[str] = []
    errors: list[str] = []
    collisions: list[str] = []

    before_fields = _count_physical_fields(data)
    before_mappings = _count_field_mappings(data)
    before_keys = _collect_local_keys(data)

    needing = _carriers_needing_migration(data)
    if not needing:
        # Still rename leftover physical_field_refs keys if any (values already CURIEs)
        n = _rewrite_physical_field_refs_everywhere(data, {})
        if n and "physical_field_refs" not in str(data):
            pass
        after_keys = _collect_local_keys(data)
        return {
            "changed": False,
            "report": ["idempotent: no physical_fields to migrate"],
            "before_fields": before_fields,
            "after_fields": _count_physical_fields(data),
            "before_mappings": before_mappings,
            "after_mappings": _count_field_mappings(data),
            "before_keys": before_keys,
            "after_keys": after_keys,
            "scalar_nodes": _count_scalar_nodes(data),
            "collisions": [],
            "errors": [],
            "field_map": {},
        }

    structures = list(data.get("data_structures") or [])
    existing_structure_ids = {
        str(s.get("element_id"))
        for s in structures
        if isinstance(s, dict) and s.get("element_id")
    }
    messages = list(data.get("messages") or [])
    existing_message_ids = {
        str(m.get("element_id"))
        for m in messages
        if isinstance(m, dict) and m.get("element_id")
    }
    access_points = [
        ap for ap in (data.get("access_points") or []) if isinstance(ap, dict)
    ]

    field_map: dict[str, str] = {}
    carriers_out: list[Any] = []
    removed_carriers: list[str] = []

    for carrier in data.get("data_carriers") or []:
        if not isinstance(carrier, dict):
            carriers_out.append(carrier)
            continue

        fields = [
            f for f in (carrier.get("physical_fields") or []) if isinstance(f, dict)
        ]
        if not fields:
            carriers_out.append(carrier)
            continue

        carrier_id = str(carrier.get("element_id") or "")
        asset_kind = str(carrier.get("asset_kind") or "")
        structure_id = _structure_element_id(carrier, data)
        old_ref = carrier.get("structure_ref")

        nodes, fmap, colls, errs = build_nodes_from_fields(
            fields,
            structure_id=structure_id,
            carrier_id=carrier_id,
        )
        collisions.extend(colls)
        errors.extend(errs)
        field_map.update(fmap)

        if structure_id not in existing_structure_ids:
            structures.append(
                _make_structure(
                    structure_id=structure_id,
                    carrier=carrier,
                    nodes=nodes,
                    old_structure_ref=old_ref,
                    report_lines=report_lines,
                )
            )
            existing_structure_ids.add(structure_id)
            report_lines.append(
                f"CREATE DataStructure {structure_id} "
                f"scalars={sum(1 for n in nodes if n.get('node_kind') == 'scalar')} "
                f"from {carrier_id}"
            )
        else:
            report_lines.append(
                f"REUSE DataStructure {structure_id} for {carrier_id}"
            )

        if asset_kind == "message_type":
            message_id = _message_element_id(carrier, data)
            parent = _find_parent_channel(carrier_id, access_points, errors)
            if message_id not in existing_message_ids:
                msg: dict[str, Any] = {
                    "element_id": message_id,
                    "name": str(carrier.get("name") or _last_segment(carrier_id)),
                    "description": carrier.get("description")
                    or f"Message migrated from {carrier_id}",
                    "lifecycle_status": carrier.get("lifecycle_status") or "draft",
                    "payload_structure_ref": structure_id,
                }
                if carrier.get("data_format"):
                    msg["content_type"] = carrier["data_format"]
                messages.append(msg)
                existing_message_ids.add(message_id)
                report_lines.append(
                    f"CREATE Message {message_id} payload={structure_id}"
                )

            if parent is not None:
                refs = list(parent.get("message_refs") or [])
                if message_id not in refs:
                    refs.append(message_id)
                    parent["message_refs"] = refs
                serves = [
                    s
                    for s in (parent.get("serves_refs") or [])
                    if str(s) != carrier_id
                ]
                if serves:
                    parent["serves_refs"] = serves
                elif "serves_refs" in parent:
                    parent.pop("serves_refs", None)
                report_lines.append(
                    f"LINK AccessPoint {parent.get('element_id')} "
                    f"message_refs+={message_id}; removed serves {carrier_id}"
                )

            removed_carriers.append(carrier_id)
            report_lines.append(f"REMOVE message_type carrier {carrier_id}")
            continue

        # Regular carrier: point structure_ref, drop physical_fields
        new_carrier = dict(carrier)
        new_carrier["structure_ref"] = structure_id
        new_carrier.pop("physical_fields", None)
        carriers_out.append(new_carrier)
        report_lines.append(
            f"UPDATE carrier {carrier_id} structure_ref={structure_id}; "
            f"removed physical_fields ({len(fields)})"
        )

    data["data_carriers"] = carriers_out
    if structures:
        data["data_structures"] = structures
    if messages:
        data["messages"] = messages

    n_map = _rewrite_mapping_refs(data, field_map)
    if n_map:
        report_lines.append(f"REWROTE {n_map} field_mapping refs → structure#local_key")

    n_pref = _rewrite_physical_field_refs_everywhere(data, field_map)
    if n_pref:
        report_lines.append(
            f"REWROTE physical_field_refs → schema_node_refs ({n_pref} ops)"
        )

    for line in collisions:
        report_lines.append(line)

    report_lines.extend(
        apply_binding_revision_policy(
            data,
            demo=demo,
            reason="physical-field-to-schema-node-migration",
        )
    )

    after_fields = _count_physical_fields(data)
    after_mappings = _count_field_mappings(data)
    after_keys = _collect_local_keys(data)
    scalar_nodes = _count_scalar_nodes(data)

    if before_fields != scalar_nodes and not errors:
        # Intermediate object nodes excluded from scalar count by design;
        # scalar count should equal PhysicalField count for migrated carriers.
        report_lines.append(
            f"NOTE scalar_nodes={scalar_nodes} physical_fields_before={before_fields}"
        )
    if before_mappings != after_mappings:
        errors.append(
            f"INVARIANT field_mapping count {before_mappings} → {after_mappings}"
        )

    return {
        "changed": True,
        "report": report_lines,
        "before_fields": before_fields,
        "after_fields": after_fields,
        "before_mappings": before_mappings,
        "after_mappings": after_mappings,
        "before_keys": before_keys,
        "after_keys": after_keys,
        "scalar_nodes": scalar_nodes,
        "collisions": collisions,
        "errors": errors,
        "field_map": field_map,
        "removed_carriers": removed_carriers,
    }


def _resolve_target(data: dict[str, Any]) -> dict[str, Any]:
    """Pick ModelPackage-like mapping that holds data_carriers."""
    if "data_carriers" in data or "data_structures" in data:
        return data
    if "spec" in data and isinstance(data["spec"], dict):
        body = data["spec"].get("body")
        if isinstance(body, dict) and (
            "data_carriers" in body or "physical_fields" in str(body)
        ):
            return body
    if "body" in data and isinstance(data["body"], dict):
        body = data["body"]
        if "data_carriers" in body:
            return body
    return data


def format_migration_report_md(path: Path, result: dict[str, Any]) -> str:
    lines = [
        f"# Migration report: `{path}`\n",
        f"- changed: {result.get('changed')}\n",
        f"- physical_fields: {result.get('before_fields')} → "
        f"{result.get('after_fields')}\n",
        f"- scalar SchemaNode: {result.get('scalar_nodes')}\n",
        f"- field_mapping count: {result.get('before_mappings')} → "
        f"{result.get('after_mappings')}\n",
        f"- local_key set size: {len(result.get('before_keys') or [])} → "
        f"{len(result.get('after_keys') or [])}\n",
        "\n## Log\n",
    ]
    for line in result.get("report") or []:
        lines.append(f"- {line}\n")
    if result.get("collisions"):
        lines.append("\n## local_key collisions\n")
        for c in result["collisions"]:
            lines.append(f"- {c}\n")
    if result.get("field_map"):
        lines.append("\n## Field → SchemaNode map\n")
        for old, new in sorted((result.get("field_map") or {}).items()):
            lines.append(f"- `{old}` → `{new}`\n")
    if result.get("errors"):
        lines.append("\n## Errors\n")
        for e in result["errors"]:
            lines.append(f"- {e}\n")
    return "".join(lines)


def migrate_file(
    path: Path,
    *,
    apply: bool = False,
    demo: bool = False,
    report_path: Path | None = None,
) -> dict[str, Any]:
    data, engine = _load_yaml(path)
    if not isinstance(data, dict):
        return {"path": str(path), "changed": False, "errors": ["not a mapping"]}

    target = _resolve_target(data)
    # Dry-run: mutate a copy so source file stays intact unless --apply
    work = target if apply else copy.deepcopy(target)
    result = migrate_document(work, demo=demo)
    result["path"] = str(path)
    result["engine"] = engine

    if apply and result.get("changed"):
        # Copy mutated work back into original target when we deep-copied
        if work is not target:
            target.clear()
            target.update(work)
        _dump_yaml(data, path, engine)

    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            format_migration_report_md(path, result),
            encoding="utf-8",
        )
        result["report_path"] = str(report_path)

    return result


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("paths", nargs="+", type=Path, help="YAML ModelPackage files")
    p.add_argument(
        "--apply",
        action="store_true",
        help="Write migrated YAML in place (default: dry-run)",
    )
    p.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Write migration-report.md to this path "
        "(for multiple inputs, treated as directory)",
    )
    p.add_argument(
        "--demo",
        action="store_true",
        help="Recompute integrity_digest in place (fixtures); else new revision",
    )
    args = p.parse_args(argv)

    rc = 0
    multi = len(args.paths) > 1
    for path in args.paths:
        if not path.is_file():
            print(f"MISSING {path}", file=sys.stderr)
            rc = 1
            continue
        report_path: Path | None = None
        if args.report is not None:
            if multi or args.report.is_dir() or str(args.report).endswith(("/", "\\")):
                report_dir = args.report
                report_dir.mkdir(parents=True, exist_ok=True)
                report_path = report_dir / f"{path.stem}-migration-report.md"
            else:
                report_path = args.report

        result = migrate_file(
            path,
            apply=args.apply,
            demo=args.demo,
            report_path=report_path,
        )
        status = "CHANGED" if result.get("changed") else "OK"
        mode = "APPLY" if args.apply else "DRY-RUN"
        print(
            f"{mode} {status} {path} "
            f"fields={result.get('before_fields')}->{result.get('after_fields')} "
            f"scalars={result.get('scalar_nodes')}"
        )
        if result.get("report_path"):
            print(f"  report: {result['report_path']}")
        for e in result.get("errors") or []:
            print(f"  ERROR: {e}", file=sys.stderr)
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
