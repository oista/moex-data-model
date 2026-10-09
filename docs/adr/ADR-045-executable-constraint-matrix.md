---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# ADR-045: Executable constraint matrix

**Date:** 2026-10-06  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-007](ADR-007-pydantic-dto-not-validator.md), [ADR-010](ADR-010-owl-not-primary-validation.md), [ADR-013](ADR-013-specification-requirements-catalog.md), [ADR-038](ADR-038-datastructure-and-schemanode.md), [ADR-044](ADR-044-model-element-decomposition.md)  
**Inventory:** [constraint-matrix-inventory-report.md](../architecture/constraint-matrix-inventory-report.md), [invariant-candidates.csv](../architecture/invariant-candidates.csv)  
**LinkML support:** [linkml-rules-support.md](../architecture/linkml-rules-support.md)

## Context

Замечание аудита P0: инварианты модели описаны текстом (ADR, спецификация, `description` классов и слотов), но у большинства нет проверки, которую выполняет машина, а там, где проверка есть, её нельзя прослеживать до источника и до теста.

Фактическое состояние (инвентаризация PR-C0):

- В схемах DAMS 17 правил `rules` в 9 блоках; они не пронумерованы, не связаны с источником и не покрыты негативными тестами.
- Часть тех же инвариантов дублируется проверками DAMS (`packages/specification-dams/src/moex_dams/rules/*`) и требованиями каталога ADR-013 (`DAMS-REQ-*`), связи между ними нет.
- Для RDF-представления проверок нет: `gen-shacl` LinkML 1.11.1 правила не переносит.
- Шаги `validate-*` вызывают `Validator(schema)` без плагинов и фактически ничего не проверяют.

## Decision

### D1. Три уровня проверки

Каждый инвариант проверяется машиной на одном или нескольких уровнях. Уровень без негативного теста считается не реализованным.

| Уровень | Механизм | Область |
|---|---|---|
| **L1** | LinkML `rules` в классе схемы | условия внутри одного экземпляра |
| **L2** | DAMS-валидаторы (Python, `moex_dams/rules`, подключены в `architecture-check` и `publish-gate`) | ссылки между объектами, уникальность, графовые условия, сравнение значений |
| **L3** | SHACL (ручные формы + сгенерированные) | RDF-представление |

### D2. Матрица инвариантов

Единый реестр `constraint-matrix.yaml` (путь согласуется в PR-C1) с описанием в LinkML-схеме `constraint-matrix.schema.yaml`; валидируется тем же инструментом, что остальные данные. Запись:

- `id` (`INV-NNN`), `title`, `statement`, `source` (ссылка на ADR, раздел или `description`), `scope`, `levels`, `severity` (`error`/`warning`);
- `implementation` по уровням (`linkml_rule`, `dams_validator`, `shacl`), `requirement_refs` (коды `DAMS-REQ-*`, если проверка уже есть в каталоге ADR-013);
- `tests` (`valid`, `invalid` на каждом уровне);
- `status`: `planned` (ещё не написано), `implemented-untested` (работает в схеме, негативного теста нет), `implemented`, `waived` (обязателен `waiver_reason`).

Текст инварианта хранится только в матрице; документы, код и схемы ссылаются на `INV-NNN`.

### D3. Правила выбора уровня

1. Условие внутри одного экземпляра, выразимое через `equals_string`, `value_presence`, `any_of`, `pattern`: L1.
2. Ссылки между объектами, уникальность, циклы, сравнение двух слотов, версии и даты: L2.
3. Любой инвариант, который должен проверяться в RDF: L3 вручную, пока генератор не переносит правило (проверяется тестом, не предполагается).
4. L1 не используется, если spike показал неверное поведение генератора для данного шаблона (`equals_string` на булевом слоте; `ABSENT` на нескольких слотах без разбиения). Инвариант переносится на L2/L3 с записью в матрице.
5. Новое правило не ослабляет унаследованные ограничения (монотонность), все слоты в условиях имеют объявленный `range`.
6. Не создаётся параллельная система проверок: L2 размещается рядом с существующими валидаторами; запись матрицы ссылается на уже существующий код требования.

