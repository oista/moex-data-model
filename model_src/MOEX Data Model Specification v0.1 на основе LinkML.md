# MOEX Data Model Specification v0.1 на основе LinkML

## Статус документа

| Атрибут | Значение |
|---|---|
| Наименование | MOEX Data Model Specification |
| Сокращение | MDMS |
| Версия | 0.1.0 |
| Статус | Архитектурный прототип / draft |
| Канонический формат | LinkML YAML |
| Область действия | Корпоративная модель данных и модели данных ИТ-решений Группы МБ |
| Основной исполняющий компонент | Репозиторий моделей и `dmr engine` |

**MDMS (MOEX Data Model Specification)** — внутренний стандарт MOEX, определяющий метамодель, правила представления и машинной проверки корпоративной модели данных и моделей данных ИТ-решений. MDMS не является новым языком моделирования: версия 0.1 использует LinkML как базовый язык метамодели и добавляет MOEX-специфичные сущности, профили, ограничения и интеграционные правила.

Версия 0.1 содержит одновременно нормативное описание и проверенный машинно-читаемый прототип. Прототип включает восемь LinkML-модулей, примеры модели ИТ-решения, потока из Clinkr и модельной спецификации дата-контракта, а также сгенерированные JSON Schema, SHACL и OWL-проекции.

# Часть 1. Основания

## Назначение

Каждое ИТ-решение MOEX, включающее одну или несколько ИТ-систем, должно иметь собственный версионируемый артефакт модели данных. Он описывает значимые данные решения на концептуальном, логическом и физическом уровнях, связывает бизнес-смысл с техническими представлениями и служит источником модельной части дата-контрактов.

Корпоративная архитектурная концепция определяет модель данных как машиночитаемую структуру из концептуального, логического и физического уровней. Логический уровень организован в доменные контексты и связан как с концептуальными сущностями, так и с физическими «квантами данных» — таблицами, файлами, API endpoints и другими управляемыми объектами.[^1]

Дата-контракт MOEX не должен становиться самостоятельным источником описания передаваемых данных. Он фиксирует факт, способ и условия использования данных, тогда как модель ИТ-решения фиксирует состав, физическое размещение, семантику и классификацию; в контракт могут включаться только заранее опубликованные физические объекты, связанные с логическими сущностями и атрибутами.[^2]

## Цели

MDMS должна обеспечивать:

- единый способ описания моделей разных ИТ-решений;
- стабильную идентичность элементов независимо от переименований и физической реализации;
- явное разделение концептуального, логического и физического уровней;
- описание кросс-системных понятий, например «Клиент» и «Финансовый инструмент»;
- описание локальных реализаций корпоративных понятий в доменных контекстах и ИТ-решениях;
- трассировку `ИТ-решение → физический объект → логическая сущность → интеграция → дата-контракт → DQ/SLA/политики`;
- наследование классификации и маркировки данных модельной спецификацией дата-контракта;
- использование внешних мастер-справочников без создания теневых копий;
- Git-based authoring, review, diff, CI/CD и автоматическую генерацию производных артефактов;
- детерминированный контекст для каталога, графа знаний и AI-агентов.

## Принципы

### Модель решения обязательна

Владелец ИТ-решения отвечает за актуальность его модели. В ней должны быть описаны данные, создаваемые, изменяемые, публикуемые или принимаемые решением, если они участвуют в интеграции, управлении, контроле качества или регулировании доступа; всё, что доступно за периметром решения или поступает извне, должно быть опубликовано в модели до создания соответствующего дата-контракта.[^2]

### Семантика отделена от транспорта

Логическая сущность не создаётся отдельно для каждого API, топика или таблицы. Одна логическая сущность может быть реализована несколькими физическими объектами и участвовать в нескольких интеграциях; OpenAPI, AsyncAPI, Avro, JSON Schema и DDL сохраняют роль авторитетных технических схем, а MDMS связывает их элементы с логической семантикой.[^3][^2]

### Ссылки вместо копирования

Модель решения ссылается на EAM, бизнес-глоссарий, организационные роли, политики, процессы, Clinkr и дата-каталог по стабильным идентификаторам. В MDMS допускается локальная ссылочная проекция записи справочника для валидации и отображения, но она не становится мастер-копией.

### Mapping — объект первого класса

Соответствие между концептуальным, логическим и физическим элементами описывается самостоятельной сущностью `Mapping`, а не неформальным комментарием. Mapping имеет стабильный ID, тип, кардинальность, преобразование, происхождение, статус согласования, confidence и период действия.

### Классификация наследуется

Класс данных и маркировка чувствительности задаются в модели решения и наследуются модельной спецификацией дата-контракта; вручную исправлять их в контракте нельзя. Для каждого передаваемого объекта должен выполняться контроль наличия класса данных и маркировки.[^2]

### Версии разделены

Следует независимо управлять:

- `apiVersion` — версией метамодели MDMS;
- `modelVersion` — версией модели ИТ-решения или корпоративной модели;
- `implementationVersion` — версией конкретной модельной спецификации дата-контракта;
- `contractVersion` — версией композитного дата-контракта;
- `modelRevision` — неизменяемой технической ревизией модели, например Git commit.

Стандарт дата-контрактов уже разделяет версию стандарта спецификации и версию конкретной реализации, а дочерние спецификации эволюционируют независимо.[^2]

