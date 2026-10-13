---
status: Planned
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# Aggregate schema train 6.0.0

**Status:** Planned — not started  
**Owner (train lead):** DAMS maintainers  
**Go-ahead required from:** Product (explicit) + ADR-051 D4 evidence gate  
**Normative:** [ADR-051](../adr/ADR-051-dams-schema-compatibility.md) D3–D4, [ADR-052](../adr/ADR-052-identity-and-versioning.md) D5, [ADR-053](../adr/ADR-053-qualified-assertion.md) D3, [ADR-044](../adr/ADR-044-model-element-decomposition.md)  
**Index:** [P2-BACKLOG.md](P2-BACKLOG.md) (Group 0 / F0-3)  
**Lookup:** [identity-map.md](../architecture/identity-map.md)

This file turns residual **audit P1 / Wave D deferred** items into trackable work packages. It is **not** an open defect against closed ADRs. Do not start schema work until every **Entry criterion** below is checked.

---

## Entry criteria (train gate)

All of the following must be true before the first schema PR of the series:

| # | Criterion | Evidence |
|---|---|---|
| G1 | **Explicit Product go-ahead** recorded (issue comment, ADR amendment, or CHANGELOG note) | Product |
| G2 | **ADR-051 D4 evidence gate:** ≥3 independent authored instances exercise each removed/changed surface, **or** written exception in the series CHANGELOG + this file | DAMS maintainers |
| G3 | Multi-PR series plan saved under `{repo}/.cursor/plans/` with name `moex-data-model: Schema train 6.0.0` | DAMS maintainers |
| G4 | Series ADR (or this file) names which PR uses the **PR-5 exception** (schema + data + regen) vs separate commits | DAMS maintainers |
| G5 | Aggregate on `main` is ≥ **5.1.0**; [SCHEMA-VERSION-TIMELINE.md](SCHEMA-VERSION-TIMELINE.md) current; `make check` + `make dams-packages-check` green | CI |
| G6 | No open High-severity audit R3 blockers that block assess/matrix trust (L2 wiring meta-test debt is **not** a hard blocker) | DAMS maintainers |

Until G1–G6 pass, keep shipping **minors** (F0-4 allowlist ratchet, Group 1–3 backlog) under ADR-051.

---

## Work packages (one theme per PR / stacked commit)

| ID | Theme | Owner | Breaking? | Entry criteria (package-local) | Exit criteria | Sources |
|---|---|---|---|---|---|---|
| **T6-1** | Rename `ModelPackage.api_version` → `dams_specification_version` + `ruamel` migration (`--check`/`--write`) for all packages/examples | DAMS maintainers | **Yes** (slot rename) | G1–G6; inventory of all `api_version:` occurrences | Zero `api_version` in authored DAMS YAML; slot gone; docs/glossary/identity-map updated; timeline row **6.0.0** | ADR-052 D2/D5#1 |
| **T6-2** | Move `ModelSelection` / `SelectedEntity` / `SelectedAttribute` / `DataFlowEntityBinding` off full `ModelElement` onto `EmbeddedElement` (or slim `IdentifiedElement` without `NamedElement`/`HasLifecycle` where not needed) | DAMS maintainers | **Yes** (identity/lifecycle shape) | G1–G6; per-class inventory (required slots, consumers in viewer/API/web) | Classes exit [ADR-052 allowlist](../adr/ADR-052-identity-and-versioning.md); architecture-check ceiling lowered; no artificial `name`/`lifecycle` on selection helpers | ADR-052 D5#2; ADR-044 D5 |
| **T6-3** | Remove Wave C deprecated orphans: `native_name`/`native_type` (core orphans), `transformation_ref`/`transformation_expression` on `Mapping`, unused `LogicalDataTypeEnum` | DAMS maintainers | **Yes** (slot/enum removal) | G1–G6; grep shows no authored use **or** migration rewrites them; if lineage needs hooks → **stop** and open lineage ADR first (ADR-053 D3) | Slots/enum absent; residue test; INV/matrix rows adjusted | ADR-052 D5#3; ADR-053 D3; P2 F0-3 |
| **T6-4** | Optional: introduce `VersionedArtifact` mixin in `moex-base` **only if** ADR-044 D6 trigger holds (≥3 classes with `previous_version_ref` + content digest/revision) | DAMS maintainers | Additive inside major train **or** separate minor | G1–G6 **and** documented third consumer | Mixin applied; no core↔structure cycle | ADR-052 D3; ADR-044 D6 |
| **T6-5** | Optional: `RelationshipEnd` / Conceptual vs Logical relationship profiles (else keep L2 INV-053 only) | DAMS maintainers | Depends on design | Product priority **or** INV-053 insufficient for a concrete consumer | Schema + INV + fixtures **or** written “stay L2-only” note in series CHANGELOG | ADR-052 D5#4; Wave C INV-053 |
| **T6-6** | Strengthen Mapping endpoint typing at L1 where generators allow (JSON Schema / Pydantic item types); keep L2 as SoT for id→class resolution | DAMS maintainers | Prefer **non-breaking** (tighter generated artifacts) | Spike report (LinkML 1.x limits; ADR-046 spike baseline); no false invalids on 8 packages | Spike + optional gen improvements landed **or** waiver “L2 remains normative for kinds” in ADR-046 amendment | Audit mapping §; ADR-046 |
| **T6-7** | Rich ownership / stewardship: role type, scope beyond `assignment_scope`, delegation — **without** inventing `StewardshipAssignment` unless ADR-049 is amended | DAMS maintainers | Additive preferred | Product priority; ADR-049 D7 map still holds | Slots on `OwnershipAssignment` **or** ADR-049 amendment rejecting audit extras | Audit governance §; ADR-049 D7 / Out of scope |
| **T6-8** | Manifest `DocumentKind` expansion (flows, bindings, governance sets, requirement catalogs) + envelopes — **only when** first non-package envelope is authored | DAMS maintainers | Additive (manifest module) then consumers | First real envelope file exists (not a speculative kind) | Kinds in `moex-repository-manifest`; viewer/loader paths; ADR-054 update | ADR-054 Deferred; P2 F3-1/F3-2 |

