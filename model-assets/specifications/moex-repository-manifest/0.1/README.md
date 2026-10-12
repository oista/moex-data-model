# moex-repository-manifest

LinkML schema for the **repository document index** (`manifest.yaml`) and lock
line shapes (`manifest.lock`), per [ADR-047](../../../docs/adr/ADR-047-repository-manifest-and-lock.md).

This is **not** the DAMS domain model. It lives as a sibling specification under
`model-assets/specifications/` so that:

- it is **not** globbed into DAMS artifact generation (`moex-dams/0.1/schemas/*.yaml`);
- it is **not** imported by `moex-dams.yaml` in the P1 series (keeps `generated/**` stable);
- it has **no** `specification.yaml` / `publish.yaml` yet (viewer would otherwise publish it).

## Layout

| Path | Role |
|---|---|
| `schemas/moex-repository-manifest.yaml` | Schema source of truth |
| Instance (repo root relative) `model-assets/implementations/manifest.yaml` | Hand-edited index (added in a later PR) |
| Instance `model-assets/implementations/manifest.lock` | Generated JSON Lines (later PR) |

## Classes

- `RepositoryManifest` (`tree_root`) — index header + `documents`
- `DocumentRef` — one addressable document (`kind: package` today)
- `RepositoryLockHeader` / `RepositoryLockEntry` — lock JSON Lines records

## Related

- Inventory: [p1-inventory.md](../../../docs/migration/p1-inventory.md)
- Integrity algorithm kinship: [ADR-042](../../../docs/adr/ADR-042-integrity-digest-revisions.md)
