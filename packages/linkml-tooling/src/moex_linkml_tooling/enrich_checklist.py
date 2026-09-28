"""Enrich checklist analyzer for inferred LinkML schemas (Stage 7)."""

from __future__ import annotations

from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict

from moex_modeling.conformance.domain import Diagnostic
from moex_modeling.shared.enums import DiagnosticSeverity

EnrichField = Literal["id", "description", "range", "registry_link"]

REGISTRY_CLASS_NAMES = frozenset(
    {
        "ITSystem",
        "ITSolution",
        "ITPlatform",
        "IntegrationReference",
        "GlossaryTerm",
    }
)

_REGISTRY_REF_HINTS = frozenset(
    {
        "registry_id",
        "registry_ref",
        "external_id",
        "source_uri",
        "eam_ref",
        "clinkr_ref",
        "system_ref",
        "integration_ref",
        "glossary_ref",
    }
)


class EnrichChecklistItem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    severity: str = "warning"
    path: str
    message: str
    field: EnrichField


def _slot_map(class_body: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Normalize attributes/slots into name → slot dict."""
    out: dict[str, dict[str, Any]] = {}
    attrs = class_body.get("attributes")
    if isinstance(attrs, dict):
        for name, body in attrs.items():
            if isinstance(body, dict):
                out[str(name)] = body
            else:
                out[str(name)] = {}
    slots = class_body.get("slots")
    if isinstance(slots, list):
        for name in slots:
            out.setdefault(str(name), {})
    elif isinstance(slots, dict):
        for name, body in slots.items():
            if isinstance(body, dict):
                out[str(name)] = body
            else:
                out.setdefault(str(name), {})
    return out


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def build_enrich_checklist(schema_text: str) -> list[EnrichChecklistItem]:
    """Analyze inferred LinkML YAML and return advisory enrich items."""
    try:
        data = yaml.safe_load(schema_text)
    except yaml.YAMLError:
        return [
            EnrichChecklistItem(
                code="IMPORT-ENRICH-PARSE",
                severity="warning",
                path="$",
                message="inferred schema is not valid YAML; cannot build enrich checklist",
                field="id",
            )
        ]
    if not isinstance(data, dict):
        return [
            EnrichChecklistItem(
                code="IMPORT-ENRICH-PARSE",
                severity="warning",
                path="$",
                message="inferred schema must be a YAML mapping",
                field="id",
            )
        ]

    items: list[EnrichChecklistItem] = []
    classes = data.get("classes")
    if not isinstance(classes, dict):
        return items

    top_slots = data.get("slots")
    slot_defs: dict[str, dict[str, Any]] = {}
    if isinstance(top_slots, dict):
        for sn, sb in top_slots.items():
            slot_defs[str(sn)] = sb if isinstance(sb, dict) else {}

    for class_name, class_body in classes.items():
        if not isinstance(class_body, dict):
            continue
        cpath = f"classes.{class_name}"

        if not _has_text(class_body.get("description")):
            items.append(
                EnrichChecklistItem(
                    code="IMPORT-ENRICH-DESC",
                    severity="warning",
                    path=cpath,
                    message=f"class {class_name} is missing a description",
                    field="description",
                )
            )

        if not _has_text(class_body.get("class_uri")):
            slots = _slot_map(class_body)
            has_id_slot = any(
                n in {"id", "identifier", "uid", "uuid"}
                or (isinstance(b.get("identifier"), bool) and b.get("identifier"))
                for n, b in slots.items()
            )
            if not has_id_slot:
                items.append(
                    EnrichChecklistItem(
                        code="IMPORT-ENRICH-ID",
                        severity="warning",
                        path=cpath,
                        message=(
                            f"class {class_name} lacks class_uri and an identifier-ish slot"
                        ),
                        field="id",
                    )
                )

        if class_name in REGISTRY_CLASS_NAMES:
            slots = _slot_map(class_body)
            slot_names = {n.lower() for n in slots}
            if not slot_names.intersection(_REGISTRY_REF_HINTS):
                items.append(
                    EnrichChecklistItem(
                        code="IMPORT-ENRICH-REGISTRY",
                        severity="warning",
                        path=cpath,
                        message=(
                            f"registry projection class {class_name} has no external "
                            "registry link slot (registry_id / source_uri / …)"
                        ),
                        field="registry_link",
                    )
                )

        for slot_name, slot_body in _slot_map(class_body).items():
            spath = f"{cpath}.slots.{slot_name}"
            merged = dict(slot_defs.get(slot_name, {}))
            merged.update(slot_body)

            if not _has_text(merged.get("description")):
                items.append(
                    EnrichChecklistItem(
                        code="IMPORT-ENRICH-DESC",
                        severity="warning",
                        path=spath,
                        message=(
                            f"slot {class_name}.{slot_name} is missing a description"
                        ),
                        field="description",
                    )
                )

            rng = merged.get("range")
            if rng is None or rng == "string":
                items.append(
                    EnrichChecklistItem(
                        code="IMPORT-ENRICH-RANGE",
                        severity="warning",
                        path=spath,
                        message=(
                            f"slot {class_name}.{slot_name} has weak range "
                            f"({rng!r}); refine type"
                        ),
                        field="range",
                    )
                )

    return items


def checklist_to_jsonable(
    items: list[EnrichChecklistItem],
) -> list[dict[str, Any]]:
    return [i.model_dump(mode="json") for i in items]


def checklist_summary_diagnostics(
    items: list[EnrichChecklistItem],
) -> list[Diagnostic]:
    """One WARNING summary diagnostic when checklist is non-empty."""
    if not items:
        return []
    by_field: dict[str, int] = {}
    for item in items:
        by_field[item.field] = by_field.get(item.field, 0) + 1
    parts = ", ".join(f"{k}={v}" for k, v in sorted(by_field.items()))
    return [
        Diagnostic(
            diagnostic_code="IMPORT-ENRICH-SUMMARY",
            severity=DiagnosticSeverity.WARNING,
            diagnostic_message=(
                f"enrich checklist: {len(items)} item(s) ({parts}); "
                "refine IDs, descriptions, ranges, and registry links in Monaco"
            ),
        )
    ]


__all__ = [
    "EnrichChecklistItem",
    "EnrichField",
    "REGISTRY_CLASS_NAMES",
    "build_enrich_checklist",
    "checklist_summary_diagnostics",
    "checklist_to_jsonable",
]
