# DAMS Spec explorer hierarchy

**Status:** approved  
**Date:** 2026-09-28  
**Project:** moex-data-model

## Problem

Under Spec → MOEX DAMS, readers need one left-hand hierarchy that covers
package overview / inventory tables, class navigation, and the normative YAML
files that make up the reference specification — without a flat secondary-nav
list duplicating those sections.

## Decisions (approved)

| Topic | Choice |
|-------|--------|
| Explorer roots | Dual (then quad) roots in one `type: explorer` section |
| File set under «Спецификация» | **B** — `specification.yaml` + `schemas/*.yaml` |
| YAML viewer | **A** — lightweight built-in highlight + indent fold (no libs) |
| Nav structure | Approach **1** — one explorer tree, synthetic section roots |
| Overview nest | First root `group:overview`; children = existing sections Overview / All classes / All slots / All enumerations via `kind: section_ref` |
| Secondary nav | Hide section ids nested under Overview when that root is present |
| Scope | DAMS only (`is_dams_specification_dir`); ontology explorers unchanged |

## UX

```
Specification explorer
├─ Overview                         ← section_id=overview (markdown-doc)
│   ├─ Overview                     ← section_ref → overview
│   ├─ All classes                  ← section_ref → classes
│   ├─ All slots
│   └─ All enumerations
├─ Классы                           ← schema packages → classes/enums
├─ Спецификация                     ← source_file cards (YAML + refs)
└─ Реализации                       ← implementation_ref (catalog)
```

- Click on Overview root or `section_ref` → navigate to real `PublicationSection`
  via hash `section=` (no explorer `item=`).
- Click on package / class / `source_file` → existing explorer detail cards.
- Deep links for tables remain `#…&section=classes` (etc.).

## Data contract

`wrap_dams_explorer_roots` emits roots in order:

1. `group:overview` — `section_root=overview`, `section_id=overview`, children
   `section:{id}` with `kind=section_ref`, `section_id`
2. `group:classes` — package groups (unchanged)
3. `group:spec-files` — `kind=source_file` with `path`, `version`, `description`,
   `text`, `refs_out`, `refs_in`
4. `group:implementations` — filled at build from architecture catalog

Sections stay declared in `publish.yaml`; the tree only re-parents navigation.

## Out of scope

- Ontology explorers
- examples/ / README under «Спецификация»
- CodeMirror / highlight.js
- Tabs on the architecture catalog card «MOEX DAMS»