## Требования

### Функциональные требования

| ID | Требование | Уровень |
|---|---|---|
| MDMS-F-001 | Каждый адресуемый элемент должен иметь глобально уникальный стабильный `element_id`. | MUST |
| MDMS-F-002 | `ModelPackage` модели решения должен ссылаться на одну `ITSolution`. | MUST |
| MDMS-F-003 | Модель должна различать conceptual, logical и physical elements типами метамодели, а не соглашением об именовании. | MUST |
| MDMS-F-004 | `LogicalEntity` должна принадлежать `DomainContext` и модели ИТ-решения. | MUST |
| MDMS-F-005 | Публикуемый `PhysicalObject` должен иметь Mapping к одной или нескольким логическим сущностям; каждое передаваемое поле — к логическому атрибуту или утверждённому преобразованию. | MUST |
| MDMS-F-006 | Системы, решения и платформы должны задаваться ссылками на EAM; сущность платформы называется `ITPlatform`. | MUST |
| MDMS-F-007 | Интеграционный поток должен ссылаться на интеграцию Clinkr, а не дублировать её как независимый master record. | MUST |
| MDMS-F-008 | Модельная спецификация дата-контракта должна фиксировать immutable revision модели и точный selection сущностей, атрибутов и физических представлений. | MUST |
| MDMS-F-009 | Классификация логической сущности и атрибута должна быть машиночитаемой и наследуемой контрактом. | MUST |
| MDMS-F-010 | Метрики должны храниться в опциональном analytics-профиле и ссылаться на логические сущности и атрибуты. | SHOULD |

### Нефункциональные требования

| ID | Требование | Уровень |
|---|---|---|
| MDMS-NF-001 | Канонический артефакт должен быть читаемым человеком и пригодным для Git diff/review. | MUST |
| MDMS-NF-002 | Метамодель и экземпляры моделей должны валидироваться автоматически в CI/CD. | MUST |
| MDMS-NF-003 | Из канонической схемы должны генерироваться JSON Schema, RDF/OWL, SHACL и документация. | MUST |
| MDMS-NF-004 | Разрешение внешних ссылок и контроль существования записей мастер-систем должны выполняться отдельно от базовой структурной валидации. | MUST |
| MDMS-NF-005 | Генерация производных артефактов должна быть воспроизводимой для одной ревизии. | MUST |
| MDMS-NF-006 | Breaking-change analyzer должен обнаруживать удаление элементов, сужение типа или кардинальности, усиление обязательности, изменение ключа, классификации и mapping. | SHOULD |
| MDMS-NF-007 | Исторические активные версии модели, binding и контракта должны быть доступны для аудита. | SHOULD |

## Почему LinkML

LinkML — самоописываемый язык схем: каждая LinkML-схема является экземпляром `SchemaDefinition` из собственной метамодели LinkML. Схема содержит определения классов, слотов, типов, enum и imports, поэтому MOEX может определить свою метамодель как обычную валидируемую LinkML-схему.[^4][^5]

LinkML-модели обычно создаются в YAML. Классы задают шаблоны объектов, slots являются переиспользуемыми полями и связями, а схема по умолчанию закрыта: поле, не разрешённое классом, считается ошибкой.[^6]

### Используемые механизмы

| Механизм LinkML | Применение в MDMS |
|---|---|
| `classes` | Сущности метамодели: `LogicalEntity`, `Mapping`, `DataFlow` и другие |
| `slots` | Атрибуты и типизированные связи между сущностями |
| `identifier: true` | Стабильный первичный идентификатор экземпляра класса |
| `range` | Примитив, enum или ссылка на экземпляр другого класса |
| `required`, `multivalued`, cardinality | Обязательность и кардинальность |
| `is_a` | Основная иерархия наследования |
| `mixins` | Lifecycle, ownership, classification и provenance без предметного наследования |
| `imports` | Разделение MDMS на модули и повторное использование |
| `inlined: false` | Представление связи как внешней ссылки по identifier |
| `inlined: true` | Встраивание составных частей артефакта по значению |
| `enums` | Контролируемые значения v0.1 |
| URI/CURIE | Глобальные идентификаторы и семантическая проекция |

Слот с `identifier: true` обязателен, уникально идентифицирует объект и позволяет ссылаться на него вместо встраивания. При `inlined: false` JSON-представление содержит identifier связанного объекта, а не его полную копию.[^7][^8][^9]

Imports могут задаваться CURIE или относительными путями; генераторы умеют рекурсивно объединять импортируемые определения в единый артефакт. Это позволяет хранить core, governance, registries, integration и contract binding раздельно, но выпускать консолидированную схему.[^10]

### Генерируемые представления

LinkML предоставляет генераторы JSON Schema, ProtoBuf, GraphQL, RDF, OWL, ShEx, SHACL, SQL DDL, документации и программных моделей. `gen-project` может регулярно пересобирать полный комплект downstream-артефактов после изменения схемы.[^11][^12]

В MDMS v0.1 генерация используется так:

- JSON Schema — структурная валидация YAML/JSON-экземпляров;
- SHACL — валидация RDF-проекции и графовых ограничений;
- OWL/RDF — публикация классов, свойств и связей в граф знаний;
- Mermaid/Markdown — документация и обозримые диаграммы;
- Python/Pydantic или Java — будущая интеграция с `dmr engine`.

