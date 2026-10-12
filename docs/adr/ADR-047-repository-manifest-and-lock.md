---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# ADR-047: Repository manifest and lock

**Date:** 2026-10-12  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-002](ADR-002-git-published-source.md), [ADR-031](ADR-031-technical-asset-registry.md), [ADR-042](ADR-042-integrity-digest-revisions.md) (canonical digest algorithm reused for lock `content_hash`), [ADR-044](ADR-044-model-element-decomposition.md)  
**Inventory:** [p1-inventory.md](../migration/p1-inventory.md)

## Context

`MOEXModelRepository` is the DAMS `tree_root`, but no instance YAML exists.
Implementations are discovered by globbing `implementation.yaml`. There is no
hand-edited index of documents, no per-document integrity check at repository
scope, and no declared package dependency graph for CI.

P1 addresses that **without** moving package files or changing publication
paths. Splitting large `ModelPackage` bodies is out of scope (see inventory).

## Decision

### D1. Hand-edited manifest + generated lock

- Path: `model-assets/implementations/manifest.yaml` (index only).
- Path: `model-assets/implementations/manifest.lock` (generated JSON Lines).
- Manifest is edited by humans when documents are added/removed/retargeted.
- Lock is written **only** by `moex-model lock update`. Verify/check never
  rewrite it; validate/compile/publish must not touch it.

### D2. DocumentRef fields

Each entry: `id` (stable, equals existing `SpecificationImplementation.id`),
`kind` (initially only `package`), `path` (posix path to `implementation.yaml`
relative to `model-assets/implementations/`), `version`, `owner` (required),
`depends_on` (list of document ids, hand-maintained).

### D3. Lock format and merge safety

JSON Lines: first line is a header with `lock_schema_version`; following lines
are one object per document (`id`, `content_hash`), sorted by `id`. No aggregate
hash, no timestamp — parallel edits to different packages do not conflict on
lock except when both touch the same document line (resolve by re-running
`lock update`).

### D4. Canonical content_hash (same idea as ADR-042)

```
content_hash = "sha256:" + hex(SHA-256(UTF-8(
  json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
)))
```

`payload` is `{ "descriptor": <implementation.yaml without content_digest and
revision>, "body": <parsed body YAML> }`. Hashing parsed structure (not raw
bytes) avoids CRLF/LF and key-order noise. Envelope stamps stay in files for
this series but are **not** authoritative and are **not** verified by lock;
excluding them avoids a lock ↔ stamp cycle. Binding digests (ADR-042) remain
the authority for `DataModelBinding` instances.

### D5. LinkML module placement (versioned from day one)

Schema source of truth:

`model-assets/specifications/moex-repository-manifest/0.1/schemas/moex-repository-manifest.yaml`

(+ short README). Classes: `RepositoryManifest` (`tree_root`), `DocumentRef`,
`RepositoryLockHeader`, `RepositoryLockEntry`, enum `DocumentKindEnum`.

**Must not:**

- live under `moex-dams/0.1/schemas/` (that directory is globbed into DAMS
  artifact generation);
- be imported by `moex-dams.yaml` in this series (would bump DAMS version and
  rewrite `generated/**` / glossary / full-spec);
- ship `specification.yaml` / `publish.yaml` for this module yet (viewer would
  publish it and change publication surface).

Hot path in the loader uses frozen pydantic models with a drift test against
LinkML slots; `check-manifest` validates instances with the LinkML validator.

### D6. Boundaries (not a third registry)

| Concept | Role |
|---|---|
| ADR-031 `TechnicalAsset` | Quanta inside a package |
| `RegistryEntry` | Projections of external master systems |
| `DocumentRef` | File index for the git repository of implementations |

Manifest class names avoid the word “registry”. Manifest `owner` (`@org/team`
or `@user`) is a code/review owner, distinct from `data_owner_ref` (ADR-023).
Manifest classes are outside the `ModelElement` hierarchy (ADR-044).

### D7. Owner

Required. Pattern: `@org/team` or `@user`. Until real handles exist,
`@moex/owner-pending` is allowed. CODEOWNERS generation and expiry policy are
deferred.

### D8. Loader and checks (series outline)

- Read-only `packages/repository-loader`: `load_manifest`, `resolve`,
  `load_package`, `assemble` (in-memory `MOEXModelRepository` shape).
- Lazy load: loading one package does not read others.
- Deterministic order: documents sorted by `id` (code point); paths
  posix-relative.
- `check-manifest`: LinkML validate + referential integrity, hash match,
  orphans (with allow-list from inventory), package-level dependency cycles,
  owner present, unique ids, paths stay under implementations root.
- First CLI consumer: `FilesystemImplementationCatalog` discovery via loader.

### D9. Manifest schema version migration

`manifest_schema_version` is semver. Breaking field renames or removals bump
the major component and require a documented migration note in this ADR (or a
follow-up ADR). Additive optional fields / new `DocumentKindEnum` values are
minor. Lock has its own `lock_schema_version` with the same rule.

## Consequences

- Editors gain an explicit document index and CI gate without moving files.
- Publish/viewer paths stay stable for the series.
- Envelope `content_digest`/`revision` remain until a later go/no-go series.
- Importing the manifest module into DAMS or publishing it in the viewer needs
  an explicit follow-up that re-baselines schema-derived artifacts.

## Alternatives

| Alternative | Why not (this series) |
|---|---|
| Split ModelPackage bodies now | Solves merge pain inside packages; orthogonal to repository index; P1b |
| Extend `implementation.yaml` instead of `manifest.yaml` | Couples kernel envelope to repo index; harder orphan/lock story |
| Put schema under `moex-dams/schemas/` | Contaminates DAMS generation / golden |
| Byte-hash of files | CRLF/LF and YAML key order break cross-OS CI |
| Aggregate lock hash | Creates whole-file merge conflicts |

## Deferred

See [p1-inventory.md](../migration/p1-inventory.md) “Deferred” and the
implementation plan’s deferred list (GitProvider reader, CODEOWNERS, stamp
removal, assembled-repo validation, viewer/API migration, extra document kinds).
