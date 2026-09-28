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
| Level group | «ИТ-решения» — requirements for IT-solution data models |
| List child | «Требования к модели» — requirement cards |
| Req-schema child | «Спецификация требований» — required-only LinkML schema projection |
| Model-spec child | «Спецификация модели» — derived `ModelPackage` skeleton from `formal_checks` |
| Example child | «Пример модели» — curated minimal `ModelPackage` under `requirements/examples/` |
| Requirement level (v0) | Always `it_solution` |
| Codes | `{SECTION}-{NNN}` with SECTION ∈ LDM, PDM, REF, ATR, FLW, CLS, GEN |

## UX

```
Specification explorer
├─ Overview
├─ Классы
├─ Спецификация
├─ Требования
│   └─ ИТ-решения
│         ├─ Требования к модели
│         │     └─ GEN-001, LDM-001, … (kind: requirement)
│         ├─ Спецификация требований
│         │     └─ minimal/*.required.yaml (kind: source_file)
│         ├─ Спецификация модели
│         │     └─ …/it-solution-model.skeleton.yaml (kind: source_file)
│         └─ Пример модели
│               └─ …/it-solution-model.example.yaml (kind: source_file)
└─ Реализации
```

## Data contract

`wrap_dams_explorer_roots` emits five roots; `group:requirements` children:

1. `group:requirements-it-solutions` — level group; description: requirements for IT-solution data models. Children:

   1. `group:requirements-list` — items with `kind=requirement`, attributes:
      `code`, `requirement_level`, `requirement_section`, `statement`, `formal_checks`
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
- UI filters for conceptual / IT-system levels
- Changing full «Спецификация» file set
- Ontology explorers
