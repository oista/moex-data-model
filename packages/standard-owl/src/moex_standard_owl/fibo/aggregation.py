"""Aggregate entity occurrences across modules."""

from __future__ import annotations

from moex_standard_owl.constants import (
    DEFINITION_JOIN,
    LABEL_JOIN,
    MODULE_JOIN,
    SHA_JOIN,
    SUPERCLASS_JOIN,
)
from moex_standard_owl.literals import join_unique
from moex_standard_owl.models import AggregatedEntity, EntityOccurrence


def aggregate_entities(
    occurrences: list[EntityOccurrence],
) -> list[AggregatedEntity]:
    """
    Aggregate by ``iri + entity_type``.

    - Merge labels, definitions, module_iri, module_path, superclasses
    - ``is_deprecated`` true if any source is deprecated
    - Keep all source file SHAs
    - Stable sort by iri, entity_type
    """
    buckets: dict[tuple[str, str], list[EntityOccurrence]] = {}
    for occ in occurrences:
        key = (occ.iri, occ.entity_type)
        buckets.setdefault(key, []).append(occ)

    aggregated: list[AggregatedEntity] = []
    for (iri, entity_type), group in buckets.items():
        # Deterministic merge order by module_path
        group = sorted(group, key=lambda o: o.module_path)
        first = group[0]
        labels = join_unique((o.label for o in group), LABEL_JOIN)
        definitions = join_unique((o.definition for o in group), DEFINITION_JOIN)
        module_iris = join_unique((o.module_iri for o in group), MODULE_JOIN)
        module_paths = join_unique((o.module_path for o in group), MODULE_JOIN)
        superclasses = join_unique((o.superclasses for o in group), SUPERCLASS_JOIN)
        shas = join_unique((o.source_file_sha256 for o in group), SHA_JOIN)
        alt_labels = join_unique((o.alternative_labels for o in group), LABEL_JOIN)
        version_iris = join_unique(
            (o.ontology_version_iri for o in group), MODULE_JOIN
        )
        imports = join_unique((o.imports for o in group), MODULE_JOIN)
        domains = join_unique((o.source_domain for o in group), MODULE_JOIN)
        replacements = join_unique(
            (o.deprecated_replacement_iri for o in group), LABEL_JOIN
        )
        label_langs = join_unique((o.label_language for o in group), LABEL_JOIN)
        def_langs = join_unique((o.definition_language for o in group), LABEL_JOIN)
        is_deprecated = any(o.is_deprecated for o in group)

        aggregated.append(
            AggregatedEntity(
                iri=iri,
                local_name=first.local_name,
                label=labels,
                definition=definitions,
                entity_type=entity_type,
                entity_type_code=first.entity_type_code,
                module_iri=module_iris,
                module_path=module_paths,
                is_deprecated=is_deprecated,
                deprecated_replacement_iri=replacements,
                superclasses=superclasses,
                source_release=first.source_release,
                source_file_sha256=shas or first.source_file_sha256,
                alternative_labels=alt_labels,
                definition_language=def_langs,
                label_language=label_langs,
                ontology_version_iri=version_iris,
                imports=imports,
                source_domain=domains,
                parse_status="ok",
                parse_error=None,
            )
        )

    aggregated.sort(key=lambda e: (e.iri, e.entity_type))
    return aggregated


def filter_for_main_mart(
    entities: list[AggregatedEntity],
    *,
    type_codes: set[str],
    include_individuals: bool,
    include_deprecated: bool,
) -> list[AggregatedEntity]:
    """
    Entities for the primary aggregated CSV marts.

    ``type_codes`` is the effective filter (caller expands it when
    ``--include-individuals`` is set). Deprecated entities are omitted
    unless ``include_deprecated`` is True.
    """
    _ = include_individuals  # encoded into type_codes by CLI
    result: list[AggregatedEntity] = []
    for ent in entities:
        if ent.entity_type_code not in type_codes:
            continue
        if ent.is_deprecated and not include_deprecated:
            continue
        result.append(ent)
    return result
