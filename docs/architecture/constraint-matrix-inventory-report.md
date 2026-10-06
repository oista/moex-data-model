---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# Constraint matrix inventory report (ADR-045, PR-C0)

**Date:** 2026-10-06  
**Schema:** `model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml` (`version: 3.0.0`), схема в PR-C0 **не менялась**  
**ADR:** [ADR-045](../adr/ADR-045-executable-constraint-matrix.md)  
**Таблица «правило × генератор»:** [linkml-rules-support.md](linkml-rules-support.md)  
**Кандидаты (автоматически):** [invariant-candidates.csv](invariant-candidates.csv) (150 строк)  
**Скрипт:** `scripts/inventory_invariants.py` (`--csv`, `--list-rules`); spike: `tmp/constraint-spike/`

Тексты инвариантов хранятся в матрице (PR-C1). Этот отчёт ссылается на источники и фиксирует предложение по уровням; предложенные уровни подлежат проверке пользователем до PR-C1.

## 1. Окружение и базовый прогон

| Параметр | Значение |
|---|---|
| ветка | `feat/constraints-c0-inventory` от `feat/model-element-pr6-mapping-3.0.0` (`5b57c32`) |
| `linkml`, `linkml-runtime` | 1.11.1, 1.11.1 (`requirements-linkml.txt`) |
| `pyshacl` | 0.40.1 (`requirements-ontology.txt`) |
| `ruamel.yaml` | 0.18.17 глобально; `apps/viewer` требует `==0.18.10`; в `requirements-linkml.txt` не закреплён |
| Python по умолчанию (`python`) | 3.10.6 |
| Python в `.python-version` | 3.12 |
| Python, которым прогнан `check_all.py` | `apps/cli/.venv/Scripts/python.exe`, **3.14.4** (строка `check_all: python=` в логе) |
| `make` | не найден в PATH; эквивалент `make check` = `python scripts/check_all.py` |

Результат `python scripts/check_all.py --keep-going`:

| Шаг | Результат |
|---|---|
| generate-contracts | OK |
| slice-cli | OK (после локальной правки LF, см. ниже) |
| validate-schemas | OK |
| validate-examples | OK |
| validate-requirements | OK |
| compare-golden | OK (после локальной правки LF) |
| architecture-check | OK |
| publish-gate | OK |

**Базовый прогон был красным** (`slice-cli`: 2 теста publish-gate; `compare-golden`: `bundle digest mismatch`). Причина: `requirements-linkml.txt` входит в golden как `toolchain_digest` (sha256 байтов файла); в закоммиченном манифесте это дайджест LF-блоба (`142f4b53...`), а рабочая копия на этой Windows-машине в CRLF (`core.autocrlf=true`, в `.gitattributes` только `* text=auto`), дайджест `48fcd82f...`. Локальный обход без изменения репозитория: строка `requirements-linkml.txt text eol=lf` в `.git/info/attributes` и повторная выгрузка файла. Постоянное решение (строка в `.gitattributes`) вне темы серии: открытый вопрос Q3.

## 2. Охват схем

14 файлов в `.../moex-dams/0.1/schemas/`: корневой `moex-dams.yaml` и 13 импортируемых модулей:

`moex-types`, `moex-registries`, `moex-base`, `moex-governance`, `moex-core`, `moex-technical`, `moex-semantic`, `moex-datatypes`, `moex-structure`, `moex-integration`, `moex-contract-binding`, `moex-analytics`, `moex-requirements`.

Число «13» из задания соответствует импортируемым модулям без корня. `model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml` не схема-источник, а сгенерированная плоская копия всех 14 файлов (`# Generated ... Do not edit by hand`); она содержит те же 17 правил и в инвентаризацию не входит. Схемы `moex-dsp` и `moex-external-alignment` вне охвата (правил нет); поле `scope` в матрице (PR-C1) позволит добавить их без смены формата.

## 3. Инварианты, уже выраженные правилами LinkML (17 правил в 9 блоках `rules`)

Задание исходит из того, что `rules` в схемах нет. В действительности 17 правил есть, но без `INV-xxx` в `description` и вне матрицы. Они идут в матрицу первыми, **без изменения условий**. Номера присвоены в порядке `--list-rules` (файл, класс, индекс).

