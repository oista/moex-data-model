# FIBO metamodel profile — design

**Date:** 2026-09-28  
**Status:** Approved for implementation  
**ADR:** [ADR-014](../../adr/ADR-014-fibo-profile-metamodel.md)  
**Guide:** [FIBO ONTOLOGY_GUIDE](https://github.com/edmcouncil/fibo/blob/master/ONTOLOGY_GUIDE.md)

## Problem

Publication Viewer treats FIBO as `reference_specification` but the explorer surfaces **domain `owl:Class` rows** (LegalPerson, BusinessDay). That is release content (`TImplBody`), not the ontology profile (`TSpecBody`). DAMS already separates Spec explorer (schema packages) from implementations.

## Decision

Two layers:

| Layer | Role | Content |
|-------|------|---------|
| **FIBO profile** | `ReferenceSpecification` | Organizational metamodel: domains, modules, ontology document headers, IRI/prefix patterns, annotation requirements |
| **FIBO release** | `SpecificationImplementation` | Preview glossary / class explorer / `AggregatedEntity` read models |

## Pydantic types (`moex_standard_owl.domain.fibo_metamodel`)

- `FiboDomain` — code, title, iri_segment
- `FiboModule` — id, domain_code, path segments, title
- `FiboOntologyDocument` — ontology/version IRI, label, abstract, license, copyright, maturity, imports, abbreviation, filename, module_id
- `FiboIriPattern` / `FiboPrefixPattern` — templates from GUIDE §FIBO standard IRI format
- `FiboElementKind` — enum of metamodel kinds (not domain instances)
- `FiboAnnotationRequirement` — required annotation property + applies_to (`ontology_header` \| `element`)
- `FiboSpecificationBody` — root TSpecBody aggregating the above

## Assets

`model-assets/specifications/moex-fibo-profile/0.1/` — envelope + mini YAML (FND/BE + BusinessDates / LegalPersons) + explorer projection for the viewer.

## Non-goals

- Port of [onto-viewer](https://github.com/edmcouncil/onto-viewer)
- OWL reasoner / full hygiene SPARQL suite
- LinkML codegen for the profile
- Full upstream FIBO RDF in git
