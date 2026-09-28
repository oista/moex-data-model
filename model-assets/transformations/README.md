# Transformation specifications (Stage 7)

YAML files here are loaded by `moex-model map --transform`.

Each file combines:

1. A `moex:` envelope (`spec_id`, `source_schema_revision`, `target_schema_revision`,
   preserved/lost semantics, optional `source_schema` / `target_schema` paths).
2. A `linkml-map` `TransformationSpecification` body (`id`, `class_derivations`, …).

## Conventions (DAMS slice migrations)

- **Slices, not full DAMS:** fixtures under `schemas/` are minimal standalone LinkML
  schemas. They are **not** `model-assets/specifications/moex-dams/0.2/`.
- **Revision tags:**
  - `dams-0.1-slice` — source (current fixture shape)
  - `dams-0.1-next-slice` — target after a breaking rename
  - Identity maps use equal revisions (`dams-0.1-slice` → `dams-0.1-slice`)
- **Schema paths:** when `source_schema_revision != target_schema_revision`, both
  `moex.source_schema` and `moex.target_schema` are **required**. Paths are relative
  to the transform YAML. Missing path → `MAP-SPEC-003`; file not found → `MAP-SPEC-004`.
- **Runtime:** ObjectTransformer loads only `source_schema`; `target_schema` is
  audit/validate-only until a later increment.
- **SQL backend:** `populated_from` only (no `expr:`).

## Migration index

| Spec | Source rev | Target rev | Kind | Sample |
|------|------------|------------|------|--------|
| `person-identity.yaml` | fixture-person-src-0.1 | fixture-person-src-0.1 | lossless | `packages/linkml-tooling/tests/fixtures/person_sample.json` |
| `person-rename-code.yaml` | fixture-person-src-0.1 | fixture-person-tgt-0.1 | partial | same |
| `dams-logical-entity-identity.yaml` | dams-0.1-slice | dams-0.1-slice | lossless | `samples/dams_logical_entity_sample.json` |
| `dams-logical-entity-rename-kind.yaml` | dams-0.1-slice | dams-0.1-next-slice | partial | same |
| `dams-logical-attribute-rename-type.yaml` | dams-0.1-slice | dams-0.1-next-slice | partial | `samples/dams_logical_attribute_sample.json` |

## Fixtures

Synthetic (generic):

- `person-identity.yaml` — lossless identity
- `person-rename-code.yaml` — synthetic migration (revision src→tgt)

DAMS slice (not a released DAMS 0.2):

- `dams-logical-entity-identity.yaml` — lossless LogicalEntity identity
- `dams-logical-entity-rename-kind.yaml` — `entity_type` → `logical_entity_kind`
- `dams-logical-attribute-rename-type.yaml` — `logical_type` → `attribute_type`
- Schemas: `schemas/dams_logical_entity_*.yaml`, `schemas/dams_logical_attribute_*.yaml`
- Samples: `samples/dams_logical_entity_sample.json`, `samples/dams_logical_attribute_sample.json`

```text
moex-model map --transform model-assets/transformations/dams-logical-entity-rename-kind.yaml \
  --sample model-assets/transformations/samples/dams_logical_entity_sample.json

moex-model map --transform model-assets/transformations/dams-logical-attribute-rename-type.yaml \
  --sample model-assets/transformations/samples/dams_logical_attribute_sample.json
```

SSSOM / glossary extract (separate contour):

- `mappings/dams-fibo.sssom.yaml`
- `glossary/skos_concepts.yaml`