**T6-1…T6-3** are the **core train** (must ship together under one aggregate **6.0.0** per ADR-051 D3).  
**T6-4…T6-5** are optional co-travelers.  
**T6-6…T6-8** may ship as **minors before or after** 6.0.0 if they do not require the core renames; list them here so they are not lost.

---

## Suggested PR series (core train)

| PR | Theme | Touches |
|---|---|---|
| PR-0 | Docs: amend this file + series plan; freeze inventory (api_version sites, selection class consumers, orphan slot usages) | docs only |
| PR-1 | Additive deprecations / dual-read helpers if needed (prefer avoid dual-read for rename — see ADR-052 D2) | schema minor **or** skip |
| PR-2 | Code readers/writers use new names / embedded shapes | packages/, apps/ |
| PR-3 | Data migration (`ruamel`) for packages + examples | model-assets/ |
| PR-4 | INV / architecture-check / residue tests | constraints, tools/ |
| PR-5 | Slot/enum **removal** + regen + timeline **6.0.0** (PR-5 exception **only** if named in series ADR) | schema + data + `generated/` |

Schema diff and data migration stay in **separate commits** unless PR-5 exception is named ([multi-pr-series](../../.cursor/rules/multi-pr-series.mdc)).

---

## Evidence gate worksheet (fill before PR-5)

| Surface removed/changed | Instances exercising it (≥3 or exception) | Migration script | Exception note (if fewer than 3) |
|---|---|---|---|
| `api_version` slot | _TBD_ | `scripts/migrate_api_version_to_dams_specification_version.py` (to create) | |
| Selection / binding `ModelElement` shape | _TBD_ | _TBD_ | |
| `transformation_*` / orphan natives / `LogicalDataTypeEnum` | _TBD_ (expect zero authored) | n/a or strip | Zero-use exception OK per ADR-051 D4#2 |

---

## Explicitly **not** in this train

| Topic | Where tracked |
|---|---|
| Protocol-neutral `Integration` / OpenAPI·AsyncAPI·ODCS·OpenLineage adapters | [P2-BACKLOG](P2-BACKLOG.md) Group 1; [ADR-055](../adr/ADR-055-integration-source-of-truth.md) |
| DCAT `Distribution`, `DataRepresentation`, `SemanticAlignment` rename | P2 Group 2 (F2-1…F2-3) |
| Abstract `Assertion` / `QualifiedRelation` in `is_a` backbone | ADR-053 D1 **non-goal**; do not reopen without amending ADR-053 |
| Runtime lineage store | ADR-053 / P2 non-goals |
| Re-adding authored topology on `DataFlow` | ADR-048 / ADR-055 |

---

## Pre-train minors (recommended, not part of 6.0.0 bump)

Ship as ordinary minors when convenient; they reduce risk before the major.

| ID | Item | Owner | Entry criteria | Source |
|---|---|---|---|---|
| **M-1** | Selection closure INV (selected fields ⊆ selected entities/objects) if still missing from matrix | DAMS maintainers | Negative fixture design ready | Audit “Negative examples” |
| **M-2** | Binding baseline/mode compatibility INV | DAMS maintainers | Rules agreed with ADR-042 consumers | Audit binding § |
| **M-3** | `LogicalAttribute` min/max cardinality consistency INV | DAMS maintainers | — | Audit cardinality § |
| **M-4** | `parent_concept_ref` cycle INV (conceptual) if not already covered | DAMS maintainers | — | Audit cycles § |
| **M-5** | `id_prefixes` allowlist ratchet (F0-4) — lower ceiling after adding `dams` prefixes to non-selection classes | DAMS maintainers | Per ADR-052 ratchet schedule | ADR-052; P2 F0-4 |

---

## Status log

| Date | Event |
|---|---|
| 2026-10-14 | File created (audit closure R3-6): residual P1 items made explicit with owners and entry criteria. Train **not** started. |
