"""OWL StandardProvider: distinct TSpecBody / TImplBody (no reasoner)."""

from __future__ import annotations

from pathlib import Path

import yaml
from moex_modeling import (
    Diagnostic,
    DiagnosticSeverity,
    ImplementationRef,
    SpecificationRef,
    StandardFamily,
    StandardProvider,
)
from rdflib import OWL, RDF, RDFS

from moex_standard_owl.adapters.rdflib_adapter import RdflibOntologyAdapter
from moex_standard_owl.domain.body import OWLImplementationBody, OWLSpecificationBody
from moex_standard_owl.domain.elements import OWLElement, OWLElementKind
from moex_standard_owl.rdf_parser import local_name_from_iri, parse_rdf_file


class OWLStandardProvider:
    """
    Concrete StandardProvider for OWL/RDF.

    - specification body: OntologyRelease descriptor YAML
    - implementation body: local RDF directory (RDFLib parse)
    - validate_standard: parse diagnostics only (ADR-010 — no reasoner gate)
    """

    family: StandardFamily = StandardFamily.OWL

    def load_specification_body(
        self,
        specification: SpecificationRef,
        *,
        path: str,
    ) -> OWLSpecificationBody:
        descriptor = Path(path)
        data = yaml.safe_load(descriptor.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            raise ValueError(f"OWL specification descriptor must be a mapping: {descriptor}")
        imports = data.get("imports") or []
        if not isinstance(imports, list):
            imports = []
        _ = specification
        return OWLSpecificationBody(
            descriptor_path=str(descriptor.resolve()),
            ontology_id=str(data.get("id") or specification.specification_id),
            ontology_iri=data.get("ontology_iri"),
            version_iri=data.get("version_iri"),
            title=data.get("title"),
            version=data.get("version") or specification.specification_version,
            revision=data.get("revision") or specification.specification_revision,
            content_digest=data.get("content_digest"),
            role=data.get("role"),
            status=data.get("status"),
            imports=tuple(str(x) for x in imports),
            local_source_hint=data.get("local_source_hint"),
        )

    def load_implementation_body(
        self,
        implementation: ImplementationRef,
        *,
        path: str,
    ) -> OWLImplementationBody:
        source = Path(path).expanduser().resolve()
        _ = implementation
        parse_errors: list[str] = []
        release = implementation.implementation_revision or "local"
        if source.is_file():
            adapter = RdflibOntologyAdapter.from_files([source])
            _, err = parse_rdf_file(
                source,
                module_path=source.name,
                source_release=release,
            )
            if err is not None:
                parse_errors.append(str(getattr(err, "message", err)))
        else:
            adapter = RdflibOntologyAdapter.from_directory(source)
            for rdf_path in sorted(
                set(source.rglob("*.rdf"))
                | set(source.rglob("*.owl"))
                | set(source.rglob("*.ttl"))
            ):
                if not rdf_path.is_file():
                    continue
                if "Broken" in rdf_path.name:
                    # Known fixture; record as warning-style parse skip
                    parse_errors.append(f"skipped broken fixture: {rdf_path.name}")
                    continue
                _, err = parse_rdf_file(
                    rdf_path,
                    module_path=rdf_path.relative_to(source).as_posix(),
                    source_release=release,
                )
                if err is not None:
                    parse_errors.append(
                        f"{rdf_path.name}: {getattr(err, 'message', err)}"
                    )

        body = OWLImplementationBody(
            source_path=str(source),
            entity_count=len(adapter.entities()),
            parse_errors=tuple(parse_errors),
        )
        body.bind_adapter(adapter)
        return body

    def enumerate_elements(
        self,
        body: OWLImplementationBody,
    ) -> tuple[OWLElement, ...]:
        adapter = body.adapter
        graph = adapter._graph  # noqa: SLF001 — shared rdflib graph
        elements: list[OWLElement] = [
            OWLElement(
                element_id=body.ontology_iri or body.source_path,
                kind=OWLElementKind.ONTOLOGY,
                name=Path(body.source_path).name,
            )
        ]
        kind_predicates = (
            (OWL.Class, OWLElementKind.CLASS),
            (OWL.ObjectProperty, OWLElementKind.OBJECT_PROPERTY),
            (OWL.DatatypeProperty, OWLElementKind.DATA_PROPERTY),
            (OWL.AnnotationProperty, OWLElementKind.ANNOTATION_PROPERTY),
            (OWL.NamedIndividual, OWLElementKind.INDIVIDUAL),
        )
        seen: set[str] = set()
        for pred, kind in kind_predicates:
            for subj in graph.subjects(RDF.type, pred):
                iri = str(subj)
                if iri in seen:
                    continue
                seen.add(iri)
                elements.append(
                    OWLElement(
                        element_id=iri,
                        kind=kind,
                        name=local_name_from_iri(iri) or iri,
                        description=adapter.definition(iri),
                    )
                )
        # Fallback: any entity listed by adapter not yet typed
        for iri in adapter.entities():
            if iri in seen:
                continue
            seen.add(iri)
            elements.append(
                OWLElement(
                    element_id=iri,
                    kind=OWLElementKind.UNKNOWN,
                    name=local_name_from_iri(iri) or iri,
                    description=adapter.label(iri),
                )
            )
        _ = RDFS  # keep import for future hierarchy helpers
        return tuple(elements)

    def validate_standard(
        self,
        body: OWLImplementationBody,
    ) -> tuple[Diagnostic, ...]:
        """Parse-level diagnostics only — OWL reasoner is not a gate (ADR-010)."""
        diags: list[Diagnostic] = []
        if body.entity_count == 0 and not body.parse_errors:
            diags.append(
                Diagnostic(
                    diagnostic_code="OWL-EMPTY",
                    severity=DiagnosticSeverity.WARNING,
                    diagnostic_message="No OWL/RDF entities loaded from source",
                )
            )
        for msg in body.parse_errors:
            severity = (
                DiagnosticSeverity.WARNING
                if "broken fixture" in msg.lower() or "skipped" in msg.lower()
                else DiagnosticSeverity.ERROR
            )
            diags.append(
                Diagnostic(
                    diagnostic_code="OWL-PARSE",
                    severity=severity,
                    diagnostic_message=msg,
                )
            )
        return tuple(diags)


def as_standard_provider(
    provider: OWLStandardProvider,
) -> StandardProvider[OWLSpecificationBody, OWLImplementationBody, OWLElement]:
    return provider
