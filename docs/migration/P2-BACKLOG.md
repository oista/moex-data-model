# P2 backlog (post audit Waves A–F)

**Date:** 2026-10-13  
**Updated:** 2026-10-14 (R2-10 — owners / targets)  
**Normative decisions:** [ADR-055](../adr/ADR-055-integration-source-of-truth.md) (Integration SoT), [ADR-051](../adr/ADR-051-dams-schema-compatibility.md), [ADR-052](../adr/ADR-052-identity-and-versioning.md), [ADR-053](../adr/ADR-053-qualified-assertion.md)  
**Out of scope for this file:** implementation, schema bumps, `generated/**`. Track work as separate series after a D4 trigger (ADR-055) or an explicit product priority.

Items below are **backlog**, not open bugs against closed ADRs. Prefer citing the ADR that already decided (or deferred) the topic; do not re-litigate inside a new spike without amending that ADR.

**Owner** = accountable role (no CODEOWNERS file yet). **Target** = earliest window, not a commitment.

| Role | Scope |
|---|---|
| `DAMS maintainers` | Schema, constraints, ADRs 044–054, architecture-check |
| `Integration` | Clinkr/EAM snapshot, topology module, adapter series (ADR-055 Group 1) |
| `Product` | Priority call when a D4 trigger is ambiguous |

---

## Group 0 — Accepted ADR follow-ups (not P2 product features)

These are unfinished acceptance checkboxes on **Accepted** ADRs. Ship as **minor** additive PRs (ADR-051), independent of Integration SoT.

| ID | Item | Source | Owner | Target | Notes |
|---|---|---|---|---|---|
| F0-1 | ~~Schema mixin `HasAssertionMetadata`~~ **Done** (aggregate 5.1.0) | [ADR-053](../adr/ADR-053-qualified-assertion.md) D1 | DAMS maintainers | — | See [CHANGELOG-assertion-metadata.md](CHANGELOG-assertion-metadata.md) |
| F0-2 | ~~L2 INV ExternalClassRef ↔ AlignsWithMapping~~ **Done** (**INV-057**) | ADR-053 D2 | DAMS maintainers | — | Dual path stays; consistency only |
| F0-3 | Identity train **6.0.0**: `api_version` → `dams_specification_version`; remove deprecated `transformation_*` unless a lineage ADR reclaims them; optional `VersionedArtifact`; exit selection/binding classes from [id_prefixes allowlist](../adr/ADR-052-identity-and-versioning.md) | [ADR-052](../adr/ADR-052-identity-and-versioning.md), ADR-053 D3 | DAMS maintainers | After ADR-051 D4 evidence gate + explicit go-ahead | Release train — not silent major-per-theme (ADR-051 D3–D4) |
| F0-4 | `id_prefixes` allowlist ratchet — add `dams` prefixes for remaining non-selection classes; lower ceiling | ADR-052 § Ratchet schedule | DAMS maintainers | Next minor after F0-3 or earlier additive minor | Ceiling must drop with each exit; see architecture-check README |

---

## Group 1 — Integration and adapters (gated by ADR-055)

Do **not** start until a [ADR-055 D4](../adr/ADR-055-integration-source-of-truth.md) revisit trigger fires, unless the item is a **pointer-only** additive slot that does not duplicate Clinkr topology (ADR-055 D3).

| ID | Item | Depends on / cites | Owner | Target | Notes |
|---|---|---|---|---|---|
| F1-1 | Production catalog snapshot (or live adapter with pinned export) replacing the Clinkr fixture | ADR-048, ADR-055 D2/D4#1 | Integration | On D4#1 (snapshot ≠ production) | Contract format already in `moex-topology` |
| F1-2 | Version-pinned OpenAPI 3.1 pointers (document/version, operationId, path/method, media type, JSON Pointer → SchemaNode) | ADR-055 D4#3, ADR-038/039 | Integration | On D4#3 or Product priority | Prefer profile types + importer; not a second topology SoT |
| F1-3 | Version-pinned AsyncAPI 3 pointers (channel / operation / message) | ADR-055 D4#3, ADR-040 | Integration | On D4#3 or Product priority | Align with catalog `catalog_operation_ref` where possible |
| F1-4 | ODCS export/import profile (schema section from DAMS selection; SLA/support stay in contract portal) | ADR-042 bindings | DAMS maintainers | Product priority | Do not clone ODCS wholesale |
| F1-5 | OpenLineage identity mapping (Dataset ↔ DataCarrier/asset; Job ↔ ExecutionAsset); runtime runs stay outside DAMS | ADR-053 D3 | DAMS maintainers | Product priority | Optional `lineage_source_ref` — do not revive polymorphic `transformation` mapping type lightly |
| F1-6 | CloudEvents envelope binding beyond `EnvelopeKindEnum` | ADR-040 | DAMS maintainers | Product priority | Envelope vs payload schema separation |
| F1-7 | Revisit protocol-neutral `Integration` / multi-party exchange **only if** D4#2 (fan-out / second consumer) forces it | ADR-048 D6, ADR-055 D1 | Integration | On D4#2 only | Default remains Clinkr SoT |

