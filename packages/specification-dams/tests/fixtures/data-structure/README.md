# Positive fixtures: DataStructure / SchemaNode

Four acceptance fixtures under `packages/specification-dams/tests/fixtures/data-structure/`.

| Fixture | Purpose |
|---|---|
| `relational-table.yaml` | Relational DataStructure, root object, scalar columns |
| `nested-json.yaml` | json_schema with depth ≥3 object tree |
| `avro-union.yaml` | Avro-like union with ≥2 branches |
| `message-headers.yaml` | Message with payload + headers structures |

Validated by LinkML + DAMS `check_data_structures`.
