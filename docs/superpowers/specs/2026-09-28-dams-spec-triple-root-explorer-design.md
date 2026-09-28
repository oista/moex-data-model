# DAMS Spec triple-root explorer

**Status:** approved for implementation  
**Date:** 2026-09-28  
**Project:** moex-data-model

## Problem

MOEX DAMS Specification explorer shows only schema-package class trees.
Readers also need the normative YAML files that compose the specification,
and a path from the spec to registered implementations — without leaving the
explorer pattern (`type: explorer`).

## Decisions

| Topic | Choice |
|-------|--------|
| Tree roots | **3**: Классы / Спецификация / Реализации |
| Spec files | `specification.yaml` + `schemas/*.yaml` |
| Реализации | Catalog nodes `role=specification_implementation` + `conforms_to=moex-dams`; click navigates to that module (choice A) |
| Approach | Single explorer section; wrap package groups under `group:classes` |
| Scope | DAMS only (detect via sibling `specification.yaml`); other explorers unchanged |
| Default expand | Классы open; Спецификация and Реализации collapsed |

## UX

```text
Specification explorer
├─ Классы
│   └─ Root / Core / … → Class / Enum
├─ Спецификация
│   └─ specification.yaml, schemas/*.yaml  (source_file cards)
└─ Реализации
    └─ Trading solution … → jump to implementation module
```

### `source_file` card

Header (name, yaml badge, version, description), refs_out / refs_in (deep-link
to other `file:…` items), collapsible YAML body (indent fold, light key highlight).

### `implementation_ref`

No embedded body. Nav click → architecture catalog / module navigation.

## Data

| Id | kind | Notes |
|----|------|-------|
| `group:classes` | group | Children = former top-level package groups |
| `group:spec-files` | group | Children = `source_file` |
| `group:implementations` | group | Children = `implementation_ref` from catalog (build-time inject) |
| `file:…` | source_file | `path`, `version`, `description`, `text`, `refs_out`, `refs_in` |
| catalog id | implementation_ref | `catalog_node_id`, `module_id`, `version`, `conforms_to` |

## Out of scope

Ontology explorers; examples/README in Spec files; CodeMirror; YAML editing;
SchemaRepository residual.
