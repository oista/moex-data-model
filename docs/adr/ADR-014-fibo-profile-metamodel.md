---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# ADR-014: FIBO profile — ReferenceSpecification; release entities — SpecificationImplementation

**Date:** 2026-09-28  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-010](ADR-010-owl-not-primary-validation.md), [ADR-007](ADR-007-pydantic-dto-not-validator.md)  
**Design:** [2026-09-28-fibo-metamodel-profile-design.md](../superpowers/specs/2026-09-28-fibo-metamodel-profile-design.md)

## Context

In the Publication Viewer, FIBO appeared as `reference_specification` while the explorer showed domain `owl:Class` terms from the glossary preview. That mixes **specification body** (how FIBO organizes ontologies) with **implementation/content** (LegalPerson, BusinessDay, …) and diverges from the DAMS pattern (explorer = `TSpecBody`; implementations nested via `conforms_to`).

EDM Council documents the organizational and terminology conventions in [ONTOLOGY_GUIDE](https://github.com/edmcouncil/fibo/blob/master/ONTOLOGY_GUIDE.md). [onto-viewer](https://github.com/edmcouncil/onto-viewer) is a useful UX reference, not a stack we embed.

## Decision

- **FIBO profile** (`moex-fibo-profile`) is a `ReferenceSpecification` expressed in OWL 2. Its body is a lean Pydantic metamodel (`FiboDomain`, `FiboModule`, `FiboOntologyDocument`, IRI/prefix patterns, `FiboAnnotationRequirement`) loaded from YAML under `model-assets/specifications/moex-fibo-profile/`.
- **FIBO release content** (glossary, class explorer, `AggregatedEntity` / catalog entities) is a `SpecificationImplementation` that `conforms_to` the profile. Domain classes are not the metamodel.
- Conventions come from ONTOLOGY_GUIDE (ontology header, IRI format, naming/labels, required annotations). We do **not** model full OWL 2 DL axioms or port onto-viewer.
- Pydantic models are DTOs / structural forms (ADR-007). OWL reasoner remains out of the primary validation path (ADR-010).
- Publication: Spec module explorer = metamodel tree; Impl module = subject-domain classes.

## Consequences

- `architecture-catalog.yaml` splits FIBO into Spec + Impl nodes with two publication modules.
- ADR-010 stays in force; this ADR only clarifies Spec vs Impl for FIBO.
- Ontology Catalog release descriptors (`moex:ontology:fibo`) remain read models of release content; the profile is a separate specification asset.

## Alternatives

| Alternative | Why not |
|---|---|
| Keep domain classes in Spec explorer | Conflates TSpecBody and TImplBody |
| LinkML codegen for the profile (like DAMS) | Deferred; YAML + hand Pydantic is enough for structure |
| Embed onto-viewer | Out of scope; different runtime and product boundary |

## Related

- ADR-007, ADR-010, ADR-013 (parallel Spec-body enrichment for DAMS requirements)
