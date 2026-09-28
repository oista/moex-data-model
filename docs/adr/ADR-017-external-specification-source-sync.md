---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# ADR-017: External specification source sync

**Date:** 2026-09-28  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-002](ADR-002-git-published-source.md), [ADR-009](ADR-009-schema-automator-draft-only.md), [ADR-010](ADR-010-owl-not-primary-validation.md), [ADR-012](ADR-012-semantic-diff-review.md), [ADR-014](ADR-014-fibo-profile-metamodel.md), [ADR-018](ADR-018-ontology-application-implementation.md)

## Context

MOEX needs reproducible local copies of external reference specifications (FIBO, OpenAPI, AsyncAPI, ODCM, JSON Schema, …). A naive “git pull the whole upstream” fails for OWL ontologies: FIBO is a large modular graph; consumers need **seeded module extracts**, not the full release. API/schema specs are file-oriented and pin cleanly to a git tag/commit.

ADR-014 already separates the FIBO **profile** (`moex-fibo-profile`) from release **content**. ADR-010 keeps OWL out of primary YAML validation. Sync must not conflate with schema-automator draft import (ADR-009) or auto-publish into the catalog/viewer (ADR-012).

## Decision

1. **Unified lifecycle port** `SpecificationSource` in the modeling kernel: `resolve_latest` → `fetch` → `materialize` → `diff` → `lock`. All source kinds share this lifecycle; **`materialize` is kind-specific**.
2. **Source kinds:** `ontology` | `api_spec` | `schema` | `data_contract_standard`.
3. **Ontologies (FIBO and peers):** Mirror a pinned upstream release into a cache, extract a module with **ROBOT** (`extract`, method BOT or STAR) from a repo-owned **seed** (IRI list), optionally `reason` for consistency of the extract, commit only the module + lock — **never** vendor the full FIBO tree.
4. **Git-based specs (OpenAPI / AsyncAPI / ODCM / JSON Schema):** Pin tag or commit SHA + content hash; materialize by copying/normalizing text artifacts under `spec/`.
5. **On-disk home:** `model-assets/external-sources/<source_id>/` with `registry.yaml`, `lockfile.yaml`, seeds/modules or `spec/`. This is **not** a `ReferenceSpecification` under `specifications/` and does **not** replace `moex-fibo-profile`.
6. **Updates** land via PR with lockfile + artifact diff (ADR-002, ADR-012). Sync does **not** auto-ingest ontology-catalog or run `moex-model publish`.
7. **ROBOT** is a pinned JAR invoked via subprocess (version recorded in the lockfile). Full ODK Docker is deferred. ROBOT `reason` may gate ontology materialize consistency; it does **not** become the primary YAML validator (ADR-010 stands).
8. **Adapters** live in `packages/external-sources`; the kernel holds only the Protocol and DTOs (no HTTP/ROBOT deps).

## Consequences

- CLI: `moex-model source list|sync|diff`.
- Catalog/viewer continue to consume content separately; extracts feed application-ontology Impl as a dependency (ADR-018), not as SpecImpl themselves. Wiring extract modules into ontology-catalog rebuild is a later step.
- schema-automator remains only on `moex-model import` (ADR-009).

## Alternatives

| Alternative | Why not |
|---|---|
| Git submodule / full FIBO vendor | Huge tree; wrong unit of change; breaks review |
| ODK-first orchestration | Heavier than needed for MVP; ROBOT JAR is enough |
| Sync == schema-automator import | Different lifecycle (mirror/pin vs draft LinkML); ADR-009 |
| One naive git-pull adapter for all kinds | Ontologies need extract/reason, not file copy |

## Related

- ADR-002, ADR-009, ADR-010, ADR-012, ADR-014, ADR-018
- Package: `packages/external-sources`
- Layout: `model-assets/external-sources/`
