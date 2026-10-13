---
status: Accepted
version: "0.1"
normative: true
supersedes: []
superseded_by: []
---

# ADR-052: Identity and versioning (five layers)

**Date:** 2026-10-13  
**Status:** Accepted  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-030](ADR-030-dams-uri-and-prefix-policy.md), [ADR-032](ADR-032-technical-asset-identity.md), [ADR-039](ADR-039-structure-node-addressing.md), [ADR-042](ADR-042-integrity-digest-revisions.md), [ADR-044](ADR-044-model-element-decomposition.md), [ADR-047](ADR-047-repository-manifest-and-lock.md), [ADR-051](ADR-051-dams-schema-compatibility.md)  
**Lookup:** [identity-map.md](../architecture/identity-map.md)  
**Audit:** Wave D2 (Identity decision gate)

## Context

The architect audit required distinguishing five identities: concept, artifact (work), version, revision, distribution. Today the repo has overlapping slots (`element_id`, `model_version`, `api_version`, `model_revision`, digests, git SHAs) without a single map. ADR-044 D6 deferred `VersionedArtifact`. `api_version` on `ModelPackage` is routinely misread as an HTTP API version.

## Decision

### D1. Five identity layers (normative map)

| Layer | Meaning | Current DAMS representation | Target (non-breaking first) |
|---|---|---|---|
| **Concept** | Stable business / semantic identity | `element_id` on conceptual entities; glossary / ontology alignments | Keep; IRI policy ADR-030 |
| **Artifact (work)** | Abstract work (series of versions) | Implicit: package / binding / structure id without version | Document as “id without version suffix”; **no** `ModelPackageSeries` class until ≥2 consumers need `current_version_ref` |
| **Version** | Immutable published SemVer of an artifact | `model_version`, `structure_version` (`is_a: artifact_version`) | Keep abstract `artifact_version`; introduce **`VersionedArtifact` mixin** only when a third class needs `previous_version_ref` + content identity (ADR-044 D6 trigger unchanged) |
| **Revision** | Content-addressed / git snapshot | Git commit; binding `model_revision`; envelope `revision`; lock `content_hash` | Keep; do not invent a fourth digest algorithm |
| **Distribution** | Concrete published file (YAML / JSON Schema / OWL / …) | Generated paths + media type in publication modules | Optional future `ArtifactDistribution` record; **not** required for 6.0.0 |

Do **not** introduce FRBR/DCAT class names into the schema until a consumer needs them; the table above is the vocabulary for docs and reviews.

### D2. Rename `api_version` → `dams_specification_version`

- Slot meaning: which **DAMS specification / metamodel** the package conforms to (product label, e.g. `dams.moex/v0.1`), **not** an HTTP API version.
- **Breaking rename** deferred to the next identity release train (planned aggregate **6.0.0**, ADR-051).
- Until then: docs and glossary must call out the misnomer; new code/comments use the phrase “DAMS specification version (`api_version`)”.
- Migration: `ruamel` script `--check`/`--write`; dual-read not required if train ships rename + data in the PR-5 exception pattern.

Optional later: `conforms_to_specification_ref` as a uriorcurie **instead of** or **in addition to** the string slot — out of scope for the first rename.

### D3. `VersionedArtifact` mixin — still deferred

Reaffirm ADR-044 D6: no mixin until a third class grows both `previous_version_ref` and a content digest/revision pair beyond `ModelPackage` / `DataStructure` / `DataModelBinding`. When introduced, it must live in `moex-base.yaml` and must not pull structure↔core cycles.

### D4. `id_prefixes` for addressable classes

- Every **concrete** class that is `IdentifiedElement` or `ModelElement` (or subclass) SHOULD declare `id_prefixes` (or inherit a non-empty set from an ancestor).
- **Architecture-check** enforces this with an explicit allowlist of legacy classes missing prefixes (shrink-only; growth requires amending this ADR § Allowlist).
- Classes with a **proprietary identifier** (LinkML single-identifier rule: `assignment_id`, `registry_id`, …) stay outside `IdentifiedElement` and are exempt; their prefix policy remains ADR-030 / domain docs.
- ADR-032 / ADR-039 remain authoritative for TechnicalAsset and SchemaNode addressing.

