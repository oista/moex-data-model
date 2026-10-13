# Archived one-shot migration scripts

Scripts here are **historical** helpers for pre-3.1.0 / pre-ADR-038 data. They are
kept for external consumers who still have legacy YAML; they are not part of the
Stage 0 or day-to-day authoring path.

| Script | Era |
|--------|-----|
| `migrate_mapping_labels.py` | Pre-3.1.0 polymorphic `mappings[]` + Mapping identity slots |
| `migrate_physical_field_to_schema_node.py` | PhysicalField → SchemaNode (ADR-038) |

Active migrate scripts remain under `scripts/` (topology, governance, typed
collections, attribute semantics, technical asset).