| ID | Правило (файл, класс, индекс) | Источник | Предлагаемые уровни | Уже есть на L2 (код) | Поведение JSON Schema / `linkml-validate` |
|---|---|---|---|---|---|
| INV-001 | `moex-core` `ConceptualProperty` #0: `property_kind=identifying` требует `is_identifying` | ADR-034:58; описание слота `is_identifying` | L2 + L3; L1 дефектен (Q1) | `semantic_layer.py:171` | **дефект**: `const: "true"` на boolean, valid `true` отклоняется |
| INV-002 | `moex-datatypes` `DataType` #0: `precision` только для `decimal` | описание слота `precision`; ADR-036 | L1 + L3 | `semantic_layer.py:370` | применяет |
| INV-003 | `DataType` #1: `scale` только для `decimal` | описание слота `scale` | L1 + L3 | `semantic_layer.py:381` | применяет |
| INV-004 | `DataType` #2: `max_length` только для `string`/`binary` | описание слота `max_length` | L1 + L3 | `semantic_layer.py:405` | применяет |
| INV-005 | `DataType` #3: `min_length` только для `string`/`binary` | описание слота `min_length` | L1 + L3 | `semantic_layer.py:405` | применяет |
| INV-006 | `ValueDomain` #0: `enumerated` требует `permissible_values` | ADR-035:28; описание `value_domain_kind` | L1 + L3 | `semantic_layer.py:306` | применяет |
| INV-007 | `ValueDomain` #1: `described` не содержит `permissible_values` | ADR-035:28 | L1 + L3 | `semantic_layer.py:315` | применяет |
| INV-008 | `ValueDomain` #2: `reference_set` не содержит `permissible_values` | ADR-035:28 | L1 + L3 | `semantic_layer.py:310,315` | применяет |
| INV-009 | `moex-semantic` `ConceptualDomain` #0: `described` не содержит `value_meanings` | ADR-035 | L1 + L3 | `semantic_layer.py:242` | применяет |
| INV-010 | `moex-structure` `DataStructure` #0: `source_pointer` требует `source_artifact_ref` | описание слота `source_pointer` («внутри `source_artifact_ref`»); ADR-038 | L1 + L3 | не найдено | применяет |
| INV-011 | `DataStructure` #1: `schema_dialect` только для `json_schema`/`openapi_schema` | ADR-038:44-51 | L1 + L3 | не найдено | применяет; **расхождение источника** (Q5) |
| INV-012 | `SchemaNode` #0: `array`/`map` требуют `item_node`, запрещают `children` | ADR-038:31; PDM-020 | L1 + L2 + L3 | `data_structure.py:358` (PDM-020.c1,c2) | применяет |
| INV-013 | `SchemaNode` #1: `scalar`/`enum` запрещают `children` и `item_node` | PDM-020 | L1 + L2 + L3 | `data_structure.py:358` (PDM-020.c3,c4) | **ослаблено**: нарушается только при одновременном наличии обоих слотов (Q2) |
| INV-014 | `SchemaNode` #2: `reference` требует `reference_target` | ADR-038:32; описание слота `reference_target` | L1 + L3 | не найдено | применяет |
| INV-015 | `moex-technical` `DataCarrier` #0: `in_memory` без `location_uri` и `region` | PDM-012 | L1 + L2 + L3 | `technical_assets.py:424`, `formal_checks.py:588` | **ослаблено** (Q2) |
| INV-016 | `AccessPoint` #0: `operation` требует `interface_ref` | PDM-011; описание слота `interface_ref` | L1 + L2 + L3 | `technical_assets.py:400` | применяет |
| INV-017 | `AccessPoint` #1: `interface` без `operation_name`, `http_method`, `path_template`, `message_refs` | ADR-040:40-41 (только `message_refs`); PDM-018 | L1 + L2 + L3 | `data_structure.py:478` (только `message_refs`) | **ослаблено** (Q2) |

Пометка «Предлагаемые уровни» относится к матрице, а не к факту реализации: L1 у всех 17 есть сейчас; L3 для каждого нужно писать вручную, потому что `gen-shacl` 1.11.1 правила не переносит (см. `linkml-rules-support.md`, §2).

## 4. Прочие кандидаты в инварианты (из `invariant-candidates.csv`, после ручного отбора)