### D4. Контроль

Скрипт `scripts/check_constraint_matrix.py` (цель `check-constraints`): каждая запись `implemented` имеет существующую реализацию на каждом заявленном уровне; для каждой реализации есть valid и invalid пример, и invalid действительно не проходит на этом уровне; каждое правило в схемах имеет `INV-NNN` в `description` и запись в матрице; `waived` без причины ошибка. Baseline существующих 17 правил фиксируется точным перечнем (файл, класс, индекс), привязанным к SHA базового коммита и sha256 списка; увеличение числа правил вне матрицы ошибка.

## Limitations found by spike (LinkML 1.11.1)

Подробно и с таблицей: [linkml-rules-support.md](../architecture/linkml-rules-support.md).

- `gen-pydantic` и `gen-shacl` игнорируют `rules` (SHACL: исходник генератора не обрабатывает `rules`; `sh:sparql` не генерируется; опции `--no-emit-rules` нет). Применяют правила только `gen-json-schema` и `linkml-validate` (на JSON Schema).
- Сравнение двух слотов в `rules` невозможно.
- `equals_string` на булевом слоте даёт `const: "true"` и отклоняет валидное значение (дефект INV-001).
- `value_presence: ABSENT` на нескольких слотах означает «не все присутствуют одновременно» (ослабляет INV-013, INV-015, INV-017).
- `deactivated: true` игнорируется JSON Schema; `inapplicable` в метамодели нет.
- `Validator(schema)` без плагинов ничего не проверяет.
- `INV-xxx` в `description` правила меняет только артефакт `doc` (`DocGenerator`, 8 страниц), не `schema_digest` и не остальные артефакты.

## Consequences

- Серия PR-C0..C5: инвентаризация и spike; формат матрицы и проверяющий скрипт; L1; L2; L3; gate и закрытие. Один PR одна тема, не смешивается с рефакторингом `ModelElement` (ADR-044) и темой Work/Version/Distribution.
- Матрица становится обязательным шагом `publish-gate` (PR-C5); сокращение матрицы (удаление инварианта, перевод в `waived`) требует ссылки на ADR.
- Исправление `Validator` без плагинов может сделать красными данные, ранее проходившие «зелёными»; список затронутых файлов показывается до правок.
- Добавление и уточнение `rules` строго ужесточает схему; решение MINOR/MAJOR/PATCH принимается пользователем в PR-C2 по списку правил (только `INV-xxx` в `description` без новых ограничений PATCH; новые ограничения формально MAJOR).
- Обновление golden после `INV-xxx` в `description` в PR-C2 отдельным коммитом; при изменении `content_digest` (а не только `schema_digest`) остановка и подтверждение.
- ADR получает статус Accepted только после слияния всех PR серии и подтверждения пользователя.

## Open questions (C3)

### Q-INV-011 / AsyncAPI

Источник ADR-038 допускает `schema_dialect` для AsyncAPI Multi Format Schema; существующее LinkML-правило и L2-валидатор `check_schema_dialect_format_family` ограничивают семейство `json_schema` / `openapi_schema` (`source_status: divergent`). В PR-C3 правило **не** расширялось и **не** сужалось: L2 зеркалит L1. Решение (расширить правило, ослабить ADR или waiver) — за владельцем модели; до решения расхождение остаётся зафиксированным в матрице и в отчёте C3.

## Alternatives rejected

| Альтернатива | Причина |
|---|---|
| Только текст в ADR | не исполнимо, P0 остаётся |
| Только L1 | нет ссылок, уникальности, сравнения слотов, RDF |
| Дублировать каталог требований ADR-013 | параллельная система; матрица ссылается на `DAMS-REQ-*` |
| Полагаться на генерацию SHACL из `rules` | `gen-shacl` 1.11.1 не переносит правила |
