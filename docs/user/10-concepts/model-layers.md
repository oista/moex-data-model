---
id: model-layers
sources:
  - docs/adr/ADR-021-dams-implementation-profile-and-levels.md
  - docs/adr/ADR-026-cmd-entity-metamodel.md
  - docs/adr/ADR-031-technical-asset-registry.md
  - docs/adr/ADR-038-datastructure-and-schemanode.md
  - docs/adr/ADR-040-message-integration-model.md
  - docs/adr/ADR-046-typed-mapping-endpoints.md
verified_at: 2026-11-02
---

# Слои модели

Внутри модели данных три описания, и это не три вида пакета.

[Понятийный слой](glossary:conceptual-layer) отвечает, о чём мы говорим. Его единица — [понятийная сущность](glossary:conceptual-entity): устойчивый предмет области, у которого есть свой смысл.

[Логический слой](glossary:logical-layer) отвечает, как этот смысл разложен в данные решения. Его единица — [логическая сущность](glossary:logical-entity). Она реализует понятийную, а не копирует её текст.

[Технический слой](glossary:physical-layer) отвечает, где данные лежат и как к ним обращаются. Единица учёта здесь — [технический объект](glossary:technical-asset), его же называют [квантом данных](glossary:data-quantum): носитель, точка доступа, контейнер или то, что данные исполняет. Колонка таблицы квантом не является. Форма данных на объекте — это [структура данных](glossary:data-structure), дерево [узлов структуры](glossary:schema-node). Отдельный вид технического описания — [сообщение](glossary:message), которым системы обмениваются.

Слои не склеивают копией полей. Связь записывают как [отображение](glossary:mapping): решение к понятию предприятия, техническое поле к логическому. Смысл свойства, допустимые значения и типы описаны отдельно и на этой странице не разбираются.

Где прочитать решение: [ADR-021](docs/adr/ADR-021-dams-implementation-profile-and-levels.md), [ADR-026](docs/adr/ADR-026-cmd-entity-metamodel.md), [ADR-031](docs/adr/ADR-031-technical-asset-registry.md), [ADR-032](docs/adr/ADR-032-technical-asset-identity.md), [ADR-033](docs/adr/ADR-033-technical-asset-quantum-boundary.md), [ADR-034](docs/adr/ADR-034-lightweight-conceptual-property.md), [ADR-035](docs/adr/ADR-035-value-domains.md), [ADR-036](docs/adr/ADR-036-datatype-system.md), [ADR-037](docs/adr/ADR-037-attribute-semantics-migration.md), [ADR-038](docs/adr/ADR-038-datastructure-and-schemanode.md), [ADR-039](docs/adr/ADR-039-structure-node-addressing.md), [ADR-040](docs/adr/ADR-040-message-integration-model.md), [ADR-041](docs/adr/ADR-041-schemanode-datatype-binding.md), [ADR-046](docs/adr/ADR-046-typed-mapping-endpoints.md).
