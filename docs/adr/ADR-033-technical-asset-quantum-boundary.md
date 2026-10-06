---
status: Accepted
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR-033: Quantum boundary

**Date:** 2026-10-05  
**Status:** Accepted  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-031](ADR-031-technical-asset-registry.md), [ADR-032](ADR-032-technical-asset-identity.md)

## Context

В `PhysicalObjectKindEnum` соседствуют и контейнеры (`database`, `schema`), и носители (`table`, `topic`, `file`), и транзитные payload/`message`, и даже поля (`column`). Без явной границы «кванта» миграция и импортёры либо плодят лишние активы, либо теряют иерархию.

Нужен критерий: что является **квантом данных** (`TechnicalAsset`), а что адресуется внутри кванта.

## Decision

### Критерий addressability

Квант данных — технический актив, который:

- имеет стабильную идентичность (`asset_namespace` + `qualified_name`, ADR-032);
- адресуется как целое в Mapping, lineage, binding’ах и потоках.

**Поля и колонки не кванты.** Они адресуются как `asset_ref` (на `DataCarrier`) + `path` / `PhysicalField` внутри структуры носителя, а не отдельным `TechnicalAsset`.

### Containers vs carriers

| Роль | Класс | Примеры kind |
|---|---|---|
| Контейнер / группировка | `DataContainer` | `database`, `schema`, `broker`, `cluster`, filesystem root |
| Носитель данных | `DataCarrier` | `table`, `view`, `file`, `stream_topic`, `message_type`, … |
| Точка доступа | `AccessPoint` | API / endpoint (данные не несёт; достижим через `serves_refs`) |
| Исполнитель | `ExecutionAsset` | job / process / runtime |

`DataFlowEntityBinding` / `SelectedEntity` ссылаются только на `DataCarrier` (`carrier_refs`). `DataContainer` в этих списках — ошибка валидации.

### Transitional payload / message

Бывшие `payload` / `message` → `DataCarrier` с `asset_kind: message_type` (transitional)
были заменены на `Message` + `DataStructure` (ADR-038 / ADR-040). Значение
`message_type` удалено из `DataCarrierKindEnum` в DAMS 2.0.0.

### Пример: Kafka

Типичная модель потока:

1. `DataContainer` — broker / cluster (родительский контейнер).
2. `DataCarrier` (`stream_topic`) — топик как носитель.
3. `DataCarrier` (`message_type`, transitional) — формат payload; связь со структурой через `structure_ref`.

Поток данных моделируется как контейнер + топик; binding’и указывают на carrier (топик / message_type), не на контейнер.

### Родители: импортёр vs миграция

- **XLSX-импортёр** (`packages/standard-linkml`): **создаёт** родительский `DataContainer` для schema / БД, если они присутствуют в источнике.
- **Скрипт миграции** `PhysicalObject` → `TechnicalAsset`: **не изобретает** родительские database/schema, которых не было в исходных данных.

## Consequences

- Граница кванта стабильна для PDM/FLW, Mapping и UI.
- Иерархия `parent_ref` осмысленна (carrier → container), без column-as-asset.
- Transitional `message_type` видны в отчёте миграции и подлежат уточнению.
- Импорт и миграция не расходятся в политике «родителей».

## Alternatives

| Alternative | Почему нет |
|---|---|
| Column / field как TechnicalAsset | взрыв кардинальности; дублирует PhysicalField + path |
| Только носители без контейнеров | теряется группировка schema/DB/broker для viewer и импорта |
| Всегда создавать родителей при миграции | выдуманные активы без источника; ломает инвариант множества element_id |

## References

- DCAT 3 — Resource, Dataset, Distribution, DataService: https://www.w3.org/TR/vocab-dcat-3/
- ArchiMate — Artifact, Technology Interface, Node (технологический слой)
- OpenLineage Naming Conventions: https://openlineage.io/docs/spec/naming
- ADR-031 (registry), ADR-032 (identity)
