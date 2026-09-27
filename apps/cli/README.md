# moex-model CLI

Inbound adapter over the vertical slice. No domain rules here: validate and
publish call `specification-dams` and `publication` application handlers.

```text
moex-model validate  → assess_implementation
moex-model publish   → export_slice_projection
```

Publication Viewer lives at [`apps/viewer/`](../viewer/).

## Commands

From repo root, after install:

```powershell
py -3.14 -m pip install -e "./packages/modeling-kernel" `
  -e "./packages/standard-linkml" `
  -e "./packages/specification-dams" `
  -e "./packages/publication" `
  -e "./apps/cli[dev]"

py -3.14 -m moex_model_cli validate --root .
py -3.14 -m moex_model_cli publish --root .
```

Defaults are resolved from asset envelopes (relative to `--root`):

- specification: `model-assets/specifications/moex-dams/0.1/specification.yaml` → `schema_body`
- implementation: `model-assets/implementations/solutions/trading-platform/implementation.yaml` → `implementation_body`
- publish out: `model-assets/implementations/solutions/trading-platform/publications/vertical_slice.json`

## Tests

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File apps/cli/scripts/check.ps1
```

Or `make check`.
