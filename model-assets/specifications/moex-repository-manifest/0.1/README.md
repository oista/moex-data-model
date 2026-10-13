# moex-repository-manifest

LinkML schema for the **repository document index** (`manifest.yaml`) and lock
line shapes (`manifest.lock`), per [ADR-047](../../../docs/adr/ADR-047-repository-manifest-and-lock.md)
and [ADR-054](../../../docs/adr/ADR-054-repository-aggregates-and-manifest.md).

This is **not** the DAMS domain model. It lives as a sibling specification under
`model-assets/specifications/` so that:

- it is **not** globbed into DAMS artifact generation (`moex-dams/0.1/schemas/*.yaml`);
- it is **not** imported by `moex-dams.yaml` (keeps `generated/**` stable);
- it has **no** `specification.yaml` / `publish.yaml` yet (viewer would otherwise publish it).

`DocumentKindEnum` is **package-only** until separate envelopes exist (ADR-054 D2).
`MOEXModelRepository` remains a validation composite; `RepositoryLoader.assemble()`
fills `model_packages` only.

## Layout

| Path | Role |
|---|---|
| `schemas/moex-repository-manifest.yaml` | Schema source of truth |
| Instance (repo root relative) `model-assets/implementations/manifest.yaml` | Hand-edited index |
| Instance `model-assets/implementations/manifest.lock` | Generated JSON Lines |

## Classes

- `RepositoryManifest` (`tree_root`) — index header + `documents`
- `DocumentRef` — one addressable document (`kind: package`)
- `RepositoryLockHeader` / `RepositoryLockEntry` — lock JSON Lines records

## Related

- Inventory: [p1-inventory.md](../../../docs/migration/p1-inventory.md)
- Aggregates decision: [ADR-054](../../../docs/adr/ADR-054-repository-aggregates-and-manifest.md)
- Integrity algorithm kinship: [ADR-042](../../../docs/adr/ADR-042-integrity-digest-revisions.md)
- Digest diagram: [MODELING_ARCHITECTURE §9.1](../../../docs/architecture/MODELING_ARCHITECTURE.md)
