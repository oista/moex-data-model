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
  -e "./packages/external-sources" `
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

## Git provider / publication

- `MOEX_GIT_PROVIDER=local` (default) → branch/commit in this repo working tree; review URL `local://…`
- `MOEX_GIT_PROVIDER=github` → GitHub REST writes + PR (`MOEX_GITHUB_TOKEN`, `MOEX_GITHUB_REPO=owner/moex-data-model`, `MOEX_GITHUB_BASE=main`)
- Publish target is **this** repository (implementation body under `model-assets/…` from `ImplementationCatalog.publication_target`)

## Implementation catalog

Workbench resolves implementations via `FilesystemImplementationCatalog` (scans `model-assets/implementations/**/implementation.yaml`). Path parameter `{implementation_id}` accepts the **canonical coordinate** (`moex:implementation:mdm:0.1.0`) or a **presentation slug** (`mdm`, `crm`, `ucd`, `esed`). Responses and `doc_key` always use the coordinate.

`doc_key` includes the version segment. Bumping an implementation version orphans prior workspace drafts until they are migrated.

Workbench-editable assets: `implementation_kind=linkml` and `implementation_profile=dams-data-model`.

## Endpoints

- `GET /health`
- `GET /implementations` — registry from on-disk envelopes
- `GET /implementations/{implementation_id}` — one asset (slug or coordinate)
- `GET /implementations/{implementation_id}/body` — published YAML text + digest
- `GET /implementations/{implementation_id}/conformance` — assess that implementation
- `POST /validation-runs` — `implementation_id` required; persist assessment
- `POST|GET /workspaces` / `GET /workspaces/{id}` — workspace lifecycle + members
- `GET|PUT /workspaces/{id}/documents/{implementation_id}` — workspace draft YAML (`doc_key` = coordinate)
- `POST /workspaces/{id}/documents/{implementation_id}/mutations` — structured ModelPackage mutations
- `POST /workspaces/{id}/documents/{implementation_id}/semantic-diff` — draft vs published preview (ADR-012)
- `POST /workspaces/{id}/diagrams` — body requires `implementation_id` (+ `profile`)
- `POST /publications` / `GET /publications/{id}` — draft → branch/commit/review (+ Idempotency-Key); `implementation_id` required
- `POST /jobs` (+ `Idempotency-Key`, `source=published|draft`) / `GET /jobs/{id}` — `implementation_id` required
- `POST /model-index/rebuild?implementation_id=` / `GET /model-index/search?q=&implementation_id=` — search projection

## Check

```powershell
.\apps\api\scripts\check.ps1
# or: make api-check
```
