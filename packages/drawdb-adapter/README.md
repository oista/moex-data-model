# moex-drawdb-adapter

DBML ↔ DAMS `ModelPackage` bridge for Stage 5 drawDB MVP (ADR-005 / ADR-006).

- `to_dbml` — delegates to `moex_dams.projection.dbml`
- `parse_dbml` — subset parser (Table / column / Note / Ref)
- `compute_model_patch` / `apply_model_patch` — controlled round-trip

Layout coordinates are **not** stored here (API `diagram_layout` table).
