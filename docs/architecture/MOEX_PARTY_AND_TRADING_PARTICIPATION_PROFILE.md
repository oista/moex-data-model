---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# MOEX Party & Trading Participation (enterprise conceptual slice)

Status: draft · ADR-021 · package
[`moex-enterprise-conceptual-model@0.1`](../../model-assets/implementations/enterprise/moex-enterprise-conceptual-model/0.1/)

## Why LegalEntity + TradingParticipation (not a single Customer)

A MOEX client is an organization / legal entity that may hold **multiple**
admissions, roles, agreements, accounts, and lifecycle states across venues and
sections. Modeling “TradingParticipant” only as a subclass of `LegalEntity`
collapses those dimensions into one type and cannot express concurrent
participations.

Canonical pattern:

```text
LegalEntity ──hasTradingParticipation──► TradingParticipation
TradingParticipation ──admittedTo──► TradingVenue
TradingParticipation ──appliesTo──► TradingSection
```

`TradingParticipation` is a **reified relationship entity**, not an alias of
`LegalEntity`. A derived view label “TradingParticipant” may be added later;
it is not the SoT.

## MOEX-local vs external FIBO

| Layer | Role |
|---|---|
| ExternalSpecificationScope | Search boundary (FND/BE/FBC); **not** an import |
| ExternalTermSelection | Reviewable FIBO term set + mappings |
| Enterprise conceptual | MOEX SoT concepts (`dams:concept/…`) |
| Solution Impl | Local logical/physical; `realizes` enterprise |
| ontology-application | OWL extension (no `dams_model_level`) |

Local extension concepts (no default FIBO equivalence): `TradingParticipation`,
`TradingSection`, `Admission`, `RegistrationAction`, `AccountRelationship`.

## Why SEC is out of scope

SEC (and DER, IND, MD, …) are deferred until instrument / issuer / listing
modeling. Including them would pull securities-domain terms into a party /
admission slice without governance.

## Mapping policy

- Default external alignment: `skos:closeMatch` / `aligns_with` as **candidate**
  until approved review.
- `owl:equivalentClass` only with approved review (selection validator).
- Solution → enterprise: `mapping_type: realizes`.
- Physical ↔ logical: `field_mapping` (mapsTo).

## draft-conformant

First slice is `draft-conformant` / `partially-reviewed`: enterprise concepts
are published; FIBO term decisions and extracted modules remain incomplete.
Not production-conformant.

## Future CSV / DSP inference

Enterprise concepts and MOEX CVs are intended to ground later import inference
for fields such as: `lei`, `inn`, `participant_code`, `admission_status`,
`trading_section`, `agreement_number`, `account_number`, `registration_action`,
`document_reference` — without binding ExternalTermSelection to solution tables.