### D5. Release train items (schema 6.0.0 — not in this ADR PR)

Subject to ADR-051 evidence gate:

1. Rename `api_version` → `dams_specification_version` (+ data migration).
2. Move `ModelSelection` / `SelectedEntity` / `SelectedAttribute` / `DataFlowEntityBinding` off full `ModelElement` onto `EmbeddedElement` or slim `IdentifiedElement` (ADR-044 remainder).
3. Remove slots already deprecated in Wave C (`native_name` / `native_type` orphans, `transformation_*` on Mapping, `LogicalDataTypeEnum` if unused).
4. Optional: `RelationshipEnd` / typed relationship profiles (may stay L2-only per Wave C INV).

Schema and data commits stay separate unless the series ADR names the PR-5 exception.

### D6. Operational identity record (Distribution — tooling, not schema)

A published generated artifact is identified by the **tracked** per-artifact manifest under `generated/manifests/` (and the bundle index). Required identity fields:

| Field | Meaning |
|---|---|
| `artifact_id` | Stable work/artifact id for that projection |
| `schema_version` | Aggregate DAMS LinkML semver from `moex-dams.yaml` `version:` |
| `schema_digest` | Content digest of the schema input (when applicable) |
| `content_digest` | Content digest of the published bytes / directory |
| `media_type` | MIME (or well-known type) of the distribution |
| `role` | Bundle part role (`json-schema`, `owl`, `contracts`, …) |

`generated_at` is **informational only**: it MUST NOT participate in identity, digests, or golden compare. Changing only `generated_at` MUST NOT change any digest.

Optional LinkML `ArtifactDistribution` class remains YAGNI (D1); the operational record closes the audit gap without a schema bump.

### D7. Git revision at release/bundle time only

A **tracked** manifest MUST NOT embed the Git SHA of the commit that contains that manifest (self-referential / non-reproducible). Git revision (`source_revision`) is attached when building the **staged** release bundle (`generated/bundles/`, gitignored): next to `schema_version` on the bundle index. Release mode refuses a dirty tree; development mode may record `unknown`.

Binding `model_revision`, envelope `revision`, and lock `content_hash` (ADR-042 / ADR-047) remain the content-addressed revision surfaces for model assets.

### Allowlist (classes without `id_prefixes` as of schema 4.1.0)

Maintained in `tools/architecture-check` (`ID_PREFIXES_ALLOWLIST`). Initial set = all concrete `IdentifiedElement`/`ModelElement` descendants that lack induced `id_prefixes` except `TechnicalAsset`, `DataStructure`, `Message` (already declared). Shrink the allowlist when prefixes are added; do not grow without amending this section.

## Consequences

- Identity vocabulary is fixed for audits and reviews without a schema rewrite.
- `api_version` rename is scheduled, not ambiguous.
- `id_prefixes` debt becomes visible in CI.
- Distribution identity is machine-checkable in manifests and publish-gate without introducing FRBR/DCAT classes.

## Alternatives

| Alternative | Why not |
|---|---|
| Introduce `ModelPackageSeries` / `ArtifactDistribution` now | YAGNI; no second consumer |
| Keep `api_version` forever | Continues audit confusion |
| Force all service classes onto `IdentifiedElement` | Breaks single-identifier rule (ADR-044) |

## Acceptance

- [x] Five-layer map published
- [x] Rename decision recorded (deferred to 6.0.0 train)
- [x] `id_prefixes` lint + allowlist
- [x] Operational identity record (D6/D7 — manifests + publish-gate; [identity-map.md](../architecture/identity-map.md))
- [ ] 6.0.0 train implementation (separate series)
