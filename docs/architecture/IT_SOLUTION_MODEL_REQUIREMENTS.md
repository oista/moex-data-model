

Связанные документы:

- `docs/adr/ADR-013-specification-requirements-catalog.md`
- `model-assets/specifications/moex-dams/0.1/requirements/it-solution-requirements.yaml`
- `model-assets/specifications/moex-dams/0.1/schemas/moex-requirements.yaml`
- `model-assets/specifications/moex-dams/0.1/publication-requirements.yaml`

# Требования к модели данных ИТ-решения

## Статус и назначение

Этот документ описывает архитектуру машиночитаемых требований к модели данных ИТ-решения в MOEX DAMS.

Требования определяют минимально необходимое содержимое модели данных решения и используются для автоматизированной оценки полноты и связности модели перед публикацией. Они применяются к DAMS-модели данных уровня `solution`, то есть к модели конкретного ИТ-решения, в которой совместно описаны логические и физические представления данных.

Документ отвечает на вопросы:

- что является требованием к модели данных ИТ-решения;
- как требования представлены в репозитории;
- какие классы требований существуют;
- какие требования исполняются автоматически;
- как устроен assess-gate;
- чем body assess отличается от publication contract;
- что считается допустимым исключением;
- какие правила обязательны в Wave 1;
- какие требования сознательно перенесены в Wave 2 и последующие волны.

Документ не описывает пользовательский интерфейс Publication Viewer. Viewer является одним из способов публикации результатов оценки, но не является источником требований и не определяет их семантику.

---

## 1. Контекст

### 1.1. Модель ИТ-решения

Модель данных ИТ-решения описывает данные, которыми конкретное ИТ-решение владеет, которые создаёт, изменяет, хранит, предоставляет или потребляет в пределах своей функциональной границы.

Пакет модели решения объединяет:

```text
Логическое представление
  ├── LogicalEntity
  ├── LogicalAttribute
  ├── Relationship
  ├── правила идентичности
  └── связи с корпоративными понятиями

Физическое представление
  ├── PhysicalObject
  ├── PhysicalField
  ├── native schemas / formats
  ├── ИТ-системы и технологии
  └── API, files, topics, datasets, tables, views

Трассируемость
  ├── logical ↔ physical mappings
  ├── solution logical → enterprise conceptual realizations
  ├── ownership / stewardship
  ├── classification
  └── lifecycle / provenance
```

Логическая и физическая модели одного решения не являются независимыми implementation packages. Это разные facets и представления единой модели данных ИТ-решения.

### 1.2. Граница пакета

Каждый DAMS solution model package:

- ссылается на одно ИТ-решение из EAM;
- охватывает совокупность ИТ-систем в составе этого решения;
- содержит логический и/или физический слой модели;
- должен быть непустым;
- содержит связи между смыслом данных и его физической реализацией;
- может включать API, event, file и database representations;
- может быть создан вручную либо как draft-результат Data Specification Player.

Физический объект всегда относится к конкретной ИТ-системе. Пакет модели относится к ИТ-решению.

```text
ИТ-решение
  ├── ИТ-система A
  │     ├── Database
  │     │     ├── Table
  │     │     └── View
  │     └── API
  │
  └── ИТ-система B
        ├── Topic
        ├── Event schema
        └── File / dataset

Solution model package
  ├── Logical entities
  ├── Physical objects
  ├── Mappings
  └── Governance metadata
```

---

## 2. Два независимых gate

Перед публикацией модели действуют два независимых контура контроля.

```text
Pre-publish gate
  ├── Schema validation
  ├── Body assess
  └── Publication contract validation
```

Успешная публикация требует прохождения всех применимых контуров:

\[
PublishAllowed =
SchemaValid
\land
BodyAssessPassed
\land
PublicationContractSatisfied
\]

### 2.1. Schema validation

Schema validation проверяет, что YAML/JSON/LinkML-артефакт соответствует метамодели:

- допустимы ли классы, slots и enum values;
- соблюдены ли базовые cardinality;
- корректны ли типы значений;
- существуют ли обязательные структурные поля;
- соответствует ли requirements catalog собственной requirements schema.

Schema validation не доказывает, что модель данных содержательно полна.

### 2.2. Body assess

Body assess проверяет содержательную минимальную полноту и связность модели.

Он отвечает на вопросы:

```text
- Есть ли у пакета связь с ИТ-решением?
- Не пуст ли пакет?
- Есть ли у сущности определение, тип, классификация и идентичность?
- Есть ли у атрибута logical type и parent entity?
- Связана ли нетехническая сущность с моделью по смыслу?
- Соотнесена ли логическая сущность с корпоративным понятием
  или имеет обоснованное исключение?
- Имеет ли physical object logical meaning или technical-only rationale?
- Есть ли mapping между physical field и logical attribute,
  либо формально объяснённое отсутствие?
```

