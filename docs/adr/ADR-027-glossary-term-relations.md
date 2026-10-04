---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# ADR-027: Glossary term relations (hierarchy vs associative vs equivalence)

**Date:** 2026-10-04  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-020](ADR-020-external-specification-scope-and-term-selection.md), [ADR-024](ADR-024-unified-class-entity.md), [ADR-025](ADR-025-definition-cascade-and-glossary.md), [ADR-026](ADR-026-cmd-entity-metamodel.md)  
**Amends:** ADR-024 (hierarchy ≠ related), ADR-025 (term-relation terminology)  
**Architecture note:** [ontology-catalog.md](../architecture/ontology-catalog.md)

## Context

ADR-024 and ADR-025 establish that every **glossary** is a **view** of
definitions for a coverage (ontology / model / corporate), not a separate
dataset. Ontology hierarchy is asserted `rdfs:subClassOf` (preview:
`parent_local_name`). Corporate term–term relations are sketched only in a
sample SKOS projection (`skos_concepts.yaml`) that is not wired into the
viewer. Model glossary rows omit `parent_concept_ref` and have no associative
links.

Without an explicit rule, related terms risk being:

1. folded into the hierarchy tree as extra edges (false is-a, cycles);
2. authored as a hand-maintained `related` column on glossary CSV/JSON
   (second graph against “glossary = view”);
3. conflated with `glossary_term_refs`, `definition_source_ref`, or
   `closeMatch` / `broadMatch` / `narrowMatch`.

ISO 25964 and SKOS separate **hierarchical** (BT/NT, broader/narrower),
**associative** (RT, `skos:related`), and **equivalence** (UF/USE, exact
match / synonym). This ADR adopts that split for all three glossary kinds.

## Decision

### Three relation families (normative)

| Family | Meaning | UI surface | Is **not** |
|---|---|---|---|
| **Hierarchy** | Kind-of / subclass / BT–NT | Tree / Classes + Taxonomy / `extends` | Related |
| **Equivalence** | Synonym, exactMatch, term assignment | Aliases, mapping, `glossary_term_refs` | Related and not hierarchy |
| **Associative (RT)** | “See also”, non-transitive | **See also** on the term card | Parent/child, closeMatch, definition source |

Rules:

1. **Related is symmetric and non-transitive.** It must not appear as a tree
   edge. Putting RT into the hierarchy invents false is-a and can introduce
   cycles.
2. **Parent/child are not duplicated in See also.**
3. **Siblings are not automatically related.**
4. **`closeMatch` / `broadMatch` / `narrowMatch`** are alignment quality
   (ADR-020 / ADR-026), not RT and not BT.
5. **Glossary rows do not author `related_terms`.** Associative links are
   **derived** from the native graph of the coverage, the same way effective
   definitions are resolved (ADR-025) rather than copied into a glossary
   dataset.

### Sources by glossary kind

| Kind | Hierarchy (native) | Associative (derived) | Equivalence / assignment |
|---|---|---|---|
| **Ontology** (ADR-024) | `rdfs:subClassOf` → `parent_local_name` | Named **object properties** between classes in the same coverage (when property data exist; ADR-024 §7). Until then See also is empty — do not invent siblings. | SSSOM / `related_glossary_terms` on ontology cards = corporate term **assignment**, not RT |
| **Model** (ADR-026) | `parent_concept_ref` on `ConceptualEntity` | Other entities linked by `Relationship` / `RelationTerm` dictionary | `glossary_term_refs` (assignment); `definition_source_ref` (text provenance, not RT); `external_class_refs.match_kind` (alignment) |
| **Corporate** | SKOS `broader` / `narrower` in the concept-scheme **projection** | SKOS `related` in the same projection | Synonyms / altLabel; mappings to DAMS / ontology IRIs |

`GlossaryTerm` remains a thin `RegistryEntry`. SKOS broader/narrower/related
live in the **projection** (`skos_glossary.py` / concept scheme YAML), not as
slots on the DAMS class. The master remains external.

### Cross-coverage

Do **not** resolve See also across glossary kinds without an explicit mapping
(exactMatch / SSSOM). A Client in the model glossary does not automatically
link to Client in FIBO.

### Viewer contract (when implemented)

One UX contract for all three views; this ADR does **not** require a viewer
change in the same wave:

1. **Tree / Classes** — hierarchy only; no related edges.
2. **Term card** (glossary card, tree detail, explorer detail) — three blocks:
   - Taxonomy: parents / children (explorer already; glossary may keep `extends`);
   - See also: chips with in-coverage deep links (`#module&section&item=`);
   - Assignment / mapping: corporate term, exactMatch — separate heading.
3. Broken target: chip without navigation (same pattern as external parent in
   `parentMeta` with `inSection: false`).
4. Inline wikilinks inside definition text are a **follow-up** (mention
   highlighting, not the relation graph). They do not replace See also and
   must not be written into the hierarchy.

## Consequences

- Normative separation of hierarchy / associative / equivalence for glossary UX
  and future projection builders.
- No schema change to `GlossaryTerm`, no hand `related` column on
  `model_glossary.json` / FIBO CSV, no related edges in tree builders.
- Follow-ups (out of this ADR’s delivery): expose `parent_concept_ref` in
  model glossary; derive See also from `Relationship`; publish object
  properties in FIBO preview; wire SKOS projection into the publication
  pipeline.

## Alternatives

| Alternative | Why not |
|---|---|
| Related as hierarchy tree edges | Breaks ADR-024 (`subClassOf`-only tree) and SKOS (RT ≠ BT) |
| Authored `related` on glossary CSV/JSON | Second graph; glossary must stay a view |
| SKOS slots on `GlossaryTerm` | Turns the registry projection into a concept scheme; master is external |
| Treat `glossary_term_refs` / `definition_source_ref` as related | Assignment and definition cascade are other ADR-025 axes |
| Auto-relate siblings | Invents associations not asserted in any native graph |

## Related

- ADR-020, ADR-024, ADR-025, ADR-026
- Sample SKOS projection: `model-assets/transformations/glossary/skos_concepts.yaml`
- Loader: `packages/semantic-mappings/src/moex_semantic_mappings/skos_glossary.py`
- Architecture: [ontology-catalog.md](../architecture/ontology-catalog.md) § «Связи с DAMS и глоссарием»