OWL и LinkML не следует считать одним и тем же: OWL предназначен прежде всего для онтологий, LinkML — для схем данных. LinkML-классы и slots могут проецироваться в OWL classes и properties, но полная OWL-семантика не должна предполагаться автоматически.[^13]

### Ограничения выбора

LinkML не задаёт готовую корпоративную семантику MOEX, поэтому MDMS является собственным управляемым профилем. Качество и выразительность разных генераторов неодинаковы; гарантировать универсальный lossless round-trip между YAML, OWL, SHACL, OpenAPI и SQL нельзя.

Базовая LinkML-валидация проверяет структуру, типы и кардинальности, но не обязана разрешать ссылки в EAM, Clinkr или каталоге. Проверка ссылочной целостности возможна дополнительным runtime/store-механизмом, однако для MOEX она должна быть централизована в reference resolver `dmr engine`, который учитывает мастер-систему и ревизию справочника.[^14]

# Часть 2. Архитектура

## Архитектурные слои

```mermaid
flowchart TB
  EAM[EAM: системы, решения, IT-платформы] --> REG[Ссылочные проекции справочников]
  GL[Бизнес-глоссарий] --> REG
  POL[Роли, политики, классификаторы] --> REG

  C[Концептуальный уровень] --> L[Логический уровень по доменным контекстам]
  L --> P[Физический уровень: кванты данных]
  REG --> C
  REG --> L
  REG --> P
  M[Mapping] --> C
  M --> L
  M --> P

  CL[Clinkr: master интеграций] --> F[DataFlow projection]
  P --> F
  L --> F
  F --> B[DataModelBinding / ModelSelection]
  DC[Дата-каталог: master контрактов] --> B

  C --> KG[RDF/OWL Knowledge Graph]
  L --> KG
  M --> KG
  P --> JS[JSON Schema / SHACL / docs]
```

Архитектура разделяет source-of-truth по функциональным областям. EAM управляет системами, решениями и платформами; Clinkr — техническим описанием интеграций; дата-каталог — дата-контрактами; репозиторий моделей — семантикой, классификацией и mappings. После создания контракта каталог может обогащать интеграционную спецификацию модельными метаданными и возвращать её в Clinkr, но при конфликте приоритет имеет master соответствующего типа данных.[^2]

## Пакет модели решения

Один `ModelPackage` — версионируемый артефакт одной модели. Для модели конкретного решения `solution_ref` обязателен и указывает на `ITSolution` из EAM. Пакет включает собственные доменные контексты, логические сущности, физические объекты и mappings; корпоративные концептуальные сущности могут подключаться импортом или стабильной ссылкой.

Рекомендуемая структура репозитория:

```text
models/
  corporate/
    conceptual-model.yaml
  solutions/
    trading/
      model.yaml
    clearing/
      model.yaml
    client-platform/
      model.yaml
mdms/
  moex-types.yaml
  moex-registries.yaml
  moex-governance.yaml
  moex-core.yaml
  moex-integration.yaml
  moex-contract-binding.yaml
  moex-analytics.yaml
  moex-mdms.yaml
```

## Концептуальный блок

### `ConceptualEntity`

Корпоративное бизнес-понятие верхнего уровня: «Клиент», «Счёт», «Сделка», «Финансовый инструмент». Оно не привязано к таблице, API или одному решению. Содержит стабильный ID, имя, определение, ссылки на глоссарий, владельца, ключевые концептуальные атрибуты и отношение специализации к другому понятию.

### `DomainContext`

Ограниченный контекст логической модели со своей терминологией и областью ответственности. Связывает логические сущности с бизнес-доменом, ИТ-решением, namespace и релевантными бизнес-процессами. Это граница, внутри которой имена и правила интерпретации должны быть однозначны.

## Логический блок

### `LogicalEntity`

Представление бизнес-сущности внутри конкретного доменного контекста и модели решения. Может ссылаться на одну или несколько концептуальных сущностей, определяет роль решения (`producer`, `consumer`, `intermediary`), ключевые атрибуты, инварианты, класс данных и governance-метаданные.

### `LogicalAttribute`

Атомарное логическое свойство сущности. Содержит бизнес-определение, логический тип, обязательность, множественность, cardinality, value set, формат, default/derived expression, ссылки на глоссарий, политики и классификацию.

### `Relationship`

Именованная связь между сущностями с ролями концов, кардинальностями и признаками identifying/associative. Она описывает предметное отношение, например «Счёт принадлежит Клиенту», и не должна использоваться вместо интеграционного потока.

## Физический блок

### `PhysicalObject`

Управляемый квант данных или точка интеграции: БД, схема, таблица, view, API, endpoint, payload, topic, queue, message, file, dataset или pipeline. Содержит ссылки на решение и систему, вид объекта, qualified name, технологию, authoritative native schema и направление использования.

Стандарт дата-контрактов требует на физическом уровне описывать базы, таблицы, API, очереди, сообщения, файлы, ETL/ELT и технические идентификаторы, а выбранный в контракте физический объект должен быть связан с соответствующей OpenAPI/AsyncAPI или иной нативной схемой.[^2]

### `PhysicalField`

