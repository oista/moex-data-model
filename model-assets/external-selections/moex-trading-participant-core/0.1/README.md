# MOEX Trading Participant Core — External Term Selection

Governance package for curated FIBO terms used in trading participant
onboarding and admission (ADR-020).

## Distinctions

| Concept | Meaning here |
|---|---|
| **Scope ≠ import** | Parent scope lists FND/BE/FBC as search boundaries only |
| **Selection ≠ full FIBO domain** | Only reviewed terms in `selection.yaml` |
| **Extracted module ≠ extension ontology** | Planned ROBOT module ≠ [moex-fibo-application](../../../implementations/ontologies/moex-fibo-application/0.1/) |
| **Mapping ≠ owl equivalence** | Default is `skos:closeMatch`; `owl:equivalentClass` needs approved review |

## Seed rule (draft)

This selection is `draft_only: true`. Seed roles on `candidate` terms emit
validation **warnings**. Production/published selections require
`decision: accepted` and `review_status: approved` for seeds.

## Files

- `selection.yaml` — selection body, CQ, terms, mappings, plan
- `extraction-plan.yaml` — ROBOT STAR plan (`output_status: planned`)
- `seeds/fibo-seed-terms.txt` — confirmed seed IRIs only
- `mappings/moex-fibo-mappings.yaml` — mapping register sidecar
- `publish.yaml` — Publication Viewer contract
