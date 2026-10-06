---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# Поддержка LinkML `rules` генераторами (ADR-045, PR-C0)

**Дата:** 2026-10-06  
**ADR:** [ADR-045](../adr/ADR-045-executable-constraint-matrix.md)  
**Отчёт:** [constraint-matrix-inventory-report.md](constraint-matrix-inventory-report.md)  
**Spike:** `tmp/constraint-spike/spike_rules.py`, `spike_real_rules.py`, `validator_default_check.py`, `spike_inv_prefix.py` (результаты: `tmp/constraint-spike/results.json`, `real-rules.json`)

Документ обновляется при каждой смене версии LinkML (пин: `requirements-linkml.txt`).

## 1. Версии, на которых получены результаты

| Компонент | Версия |
|---|---|
| `linkml` / `linkml-runtime` | 1.11.1 / 1.11.1 |
| `pyshacl` | 0.40.1 |
| Python spike | 3.10.6 (генераторы), 3.14.4 (проверка `Validator` в `apps/cli/.venv`) |
| Python `check_all.py` | см. отчёт PR-C0 (строка `check_all: python=`) |

Поведение LinkML приоритетнее ожиданий задания. Все ячейки таблиц ниже получены запуском, а не из документации.

## 2. Таблица «правило × генератор»

Мини-схема: один класс `T`, слоты `kind, a, b` (string), `n1, n2` (integer), `flag` (boolean). Для каждого правила взяты valid- и invalid-экземпляры. Значения: **применяет** (invalid отклонён, valid принят), **игнорирует** (invalid принят), **неверно** (valid отклонён), **падает** (исключение при загрузке схемы).

| Шаблон правила | `linkml-validate` (JsonschemaValidationPlugin) | `gen-json-schema` | `gen-pydantic` | `gen-shacl` + pySHACL |
|---|---|---|---|---|
| pre `equals_string`, post `required: true` | применяет | применяет | игнорирует | игнорирует |
| pre `equals_string`, post `value_presence: PRESENT` | применяет | применяет | игнорирует | игнорирует |
| post `value_presence: ABSENT` на **одном** слоте | применяет | применяет | игнорирует | игнорирует |
| post `value_presence: ABSENT` на **нескольких** слотах | **ослаблено** (см. §3.2) | **ослаблено** | игнорирует | игнорирует |
| pre `value_presence: PRESENT`, post `equals_string` | применяет | применяет | игнорирует | игнорирует |
| pre `any_of(equals_string)` | применяет | применяет | игнорирует | игнорирует |
| post `any_of(equals_string)` | применяет | применяет | игнорирует | игнорирует |
| post `equals_string` на слоте `boolean` | **неверно** (valid отклонён, §3.1) | **неверно** | игнорирует | игнорирует |
| post `pattern` | применяет | применяет | игнорирует | игнорирует |
| `elseconditions` | применяет | применяет | игнорирует | игнорирует |
| `bidirectional: true` | применяет | применяет | игнорирует | игнорирует |
| `inapplicable` на правиле / в `slot_conditions` | падает | падает | падает | падает |
| `deactivated: true` | **неверно** (правило всё равно применено, §3.4) | **неверно** | игнорирует | игнорирует |
| сравнение двух слотов (`equals_expression: "{n1}"`) | игнорирует | игнорирует | игнорирует | игнорирует |
| сравнение слота с константой (`minimum_value` в post) | применяет | применяет | игнорирует | игнорирует |
| уровень класса `exactly_one_of` + `slot_conditions` | применяет | применяет | игнорирует | игнорирует |

Дополнительно:

- `gen-owl` включает правила как общие аксиомы включения классов (GCI); это не механизм валидации (ADR-010).
- `gen-pydantic` с `metadata_mode` по умолчанию записывает правила только в `linkml_meta` (документация); проект генерирует контракты с `MetadataMode.NONE` (`scripts/generate_contracts.py`), поэтому в `generated/contracts` правил нет.
- `gen-shacl`: исходный код `linkml/generators/shaclgen.py` не содержит обработки `rules`, `slot_conditions`, `exactly_one_of`, `sparql`. Выход графа **изоморфен** с правилами и без них для всех 14 шаблонов. Опции `--no-emit-rules` в 1.11.1 **нет** (доступны `--closed/--non-closed`, `--include-annotations`, `--exclude-imports`, `--use-class-uri-names`, `--expand-subproperty-of`, `--metadata`, `--useuris`, `--mergeimports`). Следствие для L3: все инварианты уровня L1 для RDF нужно описывать ручными SHACL-формами.
- При генерации печатается `ignoring equals_string=... as unable to tell if literal` (генератор не различает литерал и значение enum). Это предупреждение, не ошибка.

## 3. Найденные ограничения и дефекты LinkML 1.11.1

### 3.1. `equals_string` на булевом слоте

