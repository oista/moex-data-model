---
status: Accepted
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# ADR-035: ConceptualDomain и ValueDomain

**Date:** 2026-10-05  
**Status:** Accepted  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-034](ADR-034-lightweight-conceptual-property.md), [ADR-036](ADR-036-datatype-system.md)

## Context

ISO 11179 разделяет Conceptual Domain (смыслы) и Value Domain (представление).
SKOS: `ConceptScheme` vs `Collection` не пересекаются; семантические связи SKOS
нельзя ставить на Collection.

## Decision

- `ConceptualDomain` ↔ `skos:ConceptScheme` (close); для плоских списков допустим
  `skos:Collection` только если нет иерархии `broader_meaning_key` — по умолчанию
  **ConceptScheme**.
- `ValueMeaning` ↔ `skos:Concept` (exact) с `skos:inScheme`.
- `ValueDomain` ↔ ISO 11179 Value Domain (close); виды: enumerated, described,
  reference_set; динамика через `ValueSetQuery` (образец LinkML `reachable_from`).
- Слоты `conceptual_domain_kind` / `value_domain_kind` разделены (разная семантика).
- Общие справочники (валюты, страны) заводить как ConceptualDomain только при
  реальной необходимости (несколько решений или внешнее выравнивание).
- ConceptualDomain / ValueMeaning — только `implementation_scope=enterprise`.
- ValueDomain — enterprise или solution; ссылка из решения не на домен другого решения.

IRI ISO 11179 не придумываются; соответствие — в `comments` и этом ADR.
