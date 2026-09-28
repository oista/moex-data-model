# Transformation specifications (Stage 7)

YAML files here are loaded by `moex-model map --transform`.

Each file combines:

1. A `moex:` envelope (`spec_id`, `source_schema_revision`, `target_schema_revision`,
   preserved/lost semantics, optional `source_schema` path).
2. A `linkml-map` `TransformationSpecification` body (`id`, `class_derivations`, …).

Fixtures:

- `person-identity.yaml` — lossless identity
- `person-rename-code.yaml` — synthetic migration (revision src→tgt)