Поле физического объекта: column, JSON property, message field, параметр API и т. п. Хранит native name/type и schema path. Бизнес-семантика не дублируется в поле, а задаётся Mapping к `LogicalAttribute`.

## Mapping-блок

### `Mapping`

Универсальное соответствие одного или нескольких source-elements одному или нескольким target-elements. Основные типы: semantic equivalence, specialization, implementation, field mapping, transformation, aggregation и derivation.

Минимальные обязательные данные: `source_refs`, `target_refs`, `mapping_type`, `mapping_cardinality`, stable ID и lifecycle. Для утверждённых mappings должны поддерживаться evidence, approval, confidence, transformation и temporal validity.

## Справочники

### `RegistryEntry`

Абстрактная локальная проекция записи внешнего справочника. Она содержит ID мастер-системы, отображаемое имя, master system, source URI и lifecycle status. Полное наполнение справочника не включается в каждую модель решения.

### EAM-сущности

| Сущность | Назначение | Master |
|---|---|---|
| `ITSystem` | Отдельная ИТ-система | EAM |
| `ITSolution` | ИТ-решение как набор систем | EAM |
| `ITPlatform` | ИТ-платформа | EAM |
| `BusinessDomain` | Домен/предметная область | Требует нормативного закрепления; в прототипе допускается EAM |

Поправка `ITPlatform`, а не обобщённое `Platform`, закреплена в v0.1, чтобы не смешивать ИТ-платформу с торговой, продуктовой или бизнес-платформой.

### Прочие ссылки

| Сущность | Master/назначение |
|---|---|
| `GlossaryTerm` | Корпоративный бизнес-глоссарий |
| `Role` | Реестр управляемых ролей |
| `OrganizationUnit` | Организационная структура |
| `DataClassificationTerm` | Категории ПДн, инсайдерской информации, тайн и иных ограничений |
| `Policy` | Политики доступа, хранения, качества и архитектурные инварианты |
| `BusinessProcess` | BPMN-репозиторий |
| `IntegrationReference` | Интеграция в Clinkr |
| `DataContractReference` | Контракт в дата-каталоге |

Внешняя ссылка задаётся как слот с `range` на соответствующий registry-class и `inlined: false`. Это структурно означает ссылку по identifier; фактическое существование записи проверяет `dmr engine` по API или снапшоту мастер-системы.

## Классификация

В v0.1 разделены четыре ортогональные характеристики, которые нельзя смешивать в одном enum:

| Атрибут | Уровень | Значения/тип | Смысл |
|---|---|---|---|
| `entity_type` | `LogicalEntity` | `core`, `derived`, `reference` | Роль сущности внутри модели решения |
| `data_class` | `LogicalEntity` | `reference_data`, `master_data`, `transactional_data`, `analytical_data`, `metadata` | Корпоративный класс самих данных |
| `business_importance` | `LogicalEntity` | `high`, `medium`, `low` | Бизнес-критичность сущности |
| `data_owner_ref` | Entity/package/object | Ссылка на `Role` | Ответственный владелец, не свободная строка |
| `governance_classification` | Entity и attribute | `public`, `internal`, `confidential`, `restricted` | Базовый уровень ограничения доступа |
| `sensitivity_term_refs` | Entity и attribute | Ссылки на классификатор | ПДн, инсайдерская информация, коммерческая/банковская тайна и другие категории |

`governance_classification` задаётся на сущности как default и может быть усилена на атрибуте. Эффективная классификация атрибута не должна быть слабее классификации сущности; это межобъектное правило реализует `dmr engine` или SHACL, а не простой enum.

`entity_type=reference` не эквивалентен `data_class=reference_data`: первое характеризует роль объекта в локальной модели, второе — нормативный класс данных, наследуемый дата-контрактом. Например, локальная read-only проекция мастер-данных клиента может иметь `entity_type=reference`, но `data_class=master_data`.

Для аудита и временной истории предусмотрена самостоятельная `ClassificationAssignment`, которая связывает произвольный элемент с термином классификации, основанием, источником, периодом действия и статусом утверждения. Inline-поля в entity/attribute служат удобным текущим представлением; assignments — нормализованной governance-историей.

## Governance-блок

### Mixins

- `HasLifecycle` — status, valid from/to, replacement reference;
- `HasOwnership` — data owner, data steward, owning unit;
- `HasBusinessClassification` — entity type, data class, importance;
- `HasGovernanceClassification` — access level, special classification terms, source and rationale;
- `HasPolicyBindings` — ссылки на применимые политики;
- `HasProvenance` — source artifact, evidence, approval and approver.

### Самостоятельные сущности

`PolicyBinding` связывает политику с произвольным элементом модели и хранит период действия и approval. `ClassificationAssignment` обеспечивает нормализованную историю классификации и не ограничивается текущим значением в объекте.

## Интеграционный блок

### `DataFlow`

`DataFlow` не является второй карточкой интеграции. Это ссылочная проекция Clinkr, необходимая для соединения топологии интеграции с семантикой модели. Источником участников, систем, платформ, уровня, класса, канала и integration specification является Clinkr; MDMS добавляет ссылки на модели, логические сущности, атрибуты и физические объекты.

