---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# ADR-025: Definition cascade and glossary terminology

**Date:** 2026-10-04  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-001](ADR-001-linkml-yaml-canonical.md), [ADR-012](ADR-012-semantic-diff-review.md), [ADR-013](ADR-013-specification-requirements-catalog.md), [ADR-020](ADR-020-external-specification-scope-and-term-selection.md), [ADR-023](ADR-023-governed-property-cascade.md), [ADR-024](ADR-024-unified-class-entity.md), [ADR-027](ADR-027-glossary-term-relations.md)  
**Amends:** ADR-023 (closes deferred `realizes` inheritance for **definitions** only), ADR-024 (generalises “glossary = view”)  
**Amended by:** [ADR-027](ADR-027-glossary-term-relations.md) (term-relation families; related ≠ assignment / definition source)  
**Requirements:** [IT_SOLUTION_MODEL_REQUIREMENTS.md](../architecture/IT_SOLUTION_MODEL_REQUIREMENTS.md)

## Context

“Glossary” and “definition” were overloaded across six places: required
`ModelElement.description`, `glossary_term_refs` → `GlossaryTerm`, viewer
`glossary` sections, hand-written `dams_glossary.json`, SKOS concept schemes,
and the developer doc `LinkML_Glossary_DAMS.md`. LDM-002 requires an
unambiguous definition, but every level copied text into `description` with no
own vs inherited distinction and no way to inherit from an ontology class or
corporate glossary term.

ADR-023 already established *declared vs effective* for governed properties
along **containment**. Definition inheritance follows a different axis —
**semantic chain** across packages and external specs (ontology class →
enterprise conceptual → solution logical → system-scoped). ADR-023 deferred
“inherit via `realizes`”; this ADR specifies that extension for definitions
only. Ownership / classification / policies stay on the containment cascade.

LinkML maps `description` to `skos:definition` and provides `alt_descriptions`
for attributed alternatives — the same pattern we need for scoped definitions.
Data catalogs treat glossary terms as assignable assets with one definition;
asset descriptions are separate. ODCS `authoritativeDefinitions` matches our
`definition_source_ref`.

## Decision

### Terminology (normative)

| Term | Meaning |
|---|---|
| **Term** (designation) | `name`, `title`, `aliases` |
| **Definition** | Single reference definition of an element at a modeling level |
| **Scoped definition** | Additional definition in a context; does **not** replace the reference definition outside that scope |
| **Glossary** | Always a **view** of definitions for a given coverage — not a dataset and not an entity. Three kinds: ontology (ADR-024), model (enterprise + solution entities), corporate (external master) |
| **`GlossaryTerm`** | Registry projection of a corporate-glossary master record (name kept for migration stability) |
| **`glossary_term_refs`** | Term *assignment* (catalog-style link); orthogonal to where the definition text comes from; **not** associative related (ADR-027) |
| **`definition_source_ref`** | Where the **definition text** is inherited or adapted from; **not** related / See also (ADR-027) |
| SKOS / hand JSON | **Projections**, not authoritative sources. `dams_glossary.json` is a candidate for generation. Corporate broader/narrower/related live in the SKOS projection (ADR-027), not on `GlossaryTerm` |

`LinkML_Glossary_DAMS.md` is a developer metamodel cheat-sheet, not a business
glossary.

### Definition cascade (second axis)

YAML stores only **declared** values. A resolver computes the **effective**
definition with provenance. Effective text is **never** written back into YAML.
Semantic diff (ADR-012) continues to compare declared slots.

```
OntologyClass (exact only) ──► ConceptualEntity ──► LogicalEntity
Corporate GlossaryTerm ──────►        │                  │
                                      │                  ▼
                                      │           ScopedDefinition (system)
                                      ▼
                               Data catalog export
```

**Resolution** `resolve_definition(element, scope=None)`:

1. Matching `scoped_definitions` for `scope` → most specific; mode `scoped`.
2. Else non-empty `description` → mode `own` (if `definition_source_ref` also
   set → “own, adapted from”).
