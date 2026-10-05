---
status: Accepted
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR-031: TechnicalAsset as unified registry of data quanta (квант данных)

**Date:** 2026-10-05  
**Status:** Accepted  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-001](ADR-001-linkml-yaml-canonical.md), [ADR-030](ADR-030-dams-uri-and-prefix-policy.md), [ADR-032](ADR-032-technical-asset-identity.md), [ADR-033](ADR-033-technical-asset-quantum-boundary.md)  
**Spike:** [technical-asset-spike-report.md](../migration/technical-asset-spike-report.md)

## Context

`PhysicalObject` — плоский класс с `PhysicalObjectKindEnum`, в котором смешаны несовместимые виды: `column`, `database`, `endpoint`, `message` и др. Один enum и одна коллекция `physical_objects` не выражают роли носителя, точки доступа, контейнера и исполнителя; downstream-правила (PDM/FLW) вынуждены фильтровать по kind.

Нужен единый реестр **квантов данных** (addressable technical assets) с явной иерархией и без дублирования связи «логический ↔ физический» вне `Mapping`.

## Decision

### Иерархия и миксины

- `TechnicalAsset` (abstract) → `DataCarrier`, `AccessPoint`, `DataContainer`, `ExecutionAsset`.
- Миксины: `HasStructure`, `HasProtocolBinding`, `Contains`, `HasLocation` (по подклассам).
- Термин предметной области: **«квант данных»** — addressable technical asset; поля/колонки квантами не являются (см. ADR-033).

### Форма коллекции (результат спайка)

**Выбран Variant B:** раздельные коллекции в `ModelPackage`:

- `data_carriers`, `access_points`, `data_containers`, `execution_assets`.

Единый реестр — **вычисляемое представление** в `ModelGraph`, не хранимый слот.

Спайк (2026-10-05) показал:

| Вариант | gen-pydantic | gen-json-schema | Вердикт |
|---|---|---|---|
| A: полиморфный `technical_assets` | схлопывается в `list[TechnicalAsset]` (поля подклассов не Union) | без `include_range_class_descendants` — только базовый `$ref`; с флагом — `anyOf` потомков | отвергнут |
| B: раздельные коллекции | `list[DataCarrier]` и т.д. — OK | точные `$ref` на подклассы — OK | **принят** |

`unique_keys` по `(asset_namespace, qualified_name)` **не срабатывают надёжно** в `linkml-validate` на иерархии. Основной механизм уникальности и межколлекционных инвариантов — **DAMS-валидатор** (`packages/specification-dams`); LinkML `unique_keys` / `rules` — дополнительный слой.

### Модульность схем

Коллекции `data_carriers` / … объявлены в `moex-core.yaml` (на `ModelPackage`), классы иерархии — в `moex-technical.yaml`. Чтобы range `DataCarrier` резолвился при генерации артефактов из core, `moex-core` импортирует `moex-technical`, а `moex-technical` импортирует `moex-core` (ModelElement). Циклический import поддерживается SchemaView / generators LinkML 1.11; **не** переопределять `ModelPackage` внутри `moex-technical` — это даёт `Conflicting URIs` между schema id модулей.

### Mapping, не realizes_refs

Связь entity ↔ quantum **не** хранится как `realizes_refs` на активе. Источник истины — `Mapping` (`entity_physical` и др.); типы концов проверяет DAMS-валидатор.

### Enums и namespace

- Три (четыре) **отдельных** enum по подклассам (`DataCarrierKindEnum`, `AccessPointKindEnum`, …), не `any_of` над одним enum.
- Слот идентичности пространства имён — `asset_namespace`, **не** переиспользование `DomainContext.namespace` (разный смысл при одном IRI слота ломает OWL/viewer).

### integrity_digest

При миграции `PhysicalObject` → `TechnicalAsset`:

- `integrity_digest` в `DataModelBinding` **пересчитывается только** для fixtures / demo.
- Для прочих моделей — новая ревизия с `compatibility_baseline_ref` на предыдущую (неизменяемость ревизии).

### Breaking change

Удаление `PhysicalObject` / `physical_objects` / `PhysicalObjectKindEnum` и переименование ссылок — **breaking** для DAMS **0.1 draft** и `moex_dams_contracts`. Номер версии схемы остаётся `0.1`, но обязателен changelog и классификация в semantic diff.

## Consequences

- Генераторы получают точные типы коллекций без хаков Union/`asset_class`.
- ModelGraph агрегирует реестр; UI/diff опираются на вычисляемый view.
- Валидатор DAMS — gate уникальности и типов концов Mapping.
- Миграция и XLSX-импорт следуют ADR-032 / ADR-033.

## Alternatives

| Alternative | Почему нет |
|---|---|
| Плоский класс + enum (как сейчас) | несовместимые kinds в одной модели |
| Наследование DCAT Dataset / Distribution / DataService | другой уровень каталога; не покрывает AccessPoint / ExecutionAsset в DAMS |
| entity → quantum без Mapping | дублирует источник истины; ломает SSSOM / review Mapping |
| Variant A: полиморфный `technical_assets` | gen-pydantic теряет подклассы; см. spike report |

## Related

- [technical-asset-spike-report.md](../migration/technical-asset-spike-report.md)
- ADR-032 (identity), ADR-033 (quantum boundary)
- ADR-001, ADR-007, ADR-010
