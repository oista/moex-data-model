"""Post-map enrichment: it-solution slots, mapping coverage, lineage."""

from __future__ import annotations

from typing import Any

from moex_standard_linkml.ingest.workbook import WorkbookTables
from moex_standard_linkml.solution_xlsx.ir import SolutionIR
from moex_standard_linkml.solution_xlsx.normalize import match_key
from moex_standard_linkml.solution_xlsx.profile import SolutionXlsxProfile, SystemDefaults
from moex_standard_linkml.solution_xlsx.trace import TraceMap


def enrich_package(
    package: dict[str, Any],
    *,
    ir: SolutionIR,
    profile: SolutionXlsxProfile,
    system: SystemDefaults,
    tables: WorkbookTables,
    trace: TraceMap,
) -> dict[str, Any]:
    defaults = profile.defaults
    package["implementation_scope"] = defaults.implementation_scope
    package["conceptual_implementation_ref"] = profile.conceptual_implementation_ref
    package["data_owner_ref"] = defaults.data_owner_ref
    package["ownership_inheritance_rule"] = defaults.ownership_inheritance_rule.strip()
    package.setdefault("solution_ref", system.solution_ref)

    lineage_by_name: dict[str, str] = getattr(tables, "_mapping_lineage", {}) or {}

    # Logical entities enrichment
    attrs_by_obj: dict[str, list] = {}
    for attr in ir.attributes:
        key = match_key(attr.object_code) or attr.object_code
        attrs_by_obj.setdefault(key, []).append(attr)

    for ent in package.get("logical_entities") or []:
        name = str(ent.get("name") or "")
        key = match_key(name) or name
        ent["data_owner_ref"] = defaults.data_owner_ref
        ent["governance_classification"] = defaults.governance_classification
        ent["business_key_kind"] = defaults.business_key_kind
        ent["identity_rule"] = defaults.identity_rule.strip()
        ent["conceptual_alignment_status"] = defaults.conceptual_alignment_status
        ent["alignment_rationale"] = defaults.alignment_rationale.strip()

        has_pk = any(a.pk for a in attrs_by_obj.get(key, []))
        if has_pk:
            ent["business_key_kind"] = "surrogate"

        for attr in ent.get("attributes") or []:
            aname = str(attr.get("name") or "")
            # Find IR attr
            ir_attr = next(
                (
                    a
                    for a in attrs_by_obj.get(key, [])
                    if match_key(a.attribute_code) == match_key(aname)
                ),
                None,
            )
            if ir_attr and ir_attr.src_attribute_code:
                attr["mapping_coverage_status"] = defaults.mapping_coverage_status_mapped
            else:
                attr["mapping_coverage_status"] = defaults.mapping_coverage_status_planned
                attr["mapping_rationale"] = defaults.mapping_rationale_planned.strip()
            attr.setdefault(
                "governance_classification", defaults.governance_classification
            )

    for po in package.get("physical_objects") or []:
        po["mapping_coverage_status"] = defaults.mapping_coverage_status_mapped
        for pf in po.get("physical_fields") or []:
            pf["mapping_coverage_status"] = defaults.mapping_coverage_status_mapped

    for mapping in package.get("mappings") or []:
        mname = str(mapping.get("name") or "")
        lineage = lineage_by_name.get(mname) or ""
        if lineage:
            base = mapping.get("description") or f"Mapping {mname}"
            mapping["description"] = f"{base}. {lineage}".strip()
        if mapping.get("mapping_type") == "entity_physical":
            mapping["approval_status"] = "proposed"

    # Package-level realizes stubs: logical entity → local conceptual stub (ADR-021).
    # Full enterprise alignment is a follow-up edit.
    mappings = list(package.get("mappings") or [])
    existing_realizes = {
        tuple(m.get("source_refs") or [])
        for m in mappings
        if m.get("mapping_type") == "realizes"
    }
    concept_by_name = {
        str(c.get("name")): str(c.get("element_id"))
        for c in (package.get("conceptual_entities") or [])
        if c.get("name") and c.get("element_id")
    }
    for ent in package.get("logical_entities") or []:
        eid = str(ent.get("element_id") or "")
        name = str(ent.get("name") or "")
        concept_id = concept_by_name.get(name)
        if not eid or not concept_id:
            continue
        key = (eid,)
        if key in existing_realizes:
            continue
        mappings.append(
            {
                "element_id": f"dams:mapping/{system.slug}/realizes_{name}",
                "name": f"realizes_{name}",
                "description": (
                    f"Локальный stub: {name} realizes conceptual {name} "
                    f"(импорт xlsx; выверка с enterprise — follow-up)."
                ),
                "lifecycle_status": defaults.lifecycle_status,
                "source_refs": [eid],
                "target_refs": [concept_id],
                "mapping_type": "realizes",
                "mapping_cardinality": "one_to_one",
                "approval_status": "proposed",
            }
        )
    package["mappings"] = mappings

    for rel in package.get("relationships") or []:
        # Draft packages may omit unbounded max; keep finite cards from builder.
        if rel.get("source_max_cardinality") is None:
            rel["source_max_cardinality"] = 999999
        if rel.get("target_max_cardinality") is None:
            rel["target_max_cardinality"] = 1
        if rel.get("source_min_cardinality") is None:
            rel["source_min_cardinality"] = 0
        if rel.get("target_min_cardinality") is None:
            rel["target_min_cardinality"] = 0

    for ctx in package.get("domain_contexts") or []:
        ctx.setdefault("solution_ref", system.solution_ref)

    trace.populate_from_package(package)
    return package
