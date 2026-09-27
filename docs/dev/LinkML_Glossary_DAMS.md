# Глоссарий терминов LinkML для MOEX Data Model Specification (DAMS)

**Статус:** Draft
**Версия:** 0.1
**Назначение:** справочник по всем конструкциям языка LinkML, использованным в метамодели DAMS (`moex-core.yaml`, `moex-types.yaml`, `moex-governance.yaml`, `moex-registries.yaml`, `moex-integration.yaml`, `moex-contract-binding.yaml`, `moex-analytics.yaml`, `moex-dams.yaml`).

Термины сгруппированы по смысловым блокам: структура схемы, классы и наследование, слоты, типы и enum-ы, ограничения и кардинальность, идентификация и ссылки, метаданные и документация, сериализация. В конце — таблица прямого соответствия «конструкция LinkML → где используется в DAMS».

---

## 1. Схема и её структура

### Schema (SchemaDefinition)
Корневой документ LinkML — YAML-файл, описывающий пространство имён, версию, импортируемые модули, классы, слоты, типы и enum-ы. Каждый файл DAMS (`moex-core.yaml`, `moex-types.yaml` и т. д.) — это одна LinkML-схема со своим `id` и `name`.

### id / name (схемы)
`id` — глобальный URI схемы (пространство имён верхнего уровня). `name` — короткое машиночитаемое имя схемы. В DAMS каждый модуль имеет собственный `id`, что позволяет ссылаться на его элементы через CURIE.

### prefixes
Блок сокращений вида `moex: https://moex.example.org/dams/`, который позволяет использовать компактные идентификаторы (CURIE) вместо полных URI во всей схеме.

### imports
Механизм подключения одной LinkML-схемы к другой. В DAMS `moex-core.yaml` импортирует `moex-types.yaml` и `moex-governance.yaml`, чтобы переиспользовать enum-ы и mixins без дублирования. Это прямой аналог `import` в языках программирования.

### default_prefix / default_range
Настройки схемы, задающие пространство имён по умолчанию для элементов без явного `class_uri`/`slot_uri`, и тип данных по умолчанию (`string`) для слотов без явного `range`.

### classes / slots / enums / types (top-level blocks)
Четыре основных раздела схемы, где определяются соответственно классы, переиспользуемые слоты, перечисления и скалярные типы. В DAMS все `*_enum` (например, `lifecycle_status_enum`) объявлены в блоке `enums` схемы `moex-types.yaml`, а mixins — в блоке `classes` схемы `moex-governance.yaml`.

---

## 2. Классы и наследование

### Class (ClassDefinition)
Основная структурная единица LinkML — аналог таблицы в реляционной БД, класса в ООП или типа объекта в JSON Schema. В DAMS классами являются, например, `ModelElement`, `LogicalEntity`, `Mapping`, `DataFlow`.

### is_a
Слот, задающий единственного **первичного родителя** класса (или слота) — классическое одиночное наследование. В DAMS почти все содержательные классы объявлены как `is_a: ModelElement`, что и делает `ModelElement` корнем всей иерархии метамодели.

### abstract
Булев флаг, помечающий класс (или слот) как **абстрактный**: он не может быть напрямую инстанцирован, но служит основанием для наследования. `ModelElement` в DAMS — классический пример abstract-класса: у него нет собственных экземпляров, только конкретные потомки (`LogicalEntity`, `PhysicalObject` и т. д.).

### mixin
Булев флаг, помечающий класс (или слот) как **mixin** — «пакет» переиспользуемых свойств, который не участвует в основной (одиночной) иерархии `is_a`, а подмешивается дополнительно. В отличие от `is_a`, у класса может быть несколько mixins одновременно.

### mixins (slot on class)
Многозначный слот, перечисляющий mixin-классы, чьи свойства подмешиваются в данный класс. В DAMS каждый содержательный класс дополнительно к `is_a: ModelElement` подключает нужный набор governance-mixins, например `mixins: [HasLifecycle, HasOwnership]`.