Body assess использует машиночитаемый каталог требований и набор исполнимых formal checks.

### 2.3. Publication contract

Publication contract проверяет, что модель опубликована с обязательными представлениями:

- существуют ли требуемые publication sections;
- покрыты ли inherited publication requirements через `satisfies`;
- присутствуют ли требуемые semantic types;
- доступны ли source artifacts;
- сформирован ли conformance result.

Publication contract не проверяет смысловое содержание slots:

```text
Publication contract не проверяет:
  - identity_rule;
  - business_key_kind;
  - governance_classification;
  - ownership;
  - mapping_coverage_status;
  - cardinality;
  - корректность logical ↔ physical mappings.
```

Эти проверки принадлежат body assess.

---

## 3. Машиночитаемый каталог

### 3.1. Расположение

Основной каталог требований к модели ИТ-решения хранится в:

```text
model-assets/specifications/moex-dams/0.1/requirements/
  it-solution-requirements.yaml
```

Метамодель требований определяется в:

```text
model-assets/specifications/moex-dams/0.1/schemas/
  moex-requirements.yaml
```

Каталог является source of truth для исполнимого подмножества требований стандарта.

Markdown, ADR и архитектурные документы объясняют нормы и решения, но не заменяют requirements catalog в автоматизированной проверке.

### 3.2. Requirement как управляемый объект

Каждое требование представлено объектом `SpecificationRequirement`.

Минимальная структура требования:

```yaml
id: LDM-004
title: Правило идентичности
statement: >
  Для логической сущности должно быть описано, по каким деловым
  признакам два экземпляра считаются одним и тем же объектом,
  и указан характер ключа и/или состав ключевых атрибутов.
severity: error

applies_to:
  implementation_profile: dams-data-model
  dams_model_level: solution
  target_kinds:
    - LogicalEntity

formal_checks:
  - id: LDM-004.c1
    kind: slot_required
    slot: identity_rule
    diagnostic_code: DAMS-REQ-LDM-004.c1
    remediation: >
      Укажите правило бизнес-идентичности сущности.

  - id: LDM-004.c2
    kind: at_least_one_slots
    slots:
      - business_key_kind
      - key_attribute_refs
    diagnostic_code: DAMS-REQ-LDM-004.c2
    remediation: >
      Укажите характер бизнес-ключа и/или ключевые атрибуты.
```

### 3.3. Пользовательская формулировка

Поле `statement` обязательно для каждого требования.

`statement`:

- формулируется на понятном русском языке;
- выражает норму, а не алгоритм проверки;
- не содержит внутренние названия LinkML-классов, slots, Python-функций или check kinds;
- может быть показано архитектору, владельцу данных, команде решения и аудитору;
- является основным нормативным текстом requirement card и diagnostic explanation.

Например:

```text
Корректно:
  «Нетехническая логическая сущность не должна быть изолированной:
  должна быть связь с другой логической сущностью, выравнивание
  с корпоративным понятием либо письменное обоснование изоляции».

Некорректно:
  «LogicalEntity должен иметь Relationship или conceptual_entity_refs,
  иначе formal_check conditional_branch не проходит».
```

Технические детали располагаются в `formal_checks`, `applies_to`, `title`, schema descriptions и implementation code.

### 3.4. Область применимости

`applies_to` задаёт, к каким объектам относится требование.

Типовые ограничения области применимости:

```yaml
applies_to:
  implementation_profile: dams-data-model
  dams_model_level: solution
  target_kinds:
    - LogicalEntity
```

или:

```yaml
applies_to:
  target_kinds:
    - PhysicalField
```

Область применимости нужна, чтобы:

- не проверять solution requirements на enterprise conceptual model;
- не применять DAMS solution rules к FIBO application ontology;
- не применять PDM rules к LogicalEntity;
- не применять ATR rules к PhysicalObject;
- не интерпретировать каждый requirement как глобальный для всего репозитория.

---

## 4. Исполнимые проверки

### 4.1. Formal checks

`formal_checks` являются исполнимым подмножеством нормативных требований.

Не каждая норма стандарта обязана иметь автоматическую проверку. Если у требования нет formal check, это означает:

```text
Требование подлежит human review.
Отсутствие automation не означает отсутствие нормы.
```

Основные check kinds Wave 1:

| Check kind | Назначение |
|---|---|
| `slot_required` | Проверяет наличие обязательного slot |
| `slot_min_cardinality` | Проверяет минимальное число значений |
| `ref_resolves` | Проверяет, что reference указывает на существующий элемент |
| `at_least_one_slots` | Требует наличие хотя бы одного значения из набора slots |
| `conditional_branch` | Проверяет условное правило вида `when → then` |
| `key_subset` | Проверяет, что набор ключевых ссылок является подмножеством допустимого набора |
| `xor_slots` | Используется только там, где одновременное наличие значений действительно бессмысленно |

