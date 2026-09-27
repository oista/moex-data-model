"""Map ER-dictionary tables to a DAMS ModelPackage dict."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from moex_standard_linkml.ingest import ids
from moex_standard_linkml.ingest.profile import IngestProfile
from moex_standard_linkml.ingest.workbook import WorkbookTables

_CARD_RE = re.compile(
    r"^\s*(\d+)\s*(?:\.\.\s*(\d+|\*|n|N))?\s*$"
)


@dataclass
class MapperError:
    sheet: str
    row: int
    message: str

    def __str__(self) -> str:
        return f"{self.sheet} row {self.row}: {self.message}"


@dataclass
class MapResult:
    package: dict[str, Any]
    errors: list[MapperError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


class MappingFailed(ValueError):
    def __init__(self, errors: list[MapperError]) -> None:
        self.errors = errors
        super().__init__("; ".join(str(e) for e in errors))


def map_er_dictionary(
    tables: WorkbookTables,
    profile: IngestProfile,
    *,
    raise_on_error: bool = True,
) -> MapResult:
    errors: list[MapperError] = []
    warnings = list(tables.warnings)
    prefix = profile.id_prefix
    slug = profile.solution_slug
    defaults = profile.defaults

    context_curie = ids.context_id(prefix, slug)
    conceptual: list[dict[str, Any]] = []
    logical: list[dict[str, Any]] = []
    entity_by_name: dict[str, str] = {}  # entity name → logical CURIE

    for i, row in enumerate(tables.entities.rows, start=2):
        name = _req_str(row.get("name"), "entities", i, "name", errors)
        if name is None:
            continue
        title = _opt_str(row.get("title")) or name
        description = _opt_str(row.get("description")) or title
        concept_curie = ids.concept_id(prefix, name)
        logical_curie = ids.logical_entity_id(prefix, slug, name)
        if name in entity_by_name:
            errors.append(
                MapperError("entities", i, f"duplicate entity name '{name}'")
            )
            continue
        entity_by_name[name] = logical_curie
        conceptual.append(
            {
                "element_id": concept_curie,
                "name": name,
                "title": title,
                "description": description,
                "lifecycle_status": defaults.lifecycle_status,
                "entity_type": defaults.entity_type,
                "data_class": defaults.data_class,
                "business_importance": defaults.business_importance,
            }
        )
        logical.append(
            {
                "element_id": logical_curie,
                "name": name,
                "title": title,
                "description": description,
                "lifecycle_status": defaults.lifecycle_status,
                "context_ref": context_curie,
                "conceptual_entity_refs": [concept_curie],
                "solution_ref": profile.solution_ref,
                "solution_data_role": defaults.solution_data_role,
                "entity_type": defaults.entity_type,
                "data_class": defaults.data_class,
                "business_importance": defaults.business_importance,
                "attributes": [],
                "key_attribute_refs": [],
            }
        )

    logical_by_curie = {e["element_id"]: e for e in logical}

    for i, row in enumerate(tables.attributes.rows, start=2):
        entity_name = _req_str(row.get("entity"), "attributes", i, "entity", errors)
        attr_name = _req_str(row.get("name"), "attributes", i, "name", errors)
        if entity_name is None or attr_name is None:
            continue
        owner = entity_by_name.get(entity_name)
        if owner is None:
            errors.append(
                MapperError(
                    "attributes",
                    i,
                    f"unknown entity '{entity_name}' (not in Entities sheet)",
                )
            )
            continue
        title = _opt_str(row.get("title")) or attr_name
        description = _opt_str(row.get("description")) or title
        is_pk = _as_bool(row.get("pk"))
        required = _as_bool(row.get("required"))
        if is_pk:
            required = True
        logical_type = profile.map_type(_opt_str(row.get("type")), is_pk=is_pk)
        attr_curie = ids.logical_attr_id(prefix, slug, entity_name, attr_name)
        attr = {
            "element_id": attr_curie,
            "name": attr_name,
            "title": title,
            "description": description,
            "lifecycle_status": defaults.lifecycle_status,
            "owner_entity_ref": owner,
            "logical_type": logical_type,
            "required": required,
            "multivalued": False,
        }
        owner_entity = logical_by_curie[owner]
        owner_entity["attributes"].append(attr)
        if is_pk:
            owner_entity["key_attribute_refs"].append(attr_curie)

    relationships: list[dict[str, Any]] = []
    if tables.relationships is not None:
        for i, row in enumerate(tables.relationships.rows, start=2):
            rel_name = _req_str(row.get("name"), "relationships", i, "name", errors)
            source_name = _req_str(
                row.get("source"), "relationships", i, "source", errors
            )
            target_name = _req_str(
                row.get("target"), "relationships", i, "target", errors
            )
            if rel_name is None or source_name is None or target_name is None:
                continue
            source_curie = entity_by_name.get(source_name)
            target_curie = entity_by_name.get(target_name)
            if source_curie is None:
                errors.append(
                    MapperError(
                        "relationships",
                        i,
                        f"unknown source entity '{source_name}'",
                    )
                )
                continue
            if target_curie is None:
                errors.append(
                    MapperError(
                        "relationships",
                        i,
                        f"unknown target entity '{target_name}'",
                    )
                )
                continue
            source_min, source_max = _parse_cardinality(
                row.get("source_card"), "relationships", i, "source_card", errors
            )
            target_min, target_max = _parse_cardinality(
                row.get("target_card"), "relationships", i, "target_card", errors
            )
            rel: dict[str, Any] = {
                "element_id": ids.relationship_id(prefix, slug, rel_name),
                "name": rel_name,
                "title": rel_name,
                "description": f"Relationship {rel_name}",
                "lifecycle_status": defaults.lifecycle_status,
                "source_entity_ref": source_curie,
                "target_entity_ref": target_curie,
            }
            source_role = _opt_str(row.get("source_role"))
            target_role = _opt_str(row.get("target_role"))
            if source_role:
                rel["source_role"] = source_role
            if target_role:
                rel["target_role"] = target_role
            if source_min is not None:
                rel["source_min_cardinality"] = source_min
            if source_max is not None:
                rel["source_max_cardinality"] = source_max
            if target_min is not None:
                rel["target_min_cardinality"] = target_min
            if target_max is not None:
                rel["target_max_cardinality"] = target_max
            if row.get("identifying") is not None:
                rel["identifying"] = _as_bool(row.get("identifying"))
            relationships.append(rel)

    package: dict[str, Any] = {
        "element_id": ids.package_id(prefix, slug, profile.model_version),
        "name": profile.package_name,
        "title": profile.package_title,
        "description": profile.package_description,
        "lifecycle_status": defaults.lifecycle_status,
        "api_version": profile.api_version,
        "model_version": profile.model_version,
        "solution_ref": profile.solution_ref,
        "conceptual_entities": conceptual,
        "domain_contexts": [
            {
                "element_id": context_curie,
                "name": defaults.context_name,
                "title": defaults.context_title,
                "description": defaults.context_description,
                "lifecycle_status": defaults.lifecycle_status,
                "domain_ref": defaults.domain_ref,
                "solution_ref": profile.solution_ref,
                "namespace": defaults.namespace,
            }
        ],
        "logical_entities": logical,
        "relationships": relationships,
    }

    result = MapResult(package=package, errors=errors, warnings=warnings)
    if raise_on_error and errors:
        raise MappingFailed(errors)
    return result


def _req_str(
    value: Any,
    sheet: str,
    row: int,
    field: str,
    errors: list[MapperError],
) -> str | None:
    text = _opt_str(value)
    if text is None:
        errors.append(MapperError(sheet, row, f"missing required field '{field}'"))
        return None
    return text


def _opt_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _as_bool(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "y", "x", "pk"}


def _parse_cardinality(
    value: Any,
    sheet: str,
    row: int,
    field: str,
    errors: list[MapperError],
) -> tuple[int | None, int | None]:
    text = _opt_str(value)
    if text is None:
        return None, None
    match = _CARD_RE.match(text)
    if not match:
        errors.append(
            MapperError(
                sheet,
                row,
                f"invalid cardinality '{text}' in '{field}' "
                f"(expected N or N..M / N..*)",
            )
        )
        return None, None
    minimum = int(match.group(1))
    upper = match.group(2)
    if upper is None:
        return minimum, minimum
    if upper in {"*", "n", "N"}:
        return minimum, None
    return minimum, int(upper)
