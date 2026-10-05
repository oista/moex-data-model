# moex-publication

Read-model projection from the modeling vertical slice
(`assess_implementation` → `PublicationModule` / static JSON for [`apps/viewer`](../../apps/viewer/)).

## Export slice JSON for the viewer

```powershell
py -3.14 -m pip install -e "./packages/modeling-kernel" `
  -e "./packages/standard-linkml" `
  -e "./packages/specification-dams" `
  -e "./packages/publication[dev]"

py -3.14 -m moex_publication.cli export-slice `
  --schema model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml `
  --implementation model-assets/implementations/solutions/mdm/mdm-solution-model.yaml `
  --out model-assets/implementations/solutions/mdm/publications/vertical_slice.json
```

Manifest: [`publish.yaml`](../../model-assets/implementations/solutions/mdm/publish.yaml)
includes sections that read this JSON.
