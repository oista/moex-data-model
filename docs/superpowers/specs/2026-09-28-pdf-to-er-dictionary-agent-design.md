# PDF → ER-dictionary agent (instruction + model contract)

**Status:** delivered (agent docs)  
**Date:** 2026-09-28  
**Project:** moex-data-model

Delivered artifacts: [`docs/agents/pdf-to-er-dictionary.md`](../../agents/pdf-to-er-dictionary.md), [`docs/agents/er-dictionary-model-contract.md`](../../agents/er-dictionary-model-contract.md). Runtime fills (`gaps.md`, OKITA CSVs) remain per-run agent output.

## Problem

Source descriptions of data structures live in heterogeneous PDFs (CRM entity
sheets, domain/logical models, API connector docs). Operators need an AI agent
that fills the ER-dictionary CSV set used by `moex_standard_linkml` ingest,
strictly against the sheet contract, without inventing missing fields, and with
a hard validation gate before delivery.

## Decisions (approved)

| Topic | Choice |
|-------|--------|
| Output location | Overwrite `packages/standard-linkml/tests/fixtures/er-dictionary` |
| Sheets in scope | Entities, Attributes, Relationships, PhysicalObjects, PhysicalFields, Mappings |
| Conceptual | Out of scope — do not create `Conceptual.csv` (ingest compat stubs) |
| Technical names | System names in `*.name`; business RU text in `title` / `description` |
| Missing values | Do not invent; leave empty or omit the row; record in `gaps.md` |
| Packaging | Approach **1**: detailed agent instruction + markdown model contract |

## Artifacts to produce (implementation)

| Path | Role |
|------|------|
| `docs/agents/pdf-to-er-dictionary.md` | Step-by-step agent playbook |
| `docs/agents/er-dictionary-model-contract.md` | Sole structural authority for CSV columns, refs, types, checks |
| `…/fixtures/er-dictionary/gaps.md` | Written by the filling agent per run (not part of this design deliverable’s static content beyond a template note) |

The filling agent’s runtime outputs remain the fixture CSVs + `gaps.md` +
updated `profile.yaml` metadata when the source solution identity is known
from the PDFs (still: no invented EAM refs).

Default PDF input directory:

`F:\!PASSPORT\!H_DATASC\!Data Architecture\MOEX_DataModel\OKITA\pdf solutions`

## Agent workflow

1. Load `er-dictionary-model-contract.md` (mandatory; never improvise columns).
2. Enumerate PDFs; extract text (and tables when tools allow).
3. Classify each document / section: CRM entity sheet | domain/logical model | API/connector | other (glossary-only → not CSV).
4. Extract candidates into an internal working set; merge across PDFs with dedup.
5. Emit only rows that satisfy contract requiredness; everything else → `gaps.md`.
6. Run structural checks (headers, uniqueness, referential integrity).
7. Run ingest CLI validate against DAMS schema.
8. Deliver only if gate passes; otherwise fix or gap-out and re-run.

## PDF → sheet mapping

### CRM entity sheet

Signals: «Параметры объекта», «Атрибуты объекта», columns like систем name /
type / requiredness.

- Object → `Entities` (`name` = system name, e.g. `Account`)
- Attribute rows → `Attributes`
- Lookup «Справочник X (SysName)» → `Relationships` **only if** cardinality
  (and preferably roles) are explicit in the PDF; else gap

### Domain / logical model

Signals: «Логическая модель», entity/attribute tables, FK notes.

- Entities + Attributes as stated
- Explicit FK with stated cardinality → `Relationships`
- FK without cardinality → keep attribute; relationship → `gaps.md`

### API / connector

Signals: endpoints, DTO request/response, JSON field tables.

- DTO / resource → `PhysicalObjects` **only if all required physical columns
  are present in the source text**
- Fields → `PhysicalFields`
- `Mappings` only when the PDF explicitly links a physical field to a logical
  attribute/entity

### Other

Glossary, principles, container diagrams without field structure → not CSV;
optional mention in `gaps.md`.

## Hard rules (non-negotiable)

1. **Contract supremacy.** Column sets and order come only from
   `er-dictionary-model-contract.md` (aligned with
   `packages/standard-linkml/tests/fixtures/er-dictionary/profile.yaml` and
   `packages/standard-linkml/templates/er-dictionary.profile.yaml`).
