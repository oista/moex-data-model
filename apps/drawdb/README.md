# apps/drawdb — self-hosted drawDB (ADR-005)

Isolated editor image. Workbench talks to it via **DBML + postMessage bridge**, never via drawDB's internal JSON.

## License

Upstream [drawdb-io/drawdb](https://github.com/drawdb-io/drawdb) is **AGPL-3.0**. Keep it in a separate process/image; do not bundle its sources into `apps/web`.

## Pin

See [`UPSTREAM_SHA`](UPSTREAM_SHA). Refresh:

```powershell
powershell -NoProfile -File apps/drawdb/scripts/fetch-upstream.ps1
```

## Run (Docker)

```bash
docker compose -f infra/compose/drawdb.yml up -d --build
# → http://localhost:5174
```

## Run (static bridge fallback, no Docker)

Serves the MOEX postMessage bridge page (textarea import/export) for local Workbench tests:

```bash
# from apps/drawdb
npx --yes serve static-bridge -p 5174
```

Set `VITE_DRAWDB_URL=http://localhost:5174` in `apps/web`.

## Bridge protocol

Parent (Workbench) ↔ iframe:

| Direction | `type` | Payload |
|-----------|--------|---------|
| iframe → parent | `moex:ready` | `{}` |
| parent → iframe | `moex:import-dbml` | `{ dbml: string }` |
| parent → iframe | `moex:request-export` | `{}` |
| iframe → parent | `moex:export-dbml` | `{ dbml: string }` |

Origin allowlist: `event.origin` must match parent (Workbench) origin; bridge echoes only to `event.source`.
