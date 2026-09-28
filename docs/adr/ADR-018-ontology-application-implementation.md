---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# ADR-018: Ontology SpecificationImplementation = application / extension ontology

**Date:** 2026-09-28  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-010](ADR-010-owl-not-primary-validation.md), [ADR-014](ADR-014-fibo-profile-metamodel.md), [ADR-017](ADR-017-external-specification-source-sync.md), [ADR-020](ADR-020-external-specification-scope-and-term-selection.md)

## Context

OBO Foundry and FIBO practice separate a **reference ontology** (reusable, not application-bound) from an **application / extension / project ontology** (organization-specific, imports reference terms, adds local axioms, maps to local entities).

ADR-014 correctly made `moex-fibo-profile` a `ReferenceSpecification` (organizational metamodel) and split domain classes out of the Spec explorer. It also labeled FIBO *release* content as `SpecificationImplementation`. That conflates **upstream index / extract** with a MOEX-governed application ontology.

ADR-017 pins ROBOT-extracted FIBO modules under `model-assets/external-sources/`. An extract alone is still not a governed Impl: it has no MOEX namespace, extension axioms, or DAMS bridge under MOEX ownership.

## Decision

1. For OWL, a `SpecificationImplementation` is a **MOEX-owned application ontology** (project ontology): own namespace, version, lifecycle, and publish path — **not** a subset copy of FIBO.
2. The physical body is three committed artifacts under the Impl tree (e.g. `model-assets/implementations/ontologies/moex-fibo-application/0.1/`):
   - `metamodel/fibo-import-module.ttl` — pinned upstream slice (copy or path-ref to ADR-017 extract); read-only dependency
   - `metamodel/moex-fibo-extension.ttl` — MOEX namespace additions (`rdfs:subClassOf`, local classes/properties)
   - `metamodel/moex-dams-fibo-mapping.ttl` — bridge to DAMS entities (`owl:equivalentClass`, `rdfs:subClassOf`, SKOS, or custom predicates); may also reference managed SSSOM sets
3. Ontology-specific governance fields live in a **provider descriptor** (`ontology-application.yaml`), not on the kernel envelope: `conformance_level` (e.g. `FIBO Extension Conformant`), `seed_ref`, `imported_module_ref`, `extension_ref`, `mapping_ref`.
4. Kernel `SpecificationImplementation` stays generic (identity, version/revision, digest, `conforms_to`, lifecycle) — same pattern as DAMS Impl envelopes.
5. Catalog descriptor `moex:ontology:fibo` remains an **upstream release index** for Ontology Catalog / preview glossary. It is **not** the governed SpecImpl. The governed Impl id is `moex:implementation:moex-fibo-application:0.1` (asset `moex-fibo-application`).
6. ADR-014 stands for profile Spec; this ADR **refines** (does not supersede) the Impl side: release/index ≠ application ontology.

## Consequences

- Architecture catalog distinguishes upstream FIBO index from `moex-fibo-application`.
- Viewer may keep preview modules on the upstream index; wiring the three-file Impl into publication is a later step.
- ADR-017 sync does not auto-copy extracts into the Impl tree in MVP (descriptor may path-ref external-sources).
- ADR-010 unchanged: OWL is not the primary YAML validator.

## Alternatives

| Alternative | Why not |
|---|---|
| TTL files inside `moex-fibo-profile/metamodel/` | Mixes Spec metamodel YAML with Impl OWL body |
| ROBOT extract alone as SpecImpl | No MOEX namespace, governance, or DAMS bridge |
| `conformance_level` / `seed_ref` on kernel envelope | Kernel must stay standard-agnostic (MODELING_ARCHITECTURE §4) |

## Related

- ADR-010, ADR-014, ADR-017
- Asset: `model-assets/implementations/ontologies/moex-fibo-application/`
- Provider: `OntologyApplicationDescriptor` in `packages/standard-owl`
