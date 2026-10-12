# moex-topology

LinkML schema for **catalog snapshots** and the materialized **TopologyView**
read model ([ADR-048](../../../docs/adr/ADR-048-topology-ownership.md)).

This is **not** the DAMS domain model. It lives as a sibling specification under
`model-assets/specifications/` so that:

- it is **not** globbed into DAMS artifact generation (`moex-dams/0.1/schemas/*.yaml`);
- it is **not** imported by `moex-dams.yaml` (keeps DAMS version bumps intentional);
- it has **no** `specification.yaml` / `publish.yaml` yet.

## Layout

| Path | Role |
|---|---|
| `schemas/moex-topology.yaml` | Schema source of truth |
| Instance `model-assets/catalog-snapshots/clinkr/catalog-snapshot.json` | Hand-maintained file snapshot (PR-2) |
| Generated `generated/topology/` | Materialized TopologyView per catalog_revision (PR-2) |

## Classes

- `CatalogSnapshot` (`tree_root`) — file snapshot header + objects
- `CatalogObject` — one catalog object (integration / system / …)
- `CatalogParticipant` / `CatalogOperation` — nested facts
- `TopologyView` (`materialized: true`) — read model; not hand-edited
- `TopologyFact` — one flow→topology edge set
- `DriftFinding` — one drift row from resolver

## Related

- Inventory: [topology-inventory.md](../../../docs/migration/topology-inventory.md)
- Manifest boundary kinship: [ADR-047](../../../docs/adr/ADR-047-repository-manifest-and-lock.md)
