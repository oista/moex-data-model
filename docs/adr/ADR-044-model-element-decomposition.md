---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# ADR-044: ModelElement decomposition

**Date:** 2026-10-06  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-023](ADR-023-governed-property-cascade.md), [ADR-025](ADR-025-definition-cascade-and-glossary.md), [ADR-038](ADR-038-datastructure-and-schemanode.md), [ADR-040](ADR-040-message-integration-model.md)  
**Inventory:** [model-element-inventory-report.md](../architecture/model-element-inventory-report.md), [model-element-matrix-before.csv](../architecture/model-element-matrix-before.csv)

## Context

`ModelElement` mixes `HasLifecycle` and declares `name` / `description` globally `required: true`. Consequences:

- Service / alignment objects that need only an id and a validity window inherit identity, naming, and lifecycle they do not use.
- Softening of `description` is hand-copied via `slot_usage` into six classes (`ConceptualEntity`, `ConceptualProperty`, `LogicalEntity`, `LogicalAttribute`, `RelationTerm`, `Message`).
- `Mapping` redeclares `valid_from` / `valid_to` already present in `HasLifecycle`.
- `EmbeddedElement` owns a separate `description` instead of sharing a described mixin.
- Classes with their own identifier (`ExternalClassRef.external_class_ref_id`, `ClassificationAssignment.assignment_id`, `PolicyBinding.policy_binding_id`, `RegistryEntry.registry_id`, `ValueMeaning.meaning_key`, `MOEXModelRepository.repository_id`, …) cannot become `IdentifiedElement` without colliding on LinkML's single-identifier rule.

Governed-property mixins (`HasOwnership`, `HasGovernanceClassification`, `HasPolicyBindings`, `HasBusinessClassification`) already exist and participate in the ADR-023 cascade; a new `GovernedElement` superclass is **not** introduced.

## Decision

### D1. `description` is not globally required

- `required: true` only on `ModelPackage` and `DomainContext` (plus an allowlist of classes that already require it today — see inventory; keep invariant until a later decision).
- `recommended: true` (warning) on `DataStructure` and other `ModelElement` classes without `HasDefinition` where the inventory marks them for softening.
- `Relationship.description` is optional (see D4).

### D2. One `slot_usage` for definitional description

- Move the shared `slot_usage.description` into `HasDefinition` once; delete the five copies and the `Message` copy.
- `HasDefinition` must actually induce `description`: `mixins: [DescribedElement]` (or list `description` in slots).
- Do **not** change `slot_uri` of `description` (today: default `dams:description`). Changing it to `dcterms:description` would break RDF/OWL/SHACL consumers. Add `exact_mappings: [skos:definition]` (or `close_mappings`) via `slot_usage` on `HasDefinition`; SKOS projection is documented in the OWL transform. A `slot_uri` change requires a separate ADR and PR-1b marked "breaking for RDF".

### D3. Mapping (step 1 = schema 2.1.0)

- Keep `HasLifecycle` + `HasProvenance`; drop own `valid_from` / `valid_to`.
- Deprecate `name`, `title`, `aliases`, `glossary_term_refs`, `tags` on `Mapping` via `slot_usage` (not on global slots).
- `Mapping.name` becomes `required: false` in the same step (cannot be both deprecated and required). Exception to the required-slot invariant; migration notes: Pydantic type becomes `Optional[str]`.
- Viewer / migration label = `source_refs -> target_refs` + `mapping_type`; `name` remains fallback until 3.0.0.

### D4. Relationship stays `ModelElement`

`description` optional.

### D5. Three role levels

For each schema class:

1. Referenced from outside its parent → `IdentifiedElement` (`element_id`); else `EmbeddedElement` (`local_key`).
2. Own validity / approval window → `HasValidity` / `HasProvenance`.
3. Named, searchable notion → `ModelElement` (+ `NamedElement`).

New mixin `HasValidity` (`valid_from`, `valid_to`); `HasLifecycle` includes it and adds `lifecycle_status`, `deprecated_by_ref`.

