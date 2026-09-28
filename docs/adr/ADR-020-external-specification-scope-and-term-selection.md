---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# ADR-020: External Specification Scope and Term Selection

**Date:** 2026-09-28  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-014](ADR-014-fibo-profile-metamodel.md), [ADR-016](ADR-016-publication-section-kinds-and-profiles.md), [ADR-017](ADR-017-external-specification-source-sync.md), [ADR-018](ADR-018-ontology-application-implementation.md), [ADR-019](ADR-019-publication-contract-inheritance.md)  
**Schema:** [moex-external-alignment](../../model-assets/specifications/moex-external-alignment/0.1/)

## Context

MOEX needs governed selection of terms from external reference specifications (FIBO, OpenAPI, AsyncAPI, ODCM, JSON Schema, …). ADR-017 syncs and materializes upstream pins; ADR-018 builds MOEX application ontologies on extracts. Neither defines:

- a **search/interest boundary** over an upstream version (which domains/modules are in scope for exploration);
- a **reviewable term selection** with competency questions, mapping decisions, and extraction roles.

Without this middle layer, teams either import whole FIBO domains or invent ad-hoc seed lists without governance.

## Decision

### 1. Three governance levels

```text
ExternalSpecification (+ Version)
  └── ExternalSpecificationScope
        └── ExternalTermSelection
              └── ExtractionPlan → MaterializedExternalModule (planned/actual)
                    └── feeds MOEX extension / mapping (ADR-018)
```

| Level | Meaning |
|---|---|
| ExternalSpecification[+Version] | Registered upstream identity and version pin |
| ExternalSpecificationScope | Navigational/content **search boundary** — not an import |
| ExternalTermSelection | Versioned, reviewable set of upstream terms for a use case |

Scope `included_areas` (e.g. FIBO `FND`, `BE`) **do not** auto-import domains or select all their terms.

### 2. Layout

- Sync remains under `model-assets/external-sources/` (ADR-017). Extend with `versions/<ref>/specification.yaml` for version metadata — **do not** add a parallel `external-specifications/` tree.
- Governance artifacts:
  - `model-assets/external-scopes/<id>/<version>/`
  - `model-assets/external-selections/<id>/<version>/`
- Metamodel Spec: `model-assets/specifications/moex-external-alignment/` (LinkML). Runtime DTOs + validators: `packages/modeling-kernel` `external_alignment`.

### 3. Kind mapping to ADR-017

`ExternalSpecificationKind` aligns with `SourceKind` where values overlap (`ontology`, …) and adds publication-oriented labels (`api-specification`, `schema`, `data-contract-standard`, `reference-data-standard`, `other`). Sync adapters continue to use ADR-017 enums; alignment YAML may use the richer vocabulary.

### 4. Mapping and seed rules

- Default candidate relation: `skos:closeMatch`.
- `owl:equivalentClass` / `owl:equivalentProperty` forbidden unless `review_status: approved`.
- **Draft** selection (`draft_only: true`): `extraction_role: seed` may apply to `candidate` terms → **warning**.
- **Published / non-draft** selection: seed requires `decision: accepted` and `review_status: approved`.
- Non-accepted / non-approved terms must not be treated as confirmed semantic mappings in the viewer.

### 5. Publication (ADR-019)

When a publication module uses an `ExternalTermSelection`, it inherits profile `fibo-external-term-selection` (or a generic successor) with requirements: overview, conformance, external-specification-scope, competency-questions, term-selection, mapping-table, extraction-provenance. Local section ids may differ; coverage is via `satisfies`.

Missing materialized module ⇒ publication status `draft-conformant` (visible), not a hard fail in MVP.

New `PublicationSectionKind` values (additive to ADR-016): `external-specification-scope`, `competency-questions`, `term-selection`, `mapping-table`, `dependency-list`, `extraction-provenance`.

### 6. Materialization

Scope never auto-creates a materialized module. Materialization requires `ExternalTermSelection` + `ExtractionPlan`. MVP records plans with `status: planned`; ROBOT sync remains ADR-017 CLI, not auto-run on validate.

## Consequences

- CLI: `moex-model selection validate`.
- First demo: FIBO party/participation scope + trading-participant-core selection.
- SSSOM and ADR-018 application ontology remain separate; selection may reference them later.

## Alternatives rejected

| Alternative | Why not |
|---|---|
| Import whole FIBO domain from `included_areas` | Wrong unit; ungoverned |
| Treat selection as SpecImpl | Conflates governance register with application ontology (ADR-018) |
| Parallel `external-specifications/` tree | Duplicates ADR-017 `external-sources/` |
| Default `owl:equivalentClass` | Too strong without review |

## Related

- ADR-014, ADR-016, ADR-017, ADR-018, ADR-019
- Package path: `moex_modeling.external_alignment`