Отобраны формулировки, которые (а) не выражены `required`/`range`/`pattern`, (б) имеют источник. Нумерация предварительная, окончательно закрепляется в матрице PR-C1. «Реализация» указывает то, что подтверждено чтением кода; остальное проверяется в PR-C3.

| ID | Инвариант | Источник | Уровень | Реализация |
|---|---|---|---|---|
| INV-018 | `direction` запрещён для `DataContainer` и `ExecutionAsset` | `moex-technical.yaml:93,186,201`; PDM-008 | L1 (`rules` на подклассах) + L2 | L2 есть (PDM-008); в `description` заявлено «LinkML rules», но правила в схеме нет |
| INV-019 | `message_refs` допустимы только у `AccessPoint` kind `operation`/`channel` | `moex-structure.yaml:303`; ADR-040:40-41; PDM-018 | L2; L1 покрывает только `interface` (INV-017) | L2 есть (`data_structure.py:478`) |
| INV-020 | рёбра `children`/`item_node` не образуют циклов | ADR-038:32; PDM-014 | L2 (+ L3 SPARQL) | L2 есть (`data_structure.py:175`) |
| INV-021 | реляционные признаки узла только при `schema_format=relational` | ADR-038:40-42; PDM-016 | L2 (узел не знает родителя) | L2 есть (`data_structure.py:292`) |
| INV-022 | `local_key` уникален внутри `DataStructure` | ADR-038; PDM-013 | L2 | L2 есть (`data_structure.py:143`) |
| INV-023 | `dams_model_level` допустим только для профиля `dams-data-model`; `implementation_scope` согласован с ним | ADR-021:32; `moex-core.yaml:300` | L2 | L2 вероятно в `dams_levels.py` (проверить) |
| INV-024 | `scope_ref` для `scope_kind=system` входит в `ITSolution.member_system_refs` | `moex-governance.yaml:248`; ADR-025:112 | L2 | не проверено |
| INV-025 | значения `tags` только из реестра переходных тегов | ADR-043:28,35 | L2 | residue-тест по ADR-043:35 (проверить) |
| INV-026 | URI префикса оканчивается на `/` или `#` | ADR-030:40 | L1 `pattern` или L2 | L2 есть (`ontology_uris.py:93`) |
| INV-027 | владелец пакета (`data_owner_ref`) задан; у логической сущности есть эффективная классификация | ADR-023:73-74 | L2 (каскад) | не проверено |

Каталог требований `it-solution-requirements.yaml` (ADR-013, 44 требования `GEN/LDM/ATR/REF/PDM/CLS/FLW`, проверки `formal_checks`) уже исполняемо выражает инварианты уровня L2 с кодами `DAMS-REQ-*`. Отдельную параллельную систему не создаём: запись матрицы на уровне L2 ссылается на существующий код требования (Q4).

Формулировки со словом «должен» из `IT_SOLUTION_MODEL_REQUIREMENTS.md` (47 из 150 кандидатов) и ADR 013/016/019/024 (профили секций публикации, `required`/`forbidden` kinds) относятся к каталогу требований и publication-профилям. Они не дублируются в матрице. Прочие кандидаты (UI, архитектурные границы пакетов: ADR-005, 007, 015, 022, kernel-agnostic) относятся к `architecture-check`, а не к модели данных.

## 5. Результаты spike (подробности в `linkml-rules-support.md`)

| Пункт | Результат |
|---|---|
| (a) `preconditions`/`postconditions` + `slot_conditions` (`required`, `value_presence`, `equals_string`, `any_of`, `pattern`) | JSON Schema и `linkml-validate` применяют, `gen-pydantic` и `gen-shacl` игнорируют |
| (b) `elseconditions` | то же |
| (c) `inapplicable` | поля нет в метамодели 1.11.1; `TypeError` при загрузке. Заменяется `value_presence: ABSENT` |
| (d) `bidirectional` | применяется JSON Schema обеими сторонами |
| (e) сравнение двух слотов | невозможно: `equals_expression` игнорируется всеми генераторами |
| (f) `gen-shacl` | исходник без обработки `rules`; граф изоморфен с правилами и без; опции `--no-emit-rules` нет |
| `deactivated: true` | JSON Schema всё равно применяет правило |
| `Validator(schema)` без плагинов | **ничего не проверяет** (см. Q1) |
| `INV-xxx:` в `description` | меняется только артефакт `doc` (8 страниц `DocGenerator`), `schema_digest` и остальные артефакты нет |