`xor_slots` не используется для ownership, conceptual alignment и mapping coverage, потому что в этих областях одновременно могут быть допустимы:

```text
local owner override + inherited effective owner (ADR-023 cascade)
conceptual reference + alignment rationale
physical field reference + transformation expression
```

Флаг formal_checks `effective: true` читает значения после containment cascade
(ADR-023), а не сырой YAML элемента.

### 4.2. Diagnostics

Каждая исполнимая проверка должна формировать стабильный diagnostic:

```text
DAMS-REQ-LDM-004.c1
```

Diagnostic должен содержать:

- стабильный `diagnostic_code`;
- subject: тип, имя и `element_id` объекта;
- краткое описание нарушения;
- ссылку на requirement code;
- краткую выдержку из `statement`;
- severity;
- remediation;
- source location, если она известна.

Пример:

```text
DAMS-REQ-LDM-004.c1
LogicalEntity "TradingMember" (trading:TradingMember)
does not define a business identity rule.

Required by LDM-004:
Для логической сущности должно быть описано, по каким деловым
признакам два экземпляра считаются одним и тем же объектом.

Remediation:
Укажите identity rule и характер бизнес-ключа либо ключевые атрибуты.
```

### 4.3. Проверка самого каталога

Requirements catalog является критичным governance-артефактом и должен сам проходить validation.

Проверяются как минимум:

- уникальность requirement IDs;
- соответствие code pattern;
- наличие непустого `statement`;
- допустимость severity;
- наличие и корректность `applies_to`;
- наличие хотя бы одного formal check у исполнимого Wave-1 requirement;
- поддержка `formal_check.kind` rules runner’ом;
- уникальность идентификаторов checks;
- наличие `diagnostic_code`;
- наличие remediation, если оно обязательно политикой каталога;
- существование target classes и target kinds в DAMS metamodel;
- отсутствие противоречивых applicability conditions.

Каталог с неизвестным check kind, несуществующим target class или duplicate requirement ID не должен silently pass.

---

## 5. Модель требований Wave 1

### 5.1. Назначение Wave 1

Wave 1 отвечает на вопрос:

> Существует ли модель решения как управляемый, связный и трассируемый артефакт?

Wave 1 не стремится доказать, что модель исчерпывающая, идеально нормализована или полностью отражает реальную реализацию.

Формула Wave 1:

\[
Wave1 =
Identity
+
NonEmptyModel
+
LogicalMeaning
+
PhysicalTraceability
+
ExplicitExceptions
\]

Wave 1 проверяет:

```text
- пакет идентифицируем и связан с ИТ-решением;
- модель не пуста;
- сущности, атрибуты, связи и physical objects имеют базовые сведения;
- нетехнические сущности не изолированы;
- есть identity rule;
- есть conceptual alignment либо обоснованное исключение;
- physical objects и fields имеют mappings либо формальные статусы отсутствия;
- references разрешаются;
- исключения не скрыты.
```

### 5.2. Требования уровня пакета

#### GEN-001. Идентичность и ответственность пакета

Пакет модели данных ИТ-решения должен иметь:

- стабильный идентификатор;
- название;
- описание;
- версию;
- lifecycle status;
- data owner (`data_owner_ref`) на пакете как корень containment cascade
  (ADR-023).

Потомки (логическая сущность, атрибут) могут не задавать владельца и наследуют
эффективное значение от пакета; локальный override допускается покомпонентно
(`data_owner_ref` / `data_steward_ref` / `owning_unit_ref`). Свободная строка
`ownership_inheritance_rule` — только пояснение, не источник истины.

#### GEN-002. Привязка к ИТ-решению

Пакет DAMS solution model должен:

- ссылаться на одно ИТ-решение;
- иметь scope `solution`;
- быть отличим от enterprise conceptual model.

#### GEN-003. Непустой состав модели

Пакет должен содержать хотя бы одно из:

```text
- LogicalEntity;
- PhysicalObject.
```

Пустой пакет не является моделью данных решения.

#### GEN-004. Физические объекты связаны со смыслом

Если в пакете есть physical object, который несёт данные, предоставляет payload или содержит schema/fields, он должен:

- иметь entity-level mapping на одну или несколько logical entities; либо
- быть явно помечен как `technical-only` с `mapping_rationale`.

Проверка не должна автоматически применяться к чисто инфраструктурным контейнерам, например:

```text
database instance;
schema namespace;
connection;
service account;
index;
partition;
migration metadata;
consumer group.
```

Такие объекты должны быть исключены по существующему object kind/role либо явно классифицированы как технические.

---

## 6. Логические сущности

### 6.1. Базовые сведения

Логическая сущность должна иметь:

