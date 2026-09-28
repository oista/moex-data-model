# Ontology Spec explorer (FIBO + Ontology Catalog)

**Status:** draft for review  
**Date:** 2026-09-28  
**Project:** moex-data-model

## Problem

Under Spec, ontology modules (FIBO, Ontology Catalog) show hierarchy in a
`tree` section: tree on the left, thin details on the right (title/description
only). DAMS Spec already uses `type: explorer` — sidebar navigation + rich
class cards in the main pane. Readers expect the same pattern for ontologies:
domain folders, nested type hierarchy, and class cards with full definitions
and metadata. Existing glossary / hierarchy / cards / backlinks sections must
remain.

## Decisions (approved)

| Topic | Choice |
|-------|--------|
| Layout | **B** — DAMS explorer: nav left, card in main (no right tree panel) |
| Scope | **C** — shared explorer pattern for Spec ontologies; start FIBO preview, then Ontology Catalog |
| Sidebar grouping | **C** — hybrid: top-level domain/ontology folders; inside — asserted `subClassOf` tree |
| Existing sections | **C** — keep glossary / hierarchy / cards / backlinks; add explorer alongside |
| Implementation approach | **2** — extend existing `type: explorer` (nested nav + ontology card branch); no new section type |

## UX

```
Spec → FIBO / Ontology Catalog
├─ sidebar: Domain / Ontology folders → nested subClassOf tree
├─ main: rich entity card (class click) OR domain landing (folder click)
└─ secondary nav: existing non-explorer sections unchanged
```

### Entity card (maximum available fields)

- Title: label; RU alias in parentheses when present (`label_ru` / aliases)
- Badges: `kind`, `deprecated` when true
- Definitions: English `definition` / `description`; RU `definition_ru` when present
- Identity: IRI, curie (if any), ontology_id / `source_domain`
- Taxonomy: parents and children as clickable explorer links
- Property facets when present: domain, range
- Lifecycle: `replaced_by` when deprecated
- Backlinks: count and/or list when export provides them

Domain/ontology folder cards reuse the DAMS group-card pattern (purpose +
member/root count); purpose text may be short/derived for preview domains.

## Data contract

Reuse `PublicationItem` / `PublicationSection` with `type: explorer`.

| Level | `attributes.kind` | Children |
|-------|-------------------|----------|
| Domain / ontology folder | `group` | root classes of that domain (no parent in-domain), each may nest subclasses |
| Class / entity | `class`, `individual`, or `*_property` | subclasses in the same domain |

Ontology-specific attributes on leaf/node items (as available):

`definition`, `definition_ru`, `label_ru`, `aliases`, `iri`, `curie`,
`source_domain` / `ontology_id`, `parents`, `children`, `deprecated`,
`replaced_by`, `domain`, `range`, `backlinks` (scalar or structured).

DAMS LinkML explorer stays schema-package groups with flat class/enum children;
no required change to DAMS manifests.

## Normalization

### Increment 1 — FIBO preview

- Source: `packages/ontology/publications/fibo_glossary.preview.csv`
- Build explorer items in `csv_normalizer` (or shared helper): group by
  `source_domain`; nest by `parent_local_name` within each group
- `packages/ontology/publish.yaml`: add `type: explorer` section (e.g. `id: explorer`);
  keep `glossary` and `hierarchy` sections
- Card fields from CSV columns already present

### Increment 2 — Ontology Catalog

- `publication_export`: write `ontology_explorer.json` in the same nested shape,
  including full card fields from `OntologyEntityCard` (+ binding/backlink
  summaries when available)
- Groups by `ontology_id` (or release id); trees from asserted hierarchy
- `packages/ontology-catalog/publish.yaml`: add `type: explorer` section;
  keep catalog / entities / hierarchy / cards / backlinks

## Viewer changes

- `nav-explorer`: render nested trees under groups (not only flat children);
  expand ancestors of the selected item; preserve group open/close
- `findExplorerItem` / `collectExplorerIds`: walk arbitrary depth
- `renderExplorerDetail`: if item carries ontology identity fields (or section
  tagged `ontology`), render the rich ontology card; else keep DAMS LinkML card
- Landing: domain overview chips consistent with DAMS explorer landing
- Do not change `.tree-layout` behaviour for remaining `type: tree` sections

## Out of scope

- Full FIBO mart / live RDF in the viewer
- Reasoning / inferred hierarchy
- Removing or redesigning glossary, hierarchy tree, entity-table cards, backlinks
- New section type name
- Changing DAMS schema-package explorer semantics

## Verification

- Unit: CSV/JSON → explorer nesting (domain groups + parent/child)
- Build: `build-viewer -Check` includes explorer section on FIBO (then catalog)
- Manual: Spec → FIBO → open domain → select class → card shows definition(s)
  and metadata; secondary sections still reachable

## Spec self-review

- No TBD placeholders for approved decisions
- Nested nav vs DAMS flat groups: coexistence via depth (DAMS depth 1 under group)
- Card fields degrade gracefully when optional attributes missing
- Scope split into two increments; shared UI contract first
