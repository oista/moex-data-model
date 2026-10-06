---
status: Accepted
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR-043: Transitional element tags registry

**Date:** 2026-10-05  
**Status:** Accepted  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-031](ADR-031-technical-asset-registry.md), [ADR-032](ADR-032-technical-asset-identity.md), residue test `tests/architecture/test_transitional_tags_registry.py`

## Context

План фазы 1 упоминал `annotations.transitional`. Фактически миграция пишет LinkML/DAMS слот `tags: [transitional]` на элементах ModelPackage (носители с эвристическим `asset_namespace`, payload/`message_type` и т.п.). ADR-031 Accepted — реестр меток фиксируем отдельным ADR, не правя Accepted текст.

## Decision

### Реестр допустимых переходных меток (`tags`)

| Tag | Смысл | Когда ставить | Когда снимать |
|---|---|---|---|
| `transitional` | Элемент создан/помечен миграцией или импортом с неполной семантикой (эвристический namespace, неразрешённый parent, транзитный payload и т.п.) | Миграция физического объекта к TechnicalAsset; XLSX/CSV ingest при неполной идентичности | После ручного подтверждения identity (ADR-032) и удаления эвристик; повторный publish без метки |

Иных переходных значений в `tags` **нет**. Свободные строки в `tags` для переходности запрещены: только значения из этого реестра.

Не путать с `tags` в `publish.yaml` секций viewer (каталожные ярлыки профиля) — они не являются метками переходных модельных элементов.

### Правила

1. Переходность выражается **только** через `tags`, не через `annotations.transitional`.
2. Residue-тест проверяет, что во `model-assets/**/*.yaml` значения `tags`, равные известным переходным маркерам, ⊆ реестра; неизвестные маркеры вида `transitional-*` / `legacy-*` / `tmp-*` запрещены.
3. Снятие метки — отдельный смысловой коммит/PR данных, не silent regen.

## Inventory (фаза 1, 2026-10-05)

Фактически используется только `transitional` (~28 вхождений) в:

- `model-assets/implementations/solutions/{mdm,crm,esed,ucd}/*-solution-model.yaml`
- `model-assets/implementations/imports/client-accounts-csv-draft/0.1/draft-model.yaml`
- `model-assets/specifications/moex-dams/0.1/requirements/examples/it-solution-model.example.yaml`

## Consequences

- Нет «безымянных» переходных меток.
- Расширение реестра — правка ADR-043 + тест allowlist.

## Alternatives

| Alternative | Почему нет |
|---|---|
| `annotations.transitional: "true"` | не использовано кодом миграции; слот `tags` уже в ModelElement |
| Произвольные строки в tags | ломает inventory и cleanup |
