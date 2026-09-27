# moex-model CLI

Inbound adapter over the vertical slice. No domain rules here: validate and
publish call `specification-dams` and `publication` application handlers.

```text
moex-model validate  → assess_implementation
moex-model publish   → export_slice_projection
```

The HTML viewer stays at repo-root `viewer/` (`apps/viewer` is still
target-after-slice).

## Commands

From repo root, after install:

```powershell
py -3.14 -m pip install -e "./packages/modeling-kernel" `
  -e "./packages/standard-linkml" `
  -e "./packages/specification-dams" `
  -e "./packages/publication" `
  -e "./apps/cli[dev]"

py -3.14 -m moex_model_cli validate --root .
py -3.14 -m moex_model_cli publish --root . --out model_src/examples/publications/vertical_slice.json
```

Defaults (relative to `--root`):

- schema: `model_src/schemas/moex-dams.yaml`
- implementation: `model_src/examples/trading-solution-model.yaml`

## Tests

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File apps/cli/scripts/check.ps1
```

Or `make check`.
