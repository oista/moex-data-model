---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# ADR-016: Publication section kinds and profiles

**Date:** 2026-09-28  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-014](ADR-014-fibo-profile-metamodel.md), [ADR-010](ADR-010-owl-not-primary-validation.md), [ADR-015](ADR-015-viewer-ui-atlas.md)  
**Schema:** [moex-dsp.yaml](../../model-assets/specifications/moex-dsp/0.1/schemas/moex-dsp.yaml)

## Context

The same English word «classes» means different things in LinkML and OWL:

| Axis | LinkML classes | OWL classes |
|---|---|---|
| Meaning | Data structure (slots, constraints) | Logical category / knowledge taxonomy |
| Hierarchy | Secondary (`is_a`) | Primary (`subClassOf`) |
| Navigation | Packages and entity types | Taxonomy tree |
| Publication | Attribute table | Tree with definitions |

Publication Viewer already showed this split poorly: DAMS used a «Классы» explorer root while FIBO used «metamodel» for an organizational hierarchy. Ad-hoc roots and free-text section titles drift. Inventing separate kinds such as `OWL Classes`, `SHACL Classes`, or `ER Entity` would explode the vocabulary without fixing the root cause.

`PublicationModule` must stay an open class of instances (new packages appear). What must be closed is the **semantic vocabulary of section kinds** and the **profile** that says which kinds a publication of a given shape must / should / must not carry.

## Decision

1. **Closed enum `PublicationSectionKind`** lives in the DSP metamodel (not in `modeling-kernel.yaml`). Canonical values include: `overview`, `classes`, `slots`, `enumerations`, `schema-files`, `taxonomy`, `glossary`, `identity`, `bindings`, `data-flows`, `conformance`, `source`.
2. **`taxonomy` is a separate kind**, not a view mode of `classes`. For ontology publications it is the **primary navigation axis**. It must not be required (and is forbidden) on LinkML specification profiles where hierarchy is secondary.
3. **One kind `classes`**, with **renderer mode selected by publication profile**:
   - `linkml-specification` → `data-structure` (table: name, is_a, slots, …)
   - `ontology` → `ontology-list` (alphabetical list: IRI, definition, source_domain — not slots)
4. **`ProfileSpec`** on each `PublicationProfileId` (`linkml-specification` | `ontology` | `implementation`) declares `required` / `recommended` / `forbidden` kinds:

   | Profile | Required | Recommended | Forbidden |
   |---|---|---|---|
   | `linkml-specification` | overview, classes, schema-files | enumerations, slots | taxonomy |
   | `ontology` | overview, taxonomy, glossary | classes, identity | schema-files, enumerations, slots |
   | `implementation` | overview, conformance | bindings, data-flows | taxonomy |

5. Manifest field **`profile:`** selects the ProfileSpec. Modeling language family (`ModelingStandardFamily` / catalog `expressed_in`) remains a **label**, not the profile key.
6. Manifest **`type:`** (explorer, glossary, markdown-doc, …) is the **wire/render format**. **`kind`** is semantic. They are orthogonal.
7. Soft validation in this iteration: with `profile` set, missing required / present forbidden / missing recommended → **warnings**, not build failure. Strict CI may follow later.
8. Deep taxonomy renderer options (`root_class`, `depth_limit`, `show_equivalent`, OWL reasoning, module filters) are **out of scope** for the first cut.

## Consequences

- New publication modules must pick a `profile` and section `kind`s from `PublicationSectionKind` (see Cursor rule / DSP README).
- FIBO Spec explorer primary axis becomes **taxonomy** (+ glossary); recommended `classes` is ontology-list, not a LinkML attribute table. ADR-014 Spec vs Impl split **stays**; only the UI naming/axis for Spec body changes («metamodel» label → taxonomy kind).
- DAMS must not introduce a taxonomy root; «Спецификация» maps to `schema-files`.
- Viewer code uses `get_renderer_mode(kind, profile)` instead of proliferating section kinds per formalism.

## Alternatives

| Alternative | Why not |
|---|---|
| Separate `OWL Classes` / `SHACL Classes` kinds | Combinatorial explosion; same word, different renderers belong on profile |
| `taxonomy` as a view flag on `classes` | For FIBO taxonomy is the primary nav axis, not a secondary view |
| Enum of all `module_id` / PublicationModule instances | Modules are open-ended; kinds and profiles are the closed vocabularies |
| Profile = `ModelingStandardFamily` directly | One family can back multiple publication shapes; profile is publication contract |
| Put kinds in modeling-kernel | Publication projection belongs to DSP / viewer, not domain kernel envelopes |

## Related

- ADR-014 — FIBO profile as ReferenceSpecification; release as Implementation
- ADR-010 — OWL not primary validation
- ADR-015 — Viewer UI atlas (presentation layer)