- стабильный `element_id`;
- русское бизнес-название;
- техническое имя;
- разрешимое эталонное определение (ADR-025): own `description`, либо наследование через `definition_source_ref` / единственный `conceptual_entity_refs` (режим own vs inherited виден в резолвере); статусы `pending` / `local-only` / `not-applicable` требуют own; контекстные определения уровня системы — в `scoped_definitions`, не заменяют эталон;
- lifecycle status;
- owner/steward declared locally либо унаследованные effective-значения от пакета (ADR-023);
- domain context;
- solution data role;
- `entity_type`;
- `data_class`;
- `business_importance`;
- governance classification.

### 6.2. Независимые оси классификации

Следующие характеристики не взаимозаменяемы:

| Ось | Вопрос |
|---|---|
| `entity_type` | Какую архитектурную роль играет сущность? |
| `data_class` | Какова природа данных? |
| `business_importance` | Насколько сущность важна для бизнеса? |
| `governance_classification` | Какие правила управления и доступа применимы? |

Пример корректного заполнения:

```yaml
entity_type: core
data_class: master_data
business_importance: high
governance_classification: confidential
```

### 6.3. Entity type

Wave 1 использует минимум следующие типы:

| Тип | Смысл |
|---|---|
| `core` | Самостоятельное ядро модели решения |
| `derived` | Результат вычисления, агрегации или трансформации |
| `projection` | Представление сущности/набора сущностей для конкретного use case |
| `reference` | Управляемый набор допустимых кодов, типов или состояний |
| `technical` | Сущность без самостоятельного бизнес-смысла вне реализации |

Различие `projection` и `derived`:

```text
Projection:
  Представляет существующие данные в форме, нужной конкретному
  API, read model, витрине или потребителю.

Derived:
  Возникает как результат вычисления, агрегации, трансформации
  или бизнес-правила.
```

Примеры:

```text
ParticipantReadModel
  → projection

DailyParticipantRiskSummary
  → derived
```

### 6.4. Правило идентичности

Нетехническая логическая сущность должна иметь `identity_rule`.

`identity_rule` отвечает на вопрос:

> По каким деловым признакам два экземпляра признаются одним и тем же объектом в контексте решения?

Дополнительно указывается:

- `business_key_kind`;
- и/или `key_attribute_refs`.

Допустимые типы ключа:

| Тип | Смысл |
|---|---|
| `natural` | Устойчивый бизнес-идентификатор |
| `composite` | Уникальная комбинация бизнес-атрибутов |
| `external` | Идентификатор внешней системы или реестра |
| `local` | Идентификатор, уникальный в пределах решения/контекста |
| `surrogate` | Технический ключ реализации |
| `derived` | Идентификатор, вычисляемый из других значений |

Технический `surrogate` key не заменяет business identity rule.

В Wave 1 допустимо, что сущность с `business_key_kind: surrogate` проходит проверку, если у неё есть содержательный `identity_rule`. В последующих волнах для такой сущности могут потребоваться key attribute refs, external/local identifier mapping либо формальное legacy exception.

### 6.5. Наличие атрибутов

Каждая логическая сущность должна иметь минимум один логический атрибут.

Исключение допускается только для:

```yaml
entity_type: technical
```

при наличии явного rationale.

Это правило не предназначено для маскировки абстрактных или недоописанных бизнес-сущностей. Отдельная семантика abstract entity не вводится, пока она не определена стандартом.

### 6.6. Conceptual alignment

Логическая сущность должна быть связана с корпоративной концептуальной моделью либо иметь обоснованный статус alignment.

Используются статусы:

| Статус | Смысл |
|---|---|
| `aligned` | Есть одна или несколько ссылок на conceptual entities |
| `pending` | Alignment требуется, но ещё не утверждён |
| `local-only` | Сущность имеет смысл только в данном решении; корпоративный аналог пока не требуется |
| `not-applicable` | Alignment неприменим к технической/служебной сущности |

Исполнимая матрица:

| Статус | `conceptual_entity_refs` | `alignment_rationale` |
|---|---:|---:|
| `aligned` | Обязательны `1..*` | Рекомендуется |
| `pending` | Допустимы `0..*` | Обязательно |
| `local-only` | Допустимы `0..*` | Обязательно |
| `not-applicable` | Должны отсутствовать | Обязательно; допустимо только для `technical` |

Conceptual reference и rationale могут присутствовать одновременно.

Пример:

```yaml
conceptual_alignment_status: aligned
conceptual_entity_refs:
  - moex:LegalEntity
alignment_rationale: >
  TradingMember является контекстной проекцией LegalEntity
  в границе торгового решения.
```

Это корректно. Rationale объясняет характер реализации и не отменяет alignment.

### 6.7. Семантическая включённость

Нетехническая logical entity не должна быть изолированной.

Для неё должно быть хотя бы одно:

