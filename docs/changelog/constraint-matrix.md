---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# Changelog: executable constraint matrix (ADR-045)

Журнал серии PR-C0..C5. Тексты инвариантов не дублируются: см. матрицу (с PR-C1) и [constraint-matrix-inventory-report.md](../architecture/constraint-matrix-inventory-report.md).

## PR-C0: инвентаризация и spike (схемы и `generated/**` не менялись)

**Добавлено**

- `scripts/inventory_invariants.py`, `docs/architecture/invariant-candidates.csv` (150 кандидатов).
- [ADR-045](../adr/ADR-045-executable-constraint-matrix.md) (Proposed) и строка в индексе ADR.
- [linkml-rules-support.md](../architecture/linkml-rules-support.md): таблица «правило x генератор», версия LinkML 1.11.1.
- [constraint-matrix-inventory-report.md](../architecture/constraint-matrix-inventory-report.md): 17 существующих правил, прочие кандидаты, расхождения, вопросы.
- Spike: `tmp/constraint-spike/`.

**Стало строже:** ничего.

**Затронутые данные:** нет.

**Найдено (не исправлялось, см. вопросы Q1-Q8 отчёта):** `Validator(schema)` без плагинов в `validate-*` не проверяет данные; INV-001 неисполним в JSON Schema; `ABSENT` на нескольких слотах ослаблен (INV-013, INV-015, INV-017); CRLF в `requirements-linkml.txt` ломает golden на Windows.

## PR-C1a: validation helper (основа для negative-режима)

**Добавлено**

- `moex_standard_linkml.validation.make_linkml_validator` + `error_results`.
- Проводка в `adapters/validator.py`, `ingest/validate.py`, `validate-examples.ps1`, `validate-schemas.ps1`.
- Тесты `packages/standard-linkml/tests/test_validation_helper.py`.
- Отчёт [validation-helper-c1a-report.md](../architecture/validation-helper-c1a-report.md): список данных, которые станут невалидными; таблица `source_status` для INV-001..017.

**Стало строже:** примеры и ModelPackage реально проверяются JSON Schema (closed); xlsx-ingest больше не пишет `name` на `Mapping`.

**Затронутые данные:** `requirements/examples/it-solution-model.example.yaml` (убран `name` у mappings).

**Отложено:** `validate-requirements` остаётся на vacuous `Validator` — каталог `it-solution-requirements.yaml` даёт 18 ошибок под плагином (`description`/`effective` на FormalCheck). См. отчёт C1a.

## PR-C1: constraint matrix

**Добавлено**

- `model-assets/.../constraints/constraint-matrix.schema.yaml` + `constraint-matrix.yaml` (INV-001..027).
- `scripts/check_constraint_matrix.py`, цель `check-constraints` в Makefile и `scripts/check_all.py`.
- Автогенерируемый [constraint-matrix.md](../architecture/constraint-matrix.md).
- Руководство [adding-an-invariant.md](../guides/adding-an-invariant.md).
- Тесты `packages/specification-dams/tests/test_constraint_matrix.py`.
- Пин `ruamel.yaml==0.18.10` в `requirements-linkml.txt` + обновление `toolchain_digest` бандла.

**Стало строже:** любой новый `rules` в схемах без строки матрицы ломает `check-constraints`; baseline 17 правил закреплён SHA + sha256.

**Статусы:** INV-001..017 = `implemented-untested`; INV-018..027 = `planned` (нумерация закреплена).

**Затронутые данные:** нет правок условий LinkML `rules`.

## PR-C2: L1 INV-prefix + negative fixtures

**Добавлено**

- Префикс `INV-NNN:` в `description` 17 существующих `rules` (условия не менялись).
- `examples/invariants/` — 17× valid/invalid + `manifest.yaml`; negative-режим в `validate-examples.ps1`.
- Пути `tests.l1_*` в матрице; тест `test_invariant_l1_fixtures.py`.

**Стало строже:** `validate-examples` требует, чтобы invalid-фикстуры отвергались JSON Schema.

**Версия схемы:** предложен **PATCH** (только описания rules; ограничений не добавлено). Версию `3.0.0` не бампим без подтверждения.

**Golden:** префикс меняет артефакт `doc` (`content_digest`) — отдельный коммит после подтверждения (Q6).

**Не сделано в C2 (ждут решения):** правка INV-001 (boolean `equals_string`); разбиение multi-ABSENT (INV-013/015/017); новые L1 для INV-018+.
