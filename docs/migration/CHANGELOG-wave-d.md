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

### D2 follow-up — operational identity (no schema bump)

- Lookup: [identity-map.md](../architecture/identity-map.md).
- ADR-052 D6/D7: tracked manifests carry `schema_version`, `media_type`, `role`; `generated_at` excluded from digests; Git `source_revision` only on staged release bundle (`--release` refuses dirty tree).
- Publish-gate enforces identity fields and `schema_version` == aggregate `moex-dams.yaml` `version:`.
- **Closure status (audit P1 Version identity):** closed at contract/tooling level; schema-level items (`api_version` rename, `VersionedArtifact`, LinkML `ArtifactDistribution`) remain deferred to 6.0.0 by decision.

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

Work packages, owners, and entry criteria (R3-6): [TRAIN-6.0.0.md](TRAIN-6.0.0.md) — core T6-1…T6-3 (`api_version` rename, selection/binding → `EmbeddedElement`, orphan slot removal); optional T6-4…T6-8; pre-train minors M-1…M-5. Indexed from [P2-BACKLOG.md](P2-BACKLOG.md) F0-3 / F0-5…F0-7.
