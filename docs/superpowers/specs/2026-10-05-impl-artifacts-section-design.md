# Impl «Артефакты» section (source_file cards)

**Status:** approved for implementation  
**Date:** 2026-10-05  
**Project:** moex-data-model

## Problem

IT-solution publications and `moex.concept-data-model` surface tables and diagrams
derived from authored YAML, but do not expose the YAML files themselves with the
same card UX as DAMS «Спецификация» (functional title, YAML icon, `[filename]`).

## Decisions

| Topic | Choice |
|-------|--------|
| Folder title | **Артефакты** (honest: these files *are* the implementation) |
| Icon | DAMS `source_file` YAML mark (`yamlFileMarkHtml`) on folder and leaves |
| Files | Model body + `implementation.yaml` (option B); no `publish.yaml` |
| Wire format | N× `type: source-file` sections under a nav folder (not one explorer) |
| Kind | `source` (Impl artifacts; DAMS keeps `schema-files` for Spec YAML) |
| Concept | Replace `source` entity-table; `satisfies: [dams:source]` on model body |

## Why not a single explorer section

Impl seamless nav keeps flat `section_ref` leaves under groups and must not nest
explorer trees. Focusing an explorer via `section_ref` does not show file cards.
Each artifact is therefore its own publication section rendered with
`renderSourceFileDetail`.

## UX

```text
Реализации → MDM / … / moex.concept-data-model
├─ Overview / models / …
├─ Documentation? (trading only)
└─ Артефакты
   ├─ Тело модели           → «Тело модели [*-solution-model.yaml]»
   └─ Конверт реализации    → «Конверт реализации [implementation.yaml]»
```

Enterprise conceptual also lists relation-terms and controlled-vocabularies YAML.

## Out of scope

- Generated publications (JSON, ERD, DBML) inside Артефакты
- Renaming DAMS «Спецификация»
- Cross-file refs graph for Impl YAMLs