Стандарт MOEX устанавливает, что новая кросс-системная интеграция сначала регистрируется в Clinkr, затем её справочник загружается в каталог и для неё создаётся дата-контракт. Clinkr остаётся master технического описания интеграций.[^2]

### `DataFlowEntityBinding`

Связывает поток с:

- конкретной ревизией модели источника;
- логической сущностью;
- набором передаваемых логических атрибутов;
- физическими объектами и полями;
- mappings преобразования;
- направлением.

Так поток «Клиент A → B → C» можно представить двумя объектами `DataFlow`, полученными из двух интеграций Clinkr, но оба binding могут ссылаться на одну корпоративную сущность и согласованные logical mappings.

## Контрактный блок

### `DataModelBinding`

Машиночитаемая дочерняя модельная спецификация дата-контракта. Она фиксирует:

- версию стандарта MDMS;
- версию реализации спецификации;
- contract/integration references;
- URI и semver модели решения;
- immutable revision;
- один или несколько `ModelSelection`;
- compatibility mode и baseline;
- SHA-256 digest;
- время формирования и lifecycle.

### `ModelSelection`

Переиспользуемый срез полной модели. `SelectedEntity` выбирает logical entity и физические объекты, а `SelectedAttribute` связывает логический атрибут с конкретными physical fields и transformation mapping.

Контракт содержит selection, а не полную копию модели; OpenAPI/AsyncAPI/Avro остаётся wire-schema. Это предотвращает появление трёх независимо редактируемых описаний одной структуры.

## Аналитический блок

`Metric` и `Dimension` включены в отдельный `moex-analytics` профиль. Метрика содержит expression, aggregation, grain, dimensions, measures, unit и filter и всегда ссылается на элементы логической модели. Этот блок не обязателен для базовой модели ИТ-решения и может развиваться независимо с экспортом в аналитические semantic-layer форматы.

## Валидация

### Уровень 1: LinkML

Проверяет структуру, разрешённые поля, типы, enum, required, patterns и cardinality. LinkML позволяет определять identifier/key и составные unique keys, однако область их уникальности зависит от контейнера и способа исполнения.[^15]

### Уровень 2: `dmr engine`

Должен проверять:

- разрешимость URI/CURIE и отсутствие dangling references;
- существование ITSystem/ITSolution/ITPlatform в нужной ревизии EAM;
- существование Integration в Clinkr и DataContract в каталоге;
- принадлежность систем решению и решения платформе;
- обязательные mappings для опубликованных физических объектов;
- соответствие полей native schema и physical projection;
- наследование и запрет ослабления classification;
- совместимость model/binding/contract versions;
- digest и immutable revision;
- breaking changes и physical drift.

### Уровень 3: Reality check

Сравнивает утверждённую модель с фактической БД, registry schema, OpenAPI, AsyncAPI, Avro или иным runtime-источником. Результат нормализуется как `PASS`, `WARN`, `FAIL` или `NOT_APPLICABLE` с rule ID, element path, expected/actual и evidence.

# Часть 3. Спецификации

## Модульный состав

| Файл | Назначение |
|---|---|
| `moex-types.yaml` | Пользовательские типы и controlled enums |
| `moex-registries.yaml` | Ссылочные проекции EAM, glossary, roles, policies, Clinkr и catalog |
| `moex-governance.yaml` | Lifecycle, ownership, classification, policy и provenance |
| `moex-core.yaml` | Conceptual, logical, physical model и Mapping |
| `moex-integration.yaml` | DataFlow и DataFlowEntityBinding |
| `moex-contract-binding.yaml` | DataModelBinding и ModelSelection |
| `moex-analytics.yaml` | Metric и Dimension |
| `moex-mdms.yaml` | Корневая агрегирующая схема |

Все модули импортируют `linkml:types` и необходимые нижележащие модули. Корневая схема предоставляет `MOEXModelRepository` как технический контейнер для интеграционных тестов; отдельный артефакт модели решения валидируется непосредственно как `ModelPackage`.

## Ключевые enum

```yaml
enums:
  EntityTypeEnum:
    permissible_values:
      core:
      derived:
      reference:

  DataClassEnum:
    permissible_values:
      reference_data:
      master_data:
      transactional_data:
      analytical_data:
      metadata:

  BusinessImportanceEnum:
    permissible_values:
      high:
      medium:
      low:

  GovernanceClassificationEnum:
    permissible_values:
      public:
      internal:
      confidential:
      restricted:
```

Enums v0.1 являются bootstrap-механизмом. После появления корпоративных versioned vocabulary services значения, требующие частого изменения, следует перевести в `DataClassificationTerm`/value-set references, сохранив небольшой стабильный enum только для базовых архитектурных шкал.

## Внешний справочник

```yaml
classes:
  RegistryEntry:
    abstract: true
    slots:
      - registry_id
      - registry_name
      - master_system
      - source_uri
      - registry_status

  ITPlatform:
    is_a: RegistryEntry
    description: ИТ-платформа; мастер данных — EAM.

slots:
  registry_id:
    identifier: true
    range: uriorcurie
    required: true

  platform_ref:
    range: ITPlatform
    inlined: false
```

`range: ITPlatform` типизирует ссылку, а `inlined: false` заставляет использовать identifier вместо копии записи. Проверка того, что identifier существует в EAM, относится к reference-resolution этапу.

## Ядро модели

