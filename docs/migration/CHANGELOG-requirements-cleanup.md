# Changelog: ADR-056 PR-10f requirements catalog cleanup

**ADR:** [ADR-056](../adr/ADR-056-requirements-backbone.md)  
**Follows:** PR-10c (backbone checks), PR-10d (Group D deprecate), PR-10e (schema 5.5.0)

## Removed from catalogs

Deleted **56** inactive rows (`deprecated` / `superseded`):

| Bucket | Count | Examples |
|---|---|---|
| Group A superseded | 14 | GEN-001…003, LDM-002…005, PDM-003/004, REF-003, FLW-001, … |
| Group B superseded | 1 | LDM-006 (kept as **LDM-101**) |
| Group C deprecated | 31 | ATR-001/006, REF-001, PDM-001/002/005…020, FLW-002…005, CM-* |
| Group D deprecated | 10 | GEN-004, LDM-001/007/008, ATR-002/004/005/007, CLS-001/002 |

## Remaining catalog (19)

- IT-solution: 15 backbone (`LDM-01`…`13`, `PDM-01`/`02`) + `LDM-101` + `REF-002`
- Conceptual: `CDM-01`, `CDM-02`

## Matrix / code

- `requirement_refs` for INV-033…036 → `PDM-02`; other historical refs removed with a `source` note.
- `requirement_code=` in `technical_assets.py` / `data_structure.py` / `catalog_topology.py` now uses INV ids (diagnostic codes unchanged).
- Placeholder ownership lint uses `requirement_code=LDM-11`.

## Tests / export

- `collect_requirement_rows` / CLI export: **19** rows.
- Viewer explorer sections: LDM, PDM, REF (+ CDM on conceptual root).
- Model skeletons now include `definition_resolvable` / `conditional_branch` targets (collections + `description`); assertions follow the active spine, not deleted Group D slots.
