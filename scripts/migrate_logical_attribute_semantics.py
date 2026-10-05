#!/usr/bin/env python3
"""Migrate LogicalAttribute representation to DataType / ValueDomain (ADR-037).

Modes:
  --apply   create DataType/ValueDomain, set data_type_ref/value_domain_ref
  --propose write ConceptualProperty candidates (does not modify model)

Does NOT auto-create ConceptualProperty. Denylist includes moex-dams-full.yaml.
Idempotent: re-run yields empty diff when already migrated.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

DENYLIST_NAMES = frozenset({"moex-dams-full.yaml"})
DENYLIST_MARKERS = ("не редактировать вручную", "do not edit", "auto-generated")

STARTER_TYPES: dict[str, dict[str, Any]] = {
    "string": {
        "type_name": "string",
        "type_family": "string",
        "xsd_datatype": "xsd:string",
        "linkml_type": "string",
    },
    "integer": {
        "type_name": "integer",
        "type_family": "integer",
        "xsd_datatype": "xsd:integer",
        "linkml_type": "integer",
    },
    "decimal": {
        "type_name": "decimal",
        "type_family": "decimal",
        "xsd_datatype": "xsd:decimal",
        "linkml_type": "decimal",
    },
    "boolean": {
        "type_name": "boolean",
        "type_family": "boolean",
        "xsd_datatype": "xsd:boolean",
        "linkml_type": "boolean",
    },
    "date": {
        "type_name": "date",
        "type_family": "date",
        "xsd_datatype": "xsd:date",
        "linkml_type": "date",
    },
    "datetime": {
        "type_name": "datetime",
        "type_family": "datetime",
        "xsd_datatype": "xsd:dateTime",
        "linkml_type": "datetime",
    },
    "time": {
        "type_name": "time",
        "type_family": "time",
        "xsd_datatype": "xsd:time",
        "linkml_type": "time",
    },
    "binary": {
        "type_name": "binary",
        "type_family": "binary",
        "xsd_datatype": "xsd:base64Binary",
        "linkml_type": "base64binary",
    },
    "identifier": {
        "type_name": "identifier",
        "type_family": "identifier",
        "xsd_datatype": "xsd:string",
        "linkml_type": "string",
    },
    "uri": {
        "type_name": "uri",
        "type_family": "uri",
        "xsd_datatype": "xsd:anyURI",
        "linkml_type": "uri",
    },
    "object": {
        "type_name": "object",
        "type_family": "object",
        "xsd_datatype": "xsd:anyType",
        "linkml_type": "object",
    },
    "float": {
        "type_name": "float",
        "type_family": "float",
        "xsd_datatype": "xsd:float",
        "linkml_type": "float",
    },
    "duration": {
        "type_name": "duration",
        "type_family": "duration",
        "xsd_datatype": "xsd:duration",
        "linkml_type": "duration",
    },
    "array": {
        "type_name": "array",
        "type_family": "array",
        "xsd_datatype": "xsd:anyType",
        "linkml_type": "string",
    },
}


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


def is_denied(path: Path) -> bool:
    if path.name in DENYLIST_NAMES:
        return True
    try:
        head = path.read_text(encoding="utf-8")[:2000].lower()
    except OSError:
        return False
    return any(m in head for m in DENYLIST_MARKERS)


def _type_id(logical_type: str) -> str:
    return f"dams:datatype/{logical_type}"


def _ensure_data_types(data: dict[str, Any], *, allow_create: bool) -> dict[str, str]:
    """Ensure starter DataType entries when allow_create; return map type_name -> id."""
    existing = {
        str(dt.get("type_name") or ""): str(dt.get("element_id") or "")
        for dt in (data.get("data_types") or [])
        if isinstance(dt, dict)
    }
    for lt in STARTER_TYPES:
        existing.setdefault(lt, _type_id(lt))
    if not allow_create:
        return existing
    types = list(data.get("data_types") or [])
    for lt, spec in STARTER_TYPES.items():
        if any(str(dt.get("type_name")) == lt for dt in types if isinstance(dt, dict)):
            continue
        eid = _type_id(lt)
        types.append(
            {
                "element_id": eid,
                "name": lt,
                "description": f"Корпоративный тип {lt} (стартовый набор).",
                "lifecycle_status": "active",
                "type_name": spec["type_name"],
                "type_family": spec["type_family"],
                "xsd_datatype": spec["xsd_datatype"],
                "linkml_type": spec["linkml_type"],
                "tags": ["generated", "generated_by_migration"],
            }
        )
        existing[lt] = eid
    data["data_types"] = types
    return existing


def _domain_key(attr: dict[str, Any]) -> tuple[Any, ...]:
    return (
        attr.get("logical_type"),
        attr.get("format_pattern"),
        attr.get("unit_code"),
        attr.get("value_set_ref"),
        attr.get("timezone_policy"),
    )


def _domain_id(key: tuple[Any, ...]) -> str:
    digest = hashlib.sha1(repr(key).encode("utf-8")).hexdigest()[:12]
    return f"dams:valuedomain/generated-{digest}"


def _needs_domain(key: tuple[Any, ...]) -> bool:
    _lt, fmt, unit, vs, _tz = key
    return bool(fmt or unit or vs)


def migrate_package(data: dict[str, Any], *, apply: bool) -> dict[str, Any]:
    """Mutate package in place when apply=True; always return report."""
    report: dict[str, Any] = {
        "attributes_before": 0,
        "attributes_after": 0,
        "domains_created": [],
        "types_ensured": [],
        "attrs_updated": [],
        "proposed_properties": [],
        "ambiguous": [],
        "skipped_denied": False,
    }
    if not isinstance(data, dict):
        return report

    is_enterprise = str(data.get("implementation_scope") or "") == "enterprise"
    type_map = _ensure_data_types(data, allow_create=apply and is_enterprise)
    if apply and is_enterprise:
        report["types_ensured"] = sorted(type_map.keys())
    elif apply:
        # Solution packages reference corporate CURIEs only — no local DataType copy.
        report["types_ensured"] = []
        # Drop any previously generated local data_types from a mistaken apply.
        dts = [
            dt
            for dt in (data.get("data_types") or [])
            if isinstance(dt, dict)
            and "generated_by_migration" not in (dt.get("tags") or [])
        ]
        if dts:
            data["data_types"] = dts
        elif "data_types" in data:
            del data["data_types"]

    existing_domains = {
        str(vd.get("element_id") or ""): vd
        for vd in (data.get("value_domains") or [])
        if isinstance(vd, dict)
    }
    domain_by_key: dict[tuple[Any, ...], str] = {}
    for vd in existing_domains.values():
        # reverse-map via tags not reliable; rebuild from content
        key = (
            None,  # logical type unknown from domain alone
            vd.get("format_pattern"),
            vd.get("unit_code"),
            vd.get("value_set_source"),
            None,
        )
        domain_by_key[key] = str(vd.get("element_id"))

    value_domains = list(data.get("value_domains") or [])
    attrs_flat: list[dict[str, Any]] = []
    for ent in data.get("logical_entities") or []:
        if not isinstance(ent, dict):
            continue
        for attr in ent.get("attributes") or []:
            if isinstance(attr, dict):
                attrs_flat.append(attr)

    report["attributes_before"] = len(attrs_flat)

    # Group for domain creation
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for attr in attrs_flat:
        groups[_domain_key(attr)].append(attr)

    for key, group in groups.items():
        lt, fmt, unit, vs, _tz = key
        lt_s = str(lt or "string")
        type_eid = type_map.get(lt_s) or _type_id(lt_s)

        if apply and not _needs_domain(key):
            for attr in group:
                if not attr.get("data_type_ref"):
                    attr["data_type_ref"] = type_eid
                    report["attrs_updated"].append(str(attr.get("element_id")))
            continue

        if apply and _needs_domain(key):
            did = _domain_id(key)
            if did not in existing_domains:
                kind = "reference_set" if vs else "described"
                vd: dict[str, Any] = {
                    "element_id": did,
                    "name": f"generated-{did.split('-')[-1]}",
                    "description": "Автосгенерированный ValueDomain (миграция).",
                    "lifecycle_status": "active",
                    "value_domain_kind": kind,
                    "data_type_ref": type_eid,
                    "tags": ["generated", "generated_by_migration"],
                }
                if fmt:
                    vd["format_pattern"] = fmt
                if unit:
                    vd["unit_code"] = unit
                if vs:
                    vd["value_set_source"] = vs
                value_domains.append(vd)
                existing_domains[did] = vd
                report["domains_created"].append(did)
            for attr in group:
                changed = False
                if not attr.get("value_domain_ref"):
                    attr["value_domain_ref"] = did
                    changed = True
                if not attr.get("data_type_ref"):
                    attr["data_type_ref"] = type_eid
                    changed = True
                if changed:
                    report["attrs_updated"].append(str(attr.get("element_id")))

    if apply:
        data["value_domains"] = value_domains

    # Propose ConceptualProperty candidates (never auto-create)
    name_type_solutions: dict[tuple[str, str], set[str]] = defaultdict(set)
    solution = str(data.get("solution_ref") or data.get("name") or "unknown")
    for attr in attrs_flat:
        nm = str(attr.get("name") or "")
        lt = str(attr.get("logical_type") or attr.get("data_type_ref") or "")
        if nm and lt:
            name_type_solutions[(nm, lt)].add(solution)

    for ent in data.get("logical_entities") or []:
        if not isinstance(ent, dict):
            continue
        keys = ent.get("key_attribute_refs") or []
        for kid in keys:
            report["proposed_properties"].append(
                {
                    "basis": ["identifying"],
                    "attribute_ref": kid,
                    "owner_logical_entity": ent.get("element_id"),
                    "mode": "propose",
                }
            )

    for (nm, lt), sols in name_type_solutions.items():
        if len(sols) >= 2:
            report["proposed_properties"].append(
                {
                    "basis": ["cross_solution"],
                    "name": nm,
                    "logical_type": lt,
                    "solutions": sorted(sols),
                    "mode": "propose",
                }
            )

    for attr in attrs_flat:
        if attr.get("critical_data_element") is True and not attr.get("concept_ref"):
            report["proposed_properties"].append(
                {
                    "basis": ["critical_data"],
                    "attribute_ref": attr.get("element_id"),
                    "mode": "propose",
                }
            )

    report["attributes_after"] = len(attrs_flat)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="YAML ModelPackage files")
    parser.add_argument("--apply", action="store_true", help="Write DataType/ValueDomain")
    parser.add_argument(
        "--propose",
        action="store_true",
        help="Write proposed-properties.yaml (no model changes for properties)",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Write JSON report path",
    )
    parser.add_argument(
        "--propose-out",
        type=Path,
        default=Path("proposed-properties.yaml"),
        help="Output for --propose",
    )
    args = parser.parse_args(argv)

    if not args.apply and not args.propose:
        print("Specify --apply and/or --propose", file=sys.stderr)
        return 2

    all_reports: list[dict[str, Any]] = []
    all_proposals: list[dict[str, Any]] = []

    for path in args.paths:
        if is_denied(path):
            all_reports.append(
                {"path": str(path), "skipped_denied": True, "reason": "denylist"}
            )
            print(f"SKIP (denylist): {path}")
            continue
        data, engine = _load_yaml(path)
        if not isinstance(data, dict):
            print(f"SKIP (not mapping): {path}")
            continue
        report = migrate_package(data, apply=args.apply)
        report["path"] = str(path)
        all_reports.append(report)
        all_proposals.extend(report.get("proposed_properties") or [])
        if args.apply:
            _dump_yaml(data, path, engine)
            print(
                f"APPLY {path}: attrs={report['attributes_before']} "
                f"updated={len(report['attrs_updated'])} "
                f"domains={len(report['domains_created'])}"
            )
        else:
            print(f"PROPOSE-scan {path}: candidates={len(report['proposed_properties'])}")

    if args.propose:
        import yaml

        args.propose_out.write_text(
            yaml.safe_dump(
                {"proposed_conceptual_properties": all_proposals},
                allow_unicode=True,
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        print(f"Wrote {args.propose_out} ({len(all_proposals)} candidates)")

    if args.report:
        args.report.write_text(
            json.dumps(all_reports, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"Wrote report {args.report}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
