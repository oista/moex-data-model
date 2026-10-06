---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# PR-C1a: validation helper — impact report

**Date:** 2026-10-06  
**Branch:** `feat/constraints-c1a-validation-helper` (base: `feat/constraints-c0-inventory`)  
**ADR:** [ADR-045](../adr/ADR-045-executable-constraint-matrix.md)  
**Spike inventory:** `tmp/constraint-spike/inventory_validation_impact.py`, `validation_impact.json`

## 1. What landed in C1a

| Item | Status |
|---|---|
| `moex_standard_linkml.validation.make_linkml_validator` (`JsonschemaValidationPlugin(closed=True)`) | done |
| `error_results` helper | done |
| Wired: `adapters/validator.py`, `ingest/validate.py`, `validate-examples.ps1`, `validate-schemas.ps1` | done |
| Wired: `validate-requirements.ps1` | **deferred** (would turn `check_all` red; see §2) |
| Side fix: stop emitting Mapping.`name` in xlsx ingest (`mapper.py`, `enrich.py`) + example YAML | done (ADR-044 / DAMS 3.0.0) |
| Unit tests `packages/standard-linkml/tests/test_validation_helper.py` | done |
| Catalog test documents plugin failure | done |

Схемы DAMS в C1a **не** менялись (правки `FormalCheck` / pattern `code` — отдельное решение).

## 2. Data that becomes invalid under the plugin

Прогон: `apps/cli/.venv` Python 3.14.4, LinkML 1.11.1, `JsonschemaValidationPlugin(closed=True)`. При vacuous `Validator(schema)` все эти файлы дают 0 ошибок.

| Path | Target | In `check_all` today? | Errors | Root cause | C1a action |
|---|---|---|---|---|---|
| `.../requirements/it-solution-requirements.yaml` | `RequirementCatalog` | **yes** (`validate-requirements`) | 18 | undeclared FormalCheck fields: `effective` (2), `description` (16) | plugin **not wired** here |
| `.../requirements/conceptual-model-requirements.yaml` | `RequirementCatalog` | no | 14 | `code` pattern rejects `CM-*`; plus FormalCheck.`description` | left as inventory |
| `.../requirements/examples/it-solution-model.example.yaml` | `ModelPackage` | no | was 2 | `mappings[*].name` after ADR-044 | **fixed** (removed `name`) |
| XLSX import → ModelPackage (CRM fixture) | `ModelPackage` | yes (`slice-cli`) | was many | mapper emitted Mapping.`name` | **fixed** in ingest |

**Stay valid** (plugin OK): examples `client-contract-binding`, `client-data-flow`; solutions `mdm` / `crm` / `esed` / `ucd`; `examples/ontology/valid-model-package.yaml`.

### Proposed fix options for catalogs (not done in C1a)

1. **Schema:** add optional `description` and `effective` to `FormalCheck` in `moex-requirements.yaml`; extend `code` pattern for `CM-*` if conceptual catalog stays in-tree. Requires golden regen if artifacts change.
2. **Data:** strip undeclared keys from catalogs.
3. **Gate:** keep requirements vacuous until (1)/(2); negative mode in C2 uses helper only on paths already green. Wire `validate-requirements` only after green under plugin.

## 3. `source_status` for baseline INV-001..017 (for review before C2)

| ID | Rule | Source | `source_status` | Notes |
|---|---|---|---|---|
| INV-001 | ConceptualProperty #0 | ADR-034:58; slot `is_identifying` | `aligned` | L1 JSON Schema defect (boolean `equals_string`) — level choice separate |
| INV-002 | DataType #0 precision | slot description; ADR-036 | `aligned` | |
| INV-003 | DataType #1 scale | slot description | `partial` | slot text only; ADR-036 covers decimal facets generally |
| INV-004 | DataType #2 max_length | slot description | `partial` | |
| INV-005 | DataType #3 min_length | slot description | `partial` | |
| INV-006 | ValueDomain #0 enumerated | ADR-035:28 | `aligned` | |
| INV-007 | ValueDomain #1 described | ADR-035:28 | `aligned` | |
| INV-008 | ValueDomain #2 reference_set | ADR-035:28 | `aligned` | |
| INV-009 | ConceptualDomain #0 | ADR-035 | `aligned` | |
| INV-010 | DataStructure #0 source_pointer | slot description; ADR-038 | `partial` | normative statement only in slot description |
| INV-011 | DataStructure #1 schema_dialect | ADR-038:44-51 | `divergent` | ADR allows AsyncAPI Multi Format Schema; rule limits to `json_schema`/`openapi_schema` |
| INV-012 | SchemaNode #0 array/map | ADR-038:31; PDM-020 | `aligned` | |
| INV-013 | SchemaNode #1 scalar/enum | PDM-020 | `aligned` | L1 multi-ABSENT weakened (Q2) |
| INV-014 | SchemaNode #2 reference | ADR-038:32; slot | `partial` | |
| INV-015 | DataCarrier #0 in_memory | PDM-012 | `aligned` | L1 multi-ABSENT weakened (Q2) |
| INV-016 | AccessPoint #0 operation | PDM-011; slot | `aligned` | |
| INV-017 | AccessPoint #1 interface | ADR-040:40-41; PDM-018 | `partial` | ADR names only `message_refs`; rule also bans operation fields |

Legend: `aligned` = rule matches cited source; `partial` = source thinner than rule or only slot text; `divergent` = source and rule disagree.

INV-018…027 remain **preliminary** until locked in PR-C1 matrix.

## 4. Open decisions needed before C2

1. Fix path for catalogs (§2 options 1–3): wire `validate-requirements` only after green under plugin.
2. Confirm `source_status` column above (especially INV-011).
3. Still open from C0: Q2 (multi-ABSENT), Q4 (`requirement_refs`), Q6 (golden `doc` update), Q7 (L1/L2/L3 levels).
4. Before merge of the series: re-run `check_all.py` under **Python 3.12** (`.python-version`) and attach the log — current green runs used 3.14.4 in `apps/cli/.venv`.
