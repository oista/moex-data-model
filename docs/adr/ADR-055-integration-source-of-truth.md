---
status: Accepted
version: "0.1"
normative: true
supersedes: []
superseded_by: []
---

# ADR-055: Integration source of truth (audit Wave F)

**Date:** 2026-10-13  
**Status:** Accepted  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-040](ADR-040-message-integration-model.md), [ADR-048](ADR-048-topology-ownership.md), [ADR-051](ADR-051-dams-schema-compatibility.md), [ADR-052](ADR-052-identity-and-versioning.md), [ADR-053](ADR-053-qualified-assertion.md), [ADR-054](ADR-054-repository-aggregates-and-manifest.md)  
**Backlog:** [P2-BACKLOG.md](../migration/P2-BACKLOG.md)  
**Audit:** Wave F (2026-10-01 architect audit — Integration readiness / protocol-neutral core / adapters)

## Context

The 2026-10-01 architect audit treated “integration readiness” as a first-class DAMS concern: a protocol-neutral core (`Integration` / `IntegrationParticipant` / `DataExchange` / Operation / Channel / Message), Dataset↔Distribution (DCAT), and version-pinned OpenAPI / AsyncAPI / ODCS / OpenLineage / CloudEvents adapters.

ADR-048 already chose a different shape for topology: Clinkr/EAM owns systems, platforms, channels, and spec URIs; DAMS owns semantic bindings (`DataFlowEntityBinding`) and materializes `TopologyView` from a **file snapshot**. That snapshot is still a fixture/contract, not a live catalog export (ADR-048 Consequences). ADR-040 separates `Message` from carriers; ADR-054 keeps DataFlow outside the manifest until real envelopes exist.

Without an explicit SoT ADR, audit acceptance criteria for DAMS 0.2 still read as “build the in-DAMS integration core,” which contradicts ADR-048 and invites parallel models.

## Decision

### D1. Topology and catalog facts: Clinkr / EAM

| Fact class | Owner | In DAMS |
|---|---|---|
| Solutions, systems, platforms, interfaces, channels, protocols, catalog operation ids, catalog spec URIs | Clinkr / EAM | Via `integration_ref` + `TopologyView` (ADR-048); not authored on `DataFlow` |
| Exchange meaning: selections, carriers, mappings, contract pins | DAMS | `DataFlow`, `DataFlowEntityBinding`, `DataModelBinding` |
| Effective topology for lint / queries | Generated | `TopologyView` (`moex-topology`, outside `moex-dams.yaml` imports) |

DAMS does **not** introduce `Integration`, `IntegrationParticipant`, `DataExchange`, or `IntegrationBindingSet` while ADR-048 stands. Audit name `DataExchange` maps to `DataFlowEntityBinding` (ADR-048 D3).

### D2. Catalog input for CI remains a file snapshot until revisit triggers fire

CI continues to use `model-assets/catalog-snapshots/` only (ADR-048 D2). Live `RegistryAdapter` / Clinkr API calls are **out of scope** for Stage 0 until at least one revisit trigger in D4 is met and a follow-up ADR (or an amendment to this ADR) records the adapter contract.

The snapshot format is a **contract**, not proof that production Clinkr matches the fixture. Saying “Clinkr is SoT” means ownership of facts, not that the repo currently mirrors production.

### D3. In-DAMS surfaces that stay (and may grow without becoming a second topology SoT)

Allowed without amending D1:

- `Message`, `AccessPoint`, `DataStructure` / `SchemaNode` (ADR-040 / ADR-038)
- Version-pinned **pointers** on structures or bindings (`source_artifact_ref`, `source_pointer`, `catalog_operation_ref`, `catalog_participant_ref`) — opaque or structured references to external specs, **not** a full OpenAPI/AsyncAPI import graph
- Future `Distribution` / `ArtifactDistribution`-style records when scheduled under [P2-BACKLOG.md](../migration/P2-BACKLOG.md) and ADR-052 (do not re-author identity layers here)

Forbidden without amending this ADR:

- Re-adding authored topology slots on `DataFlow`
- A parallel “integration catalog” inside DAMS that duplicates Clinkr participant/channel/operation identity

