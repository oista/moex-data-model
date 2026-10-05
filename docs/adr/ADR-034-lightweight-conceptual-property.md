---
status: Accepted
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# ADR-034: Смысл и представление — облегчённый ConceptualProperty (вариант B)

**Date:** 2026-10-05  
**Status:** Accepted  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-021](ADR-021-dams-implementation-profile-and-levels.md), [ADR-023](ADR-023-governed-property-cascade.md), [ADR-025](ADR-025-definition-cascade-and-glossary.md), [ADR-026](ADR-026-cmd-entity-metamodel.md), [ADR-035](ADR-035-value-domains.md), [ADR-036](ADR-036-datatype-system.md), [ADR-037](ADR-037-attribute-semantics-migration.md)

## Context

`LogicalAttribute` смешивает смысл, представление (`logical_type`, `format_pattern`,
`value_set_ref`, `unit_code`, …) и контекст в сущности (`required`, кардинальность).
Нужен концептуальный слой свойств по ISO 11179, но без обязательности `concept_ref`
и без массового создания свойств для каждого атрибута.

## Decision

### Вариант B (принят)

Концептуальный слой остаётся преимущественно сущностным. `ConceptualProperty`
допускается **только** для значимых атрибутов и **всегда опционально**. Большая
часть атрибутов живёт только в логическом слое.

Альтернативы отклонены:

- **A** — без свойств (нельзя выразить identifying / cross-solution на КМД).
- **C** — полный набор свойств на каждый атрибут (нарушает минимальность).

### Критерии значимости (`SignificanceBasisEnum`)

`identifying`, `externally_aligned`, `cross_solution`, `regulatory`, `critical_data`,
`governance_anchor`, `explicit_decision` (требует `significance_rationale`).

### `critical_data_element`

Булев слот на `LogicalAttribute` — **единственный источник** признака CDE.
Термин CDE в реестр классификаций / `ClassificationAssignment` **не** вводится.
`significance_basis=critical_data` опирается на этот слот.

### Деприкация представления

Слоты `logical_type`, `format_pattern`, `value_set_ref`, `unit_code` получают
LinkML `deprecated` + `deprecated_element_has_possible_replacement`
(`logical_type` → `data_type_ref`; остальные → `value_domain_ref`). Удаление —
отдельный релиз (шаг 2).

### `key_attribute_refs` на ConceptualEntity

В реальных данных КМД не заполняется (ключи — у `LogicalEntity`). Слот **не**
перенацеливается на `ConceptualProperty`; идентифицирующие свойства — через
`is_identifying`.

### Модули

`ConceptualProperty` живёт в `moex-core.yaml` (рядом с `ConceptualEntity`).
`ConceptualDomain` — `moex-semantic.yaml`; типы/ValueDomain — `moex-datatypes.yaml`.

### Выравнивание (открыто)

Субъектом будущего `SemanticAlignment` может быть `ConceptualProperty` **или**
`LogicalAttribute`. В этой задаче `SemanticAlignment` не вводится.

## Consequences

- `concept_ref` никогда не обязателен; отсутствие не даёт diagnostic.
- Миграция (`--apply`) создаёт только типы/домены; свойства — только `--propose`.
- Пометки генерации — через `tags` (`generated`), не `annotations` (слота нет).
