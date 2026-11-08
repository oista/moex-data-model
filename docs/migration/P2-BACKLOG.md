# P2 backlog (post audit Waves A–F)

**Date:** 2026-10-13  
**Updated:** 2026-11-03 (F0-7 done — INV-045, INV-046, INV-048, INV-049; M-5 / F0-4 stays open)  
**Normative decisions:** [ADR-055](../adr/ADR-055-integration-source-of-truth.md) (Integration SoT), [ADR-051](../adr/ADR-051-dams-schema-compatibility.md), [ADR-052](../adr/ADR-052-identity-and-versioning.md), [ADR-053](../adr/ADR-053-qualified-assertion.md)  
**Schema train 6.0.0:** [TRAIN-6.0.0.md](TRAIN-6.0.0.md) (entry criteria G1–G6, work packages T6-1…T6-8, pre-train minors M-1…M-5)  
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
| F0-3 | Identity / backbone train **6.0.0** — see [TRAIN-6.0.0.md](TRAIN-6.0.0.md) | [ADR-052](../adr/ADR-052-identity-and-versioning.md) D5, ADR-053 D3, ADR-044 | DAMS maintainers (train lead); Product for go-ahead (G1) | After train gate G1–G6 | **Core:** T6-1 rename `api_version`; T6-2 selection/binding → `EmbeddedElement`; T6-3 remove deprecated orphans. **Optional co-travelers:** T6-4 `VersionedArtifact`; T6-5 `RelationshipEnd`. Operational Distribution identity already closed without this bump ([identity-map.md](../architecture/identity-map.md)). |
| F0-4 | `id_prefixes` allowlist ratchet — add `dams` prefixes for remaining non-selection classes; lower ceiling | ADR-052 § Ratchet schedule; TRAIN M-5 | DAMS maintainers | Next minor after F0-3 or earlier additive minor | Ceiling must drop with each exit; see architecture-check README |
| F0-5 | Mapping endpoint **L1** typing spike (JSON Schema / Pydantic item types); L2 remains SoT for id→class | Audit mapping §; ADR-046; TRAIN T6-6 | DAMS maintainers | Minor before or after 6.0.0 | Non-goal: pretend JSON Schema resolves cross-doc `element_id` |
| F0-6 | Rich ownership slots (role type, delegation) on `OwnershipAssignment` — **no** new `StewardshipAssignment` unless ADR-049 amended | Audit governance §; ADR-049 D7; TRAIN T6-7 | DAMS maintainers | Product priority | Stewardship stays folded per ADR-049 |
| F0-7 | ~~Pre-train validation minors: selection closure, baseline/mode, `LogicalAttribute` min/max, `parent_concept_ref` cycles~~ **Done** (INV-048, INV-049, INV-045, INV-046) | Audit “Negative examples”; TRAIN M-1…M-4 | DAMS maintainers | — | L2 rows implemented. M-5 / F0-4 (`id_prefixes` ceiling) stays open |

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
| F3-1 | New `DocumentKind` values + envelopes for flows, bindings, governance sets, requirement catalogs | [ADR-054](../adr/ADR-054-repository-aggregates-and-manifest.md) D2 / Deferred; TRAIN T6-8 | DAMS maintainers | When first non-package envelope is authored | Do not invent empty kinds |
| F3-2 | Extend `assemble()` beyond packages-only when kinds exist | ADR-054 D1; TRAIN T6-8 | DAMS maintainers | After F3-1 | — |
| F3-3 | Global `element_id` collision check on assembled composite | **Done** — INV-058 + `check-manifest` (`check_global_element_ids`); hierarchy-view excluded (ADR-054) | DAMS maintainers | — | Closed |

---

## Group 4 — ADR-056 requirements backbone follow-ups

Closed series: PR-0…PR-10f ([ADR-056](../adr/ADR-056-requirements-backbone.md)). Items below are **not** open bugs against the Accepted ADR; they are deferred product / schema work.

| ID | Item | Source | Owner | Target | Notes |
|---|---|---|---|---|---|
| F4-1 | ИОД vocabulary + automate **LDM-13** (`sensitivity_term_refs`) | ADR-056 D5/D6/D7 | DAMS maintainers | Product priority | Deferred (not a defect): stays manual until Product ships vocabulary; LDM-10 covers `governance_classification` |
| F4-2 | “Current specification version” check for **LDM-02** (beyond `api_version` presence) | ADR-056 D6/D7; ADR-051/052 | DAMS maintainers | After **T6-1** | Deferred: `api_version` is product label `dams.moex/v0.1`, not aggregate 5.5.0; presence already schema-required |
| F4-3 | Fill `relationship_kind` on 31 draft solution relationships before promoting to `active` | ADR-056 D6/D7 (LDM-07 debt) | Solution owners | — | **Done** — `relationship_kind: reference` on 31 draft links; guard `test_solution_relationship_kinds.py` |
| F4-4 | Relax schema-required `context_ref` / `solution_data_role` (or keep) | ADR-056 D6/D7 | DAMS maintainers | — | **Done** — keep required (ADR-056 D7) |
| F4-5 | Remove deprecated slot `security_classification` (MAJOR) | ADR-056 PR-10e; D7 | DAMS maintainers | [TRAIN-6.0.0](TRAIN-6.0.0.md) **T6-9** | Prefer `governance_classification`; batch in aggregate 6.0.0 (not a solo major) |
| F4-6 | Pass `extra_definition_packages` in assess/`check_formal_requirements_for_repo` so LDM-04/CDM-01 inherit across packages | **Done** — `load_related_definition_packages` via `repo_root` (conceptual_implementation_ref + dams: definition refs) | DAMS maintainers | — | Closed |
| F4-7 | Replace 30 `DAMS-REQ-GEN-001.placeholder` owner stubs on crm/esed/mdm/ucd | LDM-11 | Solution owners | Product priority | Impact script baseline post PR-11a |
| F4-8 | Drift check for tracked `mdm/publications/vertical_slice.json` (or stop committing it) | publication / viewer | DAMS maintainers | Minor | Stale after catalog cleanup until regen |

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
4. For **F0-3 / train 6.0.0**, satisfy [TRAIN-6.0.0.md](TRAIN-6.0.0.md) entry criteria G1–G6 before the first schema PR; use work-package ids T6-* in commit/PR titles.
5. Open a multi-PR series plan (`moex-data-model: …`) with ADR-051 evidence gate if the series includes a major.
6. Do not mix Group 0 minor mixin work into a Group 1 adapter epic without a release-train note.