2. **No invention.** Forbidden: fabricating `system_ref`, `eam:system/…`,
   cardinalities, PKs, mappings, `object_kind`, technologies, or descriptions
   not grounded in the PDF.
3. **PhysicalObjects completeness.** Ingest requires
   `name, description, object_kind, qualified_name, system_ref, technology,
   direction, native_schema_ref`. Incomplete → omit row + gap.
4. **One merged CSV set** for the whole PDF batch; first occurrence wins on
   name conflicts; conflicts documented in `gaps.md`.
5. **Encoding.** UTF-8 CSV, header row first, comma-separated.
6. **Delivery gate.** Must pass header/ref checks **and** ingest validation.

## Model contract (summary)

Full normative detail lives in `er-dictionary-model-contract.md`. Summary:

| File | Header |
|------|--------|
| Entities.csv | `name,title,description,conceptual_ref` |
| Attributes.csv | `entity,name,title,description,type,required,pk` |
| Relationships.csv | `name,source,target,source_role,target_role,source_card,target_card,identifying` |
| PhysicalObjects.csv | `name,title,description,object_kind,qualified_name,technology,system_ref,direction,native_schema_ref` |
| PhysicalFields.csv | `object,name,description,native_name,native_type,required,schema_path` |
| Mappings.csv | `name,source,target,mapping_type,mapping_cardinality` |

Referential rules:

- `Attributes.entity` ∈ `Entities.name`
- `Relationships.source` / `target` ∈ `Entities.name`
- `PhysicalFields.object` ∈ `PhysicalObjects.name`
- Mapping tokens: `Entity` \| `Entity.attr` \| `Object` \| `Object.field`
- `conceptual_ref` left empty (no Conceptual sheet)
- Cardinality grammar when present: `N`, `N..M`, `N..*`

Type handling:

- Prefer keys from `profile.yaml` `type_map` (e.g. `VARCHAR`, `UUID`, `DECIMAL`)
- If PDF type is not in `type_map`, keep the source token as-is and note in
  `gaps.md` (ingest falls back to `string`; agent must not silently rename)

Boolean / pk columns:

- Write `true` / `false` only when explicit; otherwise leave empty
  (ingest treats empty as false — acceptable under no-invention)

## Pre-delivery checklist (blocking)

1. Headers match contract 1:1 (names and order).
2. Uniqueness: entity names; `(entity, attr)`; relationship names; physical
   object names; `(object, field)`; mapping names.
3. All cross-sheet references resolve.
4. Spot-check: no invented values vs PDF; gaps listed.
5. Ingest:

```powershell
packages/standard-linkml/.venv/Scripts/python -m moex_standard_linkml.ingest.cli ingest `
  --workbook packages/standard-linkml/tests/fixtures/er-dictionary `
  --profile packages/standard-linkml/tests/fixtures/er-dictionary/profile.yaml `
  --schema model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml `
  --out $env:TEMP/er-dictionary-ingest-check
```

6. Deliver only when mapper has zero errors and `validation.txt` reports OK.

## Out of scope

- Changing ingest Python code or DAMS schema
- Filling Conceptual sheet / ontology alignment
- OCR pipeline productization (agent may use available tools; failures → gaps)
- Automatic invention of EAM system CURIEs
- Replacing unit tests that depend on the current pilot fixture contents
  without an explicit follow-up task (note: overwriting the fixture **will**
  break pilot-shaped tests until CSVs or tests are updated)

## Risk note (fixture overwrite)

Overwriting `tests/fixtures/er-dictionary` replaces the small pilot
`TradingClient` / `Trade` sample. Downstream tests in
`packages/standard-linkml/tests/` may fail until updated. Acceptable for this
agent’s mission; call out in the playbook so operators expect a test update
pass or a separate fixture directory later.

## Success criteria

- Two durable docs under `docs/agents/` as above
- An agent following the playbook can process the OKITA PDF folder into
  contract-valid CSVs, with `gaps.md` for omissions, and pass ingest validate
  when enough explicit data exists for required columns
- No undocumented columns or invented physical `system_ref` values
