---
id: add-invariant
sources:
  - docs/adr/ADR-045-executable-constraint-matrix.md
  - docs/guides/adding-an-invariant.md
  - docs/architecture/constraint-matrix.md
  - model-assets/specifications/moex-dams/0.1/constraints/constraint-matrix.yaml
  - scripts/check_constraint_matrix.py
  - scripts/check_all.py
draft: true
---

# Добавить инвариант

Инвариант здесь — это [код проверки](glossary:invariant-code), номер строки [матрицы проверок](glossary:constraint-matrix). Файл матрицы: `model-assets/specifications/moex-dams/0.1/constraints/constraint-matrix.yaml`. Текст правила живёт здесь. В остальных местах оставляют номер вида INV-001 и ссылку на матрицу (ADR-045). Читаемый перечень строк собран в [constraint-matrix.md](docs/architecture/constraint-matrix.md).

Новую строку добавляют в этот файл: что запрещено, какой уровень машины это выполняет и какой [отрицательный тест](glossary:negative-test) обязан не пройти. Уровень без такого теста считается несделанным. Саму строку гоняет `python scripts/check_all.py --only check-constraints`. Дописать правило в схему и не завести строку матрицы этот шаг не пропустит.

Порядок полей и уровней записан в [adding-an-invariant.md](docs/guides/adding-an-invariant.md). У этой инструкции в шапке статус Proposed. Приняты решение ADR-045 и сама матрица. По тексту инструкции нельзя рассказывать, будто он уже принят: где он разойдётся с матрицей, права матрица.

Где прочитать решение: [ADR-045](docs/adr/ADR-045-executable-constraint-matrix.md).
