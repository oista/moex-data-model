---
id: model-layers
sources:
  - docs/adr/ADR-021-dams-implementation-profile-and-levels.md
  - docs/adr/ADR-026-cmd-entity-metamodel.md
  - docs/adr/ADR-031-technical-asset-registry.md
  - docs/adr/ADR-032-technical-asset-identity.md
  - docs/adr/ADR-033-technical-asset-quantum-boundary.md
  - docs/adr/ADR-034-lightweight-conceptual-property.md
  - docs/adr/ADR-035-value-domains.md
  - docs/adr/ADR-036-datatype-system.md
  - docs/adr/ADR-037-attribute-semantics-migration.md
  - docs/adr/ADR-038-datastructure-and-schemanode.md
  - docs/adr/ADR-039-structure-node-addressing.md
  - docs/adr/ADR-040-message-integration-model.md
  - docs/adr/ADR-041-schemanode-datatype-binding.md
  - docs/adr/ADR-046-typed-mapping-endpoints.md
  - model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml
  - model-assets/specifications/moex-dams/0.1/schemas/moex-datatypes.yaml
  - model-assets/specifications/moex-dams/0.1/schemas/moex-semantic.yaml
  - model-assets/specifications/moex-dams/0.1/schemas/moex-structure.yaml
  - model-assets/specifications/moex-dams/0.1/schemas/moex-technical.yaml
draft: true
---

# Слои модели

Внутри модели данных три описания, и это не три вида пакета.

[Понятийный слой](glossary:conceptual-layer) отвечает, о чём мы говорим. Его единица — [понятийная сущность](glossary:conceptual-entity): устойчивый предмет области, у которого есть свой смысл.

[Логический слой](glossary:logical-layer) отвечает, как этот смысл разложен в данные решения. Его единица — [логическая сущность](glossary:logical-entity). Она реализует понятийную, а не копирует её текст.

[Технический слой](glossary:physical-layer) отвечает, где данные лежат и как к ним обращаются. Единица учёта здесь — [технический объект](glossary:technical-asset), его же называют [квантом данных](glossary:data-quantum): носитель, точка доступа, контейнер или то, что данные исполняет. Колонка таблицы квантом не является. Форма данных на объекте — это [структура данных](glossary:data-structure), дерево [узлов структуры](glossary:schema-node) (ADR-038). Отдельный вид технического описания — [сообщение](glossary:message), которым системы обмениваются (ADR-040).

Слои не склеивают копией полей. Связь записывают как [отображение](glossary:mapping): решение к понятию предприятия, техническое поле к логическому (ADR-046).

Технический объект узнают по паре полей `asset_namespace` и `qualified_name`, а не по переименованию старого идентификатора (ADR-032). Поле `element_id` при переносе старых записей остаётся вида `dams:physical/...`. Пара полей объявлена в `model-assets/specifications/moex-dams/0.1/schemas/moex-technical.yaml`.

Квант адресуют целиком: в отображениях, привязках и потоках (ADR-033). Колонка и поле сообщения внутрь кванта не входят. Это узлы структуры на объекте.

Отдельное свойство понятия заводят не на каждый атрибут, а только когда смысл важен сам по себе: идентификатор, сверка с внешней моделью, общее для нескольких решений, регуляторика (ADR-034). Как значение записано, на атрибуте больше не хранят. На тип и на набор допустимых значений ставят ссылки `data_type_ref` и `value_domain_ref`. Свойство объявлено в `moex-core.yaml` рядом с понятийной сущностью, в том же каталоге схем.

Смысл списка значений и сам список — разные записи (ADR-035). Общие справочники вроде валют заводят на уровне предприятия, не внутри одного решения. Смысл списка — в `moex-semantic.yaml`, набор значений и типы — в `moex-datatypes.yaml`.

Корпоративные типы тоже живут в пакете предприятия, не в каждом решении (ADR-036). У типа есть имя и привязка к типу конкретной технологии. Старые поля типа и формата с атрибута сняты. Скрипт `scripts/migrate_logical_attribute_semantics.py` переносит их в тип и в набор значений и сам свойства понятий не создаёт (ADR-037).

Узел находят по адресу из идентификатора структуры и локального ключа через решётку: `dams:structure/…#local_key` (ADR-039). Это не отдельный идентификатор элемента модели. Ключ узла объявлен в `moex-structure.yaml`.

У узла может быть имя типа как в источнике, поле `native_type`, и ссылка на корпоративный тип, поле `data_type_ref` (ADR-041). Можно указать одно, другое, оба или ничего. Если указаны оба и они спорят с реестром соответствий, это предупреждение, а не отказ сборки.

Где прочитать решение: [ADR-021](docs/adr/ADR-021-dams-implementation-profile-and-levels.md), [ADR-026](docs/adr/ADR-026-cmd-entity-metamodel.md), [ADR-031](docs/adr/ADR-031-technical-asset-registry.md). Остальные номера названы выше, рядом со своим смыслом.