```yaml
classes:
  ModelPackage:
    is_a: ModelElement
    mixins:
      - HasOwnership
    slots:
      - api_version
      - model_version
      - solution_ref
      - domain_contexts
      - logical_entities
      - physical_objects
      - mappings

  LogicalEntity:
    is_a: ModelElement
    mixins:
      - HasOwnership
      - HasBusinessClassification
      - HasGovernanceClassification
      - HasPolicyBindings
    slots:
      - context_ref
      - conceptual_entity_refs
      - solution_ref
      - solution_data_role
      - attributes
      - key_attribute_refs

  PhysicalObject:
    is_a: ModelElement
    slots:
      - solution_ref
      - system_ref
      - object_kind
      - qualified_name
      - native_schema_ref
      - direction
      - physical_fields
```

## Классификация

```yaml
classes:
  HasBusinessClassification:
    mixin: true
    slots:
      - entity_type
      - data_class
      - business_importance

  HasGovernanceClassification:
    mixin: true
    slots:
      - governance_classification
      - sensitivity_term_refs
      - classification_source
      - classification_rationale

slots:
  data_owner_ref:
    range: Role
    inlined: false

  sensitivity_term_refs:
    range: DataClassificationTerm
    multivalued: true
    inlined: false
```

## Поток Clinkr

```yaml
classes:
  DataFlow:
    is_a: ModelElement
    slots:
      - integration_ref
      - contract_ref
      - source_solution_ref
      - target_solution_ref
      - source_system_ref
      - target_system_ref
      - source_platform_ref
      - target_platform_ref
      - integration_level
      - integration_class
      - integration_channel
      - integration_spec_ref
      - entity_bindings

  DataFlowEntityBinding:
    is_a: ModelElement
    slots:
      - flow_ref
      - source_model_ref
      - logical_entity_ref
      - logical_attribute_refs
      - physical_object_refs
      - physical_field_refs
      - transformation_mapping_refs
```

## Контрактный selection

```yaml
classes:
  DataModelBinding:
    is_a: ModelElement
    slots:
      - specification_version
      - implementation_version
      - contract_ref
      - integration_ref
      - model_package_ref
      - model_version
      - model_revision
      - selections
      - compatibility_mode
      - compatibility_baseline_ref
      - integrity_digest

  ModelSelection:
    is_a: ModelElement
    slots:
      - selected_entities
```

## Пример модели решения

```yaml
element_id: mdms:model/trading/1.0.0
name: trading_solution_model
description: Модель данных торгового решения.
lifecycle_status: draft
api_version: mdms.moex/v0.1
model_version: 1.0.0
solution_ref: eam:solution/TRADING

logical_entities:
  - element_id: mdms:logical/trading/Client
    name: TradingClient
    description: Локальное представление клиента.
    lifecycle_status: active
    context_ref: mdms:context/trading
    conceptual_entity_refs:
      - mdms:concept/Client
    solution_ref: eam:solution/TRADING
    solution_data_role: producer
    entity_type: core
    data_class: master_data
    business_importance: high
    data_owner_ref: org:role/CLIENT_DATA_OWNER
    governance_classification: confidential
    sensitivity_term_refs:
      - catalog:classification/PDN
```

## Проверенный результат

Прототип успешно проходит следующие проверки:

- загрузка всех восьми LinkML schema modules;
- генерация общей JSON Schema;
- генерация SHACL и OWL-проекций;
- LinkML-валидация примера `ModelPackage` без ошибок;
- LinkML-валидация примера `DataFlow` без ошибок;
- LinkML-валидация примера `DataModelBinding` без ошибок.

Генераторы LinkML предназначены именно для преобразования схемы в другие schema frameworks и документационные артефакты, а SHACL generator создаёт node shapes и property constraints из LinkML classes/slots.[^16][^11]

## Решения v0.1

Зафиксированы следующие проектные решения:

1. LinkML YAML — канонический authoring format.
2. MDMS — собственный корпоративный профиль поверх LinkML.
3. Модель конкретного решения упаковывается в `ModelPackage` и ссылается на `ITSolution`.
4. Корпоративные понятия отделены от локальных logical entities.
5. Физические native schemas не копируются в MDMS.
6. `ITPlatform` является EAM-ссылкой.
7. Потоки являются read-only projections интеграций Clinkr с semantic bindings.
8. Data contract получает `DataModelBinding`, а не полную модель.
9. `entity_type`, `data_class`, `business_importance` и `governance_classification` разделены.
10. `data_owner_ref` является ссылкой на управляемую роль.
11. Специальные категории чувствительности множественны и задаются ссылками на `DataClassificationTerm`.
12. Mapping, ClassificationAssignment и PolicyBinding являются объектами первого класса.

## Вопросы к v0.2

Перед нормативным утверждением необходимо принять решения:

