# MOEX Publication Viewer

Static HTML viewer for published modeling artifacts in this repository.

**Architecture role:** derived **read model** / publication builder over canonical Git assets.  
It is not the modeling source of truth. Platform canon:
[`docs/architecture/MODELING_ARCHITECTURE.md`](../docs/architecture/MODELING_ARCHITECTURE.md).
Target package location after the vertical slice: `apps/viewer` / `packages/publication`
(see [`docs/architecture/app_model.md`](../docs/architecture/app_model.md)); today the code lives at repo-root `viewer/`.

## Purpose

- Discover every `publish.yaml` under the repo root
- Normalize YAML / JSON / CSV / Markdown / LinkML into one publication model
- Emit a single `viewer/dist/index.html` (plus CSS/JS) with no backend

## Install

```bash
cd viewer
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

Open `viewer/dist/index.html` in a browser (`file://` works).

## Add a module

1. Place a `publish.yaml` next to your sources (`kind: publication_module`).
2. Point `source.path` relative to the manifest directory.
3. Re-run `make viewer`. The sidebar picks up the new module without UI code changes.

See `schema/publication-manifest.schema.json` for the contract.

## FIBO glossary

MVP uses the committed preview CSV at `packages/ontology/publications/fibo_glossary.preview.csv` (small sample). Full export under `packages/ontology/output/` is gitignored and requires a local FIBO clone + `python -m ontology.fibo`. To try the full mart locally, point the ontology `publish.yaml` `source.path` at `output/fibo_glossary.csv` after export.

## Check

```bash
make viewer-check
```

## Naming

Metamodel module id/title use **DAMS** (not MDMS).