### D4. Revisit triggers (any one is enough to open a follow-up)

Re-open Integration SoT (amend this ADR or supersede D1–D3) when **any** of:

1. **Real catalog export:** a production Clinkr/EAM export lands as the CI snapshot (or replaces the fixture) with stable object ids and a documented refresh process; **or**
2. **Second consumer:** a second authored `DataFlow` / implementation-owned flow set needs multi-party / fan-out modeling that ADR-048 D6 (`one integration_ref` per flow) cannot express without lying; **or**
3. **Contract adapters:** a funded series to import OpenAPI 3.1 / AsyncAPI 3 documents into DAMS with version-pinned operation/channel/message pointers and round-trip diagnostics — at that point decide whether pointers stay Clinkr-mediated or become first-class DAMS profile types.

Until then, protocol-neutral exchange core and full adapters remain **P2 backlog**, not open defects against ADR-048.

### D5. Audit DAMS 0.2 acceptance — integration / technical criteria remapped

Source: architect audit § «Acceptance criteria для DAMS 0.2» and integration/physical themes. Normative remap for this repo:

| Audit criterion (paraphrase) | Status under this ADR | Where it lives now |
|---|---|---|
| Dataset / distribution / interface / operation / channel / message / schema separated | **Partial — remapped** | TechnicalAsset + Message + AccessPoint + SchemaNode; **no** DCAT `Distribution` (P2); topology channel/operation **from catalog snapshot** (ADR-048), not DAMS classes |
| Protocol-neutral Integration / DataExchange core in DAMS | **Deferred — remapped** | Clinkr SoT + `DataFlowEntityBinding`; revisit via D4 |
| OpenAPI / AsyncAPI / ODCS version-pinned imports | **Deferred** | P2 backlog; structure-level pins only today |
| OpenLineage / CloudEvents bindings | **Deferred** | Runtime lineage outside DAMS (ADR-053 D3); CloudEvents enum only; P2 |
| Mapping endpoints validated by kind | **Closed** | ADR-046 + INV matrix (not this ADR) |
| Conceptual property ↔ glossary ↔ logical attributes | **Partial** | ADR-034/035; no `DataRepresentation` (P2) |
| Governance single SoT | **Partial** | ADR-049; inline defaults remain by design |
| No normative conditional invariant only in prose | **Partial** | ADR-045 + Waves A–C; remaining gaps tracked as INV / waivers |
| Identity policy for addressable nodes | **Partial** | ADR-052 map; 6.0.0 train for rename / VersionedArtifact |
| Document aggregates / manifest | **Closed with deferral** | ADR-047 + ADR-054 (package-only kinds) |
| Reproducible migration / golden artifacts | **In progress** | ADR-011 / ADR-051; per-series CHANGELOGs |

This table **does not** reopen closed P0/P1 ADRs. It only records which audit lines are consciously remapped for integration/adapters.

## Consequences

- Integration readiness score vs the original audit stays intentionally lower until a D4 trigger; that is a **scope decision**, not an unfinished ADR-048.
- P2 work listed in [P2-BACKLOG.md](../migration/P2-BACKLOG.md) must cite this ADR for integration items and must not invent a second topology SoT.
- ADR-053 / ADR-052 deferred items (`SemanticAlignment` rename, `ArtifactDistribution`, lineage hooks) are referenced from the backlog, not redesigned here.
- Reviewers rejecting “missing Integration class” should point at D1 + D5, not at gaps in schema coverage.

## Alternatives

| Alternative | Why not |
|---|---|
| Build audit Integration / DataExchange core now | Duplicates Clinkr; contradicts ADR-048; thin instance evidence (one flow) |
| Claim Clinkr SoT equals “production catalog in CI” | Snapshot is still a fixture; would over-claim |
| Keep audit 0.2 criteria unchanged | Creates permanent false-open defects against intentional federation |

## Acceptance

- [x] Clinkr/EAM topology SoT recorded relative to ADR-048
- [x] Snapshot vs production honesty (D2)
- [x] Revisit triggers (D4)
- [x] Audit acceptance remap table (D5)
- [x] P2 backlog file linked; no schema / `generated/` changes in this PR
