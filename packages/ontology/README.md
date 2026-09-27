# MOEX Ontology Package

Offline RDF/OWL utilities and FIBO definition export for glossary mapping and ontology-aware LLM context.

**Architecture role today:** tooling under `packages/ontology/`.  
This is **not** yet the target `packages/standard-owl` provider from
[`docs/architecture/MODELING_ARCHITECTURE.md`](../../docs/architecture/MODELING_ARCHITECTURE.md) /
[`docs/architecture/app_model.md`](../../docs/architecture/app_model.md). OWL as a first-class
`ModelingStandard` lands after the LinkML → DAMS vertical slice stabilizes.

## Requirements

- Python 3.11+ (on this machine: `py -3.14` or any 3.11+ launcher)

## Install

```bash
cd packages/ontology
# Windows (example with Python 3.14):
py -3.14 -m venv .venv
.venv\Scripts\activate
# Linux/macOS:
# python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Obtain FIBO sources (once)

```bash
git clone --branch master_2026Q2 --depth 1 https://github.com/edmcouncil/fibo.git
```

Processing does not require network access.

## Export definitions

```bash
python -m ontology.fibo \
  --source ./fibo \
  --output ./output \
  --release master_2026Q2
```

### Useful options

```text
--domains FND,BE,FBC,SEC,IND
--include-examples
--include-individuals
--include-deprecated
--types class,object_property,datatype_property,annotation_property
--format csv,xlsx,json
--verbose
--fail-on-parse-error
```

## Output marts

| File | Meaning |
|---|---|
| `fibo_glossary.csv` | **Main glossary:** active `owl:Class` with a formal definition |
| `fibo_definitions_all.csv` | Aggregated active candidates (default filter) |
| `fibo_definitions_active.csv` | `is_deprecated = false` |
| `fibo_definitions_deprecated.csv` | Deprecated entities |
| `fibo_definitions_no_definition.csv` | Entities without a formal definition |
| `fibo_parse_errors.csv` | RDF parse failures |
| `fibo_definitions.xlsx` | Multi-sheet Excel (sheet `Glossary` first after README) |
| `fibo_export_manifest.json` | Run metadata for reproducibility |

## Tests

```bash
pytest -v
```

Tests use `tests/fixtures/mini_fibo/` and do not require a full FIBO clone.

## Upstream

https://github.com/edmcouncil/fibo
