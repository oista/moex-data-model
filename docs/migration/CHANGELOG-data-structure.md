# Changelog: DataStructure / SchemaNode (breaking)

## 2026-10-06 — PR-2 removal — schema **2.0.0**

Breaking for DAMS (path `0.1/` retained; schema `version` field → `2.0.0`):

- Removed class `PhysicalField` and slots `physical_fields`, `carrier_ref`, `schema_path`.
- Removed `message_type` from `DataCarrierKindEnum` and transitional carrier annotations.
- `HasStructure.structure_ref` range → `DataStructure` (`inlined: false`).
- `HasStructure.schema_dialect` removed from mixin (lives on `DataStructure` as `uri`).
- `physical_field_refs` → `schema_node_refs` (`uriorcurie`, form `structure_id#local_key`).
- Added module `moex-structure.yaml`: `EmbeddedElement`, `DataStructure`, `SchemaNode`, `Message`.
- Deprecation window was **1.1.0** (PhysicalField marked deprecated with
  `deprecated_element_has_possible_replacement`); semantic diff expects «was deprecated».

### Migration
- Script: `scripts/migrate_physical_field_to_schema_node.py`
- Report: `docs/migration/physical-field-migration-report.md`
- Spike: `docs/migration/data-structure-spike-report.md` (Decision **FLAT**)
- Inventory: `docs/migration/data-structure-inventory.md`

### ADRs
- ADR-038 DataStructure / SchemaNode
- ADR-039 structure node addressing
- ADR-040 Message integration model
- ADR-041 SchemaNode ↔ DataType binding

## 2026-10-06 — Deprecation release — schema **1.1.0**

Additive: `moex-structure` module + Message + collections; PhysicalField /
`physical_fields` / mixin `schema_dialect` marked deprecated.
