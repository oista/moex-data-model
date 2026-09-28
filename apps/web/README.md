# moex-model-web

Web Workbench MVP (Stage 4 slice): React + Vite UI over `apps/api`.

Monaco YAML editor + entity/relationship/mapping forms. Diagram page embeds drawDB (ADR-005) via `VITE_DRAWDB_URL` (default `http://localhost:5174`). No OIDC yet.

## Dev

Terminal 1 — API:

```powershell
$env:MOEX_DATABASE_URL = "sqlite:///./.data/moex_api.sqlite"
py -3.14 -m moex_model_api
```

Terminal 2 — UI (proxies `/api` → `:8000`):

```powershell
cd apps/web
npm install
npm run dev
# http://127.0.0.1:5173
```

Set **Actor** in the sidebar (`X-Moex-Actor`).

## Check

```powershell
.\apps\web\scripts\check.ps1
# or: make web-check
```

Playwright bridge smoke (static-bridge + Diagram page, API mocked):

```powershell
.\apps\web\scripts\e2e.ps1
# or: make web-e2e
```

## Routes

| Path | Purpose |
|------|---------|
| `/` | Dashboard (health + last job) |
| `/workspaces` | List / create workspaces |
| `/workspaces/:workspaceId/import` | Stage 7b schema-automator import wizard (`generated-draft`) |
| `/workspaces/:workspaceId/transform` | Stage 7 map/transform preview|sample (linkml-map, object\|sql) |
| `/models` | Implementation registry |
| `/models/trading` | Conformance + model-index search |
| `/models/trading/edit` | Monaco YAML + entity forms + draft + Review changes + Publish draft |
| `/models/trading/diagram` | drawDB iframe + DBML submit/apply (`?profile=logical\|physical`) |
| `/models/trading/validate` | Sync validate job report |
