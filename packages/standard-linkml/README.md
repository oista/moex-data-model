# moex-standard-linkml

LinkML provider package for MOEX modeling.

- **`LinkMLStandardProvider`** — `StandardProvider` with distinct `LinkMLSpecificationBody` (SchemaView) and `LinkMLImplementationBody` (instance YAML).
- **ER-dictionary ingest** — Entities / Attributes / Relationships sheets → DAMS [`ModelPackage`](../../model_src/schemas/moex-core.yaml) + sidecar envelope.

Depends on [`moex-modeling-kernel`](../modeling-kernel/).

## Why not schema-automator / schemasheets

| Tool | Input | Output | Pilot fit |
|------|-------|--------|-----------|
| schema-automator | data rows | draft LinkML **schema** | wrong artifact |
| schemasheets | class/slot authoring rows | LinkML schema | requires rewriting the dictionary |
| **this ingest** | ER dictionary sheets | **ModelPackage** instance | matches DAMS implementation |

`schema-automator` remains ADR-009 draft-only for schema bootstrap; it is **not** a dependency here.

## Requirements

- **Python 3.11+** (system `python` on many Windows hosts is 3.10 and will fail to install this package)

## Install

From repo root (recommended — creates package `.venv`):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File packages/standard-linkml/scripts/check.ps1
```

Or manually:

```powershell
py -3.14 -m venv packages/standard-linkml/.venv
packages/standard-linkml/.venv/Scripts/python -m pip install -e "./packages/standard-linkml[dev]"
```

## Ingest

1. Export or keep your workbook as `.xlsx`, **or** one CSV per sheet (`Entities.csv`, `Attributes.csv`, `Relationships.csv`).
2. Copy [`templates/er-dictionary.profile.yaml`](templates/er-dictionary.profile.yaml) and adjust sheet/column names, `solution_ref`, `solution_slug`, and `type_map` for your Excel.
3. Run:

```powershell
packages/standard-linkml/.venv/Scripts/python -m moex_standard_linkml.ingest.cli ingest `
  --workbook path/to/model.xlsx `
  --profile packages/standard-linkml/templates/er-dictionary.profile.yaml `
  --schema model_src/schemas/moex-dams.yaml `
  --out $env:TEMP/ingest-out
```

Artifacts in `--out`:

- `{name}.package.yaml` — DAMS `ModelPackage` (logical layer + conceptual stubs)
- `{name}.envelope.yaml` — kernel-shaped implementation envelope (`conforms_to` DAMS, `body_ref`)
- `{name}.validation.txt` — validation report (`linkml.validator` against `ModelPackage`; UTF-8-safe on Windows)

## Mapping semantics (pilot)

- Entities → `LogicalEntity` + 1:1 `ConceptualEntity`
- Attributes → nested `LogicalAttribute` (`pk` → `key_attribute_refs`, types via `type_map`)
- Relationships → `Relationship` with CURIE refs
- One `DomainContext` from profile defaults
- **No** physical objects / field mappings in this slice

## Tests

```powershell
# preferred (venv + install + pytest)
powershell -NoProfile -ExecutionPolicy Bypass -File packages/standard-linkml/scripts/check.ps1

# or, if GNU make is available
make linkml-ingest-check
```

## Success criteria (pilot)

- Fixture ER dictionary maps to YAML that passes `linkml-validate --target-class ModelPackage`
- Envelope has `conforms_to` → moex-dams and `body_ref` → package file
- No `schema-automator` dependency
