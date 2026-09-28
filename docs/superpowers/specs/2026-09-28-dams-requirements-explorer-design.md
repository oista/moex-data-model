# DAMS Requirements explorer

**Status:** approved  
**Date:** 2026-09-28  
**Project:** moex-data-model  
**ADR:** [ADR-013](../../adr/ADR-013-specification-requirements-catalog.md)

## Problem

Readers of Spec → MOEX DAMS need a navigable catalog of **what must hold for an
IT-solution model to validate**, separate from the full normative LinkML YAML
under «Спецификация», with human-readable statements and machine-oriented checks.

## Decisions (approved)

| Topic | Choice |
|-------|--------|
| Source of truth | DAMS LinkML classes (`SpecificationRequirement`, `FormalCheck`, `RequirementCatalog`) |
| Catalog instances | Separate YAML under `requirements/`, not inside a solution `ModelPackage` |
| Formal checks | Structured kinds inspired by LinkML constraints + optional `diagnostic_code`; assess wiring deferred |
| Explorer placement | New root «Требования» **after** «Спецификация», before «Реализации» |
| List child | «ИТ-решение: список» — requirement cards |
| Spec child | «ИТ-решение: спецификация» — same `source_file` UI as «Спецификация», content = required-only schema projection |
| Requirement level (v0) | Always `it_solution` |
| Codes | `{SECTION}-{NNN}` with SECTION ∈ LDM, PDM, REF, ATR, FLW, CLS, GEN |

## UX

```
Specification explorer
├─ Overview
├─ Классы
├─ Спецификация
├─ Требования
│   ├─ ИТ-решение: список
│   │     └─ GEN-001, LDM-001, … (kind: requirement)
│   └─ ИТ-решение: спецификация
│         └─ minimal/*.required.yaml (kind: source_file)
└─ Реализации
```

## Data contract

`wrap_dams_explorer_roots` emits five roots; `group:requirements` children:

1. `group:requirements-list` — items with `kind=requirement`, attributes:
   `code`, `requirement_level`, `requirement_section`, `statement`, `formal_checks`
2. `group:requirements-min-spec` — `source_file` items from build-time required-only
   projection (classes/slots with `required: true` or `minimum_cardinality ≥ 1`,
   plus referenced enums)

## Out of scope

- Wiring `formal_checks` into `moex-dams-assess`
- UI filters for conceptual / IT-system levels
- Changing full «Спецификация» file set
- Ontology explorers
