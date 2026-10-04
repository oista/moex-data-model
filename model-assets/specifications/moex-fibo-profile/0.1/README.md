# FIBO ontology profile (MOEX) — lean metamodel projection

This specification asset describes the **organizational metamodel** of FIBO
(domains, modules, ontology headers, IRI/annotation conventions). Normative
structure lives under `metamodel/*.yaml` (ADR-014).

Publication (ADR-024) also surfaces an OWL **class index** and **glossary**
as two views of the same preview rows from
`packages/ontology/publications/fibo_glossary.preview.csv` — not authored in
profile YAML.

- Guide: https://github.com/edmcouncil/fibo/blob/master/ONTOLOGY_GUIDE.md
- Decision: [ADR-014](../../../../docs/adr/ADR-014-fibo-profile-metamodel.md)
- Unified Class: [ADR-024](../../../../docs/adr/ADR-024-unified-class-entity.md)
- OWL validation stance: [ADR-010](../../../../docs/adr/ADR-010-owl-not-primary-validation.md)

Governed application / extension content lives in `moex-fibo-application`
(`specification_implementation`). Upstream release preview also appears as
`moex:module:fibo`.
