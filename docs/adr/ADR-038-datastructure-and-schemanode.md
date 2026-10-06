---
status: Accepted
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR-038: DataStructure и SchemaNode

**Date:** 2026-10-06  
**Status:** Accepted  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-033](ADR-033-technical-asset-quantum-boundary.md), [ADR-036](ADR-036-datatype-system.md), [ADR-039](ADR-039-structure-node-addressing.md), [ADR-040](ADR-040-message-integration-model.md), [ADR-041](ADR-041-schemanode-datatype-binding.md), [ADR-044](ADR-044-model-element-decomposition.md)  
**Spike:** [data-structure-spike-report.md](../migration/data-structure-spike-report.md)

## Context

Структура носителя и сообщения моделировалась через `PhysicalField` / `physical_fields` на `HasStructure`, без явного дерева узлов и без стабильной адресации поля вне носителя. Нужна именованная версия структуры (`DataStructure`) с узлами (`SchemaNode`), пригодная для Mapping, semantic diff, SQL-проекций и интеграционных схем (JSON Schema, Avro, OpenAPI, AsyncAPI).

Спайк генераторов ([data-structure-spike-report.md](../migration/data-structure-spike-report.md)) сравнил вложенное дерево (`root_node` / `children_nested`) и плоский список (`nodes` + `root_local_key`). Оба варианта проходят генераторы и round-trip; inlined-рекурсия без идентификатора в LinkML неизбежна.

## Decision

### Представление дерева: Flat

**Выбран Flat** (`nodes` + `root_local_key`; decision code `FLAT`).

- `DataStructure.nodes` — плоский список `SchemaNode` (inlined list).
- `DataStructure.root_local_key` — required, указывает на корневой узел.
- Рёбра: `SchemaNode.children` / `item_node` — строки `local_key`, не вложенные объекты.
- Циклы в рёбрах запрещены DAMS-валидатором; рекурсия схемы — через `node_kind=reference`.

Плоская форма лучше стыкуется с CURIE `structure_id#local_key` (ADR-039), SQL, semantic diff и Mapping. Inlined-дерево не берём, даже если генераторы его переваривают.

### Форма и физика в одном узле

Как в ODCS: один `SchemaNode` несёт и форму (`node_kind`, `children` / `item_node`), и физические/колоночные признаки (`native_name`, `native_type`, `nullable`, `ordinal_position`, …). Отдельного «логического» узла нет.

### Реляционные признаки — только DAMS

Слоты `ordinal_position`, `is_primary_key`, `is_unique`, `foreign_key_target`, `column_position` допустимы **только** при `schema_format=relational`. Узел в LinkML не знает родителя-структуру → проверка **целиком в DAMS-валидаторе** (`moex-dams-assess` / `check_formal_requirements`). `linkml-validate` / `make validate-schemas` это **не** ловят.

### schema_format и schema_dialect

- `schema_format` — стартовый enum (`json_schema`, `avro`, `protobuf`, `xml_schema`, `relational`, `openapi_schema`, `other`). Перенос в реестр форматов — отдельная задача.
- `schema_dialect` (`uri`, optional) на `DataStructure` — диалект / версия языка схемы (заложен с 1.1.0, чтобы не делать breaking позже):
  - JSON Schema — IRI диалекта (OpenAPI `jsonSchemaDialect`, JSON Schema 2020-12);
  - AsyncAPI Multi Format Schema — идентификатор формата+версии payload schema;
  - для `relational` не заполнять.
- На миксине `HasStructure` слот `schema_dialect` deprecated в 1.1.0, снят в 2.0.0. Канон — на `DataStructure`. Wire-формат носителя (`data_format`) остаётся на активе (wire ≠ schema).

### EmbeddedElement vs IdentifiedElement

`SchemaNode` `is_a: EmbeddedElement`. `local_key` — слот **только** встраиваемых объектов: уникальность внутри родителя (`DataStructure`), не глобальный идентификатор. Не конфликтовать с `IdentifiedElement` (ADR-044): не вводить второй `description` / не делать `local_key` глобальным key. `EmbeddedElement` использует mixin `DescribedElement`; собственный слот `description` снят. Идентичность узла: `(DataStructure.element_id, local_key)`.

### Деприкация PhysicalField

Двухшаговая дисциплина (как attribute-semantics):

| Версия схемы | Действие |
|---|---|
| **1.1.0** | `PhysicalField`, `physical_fields`, `HasStructure.schema_dialect` — `deprecated` + `deprecated_element_has_possible_replacement` |
| **2.0.0** | класс и слоты **удалены**; semantic diff видит «was deprecated» |

Не удалять `PhysicalField` в том же PR, где он только помечен deprecated. Путь каталога `0.1/` сохраняется.

### Корень и прочее

- Корень: `relational` → `object`; иначе `object` или `array`.
- `realizes_attribute_ref` необязателен.
- Модуль: `moex-structure.yaml`; коллекции `data_structures` (и `messages` — ADR-040) на `ModelPackage`.

## Consequences

- Viewer / проекции собирают дерево из рёбер `local_key`.
- Mapping и selections ссылаются на `structure_id#local_key` (ADR-039).
- Негативные фикстуры «реляционный признак в JSON» assert’ятся через DAMS, не только LinkML.
- Миграция `physical_fields` → scalar-узлы + промежуточные object по dotted path — в PR-2.

## Alternatives

| Alternative | Почему нет |
|---|---|
| Nested inlined tree (`root_node` / children as objects) | хуже для diff/SQL/CURIE; нет глобального id на SchemaNode |
| Отдельные «логические» и «физические» узлы | дублирует ODCS; усложняет Mapping |
| Реляционные правила в LinkML `rules` на SchemaNode | узел не видит `schema_format` родителя |
| Удалить PhysicalField сразу в 1.1.0 | ломает живые модели без окна миграции |

## References

- AsyncAPI 3.0 Multi Format Schema Object
- OpenAPI 3.1 Schema Object / `jsonSchemaDialect`
- JSON Schema 2020-12
- Apache Avro Specification
- Open Data Contract Standard (ODCS) — form+physics in one node
- [data-structure-spike-report.md](../migration/data-structure-spike-report.md)
- ADR-033 (quantum boundary), ADR-036 (DataType), ADR-039…041