```text
- relationship с другой logical entity;
- conceptual alignment;
- realization корпоративного понятия;
- reference/dependency relation;
- documented isolation rationale.
```

Physical mapping не является достаточным доказательством semantic inclusion.

Неправильная логика:

```text
«Сущность отображена на таблицу, значит её место в модели понятно».
```

Правильная логика:

```text
«Таблица показывает, где данные реализованы;
relation/alignment/realization показывает, что данные означают».
```

---

## 7. Атрибуты и mapping coverage

### 7.1. Базовые свойства logical attribute

Каждый logical attribute должен иметь:

- parent logical entity;
- logical type/range;
- required/optional semantics;
- multivalued indicator;
- lifecycle status, если он поддерживается моделью;
- classification: локальный `governance_classification` либо наследование
  эффективного значения от сущности/пакета (ADR-023 containment cascade);
- definition и naming metadata согласно применимым правилам.

### 7.2. Status coverage между logical и physical слоями

Для LogicalAttribute и PhysicalField используется единый vocabulary:

```yaml
MappingCoverageStatusEnum:
  - mapped
  - derived
  - planned
  - inherited
  - technical-only
  - not-applicable
```

Значения означают:

| Статус | Значение |
|---|---|
| `mapped` | Есть формальное отображение между logical и physical элементами |
| `derived` | Значение определяется выражением, правилом или комбинацией источников |
| `planned` | Реализация/mapping ожидается, но ещё не создан |
| `inherited` | Mapping наследуется или делегируется другому элементу |
| `technical-only` | Элемент нужен только для технической реализации |
| `not-applicable` | Mapping неприменим по природе элемента |

`mapping_rationale` обязателен, когда статус сам по себе не объясняет исключение или решение является временным.

### 7.3. Требование к mapping logical attribute

Для logical attribute, который подлежит физической реализации в данном package, должно существовать:

```text
- reference на PhysicalField;
- и/или transformation expression;
- и/или status/rationale, объясняющие отсутствие direct physical mapping.
```

Field reference и expression могут использоваться одновременно:

```yaml
physical_field_ref: trading_access.status_cd
transformation_expression: >
  decode(status_cd, 'A', 'active', 'S', 'suspended', 'T', 'terminated')
mapping_coverage_status: derived
```

Это не нарушение XOR: expression объясняет семантическое преобразование исходного поля.

### 7.4. Статус `planned`

`planned` нужен для честного отражения target-state и незавершённых mapping работ.

Он не должен использоваться как постоянный обход обязательных mappings.

Минимальная политика:

```text
planned:
  - требует непустой mapping_rationale;
  - допустим для draft/planned/target artifacts;
  - должен давать warning или error для active/approved/released artifacts
    согласно lifecycle policy.
```

Полная проверка реализации «вся логика физически реализована» не входит в Wave 1. Она требует явной модели состояния `as-is` / `to-be` / `implemented` и относится к последующим волнам.

---

## 8. Логические связи

### 8.1. Концы связи

Logical relationship должна иметь:

- source entity;
- target entity;
- разрешимые references;
- lifecycle status;
- cardinality с обеих сторон;
- дополнительные признаки identifying/associative, если они применимы.

Для active relationships должны быть определены:

```text
source_min_cardinality
source_max_cardinality
target_min_cardinality
target_max_cardinality
```

Допустимые значения cardinality определяются метамоделью, например:

```text
0
1
положительное целое число
unbounded
```

Не допускается silently заполнять `0..*` для всех связей только ради прохождения gate.

### 8.2. Draft/imported исключения

Для draft или imported relationship допускается временная неполнота cardinality только при:

- соответствующем lifecycle status;
- явном rationale;
- отсутствии утверждения, что relationship готова к production use.

### 8.3. Что не проверяется в Wave 1

Wave 1 не требует:

- `relationship_kind`;
- автоматического выявления M:N;
- обязательного association entity для M:N;
- формальной проверки composition/aggregation;
- детальной модели role semantics.

Эти требования относятся к Wave 2, поскольку нуждаются в дополнительных slots, более зрелых примерах и снижении false-positive rate.

---

## 9. Physical objects и fields

### 9.1. Physical object

PhysicalObject — точка хранения или предоставления данных.

Примеры:

```text
Table
View
File
Dataset
API endpoint
Event topic
Message schema
Queue
External dataset
```

Каждый business-significant physical object должен иметь:

- ссылку на ИТ-систему;
- object kind;
- native name/identifier;
- technology;
- native schema или format reference;
- lifecycle status;
- entity-level mapping или technical-only exception.

### 9.2. Physical field

Каждый PhysicalField должен иметь:

- parent PhysicalObject;
- native name;
- native type;
- nullability/required semantics;
- lifecycle status, если применимо;
- mapping coverage status;
- mapping на logical attribute, expression или documented exception.

