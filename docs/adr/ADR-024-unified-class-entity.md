---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# ADR-024: Unified Class entity across LinkML and OWL publications

**Date:** 2026-10-04  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-014](ADR-014-fibo-profile-metamodel.md), [ADR-016](ADR-016-publication-section-kinds-and-profiles.md), [ADR-018](ADR-018-ontology-application-implementation.md), [ADR-027](ADR-027-glossary-term-relations.md)  
**Amends:** ADR-014 (partial), ADR-016 (ontology ProfileSpec)  
**Amended by:** [ADR-027](ADR-027-glossary-term-relations.md) (hierarchy ≠ related; associative See also from object properties)

## Context

The same domain concept (`owl:Class` / LinkML `class`) appeared under different names in the Publication Viewer: explorer `kind: class`, profile glossary `kind: concept`, taxonomy metamodel nodes, and a separate «All classes» stub. ADR-016 made `taxonomy` required for the `ontology` profile and left `classes` only recommended, so FIBO Spec (`edmc.fibo`) showed organizational metamodel as primary nav while real class rows lived only in the release preview module. That diverges from the intended UX: hierarchy and glossary are two views of the same class entities.

## Decision

1. **One semantic name `class`** for LinkML classes and OWL named classes. Differences stay in the renderer selected by publication profile (`data-structure` vs `ontology-list`), as in ADR-016.
2. **Glossary (ontology profile)** is a flat alphabetical **view** of the same class entities from the same source, not a separate data set. Profile metamodel terms (`FiboDomain`, IRI patterns, …) are documented in README / `metamodel/*.yaml`, not duplicated as glossary rows. ADR-025 generalises this: every glossary is a view of definitions for a coverage (ontology / model / corporate), never a separate entity type. **Nav:** under Overview a Glossary folder may group terms by **definition site** (schema package / domain→module); that grouping is not a second taxonomy and does not replace the flat A–Z section or the Classes `subClassOf` tree. Term cards follow [ADR-027](ADR-027-glossary-term-relations.md) (Taxonomy / See also / Assignment). Explorer leaf wire-ids may use a `glossary:` prefix to avoid colliding with Classes nodes; semantic identity remains the class/enum id.
3. **Class hierarchy** uses asserted `subClassOf` (preview: `parent_local_name`). Domain grouping (`source_domain`) nests under the Classes root. Multiple inheritance may repeat a node in several branches; the card URL/id stays canonical. Imported (`owl:imports`) classes may carry `origin` (`own` \| `imported` — not ConceptualEntity `genesis_kind`); preview data are `own`. Associative «related terms» (See also) are **not** hierarchy edges; they are derived separately when object-property data exist ([ADR-027](ADR-027-glossary-term-relations.md)).
4. **Anonymous classes / restrictions** do not appear in the tree (card detail later; out of this increment).
5. **FIBO Spec module (`edmc.fibo`)** publishes a class index from release preview data under kind `classes`, while metamodel organization moves to:
   - **Модули** → `schema-files` (domains, modules, ontology documents / `owl:imports` axis)
   - **Identity** → `identity` (IRI, prefix, annotation conventions)
6. **Ontology ProfileSpec** (amends ADR-016):
   - required: `overview`, `classes`, `glossary`
   - recommended: `schema-files`, `identity`
   - forbidden: `enumerations`, `slots`
   - kind `taxonomy` remains in the closed enum for compatibility but is **deprecated** for new modules; hierarchy belongs under `classes`.
7. **Properties** (object / data / annotation) are the next increment when source data exist; not required in this cut.
8. Soft validation (missing required → warning) from ADR-016 §7 stays; empty explorer stubs must not satisfy `classes`.

## Consequences

- ADR-014: Spec metamodel remains normative YAML/Pydantic; Spec **publication** may show a class index sourced from release/index data (partial amendment of «domain classes outside Spec explorer»).
- ADR-016 table for `ontology` profile is superseded by the ProfileSpec above.
- `moex:module:fibo` (FIBO Glossary) may keep publishing the same CSV as a release preview; alignment to `profile: ontology` is optional follow-up.
- Viewer fills Classes from the glossary source at build time so hierarchy and glossary stay in sync.
- LinkML specification modules may also publish Overview→Glossary definition-site folders plus a generated A–Z glossary view (`glossary` is **recommended** on `linkml-specification`, ADR-016).

## Alternatives

| Alternative | Why not |
|---|---|
| Keep taxonomy as required primary axis | Duplicates class hierarchy under another name; caused empty Classes stubs |
| Separate `OWL Classes` kind | Combinatorial explosion (ADR-016 already rejected) |
| Put full FIBO RDF into Spec YAML | Violates ADR-014 metamodel boundary; release/index remains the class source |

## Related

- ADR-014, ADR-016, ADR-018, ADR-027
- Publication Viewer `fibo_explorer_roots` / `enrich_fibo_explorer_classes`
