# Viewer decisions (ADR)

**Status:** Accepted  
**Date:** 2026-09-27  
**Scope:** Static Publication Viewer for `moex-data-model`

## Decisions

1. **Viewer is a published artifact, not source of truth.** Canonical models live in LinkML YAML / domain packages. The viewer only renders them.
2. **Publication manifests are module-local and declarative.** Each domain adds a `publish.yaml` next to its sources. No hardcoded UI sections.
3. **Build pipeline is static.** No runtime backend, auth, or API for MVP.
4. **HTML consumes only the normalized publication model** (`PublicationModule` / `PublicationSection` / `PublicationItem`).
5. **MVP source formats:** `yaml`, `json`, `csv`, `markdown`, `linkml-yaml`. LinkML is loaded via `SchemaView` so imports resolve.
6. **UI stack:** HTML5 + CSS variables + Vanilla JS. No React/Vite/AG Grid in MVP.
7. **Search:** build-time index embedded in HTML; client-side filter/navigation. No Lunr/Elastic.
8. **Sections appear only via manifests**, never by editing frontend code for a new module.
9. **`viewer/dist` is not committed** (covered by root `dist/` ignore). Publish via CI artifact / Pages later if needed.
10. **Large tables:** data shipped as inline JSON; JS renders rows (sort/filter/pagination). Jinja does not emit thousands of `<tr>`.
11. **Metamodel name is DAMS** (not MDMS): prefix `dams`, URI `https://data.moex.com/dams/`, root schema `moex-dams.yaml`. Old CURIE `mdms:` are not supported.
