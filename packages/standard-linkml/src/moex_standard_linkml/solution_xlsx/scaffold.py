"""Scaffold publish.yaml for a solution implementation (create-if-missing)."""

from __future__ import annotations

from pathlib import Path

import yaml

from moex_standard_linkml.solution_xlsx.profile import SystemDefaults

_ORDER = {"mdm": 310, "ucd": 320, "crm": 330, "esed": 340}


def build_publish_module(
    system: SystemDefaults,
    *,
    package_filename: str,
) -> dict:
    order = _ORDER.get(system.slug, 350)
    return {
        "module_id": f"moex:module:{system.slug}-solution",
        "kind": "publication_module",
        "version": "1",
        "order": order,
        "icon": "🧩",
        "title": system.package_title,
        "profile": "implementation",
        "description": system.package_description.strip(),
        "implementation_profile": "dams-data-model",
        "dams_model_level": "solution",
        "conformance_status": "draft-conformant",
        "implements": [
            {
                "specification_ref": "moex-dams@0.1",
                "profile_ref": "dams-solution",
                "conformance_target": "draft",
            }
        ],
        "sections": [
            {
                "id": "package",
                "title": "Package",
                "kind": "overview",
                "type": "key-value",
                "satisfies": ["dams:overview", "implementation:overview"],
                "source": {"format": "yaml", "path": package_filename},
            },
            {
                "id": "conceptual",
                "title": "Conceptual entities",
                "kind": "classes",
                "type": "entity-table",
                "source": {
                    "format": "yaml",
                    "path": package_filename,
                    "select": "conceptual_entities",
                },
                "key_column": "element_id",
                "columns": ["name", "title", "description", "entity_type", "data_class"],
                "filterable": ["entity_type", "data_class"],
            },
            {
                "id": "logical",
                "title": "Logical entities",
                "kind": "classes",
                "type": "entity-table",
                "satisfies": [
                    "dams:classes",
                    "dams:logical-entities",
                    "dams:logical-attributes",
                    "dams:relationships",
                ],
                "source": {
                    "format": "yaml",
                    "path": package_filename,
                    "select": "logical_entities",
                },
                "key_column": "element_id",
                "columns": [
                    "name",
                    "title",
                    "description",
                    "solution_data_role",
                    "governance_classification",
                ],
                "filterable": ["solution_data_role", "governance_classification"],
            },
            {
                "id": "physical",
                "title": "Physical objects",
                "kind": "bindings",
                "type": "entity-table",
                "satisfies": ["dams:physical-objects", "dams:physical-fields"],
                "source": {
                    "format": "yaml",
                    "path": package_filename,
                    "select": "physical_objects",
                },
                "key_column": "element_id",
                "columns": [
                    "name",
                    "title",
                    "description",
                    "object_kind",
                    "technology",
                ],
                "filterable": ["object_kind"],
            },
            {
                "id": "slice-summary",
                "title": "Vertical slice summary",
                "description": "Conformance + graph projection from moex-publication export-slice",
                "kind": "conformance",
                "type": "key-value",
                "satisfies": [
                    "dams:conformance",
                    "implementation:conformance",
                    "dams:declared-binding",
                ],
                "source": {
                    "format": "json",
                    "path": "publications/vertical_slice.json",
                    "select": "summary",
                },
            },
            {
                "id": "slice-nodes",
                "title": "Slice graph nodes",
                "kind": "bindings",
                "type": "entity-table",
                "satisfies": ["dams:physical-mappings"],
                "source": {
                    "format": "json",
                    "path": "publications/vertical_slice.json",
                    "select": "nodes",
                },
                "key_column": "id",
                "columns": ["kind", "name", "title", "description"],
                "filterable": ["kind"],
            },
            {
                "id": "slice-relations",
                "title": "Slice universe relations",
                "kind": "data-flows",
                "type": "entity-table",
                "source": {
                    "format": "json",
                    "path": "publications/vertical_slice.json",
                    "select": "relations",
                },
                "key_column": "id",
                "columns": ["kind", "source", "target"],
                "filterable": ["kind"],
            },
            {
                "id": "model-assessment",
                "title": "Оценка соответствия требованиям модели",
                "kind": "model-assessment",
                "type": "entity-table",
                "satisfies": ["dams:model-assessment"],
                "source": {
                    "format": "json",
                    "path": "publications/vertical_slice.json",
                    "select": "model_assessment",
                },
                "key_column": "id",
                "columns": [
                    "status",
                    "requirement_code",
                    "severity",
                    "subject",
                    "finding",
                    "remediation",
                ],
                "filterable": ["status", "severity", "requirement_code"],
            },
        ],
    }


def write_publish_if_missing(
    solution_dir: Path,
    system: SystemDefaults,
    *,
    package_filename: str,
    force: bool = False,
) -> Path | None:
    path = solution_dir / "publish.yaml"
    if path.exists() and not force:
        return None
    data = build_publish_module(system, package_filename=package_filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False),
        encoding="utf-8",
    )
    return path
