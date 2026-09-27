# moex-standard-linkml

LinkML provider package for MOEX modeling. **First module: ER-dictionary ingest.**

Converts a relational model dictionary (Entities / Attributes / Relationships sheets in XLS or CSV) into a DAMS [`ModelPackage`](../../model_src/schemas/moex-core.yaml) YAML plus a sidecar `SpecificationImplementation` envelope.

## Why not schema-automator / schemasheets

| Tool | Input | Output | Pilot fit |
|------|-------|--------|-----------|
| schema-automator | data rows | draft LinkML **schema** | wrong artifact |
| schemasheets | class/slot authoring rows | LinkML schema | requires rewriting the dictionary |
| **this ingest** | ER dictionary sheets | **ModelPackage** instance | matches DAMS implementation |

`schema-automator` remains ADR-009 draft-only for schema bootstrap; it is **not** a dependency here.

## Install

```bash
python -m pip install -e "./packages/standard-linkml[dev]"
```

## Ingest

1. Export or keep your workbook as `.xlsx`, **or** one CSV per sheet (`Entities.csv`, `Attributes.csv`, `Relationships.csv`).
2. Copy [`templates/er-dictionary.profile.yaml`](templates/er-dictionary.profile.yaml) and adjust sheet/column names, `solution_ref`, `solution_slug`, and `type_map` for your Excel.
3. Run:

```bash
moex-linkml ingest \
  --workbook path/to/model.xlsx \
  --profile packages/standard-linkml/templates/er-dictionary.profile.yaml \
  --schema model_src/schemas/moex-dams.yaml \
  --out /tmp/ingest-out
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

```bash
make linkml-ingest-check
# or
python -m pytest packages/standard-linkml/tests -q
```

## Success criteria (pilot)

- Fixture ER dictionary maps to YAML that passes `linkml-validate --target-class ModelPackage`
- Envelope has `conforms_to` → moex-dams and `body_ref` → package file
- No `schema-automator` dependency
