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
