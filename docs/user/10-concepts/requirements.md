---
id: requirements
sources:
  - docs/adr/ADR-013-specification-requirements-catalog.md
  - docs/adr/ADR-045-executable-constraint-matrix.md
  - docs/adr/ADR-056-requirements-backbone.md
  - docs/architecture/constraint-matrix.md
verified_at: 2026-11-02
---

# Требования и проверки

[Требование к модели](glossary:model-requirement) говорит, чему обязана соответствовать модель: что должно быть определено, связано и не противоречить спецификации. Требования лежат каталогом рядом со спецификацией DAMS, а не в тексте этой страницы.

Поверх каталога есть каркас нормативных правил по понятийному, логическому и физическому описанию. Коды этого каркаса и коды каталога похожи с виду, но смысл у них разный. Сверять их по номеру нельзя.

Выполняет требования [проверка соответствия](glossary:conformance-check). Машина при этом смотрит [матрицу проверок](glossary:constraint-matrix). В матрице три уровня: правило внутри одного объекта в схеме, проверка связей между объектами в коде и проверка RDF-представления. Уровень без отрицательного теста считается несделанным.

Где прочитать решение: [ADR-013](docs/adr/ADR-013-specification-requirements-catalog.md), [ADR-045](docs/adr/ADR-045-executable-constraint-matrix.md), [ADR-056](docs/adr/ADR-056-requirements-backbone.md).
