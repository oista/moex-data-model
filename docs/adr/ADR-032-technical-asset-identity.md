---
status: Accepted
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR-032: TechnicalAsset identity

**Date:** 2026-10-05  
**Status:** Accepted  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-030](ADR-030-dams-uri-and-prefix-policy.md), [ADR-031](ADR-031-technical-asset-registry.md), [ADR-033](ADR-033-technical-asset-quantum-boundary.md)

## Context

`PhysicalObject` идентифицировался в первую очередь через `element_id` (`dams:physical/...`) без явной пары «пространство имён актива + квалифицированное имя», сопоставимой с OpenLineage dataset identity. При миграции к `TechnicalAsset` нужна стабильная бизнес-идентичность, совместимая с lineage/каталогами, без ломки уже опубликованных `element_id`.

Глобальный слот `namespace` уже занят семантикой `DomainContext`; переиспользование через `slot_usage` дало бы один IRI `dams:namespace` с двумя смыслами.

## Decision

### Пара идентичности

Стабильная идентичность кванта:

- `asset_namespace` + `qualified_name`

по аналогии с OpenLineage dataset identity (`namespace` + `name`). Слот назван **`asset_namespace`**, чтобы не конфликтовать с `DomainContext.namespace`.

Уникальность пары — межколлекционно по всем подклассам `TechnicalAsset`; основной enforcement — DAMS-валидатор (см. ADR-031).

### id_prefixes и element_id

- В схеме: `id_prefixes: [dams]` (единый CURIE-префикс DAMS).
- `element_id` экземпляров **сохраняется** в форме `dams:physical/...` при миграции.

Это **осознанное отклонение** от идеи «единого префикса актива» (`dams:asset/...`): смена префикса в `element_id` ломала бы все ссылки и историю без выигрыша для authoring.

### Transitional namespace heuristic

Для активов с тегом `transitional` (слот `tags`) допускается эвристика вида `<technology>://<system id>` (например `oracle://MDM`).

Правило:

- изменение `asset_namespace` у **transitional**-актива **не** считается breaking и **не** меняет `element_id`;
- у **не-transitional** смена `asset_namespace` — breaking (меняется бизнес-идентичность).

Список transitional-namespace фиксируется в отчёте миграции для последующего уточнения.

### URI policy

Схемные IRI классов/слотов подчиняются [ADR-030](ADR-030-dams-uri-and-prefix-policy.md) (`https://data.moex.com/dams/`, без лишних `class_uri` на DAMS-классах). Instance `element_id` остаётся CURIE под `dams:`; `MOEX-ID-001` по-прежнему про instance identifiers.

## Consequences

- OpenLineage-совместимая пара для сопоставления с lineage и каталогами.
- Миграция не переписывает `element_id`; ссылки `carrier_ref` / Mapping остаются стабильными.
- Viewer и OWL видят отдельный слот `asset_namespace`, не путаясь с domain namespace.

## Alternatives

| Alternative | Почему нет |
|---|---|
| Переиспользовать слот `namespace` | конфликт семантики с `DomainContext` при одном IRI |
| Переименовать все `element_id` в `dams:asset/...` | массовый breaking без необходимости |
| Только `element_id` без пары namespace+name | слабая стыковка с OpenLineage / внешними каталогами |

## References

- OpenLineage Naming Conventions (primary): https://openlineage.io/docs/spec/naming
- ADR-030 (URI / prefix policy), ADR-031 (registry), ADR-033 (quantum boundary)
