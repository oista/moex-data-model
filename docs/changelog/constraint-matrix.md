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
