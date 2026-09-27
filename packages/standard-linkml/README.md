# moex-standard-linkml

LinkML provider package for MOEX modeling.

- **`LinkMLStandardProvider`** — `StandardProvider` with distinct `LinkMLSpecificationBody` (SchemaView) and `LinkMLImplementationBody` (instance YAML).
- **ER-dictionary ingest** — spreadsheet / CSV sheets → DAMS [`ModelPackage`](../../model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml) + sidecar envelope.

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

1. Export or keep your workbook as `.xlsx`, **or** one CSV per sheet (see sheet names below).
2. Copy [`templates/er-dictionary.profile.yaml`](templates/er-dictionary.profile.yaml) and adjust sheet/column names, `solution_ref`, `solution_slug`, and `type_map` for your Excel.
3. Run:

```powershell
packages/standard-linkml/.venv/Scripts/python -m moex_standard_linkml.ingest.cli ingest `
  --workbook path/to/model.xlsx `
  --profile packages/standard-linkml/templates/er-dictionary.profile.yaml `
  --schema model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml `
  --out $env:TEMP/ingest-out
```

Artifacts in `--out`:

- `{name}.package.yaml` — DAMS `ModelPackage`
- `{name}.envelope.yaml` — kernel-shaped implementation envelope (`conforms_to` DAMS, `body_ref`)
- `{name}.validation.txt` — validation report (`linkml.validator` against `ModelPackage`; UTF-8-safe on Windows)

## Sheets

| Sheet | Required | Role |
|-------|----------|------|
| **Conceptual** | no | `ConceptualEntity` rows (`name`, `title`, `description`) |
| **Entities** | yes | `LogicalEntity`; optional `conceptual_ref` → Conceptual `name` (`\|` for several) |
| **Attributes** | yes | nested `LogicalAttribute` on entity |
| **Relationships** | no | logical `Relationship` |
| **PhysicalObjects** | no | `PhysicalObject` (table, topic, api, …) |
| **PhysicalFields** | no | fields; `object` = PhysicalObjects.name |
| **Mappings** | no | `source` / `target` as `Entity.attr` or `Object.field` (or bare entity/object name); `\|` for several |

Example fixture: [`tests/fixtures/er-dictionary/`](tests/fixtures/er-dictionary/).

### Conceptual ↔ logical

- With a **Conceptual** sheet: concepts come only from that sheet. `Entities.conceptual_ref` must name a concept (or stay empty → no refs). Logical and conceptual names may differ (`TradingClient` → `Client`).
- **Compat (no Conceptual sheet):** empty `conceptual_ref` still creates a 1:1 stub concept from the entity name (legacy behaviour).

### Physical ↔ mapping

- `PhysicalObjects` (DAMS-required): `name`, `description`, `object_kind`, `qualified_name`, `system_ref`, `technology`, `direction`, `native_schema_ref`.
- `PhysicalFields`: `object`, `name`, `native_type`; optional `native_name`, `required`, `schema_path`.
- `Mappings`: dotted refs resolve to logical attributes / physical fields first; bare names to entities / objects. Defaults: `mapping_type=field_mapping`, `mapping_cardinality=one_to_one`.

## Mapping semantics

- Entities → `LogicalEntity` (+ `conceptual_entity_refs` or compat stubs)
- Attributes → nested `LogicalAttribute` (`pk` → `key_attribute_refs`, types via `type_map`)
- Relationships → `Relationship` with CURIE refs
- One `DomainContext` from profile defaults
- PhysicalObjects / PhysicalFields / Mappings when sheets are present

## Tests

```powershell
# preferred (venv + install + pytest)
powershell -NoProfile -ExecutionPolicy Bypass -File packages/standard-linkml/scripts/check.ps1

# or, if GNU make is available
make linkml-ingest-check
```

## Success criteria

- Fixture ER dictionary maps to YAML that passes `linkml-validate --target-class ModelPackage`
- Cross-name conceptual refs and field-level mappings round-trip in tests
- Envelope has `conforms_to` → moex-dams and `body_ref` → package file
- No `schema-automator` dependency
