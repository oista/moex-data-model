---
status: Proposed
version: "0.1"
normative: true
supersedes: []
superseded_by: []
---

# ADR-048: Topology ownership (Clinkr/EAM SoT, DAMS semantic bindings)

**Date:** 2026-10-12  
**Status:** Proposed (PR-0 of Topology ownership series)  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-013](ADR-013-specification-requirements-catalog.md), [ADR-040](ADR-040-message-integration-model.md), [ADR-042](ADR-042-integrity-digest-revisions.md), [ADR-045](ADR-045-executable-constraint-matrix.md), [ADR-046](ADR-046-typed-mapping-endpoints.md), [ADR-047](ADR-047-repository-manifest-and-lock.md)  
**Inventory:** [topology-inventory.md](../migration/topology-inventory.md)

## Context

Спека уже требует, чтобы интеграционный поток ссылался на интеграцию Clinkr, а не дублировал её как независимый master (DAMS-F-007). `DataFlow` описан как ссылочная проекция: топология и канал — данные Clinkr, семантика — модель данных.

Фактическое состояние схемы противоречит этому: на `DataFlow` обязательны локальные копии topology-фактов (`source_*` / `target_*` solution/system/platform, `integration_level` / `integration_class` / `integration_channel`, `integration_spec_ref`). При изменении каталога Clinkr/EAM эти поля drift'ят относительно источника истины.

Семантика уже отделена (`DataFlowEntityBinding`). `integration_ref` уже обязателен и использует CURIE вида `clinkr:integration/INT-00421`. В репозитории один экземпляр `DataFlow` (example); в `implementations/` коллекций `data_flows` нет.

Ограничение ADR-047: всё под `moex-dams/0.1/schemas/` попадает в генерацию DAMS-артефактов. Read-model и формат снимка каталога не должны импортироваться из `moex-dams.yaml`.

## Decision

### D1. Источник истины

| Факт | Владелец | В DAMS |
|---|---|---|
| Системы, платформы, решения, интерфейсы, каналы, протоколы, spec URI | Clinkr / EAM | Только через `integration_ref` и материализованный `TopologyView` |
| Смысл обмена: selection сущностей/атрибутов, carriers, mapping | DAMS | `DataFlowEntityBinding` (+ contract bindings) |
| Привязка семантики к операции/участнику каталога | DAMS | слоты на `DataFlowEntityBinding` |
| Эффективная топология для запросов и lint | Генерируется | `TopologyView` (read model) |

DAMS **не пишет** topology. Authored whitelist на `DataFlow`:

- `integration_ref` (обязателен)
- `contract_ref`
- `entity_bindings`
- `bound_catalog_revision` (на какой ревизии снимка привязка подтверждена)

Derived (не authored после cleanup): `source_*` / `target_*` solution/system/platform, `integration_level` / `integration_class` / `integration_channel`, `integration_spec_ref`.

### D2. Файл-снимок — единственный вход CI

На время серии источник каталога — **файл-снимок** в репозитории (`model-assets/catalog-snapshots/`). CI и валидация **не** вызывают Clinkr/EAM API. Live `RegistryAdapter` вне этой серии.

Формат снимка фиксируется как контракт модуля `moex-topology`. Допускается surrogate-ключ `catalog + qualified_name`, если у каталога нет стабильных ID.

### D3. Привязка без отдельного IntegrationBinding

Отдельный aggregate `IntegrationBinding` / `IntegrationBindingSet` **не** вводится: `DataFlowEntityBinding` уже имеет `flow_ref`; второй корень с тем же `flow_ref` создал бы внутренний drift.

Вместо этого на `DataFlowEntityBinding` добавляются:

- `catalog_operation_ref` — operationId / channel в каталоге
- `catalog_participant_ref` — внешний участник (роль уже выражена `direction`)

`binding_status` **не** хранится: это вывод resolver (resolved / stale / broken / unmapped) в drift-отчёте и в `TopologyView`. Provenance не вводится (git + `lifecycle_status` + аннотации).

`DataExchange` из аудита = существующий `DataFlowEntityBinding` (без rename).

### D4. Модуль moex-topology (не часть DAMS schema glob)

Классы `CatalogSnapshot`, `CatalogObject`, `TopologyView`, `TopologyFact`, `DriftFinding` живут в `model-assets/specifications/moex-topology/0.1/` и **не** импортируются `moex-dams.yaml` (как `moex-repository-manifest` в ADR-047).

`TopologyView` помечен `materialized: true`. Пишется только генератором в `generated/topology/` (файл на `catalog_revision`). Ручное редактирование ловится `materialize --check` / шаг `check-topology`.

### D5. Drift

| Код | Смысл | Severity (старт) |
|---|---|---|
| `orphan_ref` | объект пропал / переименован в снимке | error (block merge) |
| `unknown_catalog` | префикс `integration_ref` отсутствует в снимке | error |
| `topology_changed` | участники / канал изменились относительно `bound_catalog_revision` | warning |
| `unmapped_exchange` | операция снимка без binding или binding без `catalog_operation_ref` | warning |
| `stale_revision` | `bound_catalog_revision` отстаёт от снимка | warning |

Эскалация warning → error для critical flows — по матрице ADR-013 после калибровки. Refresh снимка — отдельный PR; orphan падает на нём.

### D6. Fan-out

Один `integration_ref` на `DataFlow`. Несколько интеграций = несколько `DataFlow`. Массив `integration_refs[]` не вводится.

### D7. Серия PR

| PR | Тема |
|---|---|
| PR-0 | Этот ADR + inventory (docs; без схем / `generated/`) |
| PR-1 | Аддитивная схема DAMS + модуль `moex-topology`; topology-слоты deprecated + `required` снят; regen |
| PR-2 | Файл-снимок + resolver / drift / materializer + `check-topology` |
| PR-3 | `effective_topology` dual-read + перевод читателей |
| PR-4 | INV в constraint-matrix + requirement-коды + фикстуры |
| PR-5 | Удаление topology-слотов (major), миграционный скрипт, docs, regen |

Паттерн окна deprecated — как ADR-046. Схемный diff и data-diff не смешиваются. `check_all` на каждом PR отдельно.

## Consequences

- После PR-5 authored `DataFlow` больше не дублирует Clinkr/EAM; lint и viewer используют `TopologyView`.
- Внешние потребители, писавшие topology на flow, получают major bump и скрипт миграции.
- Пока нет live-экспорта, снимок — fixture/контракт; адаптер под реальный экспорт — отдельная работа.
- Neo4j / operational graph вне scope (ADR-003).

## Alternatives considered

| Вариант | Почему отвергнут |
|---|---|
| Оставить topology на DataFlow как «кэш» | Не устраняет drift; противоречит DAMS-F-007 |
| Отдельный `IntegrationBinding` aggregate | Дублирует `DataFlowEntityBinding.flow_ref` |
| Live API в CI | Нестабильность каталога; ADR фиксирует файл-снимок |
| Классы TopologyView внутри `moex-dams` schemas | Ломает границу ADR-047 / переписывает `generated/**` на каждый чих снимка |
| `integration_refs[]` | YAGNI при одном flow на интеграцию |
