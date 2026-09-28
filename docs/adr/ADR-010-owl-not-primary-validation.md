---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR-010: OWL не применяется как основной механизм validation

**Date:** 2026-09-28  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Workbench detail:** [linkml_architecture.md](../architecture/linkml_architecture.md) «Ontology Engine»  
**Catalog:** [ontology-catalog.md](../architecture/ontology-catalog.md)

## Context

OWL/open-world и LinkML closed-world constraints отвечают на разные вопросы. Если валидировать YAML instances через OWL reasoner, допустимые по DAMS данные могут «пройти» из-за open world, а невалидные — не пойматься. Ontology Catalog — read-only слой над OWL, не редактор и не валидатор YAML.

## Decision

- **Основная проверка YAML/JSON instances** — LinkML validation + DAMS semantic rules (ADR-007).
- **RDF instances** — SHACL / pySHACL, когда появится RDF pipeline.
- **OWL** — reasoning, семантическая публикация, анализ непротиворечивости; **не** gate для решения «валиден ли ModelPackage».
- `gen-owl` / `gen-rdf` — derived artifacts (ADR-011), не канон.
- `linkml-owl` — optional experimental adapter, не зависимость ядра и не фундамент каталога.
- Catalog не копирует аксиомы в `OntologyEntity`; asserted hierarchy ≠ reasoner.

Изменение URI — breaking change (совместимость).

## Consequences

- Срез §13 не требует reasoner/SPARQL (уже так в ontology-catalog).
- Нельзя блокировать merge YAML только из-за OWL inconsistency без явной policy.
- OWL 2 — `ModelingStandard`; FIBO — `ReferenceSpecification`; без `OWL*` classes в kernel YAML.

## Alternatives

| Alternative | Почему нет |
|---|---|
| OWL reasoner как primary validator | open world vs DAMS constraints |
| SHACL вместо LinkML validate | другой носитель (RDF), не YAML authoring |
| Protégé-like editor в MVP | вне границы каталога |

## Related

- ADR-001, ADR-007, ADR-011, [ADR-014](ADR-014-fibo-profile-metamodel.md) (FIBO profile vs release content)
