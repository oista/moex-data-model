---
id: governance
sources:
  - docs/adr/ADR-023-governed-property-cascade.md
  - docs/adr/ADR-049-governance-assignment-authority.md
  - docs/adr/ADR-056-requirements-backbone.md
draft: true
---

# Кто за что отвечает

У элемента модели можно записать, кто им владеет, как он классифицирован и какие правила на него действуют. Если своей записи нет, значение берётся у объемлющего элемента. Цепочка зависит от того, о каком слое речь.

В модели решения она идёт от [модельного пакета](glossary:model-package) к [логической сущности](glossary:logical-entity) и дальше к её свойству. В общей модели предприятия — от пакета к [понятийной сущности](glossary:conceptual-entity). В техническом описании — от пакета к [техническому объекту](glossary:technical-asset), затем к [структуре данных](glossary:data-structure) и к [узлу структуры](glossary:schema-node).

По этим цепочкам приходят владелец, классификация и ссылки на правила. Класс данных и система-источник переходят только от логической сущности к её свойству. [Назначение ответственности](glossary:governance-assignment) их не перекрывает.

Назначение — отдельная утверждённая запись со сроком действия. Она покрывает один элемент или его вместе с вложенными. Для владельца, классификации и правил ближайшая такая запись побеждает значение на элементе. Две утверждённые записи на один и тот же элемент с разным смыслом в одно время — ошибка: проверка не выбирает одну из них наугад.

То, что видит читатель, — [действующая ответственность](glossary:effective-governance). Её собирают на дату проверки и в файл модели руками не записывают.

Значение по умолчанию пишут в том же файле пакета: `data_owner_ref`, `governance_classification`, `policy_refs`. Назначение — списки `ownership_assignments`, `classification_assignments` и `policy_bindings` в этом же файле. Короткий пример — `model-assets/specifications/moex-dams/0.1/examples/governance-assignments.example.yaml`. Свежесть действующей картины проверяет `make check-governance`. Шаг входит в общую `make check`.

Где прочитать решение: [ADR-023](docs/adr/ADR-023-governed-property-cascade.md), [ADR-049](docs/adr/ADR-049-governance-assignment-authority.md), [ADR-056](docs/adr/ADR-056-requirements-backbone.md).
