---
id: requirements
sources:
  - docs/adr/ADR-013-specification-requirements-catalog.md
  - docs/adr/ADR-045-executable-constraint-matrix.md
  - docs/adr/ADR-056-requirements-backbone.md
  - docs/architecture/constraint-matrix.md
  - model-assets/specifications/moex-dams/0.1/requirements/conceptual-model-requirements.yaml
  - model-assets/specifications/moex-dams/0.1/requirements/it-solution-requirements.yaml
  - model-assets/specifications/moex-dams/0.1/constraints/constraint-matrix.yaml
draft: true
---

# Требования и проверки

[Требование к модели](glossary:model-requirement) говорит, чему обязана соответствовать модель: что должно быть определено, связано и не противоречить спецификации. Каталог лежит рядом со спецификацией DAMS, в `model-assets/specifications/moex-dams/0.1/requirements/` (ADR-013).

Ствол каталога — [каркас требований](glossary:requirements-backbone): семнадцать правил (ADR-056). Два про понятийное описание (CDM-01 и CDM-02), тринадцать про логическое (LDM-01 … LDM-13) и два про техническое (PDM-01 и PDM-02). Раньше в том же каталоге встречался похожий номер другого вида, например LDM-001: это было другое правило, не LDM-01. Сейчас ствол записан короткими кодами. Кроме него в каталоге остаются два местных правила, LDM-101 и REF-002. Их номера к стволу не относятся.

Выполняет требования [проверка соответствия](glossary:conformance-check). Машина при этом смотрит [матрицу проверок](glossary:constraint-matrix) (ADR-045). Строка матрицы нумеруется [кодом проверки](glossary:invariant-code), вида INV-001. Этот номер кодом требования не является. Файл матрицы — `model-assets/specifications/moex-dams/0.1/constraints/constraint-matrix.yaml`. Читаемый перечень собран в [constraint-matrix.md](docs/architecture/constraint-matrix.md).

У правила в матрице до трёх уровней. Первый — условие внутри одного объекта, записанное в схеме. Второй — проверка связей между объектами в коде. Третий — проверка графового представления отдельными формами; в коде их называют SHACL. Сам из правил схемы этот уровень не появляется. Если для уровня нет [отрицательного теста](glossary:negative-test) — примера, который обязан не пройти, — уровень считается несделанным. Общая проверка репозитория смотрит матрицу и выполняет у правила только те уровни, которые там отмечены как сделанные.

Где прочитать решение: [ADR-013](docs/adr/ADR-013-specification-requirements-catalog.md), [ADR-045](docs/adr/ADR-045-executable-constraint-matrix.md), [ADR-056](docs/adr/ADR-056-requirements-backbone.md).
