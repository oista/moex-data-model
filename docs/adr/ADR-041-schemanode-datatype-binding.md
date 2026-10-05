---
status: Accepted
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR-041: Привязка SchemaNode к DataType / native type

**Date:** 2026-10-06  
**Status:** Accepted  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-036](ADR-036-datatype-system.md), [ADR-037](ADR-037-attribute-semantics-migration.md), [ADR-038](ADR-038-datastructure-and-schemanode.md)

## Context

Узлы структуры нуждаются в типовой аннотации: нативный тип диалекта источника и/или ссылка на корпоративный `DataType`. Типовая система уже зафиксирована в ADR-036 (`DataType`, `NativeTypeBinding`, seed из `LogicalDataTypeEnum`). Этот ADR **не** дублирует и **не** пересматривает ADR-036: только правила слотов на `SchemaNode`.

## Decision

### Слоты на SchemaNode

`SchemaNode` может иметь:

- `native_type` (string, optional) — имя типа как в источнике / диалекте схемы;
- `data_type_ref` (optional) — ссылка на `DataType` из корпоративного реестра (ADR-036).

Допустимы: только native, только ref, оба, или ни одного (покрытие и строгость — отдельные DAMS-правила / coverage-слоты, не предмет этого ADR).

Имя слота нативного типа на узле — `native_type` (как у бывшего `PhysicalField` в core). Слот `dialect_native_type` остаётся у `NativeTypeBinding` (ADR-036); не смешивать.

### NativeTypeBinding mismatch → warning

Если заданы и `native_type`, и `data_type_ref`, и в реестре есть `NativeTypeBinding` для этой пары (диалект / формат ↔ DataType), несовпадение нативного имени с binding’ом — **warning** (не hard error на первом этапе). Цель — сигнал качества данных, не блок публикации без явной политики.

### LogicalDataTypeEnum остаётся seed

`LogicalDataTypeEnum` по-прежнему каталог имён стартового набора `DataType` (ADR-036). Не возвращать enum как range атрибута/узла; не создавать параллельную типовую систему для SchemaNode. Миграция/ingest могут маппить имя → `dams:datatype/{name}` через существующий реестр.

### Вне scope

- Не вводить новые классы `DataType` / `NativeTypeBinding` в этом изменении.
- Не переносить этап «реестр форматов» / параметризованные типы сюда.
- Не дублировать `ValueDomain` на узле без отдельного решения (логика доменов — ADR-035/037).

## Consequences

- SchemaNode стыкуется с уже принятой типовой системой без второго seed-каталога.
- Потребители (viewer, Mapping, projections) читают `data_type_ref` так же, как у LogicalAttribute после ADR-037.
- Warning mismatch настраивается в DAMS rules; ужесточение до error — отдельное решение.

## Alternatives

| Alternative | Почему нет |
|---|---|
| Только `native_type` без DataType | нет корпоративного выравнивания; ломает цель ADR-036 |
| Только `data_type_ref` | теряется fidelity импорта из Avro/JSON Schema/DDL |
| Дублировать типовую систему на structure-модуле | расходится с ADR-036; двойной seed |
| Hard error на mismatch сразу | блокирует миграцию грязных источников |

## References

- ADR-036 (DataType / NativeTypeBinding) — нормативная типовая система
- ADR-037 (миграция семантики атрибутов)
- ADR-038 (SchemaNode)
