# moex-publication

Read-model projection from the modeling vertical slice
(`assess_implementation` → `PublicationModule` / static JSON for the root viewer).

The HTML viewer stays at repo-root [`viewer/`](../../viewer/) until after the slice
is stable (`apps/viewer` is target-after-slice only).

## Export slice JSON for the viewer

```powershell
py -3.14 -m pip install -e "./packages/modeling-kernel" `
  -e "./packages/standard-linkml" `
  -e "./packages/specification-dams" `
  -e "./packages/publication[dev]"

py -3.14 -m moex_publication.cli export-slice `
  --schema model_src/schemas/moex-dams.yaml `
  --implementation model_src/examples/trading-solution-model.yaml `
  --out model_src/examples/publications/vertical_slice.json
```

Manifest: [`model_src/examples/publish.yaml`](../../model_src/examples/publish.yaml)
includes sections that read this JSON.
