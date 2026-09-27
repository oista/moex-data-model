---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR-009: schema-automator используется только для draft import

**Date:** 2026-09-28  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Workbench detail:** [linkml_architecture.md](../architecture/linkml_architecture.md) «Import Engine»

## Context

Нужен bootstrap из JSON Schema, SQL, CSV/RDF. `schema-automator` официально экспериментальный. Автопубликация inferred schema сломает identity, descriptions и registry links.

Пилот ER-словаря в `standard-linkml` ingest выдаёт **DAMS ModelPackage instance**, не draft schema; `schema-automator` туда **не** входит.

## Decision

`schema-automator` — optional import dependency **только** для bootstrapping чужих схем в статус `generated-draft`.

Черновик не публикуется автоматически. Архитектор обогащает IDs, descriptions, ranges, registry links; publication — только после validation pipeline.

Исходный файл и параметры import job сохраняются (audit). Повторный импорт должен быть воспроизводим.

## Consequences

- Ingest ER-словаря остаётся отдельным модулем (правильный артефакт — instance, не schema).
- Isolated import jobs (IMPLEMENTATION_PLAN этап 7), когда появится Workbench wizard.
- Не добавлять `schema-automator` в runtime kernel.

## Alternatives

| Alternative | Почему нет |
|---|---|
| Автопубликация inferred schema | экспериментальный importer, дыры в identity |
| schemasheets как замена ER-ingest | другой вход (class/slot authoring), не словарь сущностей |
| Ручной-only import навсегда | слишком дорого для внешних контуров |

## Related

- ADR-008, ADR-012
- packages/standard-linkml README
