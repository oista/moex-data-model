"""Project DAMS LinkML schema to required-only YAML fragments for viewer."""

from __future__ import annotations

from typing import Any

import yaml
from linkml_runtime.utils.schemaview import SchemaView


def _slot_is_mandatory(slot) -> bool:
    if getattr(slot, "required", None) is True:
        return True
    min_card = getattr(slot, "minimum_cardinality", None)
    if min_card is not None and int(min_card) >= 1:
        return True
    return False


def project_required_only_schema(sv: SchemaView) -> dict[str, str]:
    """
    Return mapping of relative path -> YAML text for required-only projections.

    Emits one synthetic document covering classes that have at least one induced
    mandatory slot, plus enums referenced by those slots / requirement enums.
    """
    classes_out: dict[str, Any] = {}
    slots_out: dict[str, Any] = {}
    enums_needed: set[str] = set()

    for cname in sorted(sv.all_classes().keys()):
        # Skip imported linkml builtins
        if cname.startswith("linkml:"):
            continue
        induced = sv.class_induced_slots(cname)
        mandatory = [s for s in induced if _slot_is_mandatory(s)]
        if not mandatory:
            continue
        slot_names: list[str] = []
        for s in mandatory:
            sname = s.name
            slot_names.append(sname)
            if sname not in slots_out:
                entry: dict[str, Any] = {"range": s.range}
                if s.required:
                    entry["required"] = True
                if s.identifier:
                    entry["identifier"] = True
                if s.multivalued:
                    entry["multivalued"] = True
                if s.minimum_cardinality is not None:
                    entry["minimum_cardinality"] = int(s.minimum_cardinality)
                if s.pattern:
                    entry["pattern"] = s.pattern
                slots_out[sname] = entry
                # collect enum ranges
                if s.range and s.range in sv.all_enums():
                    enums_needed.add(s.range)
        cd = sv.get_class(cname)
        class_entry: dict[str, Any] = {
            "slots": slot_names,
        }
        if cd.description:
            class_entry["description"] = cd.description
        if cd.is_a:
            class_entry["is_a"] = cd.is_a
        if cd.abstract:
            class_entry["abstract"] = True
        classes_out[cname] = class_entry

    # Always include requirement-related enums for the min-spec view
    for ename in (
        "RequirementLevelEnum",
        "RequirementSectionEnum",
        "FormalCheckKindEnum",
        "CheckSeverityEnum",
        "LifecycleStatusEnum",
    ):
        if ename in sv.all_enums():
            enums_needed.add(ename)

    enums_out: dict[str, Any] = {}
    for ename in sorted(enums_needed):
        ed = sv.get_enum(ename)
        if not ed:
            continue
        pvs = {}
        for pv_name, pv in (ed.permissible_values or {}).items():
            meta: dict[str, Any] = {}
            if pv and getattr(pv, "description", None):
                meta["description"] = pv.description
            pvs[pv_name] = meta or None
        # compact null values
        pvs_clean = {
            k: (v if v else None) for k, v in pvs.items()
        }
        enums_out[ename] = {"permissible_values": pvs_clean}

    doc: dict[str, Any] = {
        "id": "https://data.moex.com/dams/minimal-required/v0.1",
        "name": "moex_dams_minimal_required",
        "description": (
            "Derived required-only projection of DAMS LinkML "
            "(classes/slots with required or minimum_cardinality>=1)."
        ),
        "classes": classes_out,
        "slots": slots_out,
        "enums": enums_out,
    }
    text = yaml.dump(
        doc,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=100,
    )
    return {"minimal/moex-dams.required.yaml": text}
