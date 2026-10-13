# DAMS schema version timeline

**Normative policy:** [ADR-051](../adr/ADR-051-dams-schema-compatibility.md).  
**Source of truth for current aggregate version:** `model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml` (`version:` field).

Catalogue path `moex-dams/0.1/` is the **product label** (MOEX DAMS 0.1). It is **not** the LinkML aggregate semver.

CI: `tests/architecture/test_schema_version_timeline.py` fails if the aggregate `version:` is missing from the table below (ADR-051 D6).

## Timeline (aggregate `moex-dams.yaml`)

| Aggregate version | Theme | Notes / changelog |
|---|---|---|
| 2.0.0 | Technical asset / DataStructure baseline | ADR-031…041; `PhysicalObject` / `PhysicalField` removed |
| 2.1.0 | ModelElement mixins (additive) | ADR-044 PR-1; `moex-base`, `HasValidity` |
| 3.0.0 | Mapping identity cleanup | ADR-044 PR-6; Mapping → `IdentifiedElement` |
| 3.1.0 | Typed Mapping collections | ADR-046 PR-5; remove `ModelPackage.mappings` |
| 3.2.0 | Topology ownership (additive) | ADR-048 PR-1; deprecate authored topology slots |
| 4.0.0 | Topology ownership (removal) | ADR-048 PR-5; [CHANGELOG-topology.md](CHANGELOG-topology.md) |
| 4.1.0 | Audit Wave C hardening | [CHANGELOG-wave-c.md](CHANGELOG-wave-c.md); INV-042…053; ADR-050 |
| 4.2.0 | Governance assignment authority (additive) | ADR-049 PR-1…4; INV-054…056 |
| 5.0.0 | Governance assignment authority (removal) | ADR-049 PR-5; [CHANGELOG-governance.md](CHANGELOG-governance.md) |
| 5.1.0 | Qualified assertion metadata (additive) | ADR-053 D1/D2; [CHANGELOG-assertion-metadata.md](CHANGELOG-assertion-metadata.md); INV-057 |
| 5.1.0 | Global `element_id` uniqueness (no aggregate bump) | INV-058 + `check-manifest`; [CHANGELOG-global-element-id.md](CHANGELOG-global-element-id.md); ADR-054 |
| 6.0.0 | *(planned)* Identity / embedded selection train | ADR-052 D5; only after ADR-051 evidence gate |

## Dual version surfaces

| Surface | Example | Meaning |
|---|---|---|
| Aggregate LinkML `version` | `4.1.0` | Breaking / additive contract for DAMS schema consumers |
| Per-module schema `version` | often `0.1.0` | Module-local; prefer aggregate for release notes |
| Spec envelope `specification.yaml` | `0.1.0` | Product / catalogue label |
| Generated artifact folder | `generated/.../moex-dams/0.1/` | Tracks catalogue path, not aggregate semver |
| Instance `ModelPackage.api_version` | `dams.moex/v0.1` | **Misnamed** — DAMS specification / product label, **not** HTTP API version; rename to `dams_specification_version` planned for **6.0.0** ([ADR-052](../adr/ADR-052-identity-and-versioning.md) D2). Lookup: [identity-map.md](../architecture/identity-map.md). |

## Related digests (not schema semver)

1. `DataModelBinding.integrity_digest` — ADR-042  
2. Envelope `content_digest` — raw body bytes at import  
3. `manifest.lock` `content_hash` — ADR-047  