- является ли master концептуальной модели единый ModelHub или enterprise modeling tool;
- кому нормативно принадлежит `BusinessDomain` и какова его master-система;
- принадлежит ли `DomainContext` только модели решения или может быть общим для нескольких решений;
- какие сущности EAM образуют точную иерархию `ITPlatform → ITSolution → ITSystem` и допускаются ли связи many-to-many;
- является ли `core|derived|reference` финальной шкалой `entity_type`;
- какой корпоративный классификатор заменяет bootstrap `DataClassEnum` и как он соотносится с НСИ, master и transactional data;
- должна ли базовая governance classification вычисляться из специальных категорий или утверждаться отдельно;
- на каком уровне действует data owner: concept, logical entity, attribute, model package или одновременно на нескольких уровнях с наследованием;
- нужна ли обязательная историческая воспроизводимость EAM/Clinkr/catalog references по состоянию на дату;
- какая сторона materializes `DataFlow`: ModelHub, дата-каталог или graph integration service;
- какой compatibility baseline обязателен: предыдущая версия binding или все активные consumer versions;
- какие LinkML-конструкции объявляются разрешённым MOEX conformance subset.

## Следующий пилот

Для v0.2 целесообразно реализовать сквозной кейс «Клиент — Счёт — Сделка — Финансовый инструмент» для двух решений и двух интеграций:

1. Утвердить 4–6 corporate conceptual entities.
2. Описать два domain contexts и локальные logical entities.
3. Подключить реальные EAM IDs систем, решений и IT-платформ.
4. Импортировать одну реальную AsyncAPI/OpenAPI и один объект БД как physical projections.
5. Создать mappings field-to-attribute.
6. Загрузить две реальные интеграции Clinkr как `DataFlow`.
7. Сформировать два `DataModelBinding` для контрактов.
8. Проверить classification inheritance и запрет ослабления.
9. Выполнить breaking-change test между двумя версиями модели.
10. Опубликовать RDF/SHACL-проекцию в тестовом knowledge graph.

---

## References

1. [3- MOEX Data Architecture - implementation concepts.docx](3- MOEX Data Architecture - implementation concepts.docx)

2. [MOEX-Data-Contracts-v2_2.docx](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100349047/12086fe1-2d4f-4fb8-a6df-9749a97a6197/MOEX-Data-Contracts-v2_2.docx?AWSAccessKeyId=ASIA2F3EMEYE23TCN32H&Signature=Z%2Btsl2TVu5ZxS9CV9FOn7JPPsv0%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEFIaCXVzLWVhc3QtMSJIMEYCIQC4Ii7rUa0ptLBI80UqhJLIv3JswgQgRuBhknGHxzi3gAIhALPElqBlXJXFduISiPLZ2iM9tuc1nE1y%2Bso0%2BQ7qJsiIKvMECBoQARoMNjk5NzUzMzA5NzA1IgzhLV62A9Ycal65uBIq0ATl8eQMunPi7Gw0eefYNzisPQqEF57w52WJ%2BhlI9l5eT1qb%2FDJakIII9egCx4av8nAhLr6H58JjLVUb6mW13i8YtjBc3ZQ5uZetbWGPXKz4qE1R1dyZ83f2JlXF9rngSn9Dq89u7i2DF5d4uXsWoaLaXLAVCFzSmZoCpR1VdCsqwsDM6ciOaOMNMyNFP8B7EdPRx6NnjaERU4YtjGwTCPYNOvGr2pT7DF%2BF7TJv0d2rXA%2FUo66A1yQ9WAojgbfVdfJ%2Fox8SEZbAxKSbiFGNa3ZlO3%2Butc%2FiXvMMNRSDlJHemU4xpbAYXKtRga35B6GO7%2BGWkqRIknGbyvIuASrwM%2BAh9qdrx%2FBrtkB89oAXiUybFEA6ZT7eC7y81nD0w80J5EIOr11RqGEwIwBvpbu8CvQc9HMmLyjYzbq0Qn%2B%2Fd0DkhzzJpPO9bIr%2FBALugDfLfcepmrdnqVZSZlDEjKGMzffRL7OLsqI414DSy1L0VB1A4CDlxUq1eGot3NMnFoh8jiXvDiCqpVECkmjxZRYP1QVV5YafEjY8ENR7MYgVJciMnlC1GauRbAEuV4CNhHTKvJYt%2FwbHO%2F8Cn0TvnNkqMLj9cZUiCIgUlIIubBFHFV5G1dldBT6xmT2rKlkCtvWBEIU2v39cdwvidX57qiHIsXPLvyHPUs1xVEC3WFPCECwkAC7Sa6cMBfdgHMcSXb8My1Lk%2B%2FF%2B9p9SNJsxDOuuk2kZrrn2qKDoRDNk3ge9g4t0xaw865SJ575J7IeSySgc6RJ6LS57Wh2VM68o2DJruUkYMM%2Bhq9UGOpcBT87z%2Bo%2BFidAprJ1B58swyVInhk7z2Z3eWnlPNgs%2FQ9yLW7re1HfYNg%2F0M6hG7%2FXqaYZX8nvo4BZ427nZDx7yz%2FebqfX%2B%2B%2Fw8EBZYk5Wfg3QKVy1FkJ8Z9W%2Fs2Aofwi2i6ylZmnnbYF6bLDQag4rMJgVtrFkktQB3nO%2BOGnDBa6fwg8ocK5BuJ45rpL7hURhN160qZ89Q%2Bg%3D%3D&Expires=1789583010) - **MOEX DATA CONTRACTS**

Описание стандарта спецификации корпоративных дата-контрактов

v.2.2

Докум...

