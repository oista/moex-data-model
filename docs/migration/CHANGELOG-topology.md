# Changelog: Topology ownership (ADR-048)

## Post-4.0.0 hygiene (R2-4)

- Removed dual-read fallback in `effective_topology` (TopologyView only;
  `source: missing` when no fact).
- Removed unused `TOPOLOGY_SLOT_MAP` and authored-slot `topology_changed`
  emission from `collect_drift` (enum value kept for a future previous-view check).
- Explicit test: committed catalog-snapshot `digest` equals `canonical_digest()`.

## 4.0.0 (PR-5)

Breaking:

- Removed authored topology slots from `DataFlow`:
  `source_solution_ref`, `target_solution_ref`, `source_system_ref`,
  `target_system_ref`, `source_platform_ref`, `target_platform_ref`,
  `integration_level`, `integration_class`, `integration_channel`,
  `integration_spec_ref`.
- Topology is read from materialized `TopologyView` (`generated/topology/`)
  built from `model-assets/catalog-snapshots/`.

Migration:

```text
python scripts/migrate_dataflow_topology.py --check
python scripts/migrate_dataflow_topology.py --write
python -m moex_dams.catalog.cli materialize --root .
```

## 3.2.0 (PR-1)

Additive:

- `DataFlow.bound_catalog_revision`
- `DataFlowEntityBinding.catalog_operation_ref` / `catalog_participant_ref`
- `DataModelBinding.catalog_revision`
- Topology slots on `DataFlow` deprecated (`required` cleared)
- Sibling module `moex-topology` (CatalogSnapshot / TopologyView shapes)
