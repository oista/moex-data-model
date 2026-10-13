# Changelog: global element_id uniqueness (INV-058)

Constraint / CI only — **no** aggregate schema bump (ADR-051 D2: new L2
invariant without slot/class changes). Lands under current aggregate **5.1.0**.

## Constraints

- **INV-058**: `element_id` must be unique across ModelPackage bodies indexed by
  the repository manifest (`scope: repository`).
- `InvariantScopeEnum` in `constraint-matrix.schema.yaml` gains permissible
  value `repository` (matrix meta-schema only; not DAMS aggregate).
- Packages with envelope `dams_model_level: hierarchy-view` are excluded
  (derived views may reuse source ids).
- Within a single package document, uniqueness remains **INV-050**.

## Runtime

- `moex_dams.rules.repository_invariants.check_repository_element_id_uniqueness`
  (shared `element_id` walk with INV-050).
- `moex_repository_loader.check.check_global_element_ids` wired into
  `run_checks` / `moex-model check-manifest`.

## Docs

- ADR-054: deferred global collision closed; hierarchy-view exclusion documented.
- P2-BACKLOG F3-3 marked done; p1-inventory deferred list updated.
