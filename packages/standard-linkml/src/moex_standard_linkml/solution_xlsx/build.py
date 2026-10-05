"""Project SolutionIR → WorkbookTables → map_er_dictionary → enrich."""

from __future__ import annotations

from typing import Any

from moex_standard_linkml.ingest.mapper import MapResult, map_er_dictionary
from moex_standard_linkml.ingest.workbook import SheetTable, WorkbookTables
from moex_standard_linkml.solution_xlsx.diagnostics import Diagnostic, Severity, SourceRef
from moex_standard_linkml.solution_xlsx.enrich import enrich_package
from moex_standard_linkml.solution_xlsx.ir import SolutionIR
from moex_standard_linkml.solution_xlsx.normalize import match_key
from moex_standard_linkml.solution_xlsx.profile import (
    SolutionXlsxProfile,
    SystemDefaults,
    system_to_ingest_profile,
)
from moex_standard_linkml.solution_xlsx.rules.fk_rules import parse_fk
from moex_standard_linkml.solution_xlsx.trace import TraceMap


def physical_name(raw: str, *, logical_names: set[str] | None = None) -> str:
    """Sanitize SrcObjectCode for mapper name keys (dots break Entity.attr refs).

    Prefix ``phys_`` when the sanitized name would collide with a logical
    entity name (bare-name resolution in map_er_dictionary prefers entities).
    """
    text = raw.strip()
    if not text:
        return text
    cleaned = text.replace(".", "_").replace(" ", "_")
    if logical_names and cleaned.casefold() in {n.casefold() for n in logical_names}:
        return f"phys_{cleaned}"
    return cleaned


