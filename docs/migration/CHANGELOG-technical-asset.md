# Changelog: TechnicalAsset migration (breaking)

## 2026-10-05 — Accepted (ADR-031 / ADR-032 / ADR-033)

Breaking removal of the flat PhysicalObject class and collection:

- Removed class PhysicalObject and enum PhysicalObjectKindEnum.
- Replaced collection physical_objects with Variant B collections:
  data_carriers, access_points, data_containers, execution_assets.
- Ingest sheet renamed to DataCarriers (asset_kind; legacy object_kind still accepted).
- Field ownership uses carrier_ref (was physical_object_ref).
- Identity: asset_namespace + qualified_name (ADR-032); fields are not quanta (ADR-033).

Migration script: scripts/migrate_physical_to_technical_asset.py.
Acceptance scan: tests/architecture/test_no_physical_object_residue.py.