### 9.3. Entity-level mapping

Entity-level mapping доказывает, какой логический смысл представляет physical object.

`PDM-003` считается выполненным, если существует явный Mapping:

```text
PhysicalObject
  ↔ Mapping(mapping_type = entity-physical)
  ↔ минимум одна LogicalEntity
```

Attribute-level mappings не должны автоматически считаться заменой entity-level mapping.

Пример:

```yaml
mapping_type: entity-physical
source_ref: trading-platform:TRADING_MEMBER
target_refs:
  - trading-platform:TradingMember
mapping_coverage_status: mapped
```

### 9.4. Attribute-level mapping

Attribute-level mapping доказывает, как physical field соотносится с logical attribute.

`PDM-004` считается выполненным, если PhysicalField:

- участвует в mapping на LogicalAttribute;
- и/или участвует в documented transformation expression;
- и/или имеет допустимый mapping coverage status и rationale.

Пример:

```yaml
mapping_type: attribute-physical
source_ref: trading-platform:TRADING_MEMBER.MEMBER_CODE
target_ref: trading-platform:TradingMember.member_code
mapping_coverage_status: mapped
```

### 9.5. Technical-only objects и fields

`technical-only` допустим для объектов и полей, не имеющих самостоятельного бизнес-смысла:

```text
surrogate database key;
ORM version column;
migration metadata;
technical audit field;
checkpoint;
retry counter;
internal partition marker;
service-only correlation token.
```

Он не должен применяться к business-significant data только потому, что mapping ещё не подготовлен.

Каждый `technical-only` exception требует `mapping_rationale`.

---

## 10. Классы требований Wave 1

| Группа | Код | Назначение |
|---|---|---|
| General | `GEN-001` | Идентичность и ответственность пакета |
| General | `GEN-002` | Привязка пакета к ИТ-решению |
| General | `GEN-003` | Непустой состав модели |
| General | `GEN-004` | Связь physical object с logical meaning |
| Logical data model | `LDM-001` | Контекст и роль данных |
| Logical data model | `LDM-002` | Наименование, resolvable definition (ADR-025), lifecycle, ownership |
| Logical data model | `LDM-003` | Независимые оси классификации |
| Logical data model | `LDM-004` | Правило идентичности и ключ |
| Logical data model | `LDM-005` | Наличие атрибутов |
| Logical data model | `LDM-006` | Conceptual alignment |
| Logical data model | `LDM-007` | Семантическая включённость |
| Logical data model | `LDM-008` | Полнота реализации зависимых концептов (warning; ADR-029) |
| Attribute | `ATR-001` | Основные свойства logical attribute |
| Attribute | `ATR-005` | Mapping logical attribute на реализацию |
| Relationship | `REF-001` | Концы relationship и разрешимость refs |
| Relationship | `REF-002` | Cardinality relationship |
| Physical data model | `PDM-001` | Основные свойства physical object |
| Physical data model | `PDM-002` | Основные свойства physical field |
| Physical data model | `PDM-003` | Mapping physical object ↔ logical entity |
| Physical data model | `PDM-004` | Mapping physical field ↔ logical attribute |

---

## 11. Wave 2: качество моделирования

### 11.1. Назначение Wave 2

Wave 2 отвечает на вопрос:

> Хорошо ли модель описана, а не только существует ли она и прослеживаема ли она?

Большинство правил Wave 2 первоначально имеют severity `warning`.

Это позволяет:

- собрать статистику нарушений на реальных моделях;
- понять, какие требования дают false positives;
- откалибровать классификации;
- не стимулировать массовое фиктивное заполнение;
- выбрать правила для последующего hardening.

### 11.2. Wave 2 области

| Область | Примеры правил |
|---|---|
| Naming | `lower_snake_case`, `UpperCamelCase`, allowed suffixes, abbreviation allowlist |
| Atomicity | Запрет составных «код + имя» или «несколько значений в одной строке» без rationale |
| Entity/data classifications | Conditional requirements для core, derived, projection, reference, master, transactional, analytical, metadata |
| Type-specific attributes | Currency для amount, unit для quantity, timezone/temporal semantics для timestamp, scale для rate |
| Relationships | `relationship_kind`, M:N heuristics, association entity, role semantics |
| Physical objects | Retention, format/contract details, endpoint metadata, access and SLA |
| Data flows | Source/target, direction, producer/consumer, integration contract, lineage |
| Governance | Security classification, personal data, regulated data, policy bindings |
| Completeness | Сопоставление as-is logical model и actual physical realization после появления implementation state |

### 11.3. Типовые Wave 2 правила

#### Naming

Проверяются:

```text
- UpperCamelCase для logical entity;
- lower_snake_case для logical attribute;
- позитивная форма is_/has_ для boolean;
- смысловые суффиксы _id, _code, _date, _timestamp,
  _amount, _quantity, _rate, _count;
- allowlist сокращений.
```

