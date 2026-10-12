---
status: Proposed
version: "0.1"
normative: true
supersedes: []
superseded_by: []
---

# ADR-046: Typed Mapping endpoints (subclasses + separate collections)

**Date:** 2026-10-12  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-021](ADR-021-dams-implementation-profile-and-levels.md), [ADR-029](ADR-029-cdm-from-er-sketch-and-realization.md), [ADR-031](ADR-031-technical-asset-registry.md), [ADR-039](ADR-039-structure-node-addressing.md), [ADR-044](ADR-044-model-element-decomposition.md), [ADR-045](ADR-045-executable-constraint-matrix.md)  
**Spike:** [typed-mapping-spike-report.md](../migration/typed-mapping-spike-report.md)

## Context

`Mapping` — один класс с `mapping_type: MappingTypeEnum` и нетипизированными `source_refs` / `target_refs` (`range: uriorcurie`). LinkML / JSON Schema / сгенерированный SHACL проверяют форму (поле есть, значение из enum, строка-ссылка), но не допустимые пары endpoint kinds.

Фактическое состояние:

- В данных ~254 mapping'а; живые типы: `field_mapping`, `entity_physical`, `realizes`, `aligns_with`. Шесть значений enum не используются.
- Типы концов для PDM проверяет только Python (`check_mapping_endpoint_types`, PDM-009); `realizes` / `aligns_with` покрыты слабее.
- Направление source/target в данных неоднородно (`entity_physical`: carrier→logical; `field_mapping`: attribute→structure#key).
- ADR-029 допускает multi-realize; кардинальность «ровно одна концептуальная» недопустима как общее правило.
- ADR-031 уже отверг полиморфный список подклассов: gen-pydantic схлопывает его в базовый тип. Нужен тот же паттерн Variant B.

## Decision

### D1. Подклассы по живой таксономии

Базовый `Mapping` остаётся. Добавляются:

| Класс | `mapping_type` | source | target | Кардинальность концов |
|---|---|---|---|---|
| `RealizesMapping` | `realizes` | LogicalEntity (и при необходимости ConceptualEntity через `any_of`) | ConceptualEntity | min 1 / min 1; many на target разрешён (ADR-029) |
| `EntityPhysicalMapping` | `entity_physical` | DataCarrier | LogicalEntity | ровно 1 / 1; `mapping_cardinality = one_to_one` |
| `FieldMapping` | `field_mapping` | LogicalAttribute | `SchemaNodeRef` | min 1 / min 1 |
| `AlignsWithMapping` | `aligns_with` | ConceptualEntity | `uri` (внешний IRI) | 1 / min 1 |

Направление source→target **не меняется** относительно существующих YAML.

### D2. Тип `SchemaNodeRef`

Новый LinkML type `typeof: uriorcurie` с pattern `^dams:structure/.+#.+$` (ADR-039). Нужен, потому что у `SchemaNode` нет глобального `element_id`.

### D3. Раздельные коллекции (Variant B)

В `ModelPackage`:

- `realizes_mappings`, `entity_physical_mappings`, `field_mappings`, `aligns_with_mappings`
- `mappings` остаётся **deprecated** на окне совместимости, затем удаляется

Единый view для читателей — хелпер `iter_mappings(data)` (читает legacy + типизированные коллекции).

### D4. Designator и уровни проверки (результат spike)

| Что | Уровень | Как |
|---|---|---|
| Фиксация `mapping_type` / `one_to_one` на подклассе | **L1** | LinkML `rules` с `equals_string` в postconditions |
| min/max cardinality концов, pattern `SchemaNodeRef` | **L1 / JSON Schema** | `slot_usage` + type pattern |
| Resolve endpoint id → фактический класс | **L2** | DAMS-валидатор (расширение PDM-009) |
| RDF `sh:class` / pattern на концах | **L3** | gen-shacl где работает + **ручные** shapes в `constraints/shacl/manual/` |

Запрещено: `equals_string` **в `slot_usage`** на слоте с range enum — `gen-shacl` падает (`equals_string` требует range `string`). Designator только через `rules`.

### D5. Deprecation enum

Значения `semantic_equivalence`, `specialization`, `implementation`, `transformation`, `aggregation`, `derivation` помечаются deprecated; удаляются в финальном PR серии после миграции данных.

### D6. Серия PR

| PR | Тема |
|---|---|
| PR-0 | Этот ADR + spike report (docs; без схем / `generated/`) |
| PR-1 | Аддитивная схема + регенерация артефактов |
| PR-2 | `iter_mappings` + перевод читателей |
| PR-3 | Миграция YAML (`ruamel`) + перевод писателей |
| PR-4 | INV в constraint-matrix, PDM-009 на подклассы, manual SHACL, примеры |
| PR-5 | Удаление legacy `mappings` / deprecated enum, changelog, docs/UML |

## Spike findings (summary)

Полный отчёт: [typed-mapping-spike-report.md](../migration/typed-mapping-spike-report.md). Скрипт: `scripts/spike_typed_mapping_generators.py`.

- **gen-pydantic:** раздельные коллекции → `list[RealizesMapping]` и т.д. (как ADR-031 Variant B). Ссылки остаются `list[str]`.
- **gen-json-schema:** точные `$ref` на подклассы; `minItems`/`maxItems`; pattern на `SchemaNodeRef`; class-range refs — всё равно `string`.
- **gen-owl:** глобальный `rdfs:range` у `source_refs` остаётся `uriorcurie`; класс-локальные `owl:allValuesFrom` на endpoint classes появляются. Конфликта нескольких глобальных range нет.
- **gen-shacl:** с designator через `rules` генерация проходит; `sh:class` для class-ranged слотов эмитится. Pattern `SchemaNodeRef` в SHACL не подтверждён — для FieldMapping target нужен ручной L3 shape.
- **equals_string на enum slot_usage:** ломает gen-shacl — не использовать.

## Consequences

- Статическая ценность генерации растёт для коллекций и кардинальности; реальная проверка «id указывает на нужный класс» остаётся L2/L3.
- ~254 строк YAML мигрируют один раз (PR-3); потребители `mappings[]` (~89 файлов кода) переводятся через `iter_mappings` с окном deprecated.
- SSSOM / `packages/semantic-mappings` и kernel `MappingProvider` не затрагиваются.
- Constraint matrix (ADR-045) получает INV для endpoint kinds Mapping.

## Alternatives

| Alternative | Почему нет |
|---|---|
| Полиморфный `mappings: list[Mapping]` + подклассы | gen-pydantic схлопывает (ADR-031) |
| Только усилить L2 без подклассов | JSON Schema / Pydantic / SHACL остаются слабыми; проблема масштабирования не закрывается |
| Переименовать slots / перевернуть direction | Ломает 254 строки и ADR-044 label без выигрыша |
| «Ровно одна концептуальная» для realizes | Противоречит ADR-029 и данным CRM |

## Related

- Spike report, ADR-031, ADR-039, ADR-044, ADR-045
- PDM-009 (`it-solution-requirements.yaml`)
