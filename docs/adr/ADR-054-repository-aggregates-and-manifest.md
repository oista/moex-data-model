---
status: Accepted
version: "0.1"
normative: true
supersedes: []
superseded_by: []
---

# ADR-054: Repository aggregates and manifest (P1b)

**Date:** 2026-10-13  
**Status:** Accepted  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-047](ADR-047-repository-manifest-and-lock.md), [ADR-042](ADR-042-integrity-digest-revisions.md), [ADR-048](ADR-048-topology-ownership.md), [ADR-049](ADR-049-governance-assignment-authority.md), [ADR-051](ADR-051-dams-schema-compatibility.md)  
**Inventory:** [p1-inventory.md](../migration/p1-inventory.md)

## Context

The architect audit asked for independently addressable aggregate roots
(ModelPackageVersion, RegistryProjectionSnapshot, IntegrationBindingSet,
DataContractBinding, GovernanceAssignmentSet, RequirementCatalog) indexed by a
repository manifest, with `MOEXModelRepository` as a generated validation
bundle — not the operational authoring unit.

ADR-047 delivered a package-only manifest and lock. No YAML under
`model-assets/implementations/` currently materializes flows, bindings,
governance-assignment sets, or requirement catalogs as separate envelopes.
Those objects live as examples, package-local content, or other trees
(requirements catalogs). Expanding `DocumentKindEnum` without addressable
files would be ceremony.

## Decision

### D1. Aggregates remain a validation composite (this series)

`MOEXModelRepository` stays the LinkML `tree_root` and an **in-memory
validation / exchange composite**. It is **not** an authored mega-document and
is **not** fully populated by the file index today.

`RepositoryLoader.assemble()` builds only:

| Slot | Source |
|---|---|
| `repository_id` | `manifest.yaml` |
| `model_packages` | bodies of every `DocumentRef` with `kind: package` |

Other tree_root collections (`registry_entries`, `data_flows`,
`data_model_bindings`, `metrics`, `dimensions`, `classification_assignments`,
`policy_bindings`, `ownership_assignments`) are **not** filled from the
manifest. They remain available for fixtures, offline bundles, and future
kinds.

### D2. DocumentKind stays `package` until envelopes exist

Do **not** add `data_flow` / `binding` / `governance_set` / `requirement_catalog`
to `DocumentKindEnum` in this series. Additive enum values are reserved for a
follow-up that also:

1. Defines envelope + body layout under `implementations/` (or a sibling root);
2. Adds at least one real indexed instance per new kind;
3. Extends lock hashing and `assemble()` for that kind;
4. Updates orphan allow-list and discovery.

Audit aggregate → current home:

| Audit root | Current home | Manifest? |
|---|---|---|
| Model package | `SpecificationImplementation` + body (`kind: package`) | Yes |
| Registry projection | `RegistryEntry` on tree_root / package-local registries | No |
| Integration / DataFlow | Example `client-data-flow.yaml`; topology from catalog snapshot (ADR-048) | No |
| Data contract binding | Rare `DataModelBinding` examples (ADR-042 digests) | No |
| Governance assignment set | Assignments on packages / examples; EffectiveGovernanceView (ADR-049) | No |
| Requirement catalog | `model-assets/specifications/moex-dams/0.1/requirements/` | No |

### D3. Viewer discovery

Publication modules under `model-assets/implementations/` are discovered from
the repository manifest: for each package `DocumentRef.path` pointing at
`…/implementation.yaml`, look for sibling `publish.yaml`. Modules outside that
tree (specifications, external-selections) stay on `rglob("publish.yaml")`.

CI / unit test asserts that the implementation-scoped rglob set equals the
manifest-derived set (coincidence gate). Root-level stray `publish.yaml` under
`implementations/` is not allowed by the orphan check.

### D4. Orphan allow-list is path-scoped

ADR-047 orphan checks switch from bare basenames (any `data-types.yaml`
anywhere) to an explicit path allow-list plus directory rules
(`**/publications/**`, sibling `publish.yaml` of an indexed package). New
top-level YAML under `implementations/` without a manifest entry or allow-list
PR fails `check-manifest`.

### D5. Three integrity mechanisms (see MODELING_ARCHITECTURE)

| Mechanism | Scope | Authority |
|---|---|---|
| `DataModelBinding.integrity_digest` (ADR-042) | Binding body | Publish / digest gate |
| Envelope `content_digest` / `revision` | Raw body bytes at import | Legacy stamps; not CI-verified |
| `manifest.lock` `content_hash` (ADR-047) | Descriptor (stamps excluded) + body, canonical JSON | `lock-verify` / Stage 0 |

Do not invent a fourth algorithm without a new ADR.

## Consequences

- P1b closes the audit “document aggregate” decision gate with an explicit
  deferral of new kinds, not a half-empty enum.
- Reviewers know `assemble()` is packages-only by contract.
- Viewer and orphan checks tighten without moving files.
- A future series that introduces real envelopes amends this ADR (or supersedes
  D2) and bumps `manifest_schema_version` minor per ADR-047 D9.

## Alternatives

| Alternative | Why not now |
|---|---|
| Add DocumentKind values with zero instances | Schema noise; no lock/assemble semantics |
| Split ModelPackage bodies | Orthogonal merge-pain fix; still deferred |
| Index requirements/ and examples/ via manifest | Different trees and envelopes; separate series |

## Deferred

Envelope layouts and `DocumentKind` values for flows, bindings, governance
sets, requirement catalogs; full `assemble()` of all tree_root slots;
GitProvider-backed reads; CODEOWNERS from manifest `owner`.

## Global `element_id` uniqueness (INV-058)

Cross-package `element_id` collisions among **source** packages are errors
(`check-manifest` → `check_global_element_ids`, matrix **INV-058**, code
`DAMS-INV-058`). Within a single package document, uniqueness remains
**INV-050**.

Packages whose envelope sets `dams_model_level: hierarchy-view` are
**excluded** (derived views may intentionally reuse source ids — today
`moex:implementation:moex-hierarchy:0.1`). Exclusion is exact-match on that
level string only.
