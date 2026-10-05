# moex-model CLI

Inbound adapter over the vertical slice. No domain rules here: validate and
publish call `specification-dams` and `publication` application handlers.

```text
moex-model validate       → assess_implementation
moex-model publish        → export_slice_projection (+ refuse generated-draft)
moex-model diagram        → ModelPackage → DBML or Mermaid erDiagram (+ sidecar / SVG)
moex-model import         → ER-dictionary ingest OR schema-automator draft
moex-model map            → SSSOM / LinkML extract / linkml-map transform
moex-model semantic-diff  → diff_implementations
moex-model source         → list / sync / diff external sources (ADR-017)
moex-model export-requirements → RequirementCatalog YAML → CSV
```

Publication Viewer lives at [`apps/viewer/`](../viewer/).

## Commands

From repo root, after install:

```powershell
py -3.14 -m pip install -e "./generated/contracts/moex-dams/0.1" `
  -e "./packages/modeling-kernel" `
  -e "./packages/standard-linkml" `
  -e "./packages/specification-dams" `
  -e "./packages/semantic-mappings" `
  -e "./packages/linkml-tooling[map,automator]" `
  -e "./packages/external-sources" `
  -e "./packages/publication" `
  -e "./apps/cli[dev]"

py -3.14 -m moex_model_cli validate --root .
py -3.14 -m moex_model_cli publish --root .
py -3.14 -m moex_model_cli diagram --root . --profile logical
# → model-assets/.../publications/logical.dbml
py -3.14 -m moex_model_cli diagram --root . --format mermaid --profile logical
# → model-assets/.../publications/logical.erd.md (+ .svg if npx available)
py -3.14 -m moex_model_cli map --root . --sssom model-assets/transformations/mappings/dams-fibo.sssom.yaml
py -3.14 -m moex_model_cli map --root . `
  --transform model-assets/transformations/person-rename-code.yaml `
  --preview packages/linkml-tooling/tests/fixtures/person_sample.json
py -3.14 -m moex_model_cli map --root . `
  --transform model-assets/transformations/person-rename-code.yaml `
  --sample packages/linkml-tooling/tests/fixtures/person_sample.json `
  --backend sql
py -3.14 -m moex_model_cli import `
  --workbook packages/standard-linkml/tests/fixtures/er-dictionary `
  --profile packages/standard-linkml/tests/fixtures/er-dictionary/profile.yaml `
  --out generated/import-pilot `
  --skip-validate
py -3.14 -m moex_model_cli import `
  --source-type json_schema `
  --source packages/linkml-tooling/tests/fixtures/mini.schema.json `
  --out generated/imports `
  --name MiniPerson
py -3.14 -m moex_model_cli export-requirements --root . --out tmp/requirements.csv
```

Defaults are resolved from asset envelopes (relative to `--root`):

- specification: `model-assets/specifications/moex-dams/0.1/specification.yaml` → `schema_body`
- implementation: `model-assets/implementations/solutions/trading-platform/implementation.yaml` → `implementation_body`
- publish out: `model-assets/implementations/solutions/trading-platform/publications/vertical_slice.json`

`import`:

- ER-dictionary → ModelPackage (`--workbook` / `--profile` / `--out`)
- schema-automator → `generated-draft` under `--out/<job_id>/` (`--source-type` / `--source` / `--out`); never auto-published (ADR-009)

`map`:

- `--sssom` / `--extract-schema` (semantic-mappings)
- `--transform` + `--preview`|`--sample` via `LinkmlMapProvider` (ADR-008)
- `--backend object` (default) or `--backend sql` (SQLCompiler + SQLite; no `expr:`)

Workbench import wizard: `/workspaces/:workspaceId/import` (Stage 7b).

## Tests

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File apps/cli/scripts/check.ps1
```

Or `make check`.
