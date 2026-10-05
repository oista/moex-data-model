# Golden diff: DataStructure / SchemaNode (DAMS 2.0.0)

Expected breaking golden changes after `make generate-artifacts` / `generate-contracts`:

- **Removed:** `PhysicalField` class diagrams/docs, `physical_fields` slot docs, `carrier_ref` (field), `schema_path`
- **Added:** `DataStructure`, `SchemaNode`, `EmbeddedElement`, `Message`, enums `SchemaFormatEnum`, `SchemaNodeKindEnum`, `EnvelopeKindEnum`
- **Changed:** `DataCarrier` (no physical_fields; structure_ref → DataStructure), `AccessPoint.message_refs`, `HasStructure` (no schema_dialect on mixin)
- **Contracts / JSON Schema / OWL / SHACL / Python:** reflect class removals and additions
- **DBML / Mermaid:** columns sourced from DataStructure scalar nodes via structure_ref

Accept golden update after review. Residue grep allowlists historical docs and migrate scripts.
