# Migration: `model_src/` → `model-assets/` + `generated/`

**Date:** 2026-09-28  
**Status:** Done (target-after-slice layout)  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md) §12

Physical move of model assets after the first vertical slice. Identities (`element_id`, schema URIs, CURIE prefixes) are unchanged — only filesystem paths.

## Path mapping

| Old path | New path |
|---|---|
| `model_src/schemas/*` | `model-assets/specifications/moex-dams/0.1/schemas/` |
| `model_src/examples/trading-solution-model.yaml` | `model-assets/implementations/solutions/trading-platform/trading-solution-model.yaml` |
| `model_src/examples/publish.yaml` | `model-assets/implementations/solutions/trading-platform/publish.yaml` |
| `model_src/examples/publications/*` | `model-assets/implementations/solutions/trading-platform/publications/` |
| `model_src/examples/*` (other YAML) | `model-assets/specifications/moex-dams/0.1/examples/` |
| `model_src/publish.yaml` | `model-assets/specifications/moex-dams/0.1/publish.yaml` |
| `model_src/README.md` | `model-assets/specifications/moex-dams/0.1/README.md` |
| `model_src/architecture-catalog.yaml` | `model-assets/specifications/moex-dams/0.1/architecture-catalog.yaml` |
| `model_src/mappings/*` | `model-assets/transformations/mappings/` |
| `model_src/glossary/*` | `model-assets/transformations/glossary/` |
| `model_src/ontologies/*` | `model-assets/implementations/ontologies/` |
| `model_src/generated/*` | `generated/artifacts/moex-dams/0.1/` |
| `model_src/moex-dams-drawdb-colored.dbml` | `generated/artifacts/moex-dams/0.1/moex-dams-drawdb-colored.dbml` |
| `viewer/` | `apps/viewer/` |

## Not moved

| Path | Reason |
|---|---|
| `packages/ontology/` | Shim over `standard-owl`; stays per [app_model.md](../architecture/app_model.md) |
| `packages/ontology-catalog/` | Already on target path |

## Envelope files (new)

| Path | Role |
|---|---|
| `model-assets/standards/linkml/1.x/standard.yaml` | `ModelingStandard` descriptor |
| `model-assets/specifications/moex-dams/0.1/specification.yaml` | `ReferenceSpecification` descriptor |
| `model-assets/implementations/solutions/trading-platform/implementation.yaml` | `SpecificationImplementation` descriptor |

## Repo root marker

Presence of:

```text
model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml
```

## Windows note

If an empty leftover `viewer/` directory remains after the move to `apps/viewer/`, it is not tracked by Git. Close IDE handles on that path and `rmdir viewer` locally.
