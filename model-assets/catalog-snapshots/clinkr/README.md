# Clinkr / EAM catalog snapshot (ADR-048)

Hand-maintained **file snapshot** used by CI and the topology materializer.
Live Clinkr/EAM API calls are out of scope for the Topology ownership series.

## Files

| Path | Role |
|---|---|
| `catalog-snapshot.json` | Snapshot instance (`CatalogSnapshot` shape from `moex-topology`) |

## Refresh

1. Export or assemble catalog objects into the JSON shape (see schema).
2. Recompute `digest` (`sha256:` + hex of canonical JSON of the payload without `digest`).
3. Bump `catalog_revision`.
4. Open a PR; `check-topology` resolves flows against the new file.

## Uniqueness

`(catalog, kind, external_id)` must be unique within `objects`. Duplicates fail snapshot load.
