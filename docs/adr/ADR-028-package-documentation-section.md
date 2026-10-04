---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# ADR-028: Package documentation section

**Date:** 2026-10-04  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-001](ADR-001-linkml-yaml-canonical.md), [ADR-012](ADR-012-semantic-diff-review.md), [ADR-015](ADR-015-viewer-ui-atlas.md), [ADR-016](ADR-016-publication-section-kinds-and-profiles.md), [ADR-025](ADR-025-definition-cascade-and-glossary.md)  
**Amends:** ADR-016 (kind `documentation`; implementation ProfileSpec recommended)  
**Schema:** [moex-dsp.yaml](../../model-assets/specifications/moex-dsp/0.1/schemas/moex-dsp.yaml)

## Context

Definitions live on elements ([ADR-025](ADR-025-definition-cascade-and-glossary.md)).
`overview` is the publication landing (structured summary + optional README).
LinkML **gen-doc** is a derived artifact ([ADR-001](ADR-001-linkml-yaml-canonical.md)),
not owner prose. Implementations had no first-class place for consumer context
or for *why the model changed*. Semantic diff ([ADR-012](ADR-012-semantic-diff-review.md))
classifies YAML deltas; it does not record rationale.

## Decision

1. New closed `PublicationSectionKind` value **`documentation`**. Render `type`
   stays `markdown-doc`. Source is `docs/toc.yaml` (YAML), not a single README.
2. Owner-authored docs are a **sidecar tree** on the implementation package
   (same revision as the model body). They are **not** slots on `ModelPackage`
   and **not** LinkML gen-doc.
3. If the section is present:
   - `docs/toc.yaml` is mandatory;
   - `docs/consumer-context.md` is mandatory (`role: contract`);
   - other pages are free but must be listed in the TOC;
   - `docs/adr/` is reserved for model decision records (template required
     when files exist). Empty ADR stubs are not required.
4. ProfileSpec **`implementation`**: `documentation` is **recommended**, not
   required. Soft warning when missing (ADR-016). Spec/ontology keep README +
   glossary; package docs remain optional there.
5. Model ADR identifiers are **package-scoped** (`trading-platform:adr:001`).
   Bare `ADR-001` is rejected (collides with this repository’s `docs/adr/`).
   `change_class` reuses ADR-012 classes plus `modeling`. Chronology is the
   TOC `role: decision` list — no parallel `CHANGELOG.md`.
6. Viewer shows a page tree from the TOC (Decisions grouped) and the
   `entry_for_agents` page first. Implementation nav may nest the section
   under a Documentation folder; page trees do not become `section_ref` children.

## Consequences

- Trading-platform (and later packages) can publish consumer/agent context
  next to the model without inventing section kinds.
- Validators fail closed on missing TOC paths, untemplated `docs/adr/` files,
  and ADRs omitted from the TOC. Orphan markdown outside `adr/` is a warning.
- Do not put reference definitions, glossary relations, or assessment findings
  in package docs.

## Alternatives

| Alternative | Why not |
|---|---|
| Only a longer README | No index for agents; mixes landing with decisions |
| Prose slots on `ModelPackage` | Hostile diffs; duplicates Git files |
| Required docs on every package | Empty stubs worse than absence |
| Autogenerate ADR from semantic-diff | Diff is *what*, not *why* |

## Related

- ADR-001, ADR-012, ADR-015, ADR-016, ADR-025
- Runtime: `apps/viewer/src/moex_publication_viewer/package_docs.py`
