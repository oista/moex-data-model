"""List ontology releases as summaries."""

from __future__ import annotations

from moex_ontology.adapters.sqlite_index import SqliteOntologyIndex
from moex_ontology.read_models.ontology_summary import OntologySummary


def list_ontologies(index: SqliteOntologyIndex) -> list[OntologySummary]:
    summaries: list[OntologySummary] = []
    for release in index.list_releases():
        counts = index.kind_counts(release.id)
        class_count = counts.get("class", 0)
        property_count = (
            counts.get("object_property", 0)
            + counts.get("data_property", 0)
            + counts.get("annotation_property", 0)
        )
        summaries.append(
            OntologySummary(
                id=release.id,
                title=release.title,
                version=release.version,
                ontology_iri=release.ontology_iri,
                version_iri=release.version_iri,
                status=release.status,
                role=release.role,
                source_uri=release.source_uri,
                imports=release.imports,
                entity_count=index.entity_count(release.id),
                class_count=class_count,
                property_count=property_count,
            )
        )
    return summaries
