# moex-model-api

Inbound HTTP adapter (Stage 3 slice). Domain rules stay in `specification-dams`;
this app wires FastAPI + SQLAlchemy adapters behind ports (ADR-003, invariant 11).

## Run (local SQLite)

```powershell
$env:MOEX_DATABASE_URL = "sqlite:///./.data/moex_api.sqlite"
py -3.14 -m pip install -e "./apps/api[dev]" `
  -e "./generated/contracts/moex-dams/0.1" `
  -e "./packages/modeling-kernel" `
  -e "./packages/standard-linkml" `
  -e "./packages/specification-dams"
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

## Endpoints

- `GET /health`
- `GET /implementations/trading/conformance` — assess default trading-platform slice
- `POST /validation-runs` — persist assessment into operational tables