3. [Vybor-spetsifikatsii-modeli-dannykh-dlia-MOEX.md](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100349047/97d99090-639d-43ee-96b2-7be370fc9d02/Vybor-spetsifikatsii-modeli-dannykh-dlia-MOEX.md?AWSAccessKeyId=ASIA2F3EMEYE23TCN32H&Signature=OZII5LKq9UB8btjEr1%2BtdsPPshg%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEFIaCXVzLWVhc3QtMSJIMEYCIQC4Ii7rUa0ptLBI80UqhJLIv3JswgQgRuBhknGHxzi3gAIhALPElqBlXJXFduISiPLZ2iM9tuc1nE1y%2Bso0%2BQ7qJsiIKvMECBoQARoMNjk5NzUzMzA5NzA1IgzhLV62A9Ycal65uBIq0ATl8eQMunPi7Gw0eefYNzisPQqEF57w52WJ%2BhlI9l5eT1qb%2FDJakIII9egCx4av8nAhLr6H58JjLVUb6mW13i8YtjBc3ZQ5uZetbWGPXKz4qE1R1dyZ83f2JlXF9rngSn9Dq89u7i2DF5d4uXsWoaLaXLAVCFzSmZoCpR1VdCsqwsDM6ciOaOMNMyNFP8B7EdPRx6NnjaERU4YtjGwTCPYNOvGr2pT7DF%2BF7TJv0d2rXA%2FUo66A1yQ9WAojgbfVdfJ%2Fox8SEZbAxKSbiFGNa3ZlO3%2Butc%2FiXvMMNRSDlJHemU4xpbAYXKtRga35B6GO7%2BGWkqRIknGbyvIuASrwM%2BAh9qdrx%2FBrtkB89oAXiUybFEA6ZT7eC7y81nD0w80J5EIOr11RqGEwIwBvpbu8CvQc9HMmLyjYzbq0Qn%2B%2Fd0DkhzzJpPO9bIr%2FBALugDfLfcepmrdnqVZSZlDEjKGMzffRL7OLsqI414DSy1L0VB1A4CDlxUq1eGot3NMnFoh8jiXvDiCqpVECkmjxZRYP1QVV5YafEjY8ENR7MYgVJciMnlC1GauRbAEuV4CNhHTKvJYt%2FwbHO%2F8Cn0TvnNkqMLj9cZUiCIgUlIIubBFHFV5G1dldBT6xmT2rKlkCtvWBEIU2v39cdwvidX57qiHIsXPLvyHPUs1xVEC3WFPCECwkAC7Sa6cMBfdgHMcSXb8My1Lk%2B%2FF%2B9p9SNJsxDOuuk2kZrrn2qKDoRDNk3ge9g4t0xaw865SJ575J7IeSySgc6RJ6LS57Wh2VM68o2DJruUkYMM%2Bhq9UGOpcBT87z%2Bo%2BFidAprJ1B58swyVInhk7z2Z3eWnlPNgs%2FQ9yLW7re1HfYNg%2F0M6hG7%2FXqaYZX8nvo4BZ427nZDx7yz%2FebqfX%2B%2B%2Fw8EBZYk5Wfg3QKVy1FkJ8Z9W%2Fs2Aofwi2i6ylZmnnbYF6bLDQag4rMJgVtrFkktQB3nO%2BOGnDBa6fwg8ocK5BuJ45rpL7hURhN160qZ89Q%2Bg%3D%3D&Expires=1789583010) - # Выбор спецификации модели данных для MOEX
## Решение
Для MOEX не стоит выбирать один внешний форма...

4. [Schema Datamodel - LinkML Model](https://linkml.io/linkml-model/latest/docs/specification/03schemas/)

5. [Metamodel Index - LinkML Model](https://linkml.io/linkml-model/latest/docs/)

6. [Models - linkml documentation](https://linkml.io/linkml/schemas/models.html)

7. [Slots - linkml documentation](https://linkml.io/linkml/schemas/slots.html)

8. [View this page - LinkML](https://linkml.io/linkml/_sources/schemas/inlining.md.txt)

9. [Slot: inlined - LinkML Model](https://linkml.io/linkml-model/latest/docs/inlined/)

10. [Imports - linkml documentation](https://linkml.io/linkml/schemas/imports.html)

11. [Generators - linkml documentation](https://linkml.io/linkml/generators/index.html) - A LinkML generator is code that transforms a linkml schema into a datamodel expressed using another ...

12. [Part 8: Generating Projects - linkml documentation](https://linkml.io/linkml/intro/tutorial08.html)

13. [OWL - linkml documentation](https://linkml.io/linkml/generators/owl.html) - Web Ontology Language OWL is a modeling language used to author ontologies. OWL is used for building...

14. [How to Check Referential Integrity - linkml-store documentation](https://linkml.io/linkml-store/how-to/Check-Referential-Integrity.html) - ... Inserting invalid data; Command Line Example using DuckDB. Load data into DuckDB; Check Referent...

15. [Adding constraints and rules - linkml documentation](https://linkml.io/linkml/schemas/constraints.html) - Unique keys are inherited: if a class defines a unique key, the unique key's constraints automatical...

16. [SHACL - linkml documentation](https://linkml.io/linkml/generators/shacl.html) - Generate SHACL (Shapes Constraint Language) shapes from a LinkML schema. SHACL shapes are used to va...

