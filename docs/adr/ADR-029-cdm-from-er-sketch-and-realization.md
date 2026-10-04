---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# ADR-029: Conceptualizing ER sketches into CDM; realization completeness (not subclass)

**Date:** 2026-10-05  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-021](ADR-021-dams-implementation-profile-and-levels.md), [ADR-023](ADR-023-governed-property-cascade.md), [ADR-025](ADR-025-definition-cascade-and-glossary.md), [ADR-026](ADR-026-cmd-entity-metamodel.md)  
**Requirements:** [it-solution-requirements.yaml](../../model-assets/specifications/moex-dams/0.1/requirements/it-solution-requirements.yaml) (LDM-008)

## Context

Enterprise ER sketches (e.g. `CModel_content04.drawio`) list tables with PK/FK
columns and unlabeled connectors. The digital enterprise conceptual model
(КМД) is a **conceptual** SoT: entities, named relationships, tiers/genesis
(ADR-026) — not an ER copy. Two recurring design questions:

1. Should `ConceptualEntity` carry “main attributes” (identity / FK columns)
   so the graph looks more structured?
2. Should `LogicalEntity` **subclass** a conceptual entity (OOP inheritance)
   instead of today’s `conceptual_entity_refs` + `Mapping(realizes)`?

Copying PK/FK into КМД or treating ЛМД as subclasses would blur layers,
collide with XOR party roles, and contradict ADR-023 (no governed cascade
along `realizes`).

## Decision

### 1. Conceptualize ER sketches — do not import columns

When lifting an ER draft into enterprise CDM:

| ER sketch | CDM |
|---|---|
| Table / entity | `ConceptualEntity` (primary or dependent per ADR-026) |
| FK column / connector | `Relationship` + `RelationTerm` (one row per pair) |
| Associative table | `entity_tier: dependent`, `dependency_kind: associative` |
| Characteristic / detail | `entity_tier: dependent`, `dependency_kind: characteristic` |
| Role table (e.g. Участники торгов) | Reified concept (`TradingParticipation`), **not** subclass of `LegalEntity` |
| PK / typed attributes | Stay on **logical** layer (`LogicalAttribute`) |

**No `ConceptualAttribute` class.** Slot `key_attribute_refs` remains unused for
identity hints in this wave; identity characteristics use dependent concepts
(e.g. `OrganizationIdentifier`).

Cardinality on sketch edges is usually absent — modelers supply
`source_min_cardinality` / `target_*` deliberately.

### 2. Solution ↔ enterprise remains alignment, not subclass

- Intra-CDM generalization: `ConceptualEntity.parent_concept_ref` only
  (e.g. `LegalEntity` → `Organization`; `SettlementCode` → `AccountRelationship`).
- Cross-layer: `LogicalEntity.conceptual_entity_refs` + optional
  `Mapping(mapping_type: realizes)` (ADR-021). Status via LDM-006.
- One logical entity may realize several concepts; grain may differ
  (solution client ≠ `LegalEntity` ≠ `TradingParticipation`).
- XOR roles (Клиент → физлицо **или** юрлицо) stay as optional relationships
  on a **primary** `Client`; do not encode as AND `depends_on_refs`.

Governed-property and definition cascades stay on their ADR-023 / ADR-025
axes — not along `realizes`.

### 3. Realization completeness (LDM-008)

When a solution package declares `conceptual_implementation_ref` and a
`LogicalEntity` is `aligned` to a **dependent** enterprise concept, the
solution SHOULD also have a logical `Relationship` to a peer logical entity
that realizes each owner listed in that concept’s `depends_on_refs`
(identifying / mandatory conceptual owner links).

Severity: **warning** (transitional; existing solutions must not fail hard).

This is structural guidance for modelers — not attribute inheritance and not
LinkML class inheritance.

## Consequences

- Trading / party slice from the drawio green domain + party hub is authored
  as conceptual entities and relationships in
  `moex-enterprise-conceptual-model`.
- Wave 2 authors the blue commercial + HR slice (Counterparty, Product/Sale/
  Payment, Department/Employee/Role, …). Deferred: ABS / accounts /
  info-systems / postings and green draft junk (curves, deposits, portfolio).
- Catalog gains LDM-008; formal_checks loads the enterprise body by
  `conceptual_implementation_ref` for the warning.
- Viewer / glossary continue to treat glossary as a generated view of
  concepts + relation terms (ADR-025/026).

## Alternatives

| Alternative | Why not |
|---|---|
| Introduce `ConceptualAttribute` + cascade into ЛМД | Duplicates LMD; ER columns are not corporate concepts; rejected in ADR-023 wave |
| `LogicalEntity` subclasses `ConceptualEntity` | Multi-realize, grain mismatch, XOR roles; ADR-021 already defines `realizes` |
| Copy all 74 drawio tables 1:1 | Mixes operational/draft tables; ADR-026 deferred full import |
| Encode Client as dependent on Person ∧ LegalEntity | AND `depends_on` contradicts XOR party typing |

## Related

- ADR-021, ADR-023, ADR-025, ADR-026
- Fixture: `model-assets/implementations/enterprise/moex-enterprise-conceptual-model/0.1/`