---

## Group 2 — Semantic / technical model deepeners

| ID | Item | Depends on / cites | Owner | Target | Notes |
|---|---|---|---|---|---|
| F2-1 | DCAT-style `Distribution` (or AccessPoint role) linked to dataset/carrier — **dataset vs distribution** | Audit physical model; ADR-031 | DAMS maintainers | Product priority | Distinct from ADR-052 **ArtifactDistribution** (publication file identity) |
| F2-2 | Thin `DataRepresentation` between `ConceptualProperty` and `LogicalAttribute` / `ValueDomain` | ADR-034 variant B | DAMS maintainers | When multi-representation required | Only if multiple representations per property become required |
| F2-3 | Rename `ExternalClassRef` → `SemanticAlignment` (+ optional `ExternalSemanticResourceRef`) | ADR-053 D2 (**explicitly deferred**) | DAMS maintainers | With or after 6.0.0 train | Breaking; glossary maps audit name → current class until then |
| F2-4 | Technology / protocol / dialect **registry objects** instead of free strings | Audit enums section | DAMS maintainers | Product priority | Additive registries + optional tighten later |
| F2-5 | Classification / entity-category **controlled vocabularies** (hierarchy, scheme version) instead of closed enums where orgs extend without DAMS release | ADR-049 out-of-scope wave; DPV-style *selection*, not copy | DAMS maintainers | Product priority | Keep baseline enums until vocab objects exist |
| F2-6 | Extract `moex-model-element` (or equivalent) to break `core ↔ structure ↔ technical` import cycles | ADR-031 / ADR-034 / ADR-040 / ADR-044 debt notes | DAMS maintainers | Packaging series | Packaging / import boundary only |

---

## Group 3 — Document aggregates (after real envelopes)

Tracked so P2 does not forget ADR-054 deferrals; not integration work.

| ID | Item | Source | Owner | Target | Notes |
|---|---|---|---|---|---|
| F3-1 | New `DocumentKind` values + envelopes for flows, bindings, governance sets, requirement catalogs | [ADR-054](../adr/ADR-054-repository-aggregates-and-manifest.md) D2 / Deferred | DAMS maintainers | When first non-package envelope is authored | — |
| F3-2 | Extend `assemble()` beyond packages-only when kinds exist | ADR-054 D1 | DAMS maintainers | After F3-1 | — |
| F3-3 | Global `element_id` collision check on assembled composite | **Done** — INV-058 + `check-manifest` (`check_global_element_ids`); hierarchy-view excluded (ADR-054) | DAMS maintainers | — | Closed |

---

## Explicit non-goals (until a new ADR)

- Runtime lineage store inside DAMS (OpenLineage platform remains SoT for runs).
- Re-adding authored topology on `DataFlow`.
- Abstract `Assertion` / `QualifiedRelation` in the `is_a` backbone (ADR-053 D1).
- Catalogue path bump `moex-dams/0.1/` → `0.2/` on every aggregate major (ADR-051 D1).

---

## How to pick up an item

1. Confirm the cited ADR still holds; amend that ADR if the decision changes.
2. For Group 1, cite which ADR-055 D4 trigger applies.
3. Confirm **Owner** (or reassign in this file in the same PR that starts the series).
4. Open a multi-PR series plan (`{Project}: …`) with ADR-051 evidence gate if the series includes a major.
5. Do not mix Group 0 minor mixin work into a Group 1 adapter epic without a release-train note.
