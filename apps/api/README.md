# moex-model-api

Inbound HTTP adapter (Stage 3 narrow-v2). Domain rules stay in `specification-dams`;
this app wires FastAPI + SQLAlchemy adapters behind ports (ADR-003, invariant 11).

## Run (local SQLite)

```powershell
$env:MOEX_DATABASE_URL = "sqlite:///./.data/moex_api.sqlite"
py -3.14 -m pip install -e "./apps/api[dev]" `
  -e "./generated/contracts/moex-dams/0.1" `
  -e "./packages/modeling-kernel" `
  -e "./packages/standard-linkml" `
  -e "./packages/specification-dams" `
  -e "./packages/git-adapter" `
  -e "./apps/cli"
py -3.14 -m moex_model_api
# http://127.0.0.1:8000/docs
```

## Run (Postgres compose)

```powershell
docker compose -f infra/compose/postgres.yml up -d
$env:MOEX_DATABASE_URL = "postgresql+psycopg://moex:moex@localhost:5432/moex"
alembic -c apps/api/alembic.ini upgrade head
py -3.14 -m moex_model_api
```

## Auth

Dev header only: `X-Moex-Actor` (default `dev`). Upserts `user_identity` + `editor` role on first write. OIDC later.

## Git provider

- `MOEX_GIT_PROVIDER=local` (default) → `LocalGitProvider`
- `MOEX_GIT_PROVIDER=github` → read-only GitHub REST (`MOEX_GITHUB_TOKEN`, `MOEX_GITHUB_REPO=owner/name`)

## Endpoints

- `GET /health`
- `GET /implementations` — known slice registry (trading)
- `GET /implementations/trading/body` — published trading YAML text + digest
- `GET /implementations/trading/conformance` — assess default trading-platform slice
- `POST /validation-runs` — persist assessment into operational tables
- `POST|GET /workspaces` / `GET /workspaces/{id}` — workspace lifecycle + members
- `GET|PUT /workspaces/{id}/documents/trading` — workspace draft YAML
- `POST /workspaces/{id}/documents/trading/mutations` — add LogicalEntity / LogicalAttribute
- `POST /jobs` (+ `Idempotency-Key`, `source=published|draft`) / `GET /jobs/{id}`
- `POST /model-index/rebuild` / `GET /model-index/search?q=` — search projection

## Check

```powershell
.\apps\api\scripts\check.ps1
# or: make api-check
```