Naming rule не заменяет definition, logical type, currency, unit или value set.

#### Atomicity

Проверяются признаки того, что один attribute не скрывает несколько независимых характеристик.

Примеры потенциальных нарушений:

```text
client_info = "123 | ООО Ромашка | active"
country_and_city = "RU, Moscow"
amount_with_currency = "1000 RUB"
```

Автоматическая проверка атомарности может быть только эвристической. Она должна формировать warning и требовать review, а не автоматически перепроектировать модель.

#### Type-specific semantics

| Тип данных | Требование |
|---|---|
| Monetary amount | Currency или currency attribute reference |
| Quantity | Unit и precision |
| Rate | Scale: decimal, percent, basis points и т.д. |
| Date | Event/business/validity semantics |
| Timestamp | Timezone policy и temporal semantics |
| Code | Value set, reference entity или code system |
| Status | Controlled vocabulary и lifecycle semantics |
| Derived attribute | Source mappings, expression, calculation time/refresh policy |

#### Conditional rules по entity type

| Entity type | Дополнительные ожидания |
|---|---|
| `core` | Не определяется только вычислением из другой сущности |
| `derived` | Sources, derivation rule, calculation time |
| `projection` | Source entity/dataset и filter/projection rule |
| `reference` | Owner of value set, lifecycle values, governance |
| `technical` | Technical rationale, ограниченный semantic scope |

---

## 12. Severity и hardening

### 12.1. Матрица severity

| Категория | Wave 1 | Wave 2 | Later |
|---|---:|---:|---:|
| Package identity / EAM link | Error | Error | Error |
| Logical entity core metadata | Error | Error | Error |
| Identity rule | Error | Error | Error |
| Entity/attribute/physical mappings с явными exceptions | Error | Error | Error |
| Reference resolution / cardinality | Error | Error | Error |
| Naming | — | Warning | Error после baseline |
| Atomicity | — | Warning | Selective error |
| Currency/unit/timezone | — | Warning | Error по data class |
| Conditional entity/data rules | — | Warning | Error после calibration |
| DataFlow / integration | — | Warning | Error для critical flows |
| Security/regulatory | — | Warning | Error после policy alignment |
| Полнота logical ↔ physical as-is mapping | — | Warning при наличии state model | Error после утверждения state model |

### 12.2. Принцип hardening

Переход `warning → error` не делается автоматически по времени.

Перед hardening должны быть:

1. baseline на нескольких реальных solution models;
2. анализ причин warnings;
3. проверка false-positive rate;
4. понятная remediation path;
5. согласованная ownership/governance policy;
6. решение ADR или change request.

---

## 13. Исключения и anti-patterns

### 13.1. Exception должен быть явным

Допустимое исключение всегда состоит из:

```text
- статуса;
- rationale;
- ограниченной области применения;
- lifecycle/ownership, если требуется.
```

Недопустимо:

```text
- silently omit mapping;
- не заполнять conceptual reference без статуса;
- считать технической бизнес-сущность без explanation;
- использовать planned как постоянное состояние;
- использовать not-applicable для ухода от semantic alignment;
- считать таблицу достаточным описанием логической сущности.
```

### 13.2. Не использовать XOR по привычке

XOR допустим, только когда два значения не могут иметь смысл одновременно.

Не использовать XOR для:

```text
declared owner override + inherited effective owner
conceptual_entity_refs + alignment_rationale
physical_field_ref + transformation_expression
```

Корректные паттерны:

```text
package data_owner_ref (required root)
  + optional local override on entity/attribute
  (absent slot = inherit via ADR-023 cascade).

conceptual refs OR valid status/rationale branch
  при этом refs + rationale допустимы.

physical field OR expression OR documented exception
  при этом field + expression допустимы.
```

### 13.3. Не путать coverage и completeness

Wave 1 проверяет coverage модели:

```text
Есть ли logical meaning?
Есть ли physical mapping?
Есть ли exception?
```

Wave 1 не проверяет полную реализацию:

```text
Все ли logical entities реализованы физически?
Все ли physical objects внесены в модель?
Все ли API/topics/files отражены?
```

Полная проверка требует явной модели состояния реализации, например:

```text
as-is
target
planned
implemented
retired
```

и относится к будущему развитию.

### 13.4. Не путать mapping и semantic inclusion

```text
Physical mapping:
  Показывает, где и как реализованы данные.

Semantic inclusion:
  Показывает место сущности в смысловой модели.
```

Наличие таблицы или API mapping не заменяет relationship, conceptual alignment, realization или isolation rationale.

---

## 14. Relation с DSP

Data Specification Player создаёт или обогащает draft solution model package.

DSP не создаёт отдельный тип требований и не отменяет DAMS assess rules.