**IdentifiedElement is not for every service class.** LinkML allows one identifier per class. Classes with a proprietary id stay on their own id and may only gain `HasValidity` / `HasProvenance`. D8 (base-class change) applies only where `element_id` already exists or is required. Exact class lists live in the inventory report.

**ValueMeaning** stays an exception: renaming `meaning_key` → `local_key` would break data; do not force `EmbeddedElement` without a data migration ADR. Recorded in the inventory report §3.

### D6. No `VersionedArtifact` mixin yet

Abstract slot `artifact_version` (range `SemVer`); `model_version` and `structure_version` use `is_a`. Revisit a mixin when a third class grows `previous_version_ref` + `content_digest`.

### D7. EmbeddedElement uses DescribedElement

Drop EmbeddedElement's own `description` slot and `slot_usage`. `EmbeddedElement` and `IdentifiedElement` do not share a parent.

### D8. Two-step migration

| Schema version | Action |
|---|---|
| **2.1.0** | Additive mixins (`moex-base`), move `slot_usage`, deprecate Mapping identity slots, introduce `HasValidity`, `artifact_version` |
| **3.0.0** | Remove deprecated Mapping identity slots; Mapping `is_a: IdentifiedElement` (+ `HasLifecycle`, `HasProvenance`, `DescribedElement`); catalogue path `0.1/` retained |

Implemented in this series: schema is at **3.0.0** after PR-6.

### Target shape (`moex-base` + `moex-core`)

```yaml
IdentifiedElement: {abstract: true, slots: [element_id]}
NamedElement:      {mixin: true, slots: [name, title, aliases]}
DescribedElement:  {mixin: true, slots: [description]}   # not required
HasSemanticAnnotations: {mixin: true, slots: [glossary_term_refs, tags]}
HasValidity:       {mixin: true, slots: [valid_from, valid_to]}
ModelElement:
  abstract: true
  is_a: IdentifiedElement
  mixins: [NamedElement, DescribedElement, HasLifecycle, HasSemanticAnnotations]
```

New classes/mixins are **not** added to `moex-structure` (ADR-040 core↔structure cycle debt).

## Alternatives considered

| Alternative | Rejected because |
|---|---|
| Soften `description` only via more `slot_usage` copies | Debt grows with every HasDefinition class |
| Set `slot_uri: dcterms:description` / `skos:definition` now | Breaking for RDF consumers; deferred to PR-1b |
| `GovernedElement` superclass | Mixins + ADR-023 cascade already cover governance |
| Force all service classes onto `IdentifiedElement` | Violates single-identifier rule; breaks existing ids |
| `VersionedArtifact` mixin now | Premature until a third versioned class appears |

## Consequences

- PR-0 commits the before-matrix and this ADR (`Proposed`); schema unchanged.
- PR-1 introduces `moex-base.yaml`, bumps schema to **2.1.0**, moves definitional `slot_usage`, keeps JSON Schema required sets (except documented Mapping.name exception in PR-3).
- Architecture-check gains an allowlist for `slot_usage.description` (PR-2); list must not grow without an ADR note.
- Duplicate ADR-034 / ADR-035 numbering is out of scope here (handled by `chore/adr-renumber-phase1-tail` → ADR-042 / ADR-043).
- Frontmatter `superseded_by: MODELING_ARCHITECTURE.md` on Accepted ADR-038 / ADR-040 / ADR-041 (and the ADR index README) is incorrect for Accepted ADRs; noted, not fixed in this ADR.

## Spike results (PR-0, LinkML 1.11.1)

See inventory report § Spike. Summary: mixin `slot_usage` with `DescribedElement` works; `exact_mappings` do not rewrite OWL predicates (SKOS projection stays in the transform); `recommended: true` is generator-safe; Pydantic MRO is `HasLifecycle, HasSemanticAnnotations, DescribedElement, NamedElement, IdentifiedElement`.
