# moex-specification-dams

DAMS specification module: MOEX semantic rules, `DamsModelGraphView`, and
`ConformanceReport` orchestration for LinkML implementations.

Does **not** hand-copy ConceptualEntity / LogicalEntity — instance data stays
as dicts loaded by `standard-linkml`; this package owns rules and graph views.

## Assess MDM solution

```powershell
py -3.14 -m pip install -e "./packages/modeling-kernel" `
  -e "./packages/standard-linkml" `
  -e "./packages/specification-dams[dev]"

py -3.14 -m moex_dams.cli assess `
  --schema model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml `
  --implementation model-assets/implementations/solutions/mdm/mdm-solution-model.yaml
```

## Projections (ADR-006)

One-way derived views from a ModelPackage YAML (not canonical):

| API | Format | Typical output |
|-----|--------|----------------|
| `project_model_package_to_dbml` / `write_dbml_artifact` | DBML | `publications/{logical,physical}.dbml` (viewer / drawDB) |
| `project_model_package_to_er_diagram` / `write_er_diagram_artifact` | Mermaid `erDiagram` | `publications/{logical,physical}.erd.md` (+ SVG via `try_render_er_svg`) |

CLI: `moex-model diagram --format dbml|mermaid --profile logical|physical` (default out under implementation `publications/`).

## Tests

```powershell
py -3.14 -m pytest packages/specification-dams/tests -q
```
