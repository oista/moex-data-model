# Publication contract nav (Impl vs Spec)

**Date:** 2026-09-28  
**Status:** Draft  
**Normative:** [ADR-019](../../adr/ADR-019-publication-contract-inheritance.md), [ADR-016](../../adr/ADR-016-publication-section-kinds-and-profiles.md), [viewer-nav-hierarchy](2026-09-28-viewer-nav-hierarchy-design.md)

## Problem

When drilling into an implementation (e.g. `moex.dsp`), the sidebar showed opaque roots **«Разделы»** and a LinkML schema package folder (**«Dsp»**) as siblings. That conflates:

- publication sections (overview, glossary, conformance);
- schema-package grouping from `groupby: schema`.

## Contract

| Profile | Primary nav roots | Schema packages |
|---|---|---|
| `implementation` | Sections by `kind` / `satisfies` (overview, conformance, bindings, …) | Not primary; omit package-folder axis |
| `linkml-specification` | ADR-016 roots: Overview, Classes, Schema files, … | Only **under** Classes (human-readable title) |
| `ontology` | Overview, Taxonomy, Glossary, … (ADR-016) | N/A |

Rules:

1. Never invent a sibling root labelled «Разделы». Orphan non-explorer sections fold into **Overview** (`section_root: overview`).
2. LinkML package groups are never top-level siblings of Overview; wrap under `group:classes` with `section_root: classes`.
3. `moex.dsp` uses `profile: linkml-specification` (player metamodel docs). It does **not** inherit DAMS `logical-entities` publication requirements. Data Impls that claim DAMS use `profile: implementation` + `satisfies`.
4. Coverage warnings (soft): missing `satisfies` for inherited required requirements when a module declares a reference contract.

## Out of scope here

Hard CI fail, full semantic-content instance scan, `PublicationConformanceReport` build artifact (ADR-019 phase 2).
