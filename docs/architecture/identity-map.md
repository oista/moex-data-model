---
status: Accepted
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# Identity map — what changed?

**Normative:** [ADR-052](../adr/ADR-052-identity-and-versioning.md) (five layers), [ADR-051](../adr/ADR-051-dams-schema-compatibility.md) (schema semver), [ADR-042](../adr/ADR-042-integrity-digest-revisions.md), [ADR-047](../adr/ADR-047-repository-manifest-and-lock.md).

Use this page to answer “what exactly changed?” without conflating version surfaces.

## Layers (short)

| Layer | Is | Is not |
|---|---|---|
| **Concept** | Stable `element_id` / IRI | A file or commit |
| **Artifact (work)** | Id of a series (package / binding / structure **without** version suffix) | A SemVer or digest |
| **Version** | Published SemVer (`model_version`, `structure_version`, aggregate schema `version`) | A Git SHA or generated timestamp |
| **Revision** | Content-addressed snapshot (Git commit, binding `model_revision`, lock `content_hash`) | SemVer marketing label |
| **Distribution** | Concrete published bytes (path + media type + `content_digest`) | The abstract work or version |

**Rules:** Version ≠ Revision ≠ Distribution. `generated_at` is never identity.

## Question → field → where

| Question | Field(s) | Where |
|---|---|---|
| Did the **model instance** change? | `ModelPackage.model_version`; binding `integrity_digest` / `model_revision` | Package YAML; binding; ADR-042 |
| Did the **DAMS schema** contract change? | Aggregate `version:` | `model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml` — [timeline](../migration/SCHEMA-VERSION-TIMELINE.md) |
| Did a **generated file** change? | Manifest `content_digest` (+ `schema_digest` when present) | `generated/manifests/*.json` |
| Which **Git commit** produced a release bundle? | Bundle `source_revision` | Staged `generated/bundles/` index (gitignored); not in tracked per-artifact manifests |
| Is the **repo lock** in sync? | `manifest.lock` `content_hash` | ADR-047 |
| Which **DAMS product/spec label** does a package claim? | `ModelPackage.api_version` | Misnamed — means DAMS specification version (e.g. `dams.moex/v0.1`), **not** HTTP API version. Rename to `dams_specification_version` planned for aggregate **6.0.0** (ADR-052 D2). |
| What is the FastAPI app version? | FastAPI `version=` | `apps/api` — unrelated to `api_version` on `ModelPackage` |

## Operational Distribution record

Tracked manifests identify a distribution with: `artifact_id`, `schema_version`, `schema_digest`, `content_digest`, `media_type`, `role` (ADR-052 D6). Publish-gate rejects missing fields and `schema_version` ≠ aggregate schema version.

Git SHA is attached only at staged bundle build time (ADR-052 D7).

## Deferred (schema train 6.0.0)

Trackable work packages, owners, and entry criteria: [TRAIN-6.0.0.md](../migration/TRAIN-6.0.0.md) (T6-1…T6-8). Summary:

- **T6-1** — Rename `api_version` → `dams_specification_version`
- **T6-2** — Selection/binding classes off full `ModelElement` → `EmbeddedElement`
- **T6-3** — Remove deprecated orphan slots / enum
- **T6-4** — Optional `VersionedArtifact` mixin (ADR-044 D6 trigger)
- LinkML `ArtifactDistribution` class remains YAGNI (ADR-052 D1); operational manifests already cover Distribution identity (D6)

These do **not** block answering “what changed?” once operational manifests and this map are in place.
