---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# ADR-019: Publication contract inheritance

**Date:** 2026-09-28  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md) §17  
**Related:** [ADR-016](ADR-016-publication-section-kinds-and-profiles.md), [ADR-014](ADR-014-fibo-profile-metamodel.md), [ADR-015](ADR-015-viewer-ui-atlas.md), [ADR-013](ADR-013-specification-requirements-catalog.md)  
**Schema:** [moex-dsp.yaml](../../model-assets/specifications/moex-dsp/0.1/schemas/moex-dsp.yaml)

## Context

`SpecificationImplementation` may declare `conforms_to` a `ReferenceSpecification` (catalog nesting, kernel envelope). That does **not** mean the implementation must copy the reference’s `PublicationModule` ids, file names, or renderers.

Without an explicit publication contract, an implementation can claim DAMS conformance while publishing an arbitrary page that omits models, mappings, provenance, or conformance status — which destroys the meaning of `SpecificationImplementation` in the Publication Viewer.

This is **not** OWL / LinkML class inheritance (`is_a` / `subClassOf`). It is inheritance of a **publication contract**: mandatory semantic publication capabilities that must be satisfied by local sections.

ADR-016 already closed `PublicationSectionKind` and base `ProfileSpec` (required / recommended / forbidden kinds per artifact type). That covers “what shape of publication this is,” not “which capabilities of *this* reference specification must be covered.”

## Decision

### 1. Three independent layers

| Layer | Lives in | What it defines |
|---|---|---|
| Base artifact profile | ADR-016 `PublicationProfileId` / `ProfileSpec` | required / recommended / forbidden **kinds** for `linkml-specification` \| `ontology` \| `implementation` |
| Reference publication contract | `PublicationRequirement` on the Spec (DSP layer) | semantic capabilities (`logical-entities`, …), cardinality, accepted renderers, `applies_when` |
| Local manifest | Impl `publish.yaml` | local `PublicationModule` / `PublicationSection` titles, paths, renderers, and **`satisfies: [requirement_id…]`** |

Local module names, paths, and grouping **may and should** differ from the reference. Coverage is proven by `satisfies`, not by identical ids.

### 2. Conformance is on sections, not module identity

```text
∀ r ∈ Required(P_reference): ∃ s ∈ Sections(I) | s ⊨ r
```

**Not** `Modules(I) = Modules(ReferenceSpecification)`.

Architectural invariant (also MODELING_ARCHITECTURE §14.13 / §17):

> A specification implementation inherits publication-profile **obligations**, not publication-module **identity**. Every mandatory `PublicationRequirement` of the inherited reference profile must be covered by at least one `PublicationSection` with an explicit `satisfies` link, an accepted renderer, and a semantically valid source. Local module names, count, grouping, and order may differ and extend without breaking conformance.

### 3. Metamodel (DSP, not modeling-kernel)

- `PublicationRequirement` — `requirement_id`, `kind`, `semantic_capability`, `obligation`, occurs, accepted section types / renderers, `expected_semantic_types`, `applies_when`, `inherited_from`, `applies_to_profile`
- `PublicationProfile` — keep ADR-016 kind lists; add `parent_profile_ref`, `requirements`
- `PublicationSection.satisfies` → `PublicationRequirement` [0..*]
- `PublicationConformanceReport` + `RequirementResult` — publication-layer report; **distinct** from kernel `ConformanceReport` (model-body semantics)

Requirement kinds (closed):

| Kind | Checks |
|---|---|
| `required-section` | A section covers the capability (via `satisfies` / kind) |
| `required-semantic-content` | Source contains entities of expected semantic types |
| `required-binding` | Explicit `implements` / `conforms_to` to the reference |
| `required-evidence` | Provenance / confidence / evidence fields present |

Obligation: `required` \| `recommended` \| `forbidden`.

### 4. Aggregation, decomposition, substitution

- **Aggregation allowed:** one section may `satisfies` many requirements.
- **Decomposition allowed:** many sections may satisfy one requirement when cardinality is `1..*` (coverage is cumulative).
- **Semantic substitution forbidden:** declaring `satisfies: dams:logical-entities` for a CSV column list without `LogicalEntity` / mapping is invalid. Check `satisfies`, source semantic type, minimum content, and bindings — not title alone.

### 5. Publication conformance statuses

Separate from kernel `ConformanceResult`:

| Status | Meaning |
|---|---|
| `conformant` | All mandatory publication requirements covered and published |
| `partially-conformant` | Skeleton held; some aspects intentionally absent or conditionally N/A |
| `draft-conformant` | Structurally covers the profile; content is generated/inferred and not owner-approved |

Default for generated/inferred DSP pipelines: `draft-conformant` with `semantic_assertion_status: inferred` and `approval_status: pending-review`.

### 6. Relationship to ADR-016

ADR-016 remains the closed vocabulary of section **kinds** and the **base** ProfileSpec for artifact type. ADR-019 adds inherited **capabilities** and `satisfies` coverage. This ADR does **not** supersede ADR-016.

Base profile `implementation` still requires kinds `overview` and `conformance`. Inherited DAMS requirements (e.g. `logical-entities`) are additional obligations when the Impl declares a conformance profile against DAMS.

### 7. Soft vs hard validation

Phase 1 used soft warnings for missing `satisfies` coverage. **Phase 2** escalates **required** publication-contract failures (missing coverage, failed semantic-content / binding / evidence) to build/`viewer-check` hard fail. Recommended gaps stay warnings. ADR-016 ProfileSpec kind checks remain soft.

### 8. Viewer navigation consequence

For `profile: implementation`, sidebar roots are publication sections by kind / `satisfies` — not opaque wrappers («Разделы») and not LinkML schema package folders as the primary axis.

For `profile: linkml-specification`, ADR-016 roots apply (Overview / Classes / …); schema packages nest **under** Classes with human-readable titles.

Player metamodel `moex.dsp` documents the DSP shell (`linkml-specification`); it is **not** required to satisfy DAMS `logical-entities`. Future CSV-draft units are separate implementations with `profile: implementation` and `satisfies` to dams requirements.

## Consequences

- Spec assets may ship `publication-requirements.yaml` (or equivalent) listing requirements per conformance profile.
- Impl `publish.yaml` sections carry `kind` and `satisfies` when a reference contract applies.
- DSP glossary and Cursor publication rule document `satisfies`.
- Kernel body conformance and publication-contract conformance stay separate reports.
- **Phase 2:** viewer build/`make viewer-check` runs a semantic-content publication contract checker; **required** failures are hard errors. Each Impl with `implements` writes `publications/publication_conformance.json`; dist gets `publication_conformance_index.json`. Statuses: `conformant` | `partially-conformant` | `draft-conformant`.

## Alternatives rejected

| Alternative | Why not |
|---|---|
| `PublicationModule extends` reference module | Forces one-to-one ids/renderers/files; breaks DSP, FIBO profiles, OpenAPI, Data Contracts |
| Profile = `ModelingStandardFamily` | One family backs multiple publication shapes; ADR-016 already rejected this |
| Requirements only as ADR-016 kinds | Kinds do not express inherited Spec capabilities or semantic content |
| Put entities in `modeling-kernel.yaml` | Publication projection belongs to DSP (ADR-016 boundary) |

## Related

- ADR-016 — section kinds and base ProfileSpec
- ADR-014 — Spec vs Impl for FIBO; Impl still needs publication contract when claiming Spec
- ADR-015 — presentation; nav roots follow contract, not ad-hoc labels
- ADR-013 — DAMS *model* requirements catalog (orthogonal to publication requirements)
