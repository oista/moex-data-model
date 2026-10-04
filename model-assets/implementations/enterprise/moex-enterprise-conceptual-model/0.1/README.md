# moex.concept-data-model (ADR-021)

Canonical **enterprise-conceptual** DAMS implementation for the Party +
trading/TKS + commercial/HR slices (ADR-029; ER sketches conceptualized
without PK/FK attributes). ABS / info-systems deferred.

## Distinctions

| Concept | Meaning here |
|---|---|
| **Enterprise conceptual ≠ solution** | No physical tables; solution Impls `realize` these entities |
| **TradingParticipation ≠ LegalEntity subclass** | Reified participation: one org, many venues/roles/statuses |
| **alignsWith ≠ implements** | External FIBO selection aligns to these concepts; SpecImpl `implements` damS |
| **MOEX CV ≠ FIBO terms** | Controlled vocabularies are moex-local |

## Scope disclaimer

Included FIBO search areas (FND/BE/FBC) live in
`ExternalSpecificationScope` — they do **not** import those FIBO domains into
this package.

## Profile

- `implementation_profile: dams-data-model`
- `dams_model_level: enterprise-conceptual`
- Publication contract: `dams-enterprise-conceptual`