`equals_string: "true"` превращается в JSON Schema `const: "true"`, а тип слота `boolean`. Валидное значение `true` отклоняется (`'true' is not of type 'boolean', 'null'`). Затрагивает правило `ConceptualProperty` №0 (INV-001): по `gen-json-schema` и `linkml-validate` экземпляр с `property_kind: identifying` и `is_identifying: true` **не может быть валидным**.

### 3.2. `value_presence: ABSENT` на нескольких слотах

Несколько слотов в `postconditions` превращаются в `then: {not: {required: [a, b, ...]}}`, то есть «не все слоты присутствуют одновременно». Наличие одного запрещённого слота не нарушает правило. Подтверждено на правилах `SchemaNode` №1, `DataCarrier` №0, `AccessPoint` №1 (`real-rules.json`: единичное нарушение принято, одновременное присутствие всех слотов отклонено). Обход: отдельное правило на каждый запрещённый слот (решение для PR-C2 после согласования; условия существующих правил в PR-C1 не меняются).

### 3.3. Сравнение двух слотов невозможно

В `slot_conditions` нет оператора сравнения со значением другого слота. `equals_expression` внутри правила игнорируется всеми четырьмя проверенными генераторами. Инварианты вида «`scale <= precision`», «`valid_from <= valid_to`» только на уровне L2 (и ручной SPARQL на L3).

### 3.4. `deactivated: true` не учитывается JSON Schema

Правило с `deactivated: true` продолжает применяться в `gen-json-schema` / `linkml-validate`. Выключать правило нужно удалением (с записью в матрице), а не флагом.

### 3.5. `inapplicable`

В метамодели 1.11.1 нет поля `inapplicable` ни у `ClassRule`, ни у `SlotDefinition` (`TypeError: ... unexpected keyword argument 'inapplicable'`). Доступны: `preconditions`, `postconditions`, `elseconditions`, `bidirectional`, `open_world`, `rank`, `deactivated`. «Неприменимость» выражается `value_presence: ABSENT`.

### 3.6. `Validator(schema)` без плагинов ничего не проверяет

`linkml.validator.Validator(schema)` при `validation_plugins=None` не запускает ни одного плагина. Проверено в `apps/cli/.venv` (Python 3.14.4, linkml 1.11.1): заведомо некорректный экземпляр `DataModelBinding` даёт 0 результатов, с `JsonschemaValidationPlugin(closed=True)` даёт 2. Вызов без плагинов используют `scripts/validate-schemas.ps1`, `scripts/validate-examples.ps1`, `scripts/validate-requirements.ps1`, `packages/standard-linkml/.../adapters/validator.py`, `.../ingest/validate.py`, `packages/specification-dams/tests/test_catalog_validate.py`. Пока это не исправлено, шаги `validate-*` в `make check` не проверяют схему. CLI `linkml-validate` по умолчанию использует `JsonschemaValidationPlugin` с `closed: true` и такой проблемы не имеет. Вынесено в открытые вопросы отчёта (блокер для режима negative в PR-C2).

## 4. Правило выбора уровня (сводка для ADR-045)

| Класс инварианта | L1 `rules` | L2 валидатор | L3 SHACL |
|---|---|---|---|
| условие внутри одного экземпляра, `equals_string` / `value_presence` / `any_of` / `pattern` | да | дублирование допустимо | форма вручную |
| условие с булевым слотом через `equals_string` | нет (§3.1) | да | форма вручную |
| запрет нескольких слотов | по одному правилу на слот (§3.2) | да | форма вручную |
| сравнение двух слотов | невозможно (§3.3) | да | SPARQL вручную |
| ссылки между объектами, уникальность, циклы | невозможно | да | SPARQL / `sh:class` вручную |

## 5. Влияние `INV-xxx` в `description` правила на golden

Эксперимент `spike_inv_prefix.py`: копия схем с префиксом `INV-NNN:` в `description` всех 17 правил, прогон генераторов `generate_artifacts.py` + pydantic-контракты.

| Артефакт | Меняется |
|---|---|
| `schema_digest` (хэшируется только корневой `moex-dams.yaml`) | нет |
| JSON Schema, pydantic-контракты (`MetadataMode.NONE`), Python, DBML, OWL, SHACL, Mermaid | нет |
| Документация `DocGenerator` (`generated/artifacts/moex-dams/0.1/docs`) | **да**: 8 страниц из 480 (`AccessPoint`, `ConceptualDomain`, `ConceptualProperty`, `DataCarrier`, `DataStructure`, `DataType`, `SchemaNode`, `ValueDomain`) |

Страницы `DocGenerator` содержат YAML определения класса вместе с `rules`, поэтому меняется `content_digest` артефакта `doc` и, каскадом, дайджест бандла. По условию серии это остановка: обновление golden в PR-C2 только отдельным коммитом и после подтверждения пользователя.
