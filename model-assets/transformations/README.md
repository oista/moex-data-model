# Transformation specifications (Stage 7)

YAML files here are loaded by `moex-model map --transform`.

Each file combines:

1. A `moex:` envelope (`spec_id`, `source_schema_revision`, `target_schema_revision`,
   preserved/lost semantics, optional `source_schema` path).
2. A `linkml-map` `TransformationSpecification` body (`id`, `class_derivations`, …).

## Fixtures

Synthetic (generic):

- `person-identity.yaml` — lossless identity
- `person-rename-code.yaml` — synthetic migration (revision src→tgt)

DAMS slice (not a released DAMS 0.2):

- `dams-logical-entity-rename-kind.yaml` — `dams-0.1-slice` → `dams-0.1-next-slice`
  renames `LogicalEntity.entity_type` → `logical_entity_kind`
- Schemas: `schemas/dams_logical_entity_source.yaml`, `schemas/dams_logical_entity_target.yaml`
- Sample: `samples/dams_logical_entity_sample.json`

```text
moex-model map --transform model-assets/transformations/dams-logical-entity-rename-kind.yaml \
  --sample model-assets/transformations/samples/dams_logical_entity_sample.json
```

SSSOM / glossary extract (separate contour):

- `mappings/dams-fibo.sssom.yaml`
- `glossary/skos_concepts.yaml`
