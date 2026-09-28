# moex-model CLI

Inbound adapter over the vertical slice. No domain rules here: validate and
publish call `specification-dams` and `publication` application handlers.

```text
moex-model validate       → assess_implementation
moex-model publish        → export_slice_projection
moex-model diagram        → ModelPackage → DBML (+ sidecar manifest)
moex-model import         → ER-dictionary ingest (standard-linkml)
moex-model map            → SSSOM load / LinkML binding extract
moex-model semantic-diff  → diff_implementations
```

Publication Viewer lives at [`apps/viewer/`](../viewer/).

## Commands

From repo root, after install:

```powershell
py -3.14 -m pip install -e "./packages/modeling-kernel" `
  -e "./packages/standard-linkml" `
  -e "./packages/specification-dams" `
  -e "./packages/semantic-mappings" `
  -e "./packages/publication" `
  -e "./apps/cli[dev]"

py -3.14 -m moex_model_cli validate --root .
py -3.14 -m moex_model_cli publish --root .
py -3.14 -m moex_model_cli diagram --root . --profile logical --out generated/artifacts/diagrams/trading-logical.dbml
py -3.14 -m moex_model_cli map --root . --sssom model-assets/transformations/mappings/dams-fibo.sssom.yaml
py -3.14 -m moex_model_cli import `
  --workbook packages/standard-linkml/tests/fixtures/er-dictionary `
  --profile packages/standard-linkml/tests/fixtures/er-dictionary/profile.yaml `
  --out generated/import-pilot `
  --skip-validate
```

Defaults are resolved from asset envelopes (relative to `--root`):

- specification: `model-assets/specifications/moex-dams/0.1/specification.yaml` → `schema_body`
- implementation: `model-assets/implementations/solutions/trading-platform/implementation.yaml` → `implementation_body`
- publish out: `model-assets/implementations/solutions/trading-platform/publications/vertical_slice.json`

`import` is ER-dictionary → ModelPackage only (ADR-009); schema-automator wizard is Stage 7.  
`map` loads SSSOM / extracts LinkML bindings (ADR-008); `linkml-map` engine is Stage 7.

## Tests

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File apps/cli/scripts/check.ps1
```

Or `make check`.
