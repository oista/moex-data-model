---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR-005: drawDB — изолированное self-hosted приложение

**Date:** 2026-09-28  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md) §16  
**Workbench detail:** [linkml_architecture.md](../architecture/linkml_architecture.md) «Интеграция drawDB»

## Context

Нужен визуальный ER-редактор. drawDB уже умеет SQL/DBML в браузере. Вшивание его исходников в Workbench web свяжет домен с чужим React-стеком и внутренним JSON.

На текущем срезе drawDB **не встроен** — есть только цветной DBML как артефакт/пример.

## Decision

drawDB разворачивается как **отдельное self-hosted frontend** (свой image) и встраивается в Workbench через editor component / iframe / microfrontend. Sharing server drawDB не обязателен.

Домен Workbench говорит с ним через **DBML + adapter**, не через внутренний JSON drawDB.

Обновление drawDB и CSP/права editor frame изолированы от основного UI.

## Consequences

- Не импортировать зависимости drawDB в `apps/web`.
- Нужен `DrawDbProjectionService` и round-trip тесты (IMPLEMENTATION_PLAN этап 5) — после стабилизации graph/diff.
- Замена editor не должна трогать kernel.

## Alternatives

| Alternative | Почему нет |
|---|---|
| Форк drawDB внутрь Workbench | дорогие апдейты, vendor JSON как канон |
| Только Mermaid | нет управляемого редактирования physical/logical |
| Native canvas в Workbench | большая собственная стоимость |

## Related

- ADR-006, ADR-012
