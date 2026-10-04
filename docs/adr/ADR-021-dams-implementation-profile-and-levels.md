---
status: Proposed
version: "0.1"
date: 2026-09-28
---

# ADR-021: DAMS-specific implementation profile and model levels

## Context

`SpecificationImplementation` is a shared envelope for many kinds of
implementations (DAMS ModelPackage, OWL application ontology, future API
profiles, data contracts). Package-level **enterprise-conceptual** vs
**solution** layers apply only to MOEX DAMS data-model implementations.

Conflating those levels with FIBO application ontologies, ExternalTermSelection,
or publication `profile:` (ADR-016) would force non-DAMS packages into the wrong
semantics.

## Decision

1. Add optional envelope fields (orthogonal to `implementation_kind` /
   `StandardFamily` and to ADR-016 publish `profile` / `implements.profile_ref`):

   - `implementation_profile`: `dams-data-model` | `ontology-application` |
     `api-specification` | `data-contract` | `other`
   - `dams_model_level`: `enterprise-conceptual` | `solution`

2. Rules:

   - `dams-data-model` ⇒ `dams_model_level` required
   - any other profile ⇒ `dams_model_level` forbidden
   - legacy envelopes without `implementation_profile` ⇒ soft warning only

3. Do **not** introduce `domain-logical` as a package level.

4. Relation separation:

   | Relation | Meaning |
   |---|---|
   | `implements` / `conforms_to` | SpecImpl → ReferenceSpec / publication contract |
   | `realizes` | solution element → enterprise conceptual entity |
   | `field_mapping` (mapsTo) | physical ↔ logical |
   | `aligns_with` | enterprise conceptual ↔ external term (projection / selection) |
   | `external_class_refs` | Canonical ConceptualEntity → external class/term with `match_kind` (ADR-026) |

5. Canonical fixtures:

   - `moex-enterprise-conceptual-model@0.1` — enterprise SoT (Party slice)
   - `trading-platform` — solution realizing enterprise
   - `moex-fibo-application` — `ontology-application` (no dams level)

6. ExternalTermSelection (ADR-020) targets enterprise conceptual entity ids
   (`dams:concept/…`), not solution tables.

## Consequences

- Publication profiles: `dams-enterprise-conceptual`; `dams-solution` aliases
  `dams-logical-and-physical`.
- Element-level `ModelLevelEnum` (conceptual/logical/physical) unchanged.
- Name collision risk: document `implementation_profile` ≠ publish `profile`.

## Related

- ADR-016, ADR-018, ADR-019, ADR-020, ADR-026
- [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)
- [MOEX_PARTY_AND_TRADING_PARTICIPATION_PROFILE.md](../architecture/MOEX_PARTY_AND_TRADING_PARTICIPATION_PROFILE.md)
