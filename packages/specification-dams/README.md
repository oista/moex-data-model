# moex-specification-dams

DAMS specification module: MOEX semantic rules, `DamsModelGraphView`, and
`ConformanceReport` orchestration for LinkML implementations.

Does **not** hand-copy ConceptualEntity / LogicalEntity — instance data stays
as dicts loaded by `standard-linkml`; this package owns rules and graph views.

## Assess trading-solution

```powershell
py -3.14 -m pip install -e "./packages/modeling-kernel" `
  -e "./packages/standard-linkml" `
  -e "./packages/specification-dams[dev]"

py -3.14 -m moex_dams.cli assess `
  --schema model_src/schemas/moex-dams.yaml `
  --implementation model_src/examples/trading-solution-model.yaml
```

## Tests

```powershell
py -3.14 -m pytest packages/specification-dams/tests -q
```
