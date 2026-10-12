# Topology ownership inventory

**Date:** 2026-10-12  
**ADR:** [ADR-048](../adr/ADR-048-topology-ownership.md)  
**Scope:** inventory of authored topology slots on `DataFlow` before the Topology ownership series.

## Schema source

Primary: [`moex-integration.yaml`](../../model-assets/specifications/moex-dams/0.1/schemas/moex-integration.yaml)  
Merged copy (schema only, not instances): [`moex-dams-full.yaml`](../../model-assets/implementations/enterprise/moex-hierarchy/moex-dams-full.yaml)

## Topology / catalog slots on DataFlow (today)

| Slot | Range | Required today | Target after series |
|---|---|---|---|
| `integration_ref` | `IntegrationReference` | yes | **authored** (keep) |
| `contract_ref` | `DataContractReference` | no | **authored** (keep) |
| `entity_bindings` | `DataFlowEntityBinding` | no | **authored** (keep; + catalog_* refs) |
| `source_solution_ref` | `ITSolution` | yes | **derived** (remove authored) |
| `target_solution_ref` | `ITSolution` | yes | **derived** |
| `source_system_ref` | `ITSystem` | yes | **derived** |
| `target_system_ref` | `ITSystem` | yes | **derived** |
| `source_platform_ref` | `ITPlatform` | yes | **derived** |
| `target_platform_ref` | `ITPlatform` | yes | **derived** |
| `integration_level` | `IntegrationLevelEnum` | yes | **derived** |
| `integration_class` | `IntegrationClassEnum` | yes | **derived** |
| `integration_channel` | `IntegrationChannelEnum` | yes | **derived** |
| `integration_spec_ref` | `uri` | yes | **derived** |

New authored slot (PR-1): `bound_catalog_revision`.

## Semantic slots on DataFlowEntityBinding (today)

| Slot | Notes |
|---|---|
| `flow_ref` | back-ref to DataFlow |
| `source_model_ref` | model URI |
| `logical_entity_ref` / `logical_attribute_refs` | semantic selection |
| `carrier_refs` / `schema_node_refs` | physical / structure |
| `transformation_mapping_refs` | mappings |
| `direction` | producer/consumer role (`FlowDirectionEnum`) |

New optional slots (PR-1): `catalog_operation_ref`, `catalog_participant_ref`.

## Instance count (2026-10-12)

| Location | DataFlow count |
|---|---:|
| `model-assets/specifications/moex-dams/0.1/examples/client-data-flow.yaml` | 1 |
| `model-assets/implementations/**` (`data_flows` collections) | 0 |
| Partial in-memory test fixture (`test_technical_asset_checks.py`) | 1 (not a YAML file) |

Canonical example `integration_ref`: `clinkr:integration/INT-00421`  
Example topology CURIE prefixes: `eam:solution/*`, `eam:system/*`, `eam:platform/*`  
Example spec URI: `https://clinkr.moex.com/specifications/INT-00421/asyncapi/2.3.0`

Related example (no topology slots): `client-contract-binding.yaml` (`DataModelBinding`, same `integration_ref`).

## Consumers of topology fields (code / docs)

| Path | Role |
|---|---|
| `apps/viewer/.../linkml_normalizer.py` | copy: Clinkr master vs DAMS semantics |
| `packages/specification-dams/.../technical_assets.py` | walks `data_flows` for `carrier_refs` (PDM-010) |
| `packages/specification-dams/.../formal_checks.py` | FLW-001 soft presence of `data_flows` |
| `docs/architecture/uml/02-solution-model-governance.puml` | note: topology required on DataFlow |
| Spec / glossary / dams_entities_list | normative prose |

`dams_to_graph.py` does **not** ingest `data_flows` today. Neo4j is out of scope (ADR-003).

## Implications for migration

- No bulk YAML rewrite in `implementations/`.
- Deprecation window is PR-shaped (PR-1…PR-4), not calendar-shaped.
- PR-5 migration script primarily targets the one example + external consumers.
