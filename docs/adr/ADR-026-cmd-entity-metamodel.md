---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# ADR-026: Conceptual entity metamodel (tier, genesis, relation terms)

**Date:** 2026-10-04  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-020](ADR-020-external-specification-scope-and-term-selection.md), [ADR-021](ADR-021-dams-implementation-profile-and-levels.md), [ADR-023](ADR-023-governed-property-cascade.md), [ADR-024](ADR-024-unified-class-entity.md), [ADR-025](ADR-025-definition-cascade-and-glossary.md)  
**Amends:** ADR-021 (§4 relation table), ADR-025 (exact source via `match_kind`)  
**Requirements:** [conceptual-model-requirements.yaml](../../model-assets/specifications/moex-dams/0.1/requirements/conceptual-model-requirements.yaml)

## Context

The enterprise conceptual model (КМД) needs a richer `ConceptualEntity` than
today’s slots (`parent_concept_ref`, `HasBusinessClassification`,
`HasDefinition`). Project ER sketches (e.g. `CModel_content04.drawio`) show:

1. Named business links with **asymmetric labels** on each side
   (Участник торгов → *участвует* → Сделка; Сделка → *совершается* → Участник).
   DAMS `Relationship` has free-text `source_role` / `target_role` and no
   governed dictionary of relation terms; inverse edges are duplicated by hand.
2. A structural split between **independent** concepts and concepts that cannot
   exist without owners (associative tables, characteristics). This is orthogonal
   to `business_importance` and `entity_type`.
3. A genesis split: concepts that **align to** an ontology class or external
   specification vs **native** MOEX concepts. Alignment today lives only in
   `Mapping(aligns_with)` without `match_kind`, so ADR-025 cannot derive
   exact-vs-close for definition inheritance from the model itself.
4. ADR-025 deferred the auto-generated **model glossary** view; relation terms
   must appear in that view alongside entities.

Name traps: `implements` is SpecImpl→Spec; `realizes` is solution→enterprise.
Conceptual→external class uses `external_class_refs` / `aligns_with`, not those
verbs.

## Decision

### 1. Relation terms

New class `RelationTerm` (`is_a: ModelElement`, mixin `HasDefinition`):

| Slot | Meaning |
|---|---|
| `forward_label` / `forward_label_en` | Label when reading source → target |
| `inverse_label` / `inverse_label_en` | Label when reading target → source (required unless `symmetric`) |
| `symmetric` | Same label both ways |
| `default_relationship_kind` | Optional default for `Relationship.relationship_kind` |
| `ontology_property_ref` | Optional IRI of an `owl:ObjectProperty` (reserve; no property import in this ADR) |

Storage: inline list `ModelPackage.relation_terms` and/or a sibling YAML
(`relation-terms.yaml`) in the enterprise package (conceptual SoT).

`Relationship` gains:

- `relation_term_ref` → `RelationTerm`
- `term_direction`: `forward` | `inverse` (which side the assertion is written from)

**One Relationship record per pair.** Labels on each side are derived from the
term. `source_role` / `target_role` remain role names, not dictionary terms.
`relationship_kind` remains the structural category (association, composition, …).

Checks: term resolves; non-symmetric terms require `inverse_label`; warning when
an `active` enterprise relationship lacks `relation_term_ref` (transitional).

### 2. Entity tier (primary vs dependent)

| Slot | Values |
|---|---|
| `entity_tier` | `primary` \| `dependent` |
| `dependency_kind` | required when dependent: `characteristic` \| `associative` |
| `depends_on_refs` | ≥1 ConceptualEntity refs when dependent; empty when primary |

- **primary**: existence does not depend on other КМД entities (FK presence in
  an ER sketch is not sufficient — e.g. Сделка is primary).
- **dependent**: cannot exist without owner(s). `characteristic` = part/detail
  of an owner; `associative` = resolves M:N between owners (Codd RM/T / IDEF1X).

Orthogonal to `entity_type`, `data_class`, `business_importance`. Not part of
the ADR-023 containment cascade.

Checks: acyclic `depends_on` graph; each `depends_on` backed by a mandatory
relationship (`source_min_cardinality >= 1`, preferably `identifying: true`);
primary forbids non-empty `depends_on_refs`.

### 3. Genesis and external class refs

| Slot | Values |
|---|---|
| `genesis_kind` | `external` \| `native` |
| `external_class_refs` | list of `ExternalClassRef` |

`ExternalClassRef` (+ `HasProvenance`):

- `target_ref` — IRI / CURIE of the external class or term
- `match_kind` — `exact` \| `close` \| `broad` \| `narrow` \| `equivalent`
  (SKOS + `owl:equivalentClass`; aligned with `moex-external-alignment`)
- `source_kind` — `ontology` \| `corporate-architecture` \| `business-model` \|
  `api-spec` \| `other`
- optional `external_specification_ref`, `selection_ref` (ADR-020)

Invariant: `external` ⇔ ≥1 `external_class_refs`; `native` ⇔ empty.
Absence of a link is allowed and implies `native`.

**Canonical store** of conceptual↔external class links is `external_class_refs`.
`Mapping(aligns_with)` remains for ExternalTermSelection projections and
non-entity elements; a warning fires on disagreement with
`external_class_refs`.

### 4. Definition inheritance (amends ADR-025)

When resolving `definition_source_ref` to an external term, **exactness** is
taken from the owning entity’s `external_class_refs[].match_kind` for that
target (`exact` / `equivalent` allow inherit; `close` / `broad` / `narrow` do
not). This closes the gap where exactness lived only in an in-memory provider.

### 5. Model glossary view

`build_model_glossary` produces a **view** (ADR-025): rows of kind `entity` and
`relation-term` with effective definition + provenance. Published under the
enterprise module’s `glossary` section; not a hand-edited JSON dataset.
`dams_glossary.json` for the DAMS *specification* module is out of scope.

## Consequences

- Schema enums and classes in `moex-types` / `moex-core`; formal checks
  CM-CON-002 / CM-CON-003 / CM-REF-002 (warning during transition).
- Enterprise Party slice migrates: tiers, genesis, relation-term dictionary,
  merge of inverse Relationship duplicates.
- Viewer shows glossary + relation terms; minimal own/inherited badge.
- Full drawio import (~70 entities) is a separate wave.

## Alternatives

| Alternative | Why not |
|---|---|
| Keep inverse as a second Relationship | Duplicates; no shared dictionary |
| Encode tier as `business_importance` | Different axis; mixes structural independence with priority |
| Only `Mapping(aligns_with)` for external classes | No `match_kind` on Mapping; poor UX on the entity |
| Third tier beyond primary/dependent | Associative vs characteristic already covered by `dependency_kind` |
| Name the link `implements` / `realizes` | Collides with SpecImpl and solution→enterprise |

## Related

- ADR-020, ADR-021, ADR-023, ADR-024, ADR-025
- Schema: `RelationTerm`, `ExternalClassRef` in `moex-core.yaml`
- Rules: `conceptual_entity.py`, `relation_terms.py`, `glossary.py`