**Использованные в DAMS mixins и их назначение:**

| Mixin | Назначение |
|---|---|
| `HasLifecycle` | Жизненный цикл элемента: `lifecycle_status`, `valid_from`, `valid_to`, `deprecated_by_ref` |
| `HasOwnership` | Владение: `data_owner_ref`, `data_steward_ref`, `owning_unit_ref` |
| `HasBusinessClassification` | Роль в бизнесе: `entity_type`, `data_class`, `business_importance` |
| `HasGovernanceClassification` | Базовая маркировка чувствительности: `governance_classification`, `classification_source`, `classification_rationale` |
| `HasPolicyBindings` | Держатель ссылок на применяемые политики: `policy_refs` |
| `HasProvenance` | Происхождение и согласование: `source_artifact_ref`, `approval_status`, `approved_by_ref`, `approved_at` |

Правило разрешения свойств в LinkML при конфликте — «глубина поиска» по порядку: локальный `slot_usage` класса → `slot_usage` в mixins (по порядку перечисления) → `slot_usage` в `is_a`-родителе → глобальное определение слота.

### Порядок наследования is_a vs mixins
Рекомендованная практика LinkML: `is_a` — для одной «главной» линии наследования (аналог таксономии), `mixins` — для сквозных, не связанных таксономически возможностей. Именно так устроена DAMS: `is_a: ModelElement` даёт единую вертикаль идентичности и жизненного цикла, а mixins добавляют горизонтальные «грани» (governance, ownership, provenance), не нарушая единую иерархию.

### tree_root
Булев флаг на классе, обозначающий **корневой класс-контейнер** всего сериализованного документа (аналог `Container` в примерах LinkML). В DAMS этим свойством помечен `MoexModelRepository` — корневой контейнер конформанс-тестового набора моделей.

### class_uri
Явно заданный URI/CURIE, на который отображается класс при генерации RDF/OWL. Используется, когда класс должен соответствовать существующему термину в внешней онтологии, а не автоматически выведенному URI на основе имени.

---

## 3. Слоты (slots)

### Slot (SlotDefinition)
Атомарная единица данных, ассоциируемая с классом, — аналог поля таблицы, атрибута объекта, свойства в JSON Schema. В спецификации LinkML это называется «metaslot» на уровне метамодели. В DAMS слотами являются, например, `element_id`, `lifecycle_status`, `entity_type`.

### attributes
Синтаксический сахар для объявления слота **прямо внутри класса**, без вынесения в общий раздел `slots`. Рекомендуемая практика LinkML — использовать `attributes` только для по-настоящему класс-специфичных полей без потенциала переиспользования, а переиспользуемые слоты объявлять в глобальном разделе `slots`. В DAMS этот подход виден в том, что общие governance-поля вынесены в mixins и переиспользуются, а класс-специфичные поля (например, `mapping_type` у `Mapping`) объявляются локально.

### slot_usage
Механизм **уточнения** уже объявленного (унаследованного или переиспользуемого) слота в контексте конкретного класса — без создания нового имени слота. Через `slot_usage` можно:
- сузить `range` (например, до более специфичного подкласса);
- сделать необязательный слот обязательным (`required: true`);
- изменить `multivalued` или задать точную кардинальность.

LinkML в этом смысле **монотонен**: `slot_usage` может только *добавлять* ограничения, а не ослаблять их. В DAMS `slot_usage` применяется там, где общий mixin-слот (например, `data_owner_ref` из `HasOwnership`) нужно связать с конкретным `range` в контексте конкретного класса.

### slot_uri
Явно заданный URI/CURIE слота при отображении в RDF/OWL — аналог `class_uri`, но для свойства, а не класса.

### range
Тип значения слота: либо встроенный LinkML `type` (строка, целое число и т. д.), либо другой класс схемы (тогда слот становится «объектным свойством» — ссылкой), либо enum. В DAMS `range: LogicalEntity` у слота `owner_entity_ref` в `LogicalAttribute` задаёт, что значение этого слота — ссылка на экземпляр `LogicalEntity`.

