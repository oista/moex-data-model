# moex-linkml-tooling

Optional adapters for Stage 7:

| Extra | Implements | Upstream |
|-------|------------|----------|
| `[map]` | `MappingProvider` via `LinkmlMapProvider` | `linkml-map` ObjectTransformer only |
| `[automator]` | `ImportDraftEngine` via `SchemaAutomatorImportEngine` | `schema-automator` |

## Import source matrix

| `source_type` | Support | Engine |
|---------------|---------|--------|
| `json_schema` | required | `JsonSchemaImportEngine` |
| `sql` | required | DDL → temp SQLite → `SqlImportEngine` |
| `csv` | best-effort | `TabularImportEngine` when available; else `unsupported` diagnostic |
| `rdf` | best-effort | `OwlImportEngine` when available; else `unsupported` diagnostic |

Drafts always get `status: generated-draft` and are never auto-published.

## Expression policy (map)

`unrestricted_eval` is always false on ObjectTransformer. Specs containing `expr:` fail validation unless `moex.allow_unrestricted_eval: true` **and** every expression string is on the provider allowlist (default allowlist is empty → all expr rejected).
