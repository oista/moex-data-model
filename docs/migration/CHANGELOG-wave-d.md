# Changelog: audit Wave D (ADR decisions)

Docs / architecture-check only — **no** aggregate schema bump in this wave.

## D1 — ADR-051 Compatibility

- Semver rules for aggregate DAMS `version`.
- Release-train policy for breaking work.
- Evidence gate for MAJOR.
- Timeline: [SCHEMA-VERSION-TIMELINE.md](SCHEMA-VERSION-TIMELINE.md).

## D2 — ADR-052 Identity

- Five-layer identity map (concept / artifact / version / revision / distribution).
- `api_version` → `dams_specification_version` scheduled for 6.0.0 train.
- `VersionedArtifact` still deferred (ADR-044 D6).
- `id_prefixes` lint + shrink-only allowlist in `tools/architecture-check`.

## D3 — ADR-053 Qualified assertion

- Design for `HasAssertionMetadata` mixin; **implemented in aggregate 5.1.0** ([CHANGELOG-assertion-metadata.md](CHANGELOG-assertion-metadata.md)).
- `ExternalClassRef` canonical; `AlignsWithMapping` projection; consistency **INV-057**.
- Transformation hooks removed in 6.0.0 unless a lineage ADR reclaims them.

## D4 — governance consumer hardening (ADR-049 on main)

- Preferred import: `moex_dams.rules.assignment_resolver` (`resolve_governed` / `diagnose_governance`).
- Audit R2-9: physical split — `_apply_assignments` / `resolve_governed` / `diagnose_governance` live in `assignment_resolver.py`; `cascade.py` is ADR-023 containment only (see ADR-049 D9).
- Conflicting `PolicyBinding` with `binding_effect=replace` → `conflicting_assignments`.
- `formal_checks` accept `as_of` / `assignments` / `repo_root` (configured `as_of` from `moex-governance-view`).
- `EffectiveGovernanceView` discovery includes ADR-047 manifest package bodies.
- ADR-049 D7 audit name map + D8 consumer notes.

## D5 — deferred

Breaking identity train (6.0.0) only after ADR-051 evidence gate and explicit go-ahead.
