# Viewer nav hierarchy

**Status:** approved for implementation  
**Date:** 2026-09-28  
**Project:** moex-data-model  
**Clarifies:** [dams-spec-explorer-hierarchy-design](2026-09-28-dams-spec-explorer-hierarchy-design.md),
[dams-spec-triple-root-explorer-design](2026-09-28-dams-spec-triple-root-explorer-design.md)

## Problem

The left sidebar was composed from three independent layers:

1. Architecture catalog Spec buttons with always-visible Impl siblings (`nav-impl-children`)
2. Active module `type: explorer` body (Overview / Классы / … / Реализации)
3. Flat `nav-secondary` for leftover `PublicationSection`s

That produced a visual “second menu” (explorer after floating Impls), inconsistent
expand/collapse, and nodes without a selectable description card.

## Decisions

| Topic | Choice |
|-------|--------|
| Single tree | Catalog Spec roots + publication explorer body of the active module |
| Spec↔Impl placement | Only under explorer `group:implementations` (build enrich from catalog) |
| Catalog Impl siblings | Removed from sidebar (`nav-impl-children` gone) |
| Spec row | Selectable + collapsible; children = explorer roots when expanded/active |
| Active Impl body | Explorer of `currentModuleId` under its Spec parent; no sibling Impl list |
| Secondary nav | Only sections not reachable via explorer `section_ref` / Overview nest |
| Content Implementations block | Kept on Spec catalog/module landing cards; not duplicated as sidebar siblings |
| `implementation_ref` click | Select → description card + explicit Open → Impl module |

## Principles

1. **Catalog is the Spec↔Impl graph.** `architecture-catalog` (`role`, `conforms_to`,
   `module_id`, `description`) is the only source of those edges.
2. **Explorer is the Spec/Impl body.** `PublicationItem` trees (`kind`, `purpose`,
   `structure_why`, `description`, children) define sections inside a module.
3. **Viewer does not invent a third hierarchy.** No parallel Impl list under Spec;
   no secondary buttons for sections already nested under Overview.
4. **Every nav node is selectable and has a description** (catalog / item / module
   fallback). Empty description is a data bug, not a UI mode.
5. **Every node with children collapses/expands** via a disclosure control; label
   click selects and expands if closed; second click on the same selected parent
   collapses (symmetric with existing group behaviour).

## Target UX

```text
Spec moex.dams                         ← select + toggle
├─ Overview
├─ Классы
├─ Спецификация
├─ Требования
└─ Реализации                          ← only place for Impls
   ├─ moex.dsp                         ← implementation_ref card → Open
   └─ Trading solution

Spec edmc.fibo
├─ Overview
├─ … metamodel groups …
└─ Реализации
   └─ FIBO release …

Implementations without specification  ← orphans only
Other publications                     ← modules not in catalog
```

When an Impl module is open, breadcrumb/chrome keep Spec → Impl; sidebar body
under that Spec is the Impl module explorer (not Spec explorer + Impl siblings).

## Logical NavNode contract

Viewer rows behave as if backed by:

| Field | Meaning |
|-------|---------|
| `id` | Catalog node id or explorer item id |
| `title` | Display label |
| `description` | Card text (required in data; UI shows fallback only as last resort) |
| `kind` / `role` | `reference_specification`, `specification_implementation`, or explorer `kind` |
| `children` | Nested nav nodes (explorer items or none) |
| `navTarget` | Hash focus: `{ node, module, section?, item? }` |

Composition (build-time + client):

- Roots = catalog `reference_specification` (+ orphan Impls / other modules).
- Spec body = that Spec’s `PublicationModule` explorer items (after
  `wrap_*_explorer_roots` + `enrich_*_explorer_implementations`).
- Impl entries inside Spec = `kind: implementation_ref` children of
  `group:implementations`, not catalog buttons.

## Interaction matrix

| Node | Select shows | Expand | Navigate further |
|------|--------------|--------|------------------|
| Spec (catalog) | Spec description card (catalog \|\| module) | Toggles explorer body | Body stays under Spec |
| Explorer `group` | Purpose / structure_why card | Toggle children | — |
| `section_ref` | Opens target `PublicationSection` | N/A (leaf) | Hash `section=` |
| Class / enum / file / requirement | Existing detail cards | Toggle if has kids | — |
| `implementation_ref` | Impl description card + Open | N/A | Open → Impl module |
| Secondary section btn | That section | N/A | Hash `section=` |

## What was the “second menu”?

Not a product feature. It was the Spec explorer appended after catalog Impl
siblings, so Overview looked like a new root menu. Removing `nav-impl-children`
restores Spec → explorer as one parent/child tree.

## Out of scope

- React `apps/web` ModelExplorer
- Changing `wrap_dams_explorer_roots` root set (already correct)
- Removing content-area Implementations block on Spec landing cards
