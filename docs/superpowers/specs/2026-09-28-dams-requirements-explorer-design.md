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
| Level group | «Концептуальная модель» + «ИТ-решения» (+ «Публикация» ADR-019) |
| List child | «Требования к модели» — requirement cards |
| Req-schema child | «Спецификация требований» — required-only LinkML schema projection |
| Model-spec child | «Спецификация модели» — derived `ModelPackage` skeleton from `formal_checks` |
| Example child | «Пример модели» — curated example under ИТ-решения only (not conceptual) |
| Requirement level | `conceptual_model` \| `it_solution` |
| Codes | IT: `{SECTION}-{NNN}`; conceptual: `CM-{SECTION}-{NNN}` |

## UX

```
Specification explorer
├─ Overview
├─ Классы
├─ Спецификация
├─ Требования
│   ├─ Концептуальная модель
│   │     ├─ Требования к модели
│   │     │     └─ CM-GEN-001, CM-CON-001, … (kind: requirement)
│   │     ├─ Спецификация требований
│   │     │     └─ minimal/*.required.yaml (kind: source_file)
│   │     └─ Спецификация модели
│   │           └─ …/conceptual-model.skeleton.yaml (kind: source_file)
│   ├─ ИТ-решения
│   │     ├─ Требования к модели
│   │     │     ├─ LDM (folder + code) → LDM-* (kind: requirement)
│   │     │     ├─ PDM → PDM-*
│   │     │     ├─ REF → REF-*
│   │     │     ├─ ATR → ATR-*
│   │     │     ├─ FLW → FLW-*
│   │     │     ├─ CLS → CLS-*
│   │     │     └─ GEN → GEN-*
│   │     ├─ Спецификация требований
│   │     │     └─ minimal/*.required.yaml (kind: source_file)
│   │     ├─ Спецификация модели
│   │     │     └─ …/it-solution-model.skeleton.yaml (kind: source_file)
│   │     └─ Пример модели
│   │           └─ …/it-solution-model.example.yaml (kind: source_file)
│   └─ Публикация
│         ├─ Требования публикации
│         └─ Спецификация
└─ Реализации
```

## Data contract

`wrap_dams_explorer_roots` emits five roots; `group:requirements` children:

0. `group:requirements-conceptual` — enterprise-conceptual level (ADR-021). Children:

   1. `group:requirements-conceptual-list` — items with `kind=requirement`,
      `requirement_level=conceptual_model`
   2. `group:requirements-conceptual-min-spec` — same required-only schema projection
   3. `group:requirements-conceptual-model-spec` — skeleton from
      `project_conceptual_model_skeleton` (no example child)

1. `group:requirements-it-solutions` — level group; description: requirements for IT-solution data models. Children:

   1. `group:requirements-list` — section folders (`group_style=section_folder`,
      `requirement_section` = LDM|PDM|REF|ATR|FLW|CLS|GEN in enum order, non-empty
      only); each folder holds `kind=requirement` leaves with attributes:
      `code`, `requirement_level`, `requirement_section`, `statement`, `formal_checks`.
      Nav mark: folder icon + three-letter section code.
   2. `group:requirements-min-spec` — `source_file` items from build-time required-only
      projection (classes/slots with `required: true` or `minimum_cardinality ≥ 1`,
      plus referenced enums)
   3. `group:requirements-model-spec` — `source_file` items from
      `project_it_solution_model_skeleton` (ModelPackage-shaped placeholders from
      `formal_checks`)
   4. `group:requirements-model-example` — curated `source_file` YAML under
      `requirements/examples/`

## Out of scope

- Wiring `formal_checks` into `moex-dams-assess`
- Curated conceptual-model example YAML
- Changing full «Спецификация» file set
- Ontology explorers
