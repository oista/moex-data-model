---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR-004: Модульный монолит вместо микросервисов

**Date:** 2026-09-28  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md) §6–7, [app_model.md](../architecture/app_model.md)

## Context

Платформа объединяет validation, generation, Git publish, later API/UI. Микросервисы на старте усложнят версионирование схем и диагностику. При этом границы модулей уже нужны: kernel ≠ LinkML provider ≠ DAMS rules ≠ publication.

## Decision

Первая промышленная версия — **модульный монолит**: один деплойный контур (позже API+worker из одного Python distribution, разные entrypoints), жёсткие **пакетные границы**.

Долгие операции — worker/queue, не отдельные «микросервисы ради микросервисов». Compiler, ontology engine, integrations можно выделить позже, не ломая ports.

Текущее дерево это уже отражает: `packages/modeling-kernel`, `standard-linkml`, `specification-dams`, `publication`, inbound `apps/cli`.

## Consequences

- Зависимости только внутрь: CLI → application packages → kernel; не наоборот.
- Нет распределённых `if standard == "linkml"` в kernel.
- OCI images (web/api/worker/drawdb) — later Workbench, не аргумент дробить домен сейчас.

## Alternatives

| Alternative | Почему нет |
|---|---|
| Микросервис на каждый generator | взрыв контрактов, общая транзакция публикации |
| Один пакет «на всё» | смешает kernel и LinkML bodies |
| Отдельный сервис на каждый standard | рано; provider — пакет, не сеть |

## Related

- ADR-005 (drawDB — отдельный frontend image, не доменный сервис)
- app_model.md target-after-slice
