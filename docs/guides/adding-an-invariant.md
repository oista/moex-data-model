---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# Как добавить инвариант (ADR-045)

Краткий порядок для серии constraint matrix. Текст инварианта живёт только в матрице; везде остальное — ссылка `INV-NNN`.

## 1. Запись в матрице

1. Откройте `model-assets/specifications/moex-dams/0.1/constraints/constraint-matrix.yaml`.
2. Добавьте объект в `invariants` с полями: `id`, `title`, `statement`, `source`, `source_status`, `scope`, `levels`, `severity`, `status`.
3. `status`:
   - `planned` — ещё не написано;
   - `implemented-untested` — есть реализация, нет негативного теста;
   - `implemented` — на каждом заявленном уровне есть valid и invalid, и invalid реально падает;
   - `waived` — только с `waiver_reason`.
4. При наличии проверки в каталоге ADR-013 укажите `requirement_refs` (`DAMS-REQ-*` / `PDM-*`).
5. Заполните `implementation` (`linkml_rule` / `dams_validator` / `shacl`) по выбранным уровням.

Схема полей: `constraint-matrix.schema.yaml`. Автотаблица: `docs/architecture/constraint-matrix.md` (пишет `check_constraint_matrix.py`).

## 2. Выбор уровня

| Условие | Уровень |
|---|---|
| Один экземпляр, `equals_string` / `value_presence` / `any_of` / `pattern` | L1 |
| Булев слот через `equals_string`, сравнение двух слотов, ссылки, уникальность, циклы | L2 (и/или ручной L3) |
| Нужна проверка в RDF | L3 вручную (`shacl/manual`, PR-C4); `gen-shacl` правила не переносит |

Подробности spike: [linkml-rules-support.md](../architecture/linkml-rules-support.md).

## 3. Реализация и тесты

- **L1:** блок `rules` в классе схемы; в `description` правила — префикс `INV-NNN:` (с PR-C2). Условия существующих 17 правил в C1 не менять.
- **L2:** валидатор рядом с `moex_dams/rules`, ссылка из матрицы; не дублировать каталог требований — ссылайтесь на `requirement_refs`.
- **L3:** ручная форма + pySHACL с `sh:sourceShape` на INV-NNN (PR-C4).
- Для `status: implemented` укажите пути в `tests` (`l1_valid` / `l1_invalid` …). Скрипт проверяет, что файлы есть.

## 4. Проверка

```text
python scripts/check_constraint_matrix.py
python scripts/check_all.py --only check-constraints
```

Baseline из 17 правил (`baseline.rules` + `rules_sha256`) нельзя расширять «тихим» добавлением `rules` в схему без новой строки матрицы: `check-constraints` упадёт.

## 5. Документация

- Changelog серии: [constraint-matrix.md](../changelog/constraint-matrix.md).
- Не копируйте `statement` в ADR — только `INV-NNN` и ссылка на матрицу.