### multivalued
Булев флаг: слот может принимать **список значений**, а не одно. В DAMS `policy_refs` в mixin `HasPolicyBindings` — многозначный слот (список ссылок на `Policy`).

### required
Булев флаг: слот обязателен для заполнения. В DAMS, например, `description` у `ModelElement` помечен обязательным, чтобы у каждого элемента модели была документация.

### recommended
Более мягкая версия `required`: слот желателен, но не строго обязателен; используется линтером (`linkml-lint`) как проверяемая best-practice, а не как жёсткая валидационная ошибка.

### identifier
Булев флаг, превращающий слот в **идентифицирующий слот класса**. Он автоматически становится `required`; класс с identifier-слотом можно инстанцировать по ссылке в JSON-сериализации (не встраивая целиком), и на такой слот накладывается ограничение уникальности во всей модели. В DAMS роль identifier-слота играет `element_id` у `ModelElement` (и производный `registry_id` у `RegistryEntry`).

### key
Более слабая альтернатива `identifier`: обеспечивает уникальность значения слота в пределах контейнера, но не даёт остальных свойств identifier-слота (нет глобальной уникальности и особого поведения при сериализации).

### minimum_cardinality / maximum_cardinality / exact_cardinality
Явное указание допустимой длины списка значений при `multivalued: true`: минимальное количество элементов, максимальное количество, либо ровно заданное число элементов. В DAMS `minimum_cardinality`/`maximum_cardinality` используются у `LogicalAttribute` для описания допустимого числа значений сложных многозначных атрибутов.

### inlined / inlined_as_list
Флаги, управляющие тем, как объектное значение слота (ссылка на другой класс) представляется в сериализации: как встроенный (inline) вложенный объект/словарь, либо как встроенный список объектов, в противоположность представлению по ссылке на identifier.

### ifabsent
Значение или выражение по умолчанию для слота, если оно не задано явно в экземпляре данных.

### pattern
Регулярное выражение, ограничивающее допустимый формат строкового значения слота (например, для проверки формата URI, кода или маски).

### subproperty_of
Слот объявляется семантическим **подсвойством** другого, более общего слота — используется при генерации RDF/OWL и при построении property-иерархий, а также транслируется в ограничения типа `Literal` при генерации Pydantic-классов.

---

## 4. Типы данных (types)

### Type (TypeDefinition)
Скалярный тип данных — аналог примитивного типа в языке программирования: `string`, `integer`, `float`, `boolean`, `date`, `datetime`, `time`, `uri`, `uriorcurie` и другие встроенные типы LinkML. Определять собственные типы не обязательно — можно использовать встроенные, но DAMS явно фиксирует свой набор логических типов через enum, а не через кастомные LinkML `types`.

### logical_data_type_enum (пример типового enum DAMS)
В DAMS вместо создания россыпи кастомных LinkML `TypeDefinition` для каждого логического типа данных выбран другой путь: единый enum `logical_data_type_enum` со значениями `string`, `integer`, `decimal`, `boolean`, `date`, `datetime`, `time`, `binary`, `identifier`, `uri`, `object`. Это осознанное архитектурное решение — типизация атрибута описывается как классифицирующее значение (enum), а не как отдельный LinkML `range`-тип, потому что реальный физический тип определяется на уровне `PhysicalField`, а не `LogicalAttribute`.

---

## 5. Перечисления (enums)

### Enum (EnumDefinition)
Управляемый список допустимых значений для слота — аналог `enum` в языках программирования, выпадающего списка в форме или ограниченного домена значений в реляционной БД. В LinkML enum-ы, в отличие от простых строк, можно валидировать автоматически и (опционально) связывать с внешними онтологиями через `meaning`.

