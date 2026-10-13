# moex-governance-view

LinkML schema for the materialized **EffectiveGovernanceView** read model
([ADR-049](../../../docs/adr/ADR-049-governance-assignment-authority.md)).

This is **not** the DAMS domain model. It lives as a sibling specification under
`model-assets/specifications/` so that:

- it is **not** globbed into DAMS artifact generation (`moex-dams/0.1/schemas/*.yaml`);
- it is **not** imported by `moex-dams.yaml` (keeps DAMS version bumps intentional);
- it has **no** `specification.yaml` / `publish.yaml` yet.

## Layout

| Path | Role |
|---|---|
| `schemas/moex-governance-view.yaml` | Schema source of truth |
| `as_of.txt` | Fixed `as_of` date for CI materialize/check (not wall-clock) |
| Generated `generated/governance/` | Materialized EffectiveGovernanceView per as_of |

## Classes

- `EffectiveGovernanceView` (`materialized: true`) — read model; not hand-edited
- `EffectiveElementGovernance` — effective slots for one model element
- `EffectiveSlot` — one slot value with layer / provenance

## Related

- Inventory: [governance-inventory.md](../../../docs/migration/governance-inventory.md)
- Cascade: [ADR-023](../../../docs/adr/ADR-023-governed-property-cascade.md)
- Manifest boundary kinship: [ADR-047](../../../docs/adr/ADR-047-repository-manifest-and-lock.md)