3. Else `definition_source_ref` → recursively resolve target; mode `inherited`.
   Ontology targets require an **exact** correspondence (`skos:exactMatch` /
   `owl:equivalentClass`). Exactness is taken from the owning
   `ConceptualEntity.external_class_refs[].match_kind` when present (ADR-026),
   else from the external definition provider. `closeMatch` / `broadMatch` do
   **not** inherit; the element must declare its own `description` (may still
   cite the source via `definition_source_ref` as attribution).
4. Else for `LogicalEntity` with exactly one `conceptual_entity_refs` →
   inherit that concept’s reference definition (implicit). Multiple refs
   without an explicit source or own text → error.
5. Else unresolved → diagnostic.

Result: `(text, language, source_element_id, level, mode, scope, source_hash)`.

**Alignment status:** `aligned` may inherit; `pending` / `local-only` /
`not-applicable` require own `description`.

**v1 coverage:** `ConceptualEntity`, `LogicalEntity`, `LogicalAttribute`
(attributes: own only). Physical elements do not carry definitions; semantics
come from `Mapping`. Language is a separate axis (resolver returns language;
`definition_ru` etc. out of v1). Drift reports for inherited text — follow-up.

### Schema

- Mixin `HasDefinition`: `definition_source_ref`, `definition_rationale`,
  `scoped_definitions`.
- Class `ScopedDefinition` (+ `HasProvenance`): `scope_kind` (v1: `system`),
  `scope_ref`, `text`, `relation_to_reference`
  (`refines` / `narrows` / `alternative` / `replaces`), `rationale`.
- On definition-bearing classes: `slot_usage: description: required: false`
  (LinkML idiom). Keep slot name `description` (`skos:definition`); do **not**
  introduce a parallel `definition` slot.
- `scope_ref` for `system` must be a member of the solution’s
  `ITSolution.member_system_refs`.

### formal_checks

- LDM-002.c3: resolvable **effective** definition (not raw `description` alone).
- Error: missing / non-exact ontology source; ambiguous multi-ref without
  source; `scope_ref` outside solution systems.
- Warning: own override without `definition_rationale`.
- Info: declared text equals inherited (redundant); `description` equals
  `title`.

### Compatibility

| Consumer | Mapping |
|---|---|
| Data catalog | Effective definition → asset description; `glossary_term_refs` → term assignment; scoped → system-scoped asset description |
| Ontology / FIBO | Inherit only under exact match; otherwise adapted own text + attribution |
| ODCS | `definition_source_ref` ≈ `authoritativeDefinitions` |
| LinkML | Same slot as `skos:definition`; scoped ≈ `alt_descriptions` with richer scope metadata |

## Consequences

- New resolver module (not an extension of `GOVERNED_FAMILIES`).
- Existing models with filled `description` remain valid as `own`.
- Viewer provenance UI and auto-generated model glossary are delivered under
  ADR-026 (`build_model_glossary`); the resolver contract remains the interface.
- ADR-023’s deferred “inherit via `realizes`” is **closed for definitions**;
  other governed families still do not inherit across `realizes`.
- Exact-match source for ontology targets is amended by ADR-026
  (`external_class_refs.match_kind`).

## Alternatives

| Alternative | Why not |
|---|---|
| New slot `definition` beside `description` | Duplicates LinkML’s `skos:definition` mapping; two texts to keep in sync |
| Copy-down into YAML | Same defects as ADR-023 (lost inherit vs override, noisy diffs) |
| Union of definitions | Ambiguous “one reference definition” invariant |
| Inherit via `closeMatch` | SKOS closeMatch is not substitutable; false precision |
| Scoped defs as separate glossary entities | Explodes term identity; scoped text is contextual, not a new term |
| Extend containment cascade for definitions | Cross-package / external sources; wrong axis |

## Related

- ADR-001, ADR-012, ADR-013, ADR-020, ADR-023, ADR-024, ADR-026, ADR-027
- Resolver: `packages/specification-dams/src/moex_dams/rules/definitions.py`
)