### permissible_values
Список конкретных допустимых значений enum-а. Каждое значение может иметь собственное `description` и `meaning` (ссылку на онтологический термин, например `PATO:0001421`). В DAMS у enum-ов DAMS (например, `lifecycle_status_enum: draft, active, deprecated, retired`) `permissible_values` — это просто перечисленные значения без привязки к внешним онтологиям, поскольку это внутренние операционные статусы, а не онтологические понятия.

### meaning
Необязательная ссылка от конкретного значения enum-а на термин внешней онтологии/словаря (используется при генерации OWL/RDF, чтобы конкретное значение enum-а стало семантически связанным понятием, а не просто строкой).

### Полный список enum-ов, используемых в DAMS

| Enum | Значения (кратко) | Назначение |
|---|---|---|
| `lifecycle_status_enum` | draft, active, deprecated, retired | Статус жизненного цикла любого `ModelElement` |
| `approval_status_enum` | proposed, approved, rejected, superseded | Статус согласования (mapping, provenance) |
| `model_level_enum` | conceptual, logical, physical | Архитектурный уровень модели |
| `entity_type_enum` | core, derived, reference | Роль сущности в бизнес-модели |
| `data_class_enum` | reference_data, master_data, transactional_data, analytical_data, metadata | Класс данных сущности |
| `business_importance_enum` | high, medium, low | Бизнес-значимость сущности |
| `governance_classification_enum` | public, internal, confidential, restricted | Уровень чувствительности данных |
| `logical_data_type_enum` | string, integer, decimal, boolean, date, datetime, time, binary, identifier, uri, object | Логический тип атрибута |
| `physical_object_kind_enum` | database, schema, table, view, column, api, endpoint, payload, topic, queue, message, file, dataset, pipeline | Вид физического объекта данных |
| `flow_direction_enum` | inbound, outbound, internal, bidirectional | Направление потока данных |
| `solution_data_role_enum` | producer, consumer, intermediary | Роль решения относительно данных |
| `integration_channel_enum` | api, queue, database, file, other | Канал интеграции |
| `integration_class_enum` | EAP, EDA | Класс интеграции (событийная/прикладная) |
| `integration_level_enum` | intraplatform, interplatform | Уровень интеграции |
| `mapping_type_enum` | semantic_equivalence, specialization, implementation, field_mapping, transformation, aggregation, derivation | Тип соответствия (mapping) |
| `mapping_cardinality_enum` | one_to_one, one_to_many, many_to_one, many_to_many | Кардинальность mapping |
| `compatibility_mode_enum` | backward, forward, full, none | Режим совместимости версий |
| `enforcement_result_enum` | pass, warn, fail, not_applicable | Результат проверки политики/правила |

---

## 6. Ограничения и правила

### Boolean slots уровня "constraints"
Помимо `required`/`multivalued`/`identifier`, LinkML предоставляет слоты, которые в DAMS используются на уровне `Relationship` для описания природы связи:

### identifying (в контексте Relationship)
Булев флаг у класса `Relationship` в DAMS: обозначает, что связь является **идентифицирующей** (аналог identifying relationship в ER-моделировании — когда первичный ключ дочерней сущности зависит от родительской).

### associative (в контексте Relationship)
Булев флаг у `Relationship`: обозначает, что связь **ассоциативная**, то есть сама является сущностью верхнего уровня (аналог "table-relationship" или связывающей таблицы many-to-many, а не простого FK).

### rules
Более сложная (в DAMS не задействованная в базовом ядре, но доступная в языке LinkML) конструкция условной логики: набор `preconditions`/`postconditions` для описания зависимых ограничений (например: «если `data_class = transactional_data`, то `business_importance` обязателен»). Упоминается в архитектурном плане как часть языка, которую DBML/OWL не могут выразить напрямую.

### unique_keys
Механизм задания составных уникальных ключей на уровне класса (комбинация нескольких слотов, которая должна быть уникальной) — аналог составного `UNIQUE`-ограничения в реляционной БД.

---

## 7. Идентификация, ссылки и URI

