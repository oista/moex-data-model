# moex-model-web

Web Workbench MVP (Stage 4 slice): React + Vite UI over `apps/api`.

Monaco YAML editor + entity forms (add/update/delete LogicalEntity/Attribute). No drawDB or OIDC yet.

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

## Routes

| Path | Purpose |
|------|---------|
| `/` | Dashboard (health + last job) |
| `/workspaces` | List / create workspaces |
| `/models` | Implementation registry |
| `/models/trading` | Conformance + model-index search |
| `/models/trading/edit` | Monaco YAML + entity forms + draft + Publish draft |
| `/models/trading/validate` | Sync validate job report |