```text
CSV / DDL / OpenAPI / AsyncAPI
  → profiling
  → inference
  → draft solution model
  → body assess
  → diagnostics and remediation
  → human review
  → promotion to governed solution model
```

Для DSP-generated draft особенно важны:

- `planned`;
- `derived`;
- `pending`;
- `mapping_rationale`;
- confidence/evidence;
- unresolved ambiguities;
- promotion target.

DSP может сформировать candidate mappings, но не должен silently объявлять semantic alignment или production completeness.

---

## 15. Relation с enterprise conceptual model и внешними стандартами

Логическая сущность решения по умолчанию должна стремиться к связи с enterprise conceptual model.

```text
Solution LogicalEntity
  ── realizes / aligns to ──► Enterprise ConceptualEntity
```

Внешние reference specifications не подменяют корпоративную концептуальную модель.

```text
FIBO / ODCM / other external specification
  ├── ExternalSpecificationScope
  ├── ExternalTermSelection
  └── semantic alignment
          │
          ▼
Enterprise Conceptual Model
  (entity_tier, genesis_kind, external_class_refs, RelationTerm — ADR-026)
          │
          ▼
Solution Data Model
```

Для solution model допустимы local external mappings, но они должны быть явно отмечены как локальные или исключительные. Основной semantic target для ExternalTermSelection — enterprise conceptual layer.

### 15.1 ConceptualEntity metamodel (ADR-026)

Корпоративная концептуальная сущность дополнительно несёт:

| Ось | Слоты | Смысл |
|---|---|---|
| Уровень | `entity_tier`, `dependency_kind`, `depends_on_refs` | `primary` vs `dependent` (characteristic / associative). Не путать с `business_importance`. FK в ER-схеме ≠ dependent. |
| Генезис | `genesis_kind`, `external_class_refs` | `external` ⇔ есть выравнивание на класс онтологии / внешней спецификации с `match_kind`; `native` — без внешних родителей. Канон — `external_class_refs`; `Mapping(aligns_with)` — проекция. |
| Связи | `RelationTerm` + `Relationship.relation_term_ref` | Прямая и обратная формулировка из справочника; одна запись `Relationship` на пару. |

Требования каталога: `CM-CON-002` (tier), `CM-CON-003` (genesis), `CM-REF-002` (relation term). Exactness для наследования определений (ADR-025) берётся из `match_kind` (`exact` / `equivalent`). Модельный глоссарий КМД — генерируемое view (`build_model_glossary`), не отдельный dataset.

---

## 16. Что не входит в текущую область

Следующие темы сознательно не входят в Wave 1:

```text
- Полный RACI model для ownership/stewardship.
- Nested BusinessKey class.
- Автоматическое выявление composite string attributes.
- Полная проверка M:N и обязательное создание association entities.
- Полная модель relationship kind.
- Security classification и regulated/personal data policy enforcement.
- DataFlow completeness.
- EAM live lookup.
- Проверка полного соответствия actual physical implementation.
- AI-generated lineage UI.
- Автоматическая коррекция модели по результатам assess.
```

Эти темы могут быть добавлены в последующие Waves после baseline реальных моделей и отдельного архитектурного решения.

---

## 17. Практический порядок работы

При создании или изменении solution model рекомендуется следующий порядок:

```text
1. Создать/обновить package identity и EAM reference.

2. Описать ключевые LogicalEntity:
   names, definitions, classifications, identity rules.

3. Добавить LogicalAttribute и Relationship.

4. Установить conceptual alignment:
   aligned / pending / local-only / not-applicable.

5. Описать PhysicalObject и PhysicalField для известной реализации.

6. Добавить entity-level и attribute-level mappings.

7. Явно оформить exceptions:
   planned, derived, inherited, technical-only, not-applicable.

8. Запустить schema validation и body assess.

9. Исправить errors и разобрать warnings.

10. Сформировать publication sections и пройти ADR-019 contract.

11. Опубликовать модель и зафиксировать lifecycle/version.
```

---

## 18. Ключевые инварианты

```text
1. Непустой package не равен полной модели, но пустой package моделью не является.

2. Logical entity не равна table.

3. Physical mapping не равен semantic inclusion.

4. Conceptual alignment не равен OWL equivalence.

5. Exception без статуса и rationale не является исключением.

6. Technical-only не должен использоваться для бизнес-данных.

7. Planned не должен быть постоянной заменой mapping.

8. Containment cascade (ADR-023): absent slot наследует effective от родителя;
   локальный override допустим; copy-down в YAML не используется.

9. Source field и transformation expression могут сосуществовать.

10. Publication completeness не равна semantic completeness.

11. Отсутствие automated check не отменяет нормативное требование:
    оно остаётся предметом human review.

12. Ужесточение rules возможно только после baseline на реальных моделях.
```
