# Data Specification Player

Static HTML player for published modeling artifacts in this repository
(**MOEX Atlas** visual system — see [`docs/adr/ADR-015-viewer-ui-atlas.md`](../../docs/adr/ADR-015-viewer-ui-atlas.md)).

**Architecture role:** derived **read model** / publication builder over canonical Git assets.  
It is not the modeling source of truth. Platform canon:
[`docs/architecture/MODELING_ARCHITECTURE.md`](../../docs/architecture/MODELING_ARCHITECTURE.md).
Package location: `apps/viewer` (see [`docs/architecture/app_model.md`](../../docs/architecture/app_model.md)).

## Purpose

- Discover every `publish.yaml` under the repo root
- Normalize YAML / JSON / CSV / Markdown / LinkML into one publication model
- Emit a single autonomous `apps/viewer/dist/index.html` (CSS/JS/fonts inlined) with no backend

## Install

```bash
cd apps/viewer
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
```

Requires Python 3.11+. From repo root (after install):

```bash
make viewer
# or
python -m moex_publication_viewer.cli build --root .
```

Open `apps/viewer/dist/index.html` in a browser (`file://` works).

## Architecture navigation

Sidebar order follows [`architecture-catalog.yaml`](../../model-assets/specifications/moex-dams/0.1/architecture-catalog.yaml):

- **Reference specification** nodes (DAMS, FIBO, …)
  - nested **Specification implementation** nodes (`conforms_to`)
- Implementations without a parent specification
- **Other publications** (modules not listed in the catalog, e.g. Ontology Catalog)

`ModelingStandard` is not a tree level; specifications may carry an `expressed_in` label (LinkML, OWL 2).

## Add a module

1. Place a `publish.yaml` next to your sources (`kind: publication_module`).
2. Set **`profile:`** (`linkml-specification` | `ontology` | `implementation`) and section **`kind:`** values from `PublicationSectionKind` ([ADR-016](../../docs/adr/ADR-016-publication-section-kinds-and-profiles.md)).
3. Point `source.path` relative to the manifest directory (`type:` remains the render/wire format).
4. Optionally register the module in `architecture-catalog.yaml` (`module_id`, `conforms_to` / `expressed_in`).
5. Re-run `make viewer`. The sidebar picks up the new module without UI code changes.

See `schema/publication-manifest.schema.json` for the contract.

### Solution ER diagrams (`type: mermaid-diagram`)

Implementation modules may publish pre-generated Mermaid erDiagram artifacts:

- `publications/logical.erd.md` + sibling `.svg`
- `publications/physical.erd.md` + sibling `.svg`

Generate with `moex-model diagram --format mermaid --profile logical|physical` (SVG needs Node/`npx`). The player shows the SVG by default and a **Исходник** tab for the Mermaid text — no mermaid.js / CDN in `index.html`.

## FIBO glossary

MVP uses the committed preview CSV at `packages/ontology/publications/fibo_glossary.preview.csv` (small sample). Full export under `packages/ontology/output/` is gitignored and requires a local FIBO clone + `python -m ontology.fibo`. To try the full mart locally, point the ontology `publish.yaml` `source.path` at `output/fibo_glossary.csv` after export.

## Check

```bash
make viewer-check
```

## Naming

Metamodel module id/title use **DAMS** (not MDMS).
