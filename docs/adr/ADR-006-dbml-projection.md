---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR-006: DBML — проекция, а не источник истины

**Date:** 2026-09-28  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md) §10, §16

## Context

DBML удобен для ER-диаграмм, но не выражает mixins, abstract classes, slot usage, URI/CURIE, rules, governance, cross-layer mappings. Если сделать DBML каноном, семантика DAMS потеряется при round-trip.

## Decision

DBML — **derived projection** (`GENERATED_FROM`) из канонического LinkML (ADR-001), плюс отдельный **layout store** (координаты canvas не в YAML модели).

Изменения из drawDB превращаются в **ModelPatch** → semantic diff → validation → запись в LinkML. Неизвестные annotations и element_id опубликованных элементов нельзя терять или переписывать из диаграммы.

Режимы первой версии Workbench: physical — управляемый round-trip; logical — частичный; conceptual — ограниченно; governance/ontology — не через ERD.

## Consequences

- `moex-dams-drawdb-colored.dbml` — golden sample генератора, не ручной master.
- Запрет «экспортировали DBML и заменили YAML».
- Нужны round-trip golden tests, когда появится adapter.

**MVP landed (2026-09-28):** adapter round-trip + Workbench confirm via semantic diff before workspace apply. Metamodel DBML golden regen remains Stage 6.

## Alternatives

| Alternative | Почему нет |
|---|---|
| DBML как канон | потеря LinkML/DAMS semantics |
| Внутренний JSON drawDB как канон | vendor lock-in |
| Только односторонний view forever | не закрывает Workbench MVP, но допустимо дольше на срезе |

## Related

- ADR-001, ADR-005, ADR-012
