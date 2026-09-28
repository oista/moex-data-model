---
status: Accepted
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# Viewer decisions (ADR)

**Status:** Accepted  
**Date:** 2026-09-27  
**Scope:** Static Publication Viewer for `moex-data-model`  
**Normative parent:** [MODELING_ARCHITECTURE.md](MODELING_ARCHITECTURE.md) (Proposed 0.2)

## Decisions

1. **Viewer is a published artifact, not source of truth.** Canonical models live in LinkML YAML / domain packages. The viewer only renders them (architecture invariant 10: read model does not change domain state).
2. **Publication manifests are module-local and declarative.** Each domain adds a `publish.yaml` next to its sources. No hardcoded UI sections.
3. **Build pipeline is static.** No runtime backend, auth, or API for MVP.
4. **HTML consumes only the normalized publication model** (`PublicationModule` / `PublicationSection` / `PublicationItem`).
5. **MVP source formats:** `yaml`, `json`, `csv`, `markdown`, `linkml-yaml`. LinkML is loaded via `SchemaView` so imports resolve.
6. **UI stack:** HTML5 + CSS variables + Vanilla JS. No React/Vite/AG Grid in MVP. **Presentation standard:** [ADR-015 MOEX Atlas](../adr/ADR-015-viewer-ui-atlas.md) and [design principles](../design/viewer-atlas/README.md) (surfaces, tokens, shell, a11y). Pipeline/manifest rules in this file still win over visual details.
7. **Search:** build-time index embedded in HTML; client-side filter/navigation. No Lunr/Elastic. Atlas UX: command palette (`Ctrl/Cmd+K`), not a second information architecture.
8. **Sections appear only via manifests**, never by editing frontend code for a new module.
9. **`viewer/dist` is not committed** (covered by root `dist/` ignore). Publish via CI artifact / Pages later if needed.
10. **Large tables:** data shipped as inline JSON; JS renders rows (sort/filter/pagination). Jinja does not emit thousands of `<tr>`.
11. **Metamodel name is DAMS** (not MDMS): prefix `dams`, URI `https://data.moex.com/dams/`, root schema `moex-dams.yaml`. Old CURIE `mdms:` are not supported.
12. **DAMS explorer is a projection of the specification body (`TSpecBody`), not the implementation body (`TImplBody`) and not the modeling kernel.** Sidebar groups are LinkML schema packages (`from_schema` / `in_schema`), not `is_a` inheritance and not ModelPackage conceptual/logical/physical layers.
13. **Paths stay at root `viewer/` until the vertical slice** (`apps/viewer` / `packages/publication` are target-after-slice only).
14. **Ontology glossary links** from slots such as `glossary_term_refs` are optional `PROJECTS_TO`-style deep links into the FIBO publication module when ids match; they are not `CONFORMS_TO`.
15. **Impl / Spec nav follows publication contract (ADR-019).** For `profile: implementation`, sidebar roots are sections by `kind` / `satisfies` — not an opaque «Разделы» wrapper and not LinkML package folders as the primary axis. For `profile: linkml-specification`, ADR-016 roots apply; schema packages nest only under Classes. Orphan non-explorer sections fold into **Overview**, never a sibling labelled «Разделы». See [publication-contract-nav](../superpowers/specs/2026-09-28-publication-contract-nav.md).