## 6. Расхождения с исходным заданием

1. `rules` в схемах уже есть: 17 правил в 9 блоках.
2. База PR-C0 не `main`, а `feat/model-element-pr6-mapping-3.0.0` (решение пользователя); ветки серии ADR-044 запушены в `origin`.
3. `make` недоступен, эквивалент `python scripts/check_all.py`; используется Python 3.14.4 из `apps/cli/.venv`, а не 3.12 из `.python-version`.
4. Базовый `check_all` красный на Windows из-за CRLF в `requirements-linkml.txt` (см. §1); зелёный после локального LF.
5. В схемах условия записаны через `value_presence`, а не `required`; `required: true` встречается один раз (`AccessPoint` #0).
6. `gen-shacl` 1.11.1 не переводит правила в `sh:sparql` (и вообще никак), опции `--no-emit-rules` нет. В PR-C4 все формы L3 пишутся вручную.
7. Метамодель 1.11.1 не имеет `inapplicable`.
8. Схем в `schemas/` 14, а не 13 (13 импортируемых + корневой).
9. `docs/guides/` и корневого `CHANGELOG` нет; журнал серии: `docs/changelog/constraint-matrix.md`.
10. Пин `ruamel.yaml` в `requirements-linkml.txt` меняет `toolchain_digest` и, как следствие, golden `moex-dams-bundle.json` (в PR-C0 diff по `generated/**` должен быть пуст). Пин перенесён в начало PR-C1 отдельным коммитом вместе с пересчётом манифеста бандла (Q3).

## 7. Открытые вопросы и решения, нужные от пользователя

| # | Вопрос | Предложение |
|---|---|---|
| Q1 | Все шаги `validate-*` и адаптеры вызывают `Validator(schema)` без плагинов и ничего не проверяют; режим negative (PR-C2) и тесты L1 на этом не работают. Кроме того, INV-001 в JSON Schema неисполним для валидных данных | Перед PR-C2 отдельный PR: общий хелпер с `JsonschemaValidationPlugin(closed=True)` и замена вызовов; список данных, которые станут невалидными, показывается до правок. Исправление INV-001 (булев слот) только в PR-C2 с вашего решения |
| Q2 | `value_presence: ABSENT` на нескольких слотах ослаблен в JSON Schema (`not required [все]`): INV-013, INV-015, INV-017 | В PR-C2 заменить одним правилом на слот (меняет семантику, не в C1) либо принять и закрыть L2/L3; нужно ваше решение |
| Q3 | CRLF в `requirements-linkml.txt` ломает golden на Windows; пин `ruamel.yaml` меняет golden бандла | Добавить `requirements-linkml.txt text eol=lf` в `.gitattributes` отдельным chore-коммитом; пин `ruamel.yaml==0.18.10` (как в `apps/viewer`, без конфликта) в начале PR-C1 вместе с пересчётом манифеста; подтвердить версию (0.18.10 вместо 0.18.17) |
| Q4 | Каталог требований (`DAMS-REQ-*`) уже содержит исполняемые проверки L2 | В матрицу добавить поле `requirement_refs`; в `source` указывать код требования; подтвердить |
| Q5 | Источник INV-011 допускает `schema_dialect` для AsyncAPI Multi Format Schema, правило ограничивает `json_schema`/`openapi_schema`; для INV-010, INV-017 (кроме `message_refs`), INV-014 текстового источника нет, только описание слота | Оставить как есть; отметить в матрице `source_status: partial`; нужна проверка владельцем модели |
| Q6 | INV-xxx в `description` в PR-C2 изменит `content_digest` артефакта `doc` (8 страниц) и дайджест бандла | Условие остановки из задания: подтвердить, что обновление golden (отдельный коммит с diff) допустимо |
| Q7 | Уровни L1/L2/L3 в таблицах §3-§4 | Проверить до PR-C1 |
| Q8 | Статусы матрицы: `planned` / `implemented-untested` / `implemented` / `waived`; baseline фиксируется точным перечнем 17 правил (файл, класс, индекс) с SHA базового коммита и sha256 списка | Принято в плане |