def ir_to_workbook_tables(
    ir: SolutionIR,
    system: SystemDefaults,
) -> tuple[WorkbookTables, TraceMap]:
    """Build in-memory ER-dictionary tables from IR (mode A + physical B fields)."""
    trace = TraceMap()
    entities: list[dict[str, Any]] = []
    attributes: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    physical_objects: list[dict[str, Any]] = []
    physical_fields: list[dict[str, Any]] = []
    mappings: list[dict[str, Any]] = []

    phys_names: set[str] = set()
    field_keys: set[tuple[str, str]] = set()
    logical_names = {o.object_code for o in ir.objects.values()}

    # Sort objects by code for stability
    for key in sorted(ir.objects.keys()):
        obj = ir.objects[key]
        title = obj.object_name or obj.object_code
        desc = obj.src_description or title
        entities.append(
            {
                "name": obj.object_code,
                "title": title,
                "description": desc,
                "conceptual_ref": None,
            }
        )
        trace.bind_entity(obj.object_code, obj.source_ref)

        phys_raw = obj.src_object_code or obj.object_code
        phys_name = physical_name(phys_raw, logical_names=logical_names)
        if phys_name not in phys_names:
            phys_names.add(phys_name)
            physical_objects.append(
                {
                    "name": phys_name,
                    "title": obj.src_object_name or title,
                    "description": desc,
                    "object_kind": system.object_kind,
                    "qualified_name": phys_raw,
                    "technology": system.technology,
                    "system_ref": system.system_ref,
                    "direction": system.direction,
                    "native_schema_ref": system.native_schema_ref(phys_name),
                }
            )

    # Attributes sorted by sort_order then name
    attrs_sorted = sorted(
        ir.attributes,
        key=lambda a: (
            match_key(a.object_code) or "",
            a.sort_order if a.sort_order is not None else 10**9,
            a.attribute_code,
        ),
    )

    for attr in attrs_sorted:
        attributes.append(
            {
                "entity": attr.object_code,
                "name": attr.attribute_code,
                "title": attr.attribute_description or attr.attribute_code,
                "description": attr.attribute_description or attr.attribute_code,
                "type": attr.data_type or "string",
                "required": "Y" if (attr.mandatory or attr.pk) else None,
                "pk": "Y" if attr.pk else None,
            }
        )
        trace.bind_attribute(attr.object_code, attr.attribute_code, attr.source_ref)

        if attr.src_attribute_code:
            obj = ir.object_by_code(attr.object_code)
            phys_raw = (
                (obj.src_object_code if obj and obj.src_object_code else None)
                or attr.src_object_code
                or attr.object_code
            )
            phys_name = physical_name(phys_raw, logical_names=logical_names)
            if phys_name not in phys_names:
                phys_names.add(phys_name)
                physical_objects.append(
                    {
                        "name": phys_name,
                        "title": phys_raw,
                        "description": phys_raw,
                        "object_kind": system.object_kind,
                        "qualified_name": phys_raw,
                        "technology": system.technology,
                        "system_ref": system.system_ref,
                        "direction": system.direction,
                        "native_schema_ref": system.native_schema_ref(phys_name),
                    }
                )
            # Field names may also contain dots — sanitize for dotted refs
            field_name = physical_name(attr.src_attribute_code)
            fkey = (phys_name, field_name)
            if fkey not in field_keys:
                field_keys.add(fkey)
                physical_fields.append(
                    {
                        "object": phys_name,
                        "name": field_name,
                        "description": attr.src_attribute_description
                        or attr.attribute_description
                        or attr.src_attribute_code,
                        "native_name": attr.src_attribute_code,
                        "native_type": attr.src_data_type or attr.data_type or "string",
                        "required": "Y" if (attr.mandatory or attr.pk) else None,
                    }
                )
            map_name = f"map_{attr.object_code}_{attr.attribute_code}"
            lineage = ""
            if attr.base_src_scode or attr.base_src_object_code:
                lineage = (
                    f" BaseSrc={attr.base_src_scode or ''}/"
                    f"{attr.base_src_sname or ''}/"
                    f"{attr.base_src_object_code or ''}"
                )
            mappings.append(
                {
                    "name": map_name,
                    "source": f"{attr.object_code}.{attr.attribute_code}",
                    "target": f"{phys_name}.{field_name}",
                    "mapping_type": "field_mapping",
                    "mapping_cardinality": "one_to_one",
                    "_lineage": lineage.strip(),
                }
            )

    # Relationships from FK
    seen_rel: set[str] = set()
    for attr in attrs_sorted:
        if not attr.fk:
            continue
        parsed = parse_fk(attr.fk)
        if parsed is None:
            continue
        target_obj, _target_attr = parsed
        # Resolve canonical target object spelling
        tdef = ir.object_by_code(target_obj)
        target_name = tdef.object_code if tdef else target_obj
        rel_name = f"{attr.object_code}_to_{target_name}_via_{attr.attribute_code}"
        if rel_name in seen_rel:
            continue
        seen_rel.add(rel_name)
        relationships.append(
            {
                "name": rel_name,
                "source": attr.object_code,
                "target": target_name,
                "source_role": attr.attribute_code,
                "target_role": None,
                # Finite max: LinkML mapper maps "*" → None, which fails REF-002.
                "source_card": "0..999999",
                "target_card": "0..1",
                "identifying": "Y" if attr.pk else None,
            }
        )

    # Entity-level physical mappings (one per logical entity → its phys object)
    # Prefer physical→logical order (matches mdm / GEN-004).
    for key in sorted(ir.objects.keys()):
        obj = ir.objects[key]
        phys_name = physical_name(
            obj.src_object_code or obj.object_code, logical_names=logical_names
        )
        if phys_name not in phys_names:
            continue
        map_name = f"entity_phys_{obj.object_code}"
        mappings.append(
            {
                "name": map_name,
                "source": phys_name,
                "target": obj.object_code,
                "mapping_type": "entity_physical",
                "mapping_cardinality": "one_to_one",
                "_lineage": "",
            }
        )

    tables = WorkbookTables(
        entities=SheetTable("entities", "Entities", entities),
        attributes=SheetTable("attributes", "Attributes", attributes),
        relationships=SheetTable("relationships", "Relationships", relationships),
        conceptual=None,
        physical_objects=SheetTable(
            "physical_objects", "PhysicalObjects", physical_objects
        ),
        physical_fields=SheetTable(
            "physical_fields", "PhysicalFields", physical_fields
        ),
        mappings=SheetTable("mappings", "Mappings", mappings),
        warnings=[],
    )
    # Stash lineage on tables via attribute for enrich
    tables._mapping_lineage = {  # type: ignore[attr-defined]
        m["name"]: m.get("_lineage") or "" for m in mappings
    }
    return tables, trace


def build_package(
    ir: SolutionIR,
    profile: SolutionXlsxProfile,
    system: SystemDefaults,
) -> tuple[dict[str, Any], list[Diagnostic], TraceMap, MapResult]:
    """Full IR → ModelPackage dict."""
    tables, trace = ir_to_workbook_tables(ir, system)
    ingest_profile = system_to_ingest_profile(system, profile)
    result = map_er_dictionary(tables, ingest_profile, raise_on_error=False)
    mapper_diags: list[Diagnostic] = []
    for err in result.errors:
        mapper_diags.append(
            Diagnostic(
                code="SXI-MAP-001",
                severity=Severity.ERROR,
                message_ru=str(err),
                remediation="Исправьте исходные данные или профиль.",
                source_ref=SourceRef(sheet=err.sheet, row=err.row),
            )
        )
    package = enrich_package(
        result.package,
        ir=ir,
        profile=profile,
        system=system,
        tables=tables,
        trace=trace,
    )
    return package, mapper_diags, trace, result