### CURIE (Compact URI)
Сокращённая форма URI вида `prefix:local_id` (например, `moex:LogicalEntity`), которая разворачивается в полный URI через таблицу `prefixes` схемы. Используется во всей DAMS для стабильных идентификаторов реестровых объектов (`registry_id`) и элементов модели (`element_id`).

### URI vs URIorCURIE (типы данных)
Встроенные LinkML-типы для хранения полных URI (`uri`) или значений, которые могут быть либо CURIE, либо полным URI (`uriorcurie`). Использование `uriorcurie` вместо простого `string` даёт валидатору возможность проверять корректность формата ссылки.

### Reference slot (паттерн ссылки, не отдельная конструкция языка)
В DAMS повсеместно используется паттерн: слот с суффиксом `_ref` (например, `data_owner_ref`, `solution_ref`) — это обычный LinkML-слот с `range`, указывающим на другой класс, реализующий ссылку по identifier, а не встраивание объекта целиком (`inlined: false` по умолчанию для non-required ссылок).

---

## 8. Метаданные и документация схемы

### description
Слот, присутствующий практически на любом элементе схемы (класс, слот, enum, permissible value) — человекочитаемое описание назначения элемента. В DAMS `description` обязателен (`required: true`) на уровне `ModelElement`, что гарантирует документированность каждой сущности метамодели.

### title
Более короткое, презентационное имя элемента, отличное от машиночитаемого `name` — используется, например, в генераторах JSON Schema для поля `title`.

### comments / notes
Свободные текстовые аннотации к элементу схемы для внутренних заметок разработчиков схемы, не предназначенные для конечных пользователей данных (в отличие от `description`).

### annotations
Механизм произвольных пар «ключ-значение», прикрепляемых к любому элементу схемы, для расширения метаданных без изменения самой метамодели LinkML (аналог generator-specific hints). Именно через `annotations` в архитектуре Workbench предлагается хранить, например, `physical_name` для DBML-профиля, не меняя базовую конструкцию.

### examples
Блок примеров валидных значений слота или экземпляров класса, встраиваемый прямо в схему и используемый при генерации документации (`gen-doc`).

### deprecated
Слот, указывающий, что элемент схемы устарел и не должен использоваться в новых моделях (в DAMS для этой цели вместо встроенного `deprecated` на уровне класса используется прикладной enum-статус `lifecycle_status_enum: deprecated`, реализованный через mixin `HasLifecycle` — то есть жизненный цикл вынесен в бизнес-модель, а не в саму LinkML-схему).

### see_also
Ссылка (URL) на внешний источник дополнительной информации об элементе схемы.

### from_schema
Автоматически формируемый LinkML слот метамодели, указывающий, из какой именно исходной схемы (файла) происходит данный элемент — важно при работе с составными, импортирующими друг друга схемами, как в DAMS.

---

## 9. Генерация и совместимость

### metamodel
Схема, описывающая саму LinkML — то есть «схема схем». Классы и слоты LinkML (`ClassDefinition`, `SlotDefinition`, `EnumDefinition` и т. д.) сами являются экземплярами метамодели. Валидация схемы DAMS «на корректность LinkML» — это, по сути, валидация относительно этой метамодели.

### SchemaView
Программный API (в `linkml-runtime`), предоставляющий доступ к разрешённой, «плоской» версии схемы: с уже вычисленными наследуемыми слотами, примененными mixins и раскрытыми `slot_usage`. Используется backend-компонентами MOEX Workbench (Schema Service) для построения `ModelGraph`.

### induced slot
Итоговое, полностью вычисленное определение слота **в контексте конкретного класса** — после применения всей цепочки наследования (`is_a`, `mixins`, `slot_usage`) к базовому определению слота. Это то определение, которое реально «видит» генератор при обработке класса.

