---
status: Accepted
version: "0.1"
normative: true
supersedes: []
superseded_by: []
---

# ADR-051: DAMS schema compatibility (semver + release trains)

**Date:** 2026-10-13  
**Status:** Accepted  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-011](ADR-011-reproducible-artifacts.md), [ADR-012](ADR-012-semantic-diff-review.md), [ADR-030](ADR-030-dams-uri-and-prefix-policy.md), [ADR-042](ADR-042-integrity-digest-revisions.md), [ADR-047](ADR-047-repository-manifest-and-lock.md)  
**Timeline:** [SCHEMA-VERSION-TIMELINE.md](../migration/SCHEMA-VERSION-TIMELINE.md)  
**Audit:** Wave D1 (2026-10-01 architect audit — Compatibility decision gate)

## Context

Aggregate DAMS schema `version` moved 2.0 → 3.0 → 4.0 → 5.0.0 (ADR-049 PR-5) → 5.1.0 (ADR-053 additive) while the catalogue path stayed `moex-dams/0.1/`. Breaking removals shipped with thin instance evidence (often one example). Consumers need one place that defines:

1. What major / minor / patch mean for DAMS.
2. How `moex-dams.yaml` `version:` relates to the `0.1/` path and generated folders.
3. When a major bump is allowed (evidence bar).
4. That breaking themes are batched into a **release train**, not one major per theme.

## Decision

### D1. Aggregate semver is the consumer contract

- **Source of truth:** `model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml` → `version:`.
- **Catalogue path `0.1/`** and envelope `specification.yaml` version are the **product label** (MOEX DAMS 0.1). They do **not** bump with every aggregate major until a product-level 0.2 decision.
- Generated artifact folders under `generated/**/moex-dams/0.1/` follow the catalogue path.
- Per-module schema files may keep local `0.1.0`; release notes cite the **aggregate** version.

### D2. Semver rules for DAMS schema

| Kind | When | Examples |
|---|---|---|
| **MAJOR** | Remove or rename a published class/slot/enum value; tighten requiredness; change identifier shape; change IRI policy (ADR-030); change meaning of an existing slot | ADR-046 PR-5 `mappings` removal; ADR-048 PR-5 topology slot removal |
| **MINOR** | Additive classes/slots/enums; deprecate without removal; new INV rows; new optional collections; new sibling modules **outside** `moex-dams.yaml` imports | ADR-048 PR-1; Wave C 4.1.0 |
| **PATCH** | Docs-only in schema descriptions, fixture fixes, validator bugfixes that do not change accepted instance sets, generated golden refresh without schema shape change | digest pin updates |

Sibling modules (`moex-topology`, `moex-repository-manifest`, future governance-view) bump their own versions independently and **do not** force a DAMS aggregate major unless they require a DAMS slot/class change.

### D3. Release trains for breaking work

- Prefer **one aggregate major** that batches related breaking items (identity rename, embedded selection migration, orphan slot removal) over a major per ADR theme.
- Between majors: ship minors with deprecation windows (multi-PR series: additive → dual-read → invariants → removal).
- **PR-5 exception** (schema removal + example migration + regen in one commit) is allowed only when the series ADR Decision explicitly names it; otherwise schema diff and data migration stay separate commits (`.cursor/rules/multi-pr-series.mdc`).

### D4. Evidence gate for MAJOR

A major bump requires **at least one** of:

1. **Coverage:** ≥ 3 independent authored instances (implementations or normative examples) exercise the removed/changed surface, **or**
2. **Explicit exception** recorded in the series CHANGELOG + ADR: “zero/one instance in repo; external consumers notified; migration script provided.”

Thin majors (one example only) remain possible under (2) but must not be silent.

### D5. Compatibility surfaces consumers must watch

| Surface | ADR / location |
|---|---|
| Schema shape + aggregate version | this ADR; `moex-dams.yaml` |
| Binding digest / revision | ADR-042 |
| Manifest lock hash | ADR-047 |
| Schema IRI / prefixes | ADR-030 |
| Package semantic diff (instance) | ADR-012 (process) |

`CompatibilityModeEnum` on `DataModelBinding` is **contract-level** compatibility between model revisions, not DAMS schema semver.

### D6. Timeline document

[SCHEMA-VERSION-TIMELINE.md](../migration/SCHEMA-VERSION-TIMELINE.md) is the living table of aggregate versions. Update it in the same PR that bumps `moex-dams.yaml` `version:`.

## Consequences

- Wave D / future 6.0.0 identity train must cite this ADR and fill the evidence gate.
- ADR-049 governance landed as aggregate **5.0.0** (PR-5 removal) after additive **4.2.0**; see [SCHEMA-VERSION-TIMELINE.md](../migration/SCHEMA-VERSION-TIMELINE.md).
- CI does not auto-enforce the evidence gate; reviewers and CHANGELOG checklist do.

## Alternatives

| Alternative | Why not |
|---|---|
| Bump catalogue path to `0.2/` on every major | Couples product marketing to schema churn |
| Calendar deprecation only | Repo has few instances; PR-staged windows fit better |
| Major per theme forever | Audit found version noise harms trust |

## Acceptance

- [x] Semver table published
- [x] Timeline doc created
- [x] Evidence gate and release-train rule recorded