### generator
Компонент LinkML-инструментария, преобразующий схему в другое представление: JSON Schema, Pydantic, RDF, OWL, SHACL, DBML, документацию. Не является частью языка схемы как такового, но необходим для понимания того, зачем нужны те или иные конструкции (например, `class_uri` осмыслен только в контексте RDF/OWL-генерации).

### compatibility (schema versioning)
Не встроенная в язык LinkML конструкция, а прикладной паттерн DAMS: слоты `compatibility_mode` (см. `compatibility_mode_enum`) и `compatibility_baseline_ref` в классе `DataModelBinding` описывают, в каком режиме (backward/forward/full/none) новая версия модели совместима с предыдущей — это уровень MOEX semantic rules поверх LinkML, а не свойство самого языка.

---

## 10. Соответствие: конструкция LinkML → применение в DAMS

| Конструкция LinkML | Где используется в DAMS |
|---|---|
| `imports` | `moex-core.yaml` импортирует `moex-types.yaml`, `moex-governance.yaml` |
| `is_a` | Все классы верхнего уровня наследуются от `ModelElement` |
| `abstract` | `ModelElement` — абстрактный корень иерархии |
| `mixin` + `mixins` | `HasLifecycle`, `HasOwnership`, `HasBusinessClassification`, `HasGovernanceClassification`, `HasPolicyBindings`, `HasProvenance` |
| `tree_root` | `MoexModelRepository` |
| `identifier` | `element_id` у `ModelElement`, `registry_id` у `RegistryEntry` |
| `required` | `description` у `ModelElement`, `lifecycle_status` и др. |
| `multivalued` | `policy_refs`, `member_system_refs`, ссылки в junction-классах |
| `minimum_cardinality` / `maximum_cardinality` | Ограничения кардинальности у `LogicalAttribute`, `Relationship` |
| `slot_usage` | Уточнение `range` mixin-слотов (например, `data_owner_ref`) в конкретных классах |
| `range` (class) | Все `_ref`-слоты, указывающие на другие классы модели |
| `range` (enum) | `lifecycle_status`, `entity_type`, `data_class` и остальные `*_enum` слоты |
| `enums` / `permissible_values` | Полный список из 18 enum-ов в `moex-types.yaml` |
| `abstract` (registry) | `RegistryEntry` — абстрактный базовый класс для проекций EAM/Clinkr/каталога |
| `identifying` / `associative` | Класс `Relationship` |
| `annotations` | Планируемый механизм хранения generator-specific hints (например, DBML physical_name) |
| `description` | Обязательное поле документации на каждом классе, слоте и enum-значении |

---

## Итоговые принципы, зафиксированные в DAMS через LinkML

1. **Одна вертикаль идентичности.** Всё, что имеет смысл в модели данных MOEX, — потомок `ModelElement` через `is_a`. Это даёт единый `element_id`, единый `lifecycle_status` и единую точку входа для ссылок.
2. **Governance — горизонтальный срез, а не вертикаль.** Владение, классификация чувствительности, происхождение и согласование не встроены в основную иерархию наследования, а подключаются как независимые mixins — это позволяет применить, например, `HasGovernanceClassification` и к `LogicalEntity`, и к `PhysicalObject`, и к `Mapping`, не создавая для них общего предка ниже `ModelElement`.
3. **Enum вместо свободной строки — везде, где возможен закрытый список значений.** Ни один статус, класс данных или тип в DAMS не выражен как обычная `string` — для каждого заведён `*_enum`, что даёт автоматическую валидацию через `linkml-validate`.
4. **Ссылки, а не встраивание.** Связи между классами реализованы через identifier-ссылки (`_ref`-слоты с `range` на другой класс), а не через глубокое вложение объектов, что отражает философию «реестр + ссылка», используемую для проекций EAM/Clinkr/каталога (`RegistryEntry` и его потомки).
5. **`slot_usage` как механизм специализации без дублирования.** Общие governance-слоты из mixins получают класс-специфичный `range` (например, ссылку именно на `Role` для `data_owner_ref`) без повторного объявления самого слота.
