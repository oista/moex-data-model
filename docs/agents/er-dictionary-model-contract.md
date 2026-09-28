# ER-dictionary model contract (agent authority)

**Status:** normative  
**Project:** moex-data-model  
**Consumers:** agents that fill ER-dictionary CSV for `moex_standard_linkml` ingest  

This document is the **sole structural authority** for CSV shape. Do not invent
columns, rename headers, reorder columns, or add sheets beyond those listed.
If this contract conflicts with a PDF layout, **the contract wins**; PDF content
is mapped into these columns or recorded in `gaps.md`.

Aligned with:

- `packages/standard-linkml/tests/fixtures/er-dictionary/profile.yaml`
- `packages/standard-linkml/templates/er-dictionary.profile.yaml`
- ingest mapper: `packages/standard-linkml/src/moex_standard_linkml/ingest/mapper.py`
- DAMS enums: `model-assets/specifications/moex-dams/0.1/schemas/moex-types.yaml`

---

## 1. Output package

Target directory (filling runs for this mission):

`packages/standard-linkml/tests/fixtures/er-dictionary/`

| File | Required for ingest | Role |
|------|---------------------|------|
| `profile.yaml` | yes | sheet/column map, `type_map`, solution defaults |
| `Entities.csv` | **yes** | logical entities |
| `Attributes.csv` | **yes** | logical attributes |
| `Relationships.csv` | no | logical relationships |
| `PhysicalObjects.csv` | no | physical objects |
| `PhysicalFields.csv` | no | physical fields |
| `Mappings.csv` | no | logical↔physical mappings |
| `gaps.md` | agent deliverable | omissions / conflicts / unmapped facts |
| `Conceptual.csv` | **out of scope** | do **not** create |

Encoding: UTF-8, comma-separated, first row = header exactly as specified,
no extra columns. Prefer no BOM.

Empty optional cell = leave blank (do not write `null` / `-` / `N/A` unless that
literal appears as a real value in the source — normally leave blank).

---

## 2. Sheet contracts

### 2.1 `Entities.csv`

```
name,title,description,conceptual_ref
```

| Column | Required in row | Semantics |
|--------|-----------------|-----------|
| `name` | **yes** | Technical entity id. System name from PDF (`Account`, `Organization`). Unique. |
| `title` | no | Business display name (RU ok). If unknown, leave empty (ingest may fall back to `name`). |
| `description` | no | Business description from PDF. Empty if absent. |
| `conceptual_ref` | no | **Always empty** for this mission (no Conceptual sheet). |

Rules:

- One row per logical entity.
- Dedup key: `name` (case-sensitive as written; prefer exact system spelling from PDF).
- Do not transliterate Russian titles into `name`.

### 2.2 `Attributes.csv`

```
entity,name,title,description,type,required,pk
```

| Column | Required in row | Semantics |
|--------|-----------------|-----------|
| `entity` | **yes** | Must equal an `Entities.name`. |
| `name` | **yes** | System attribute name (`MoexINN`, `clientId`, `inn`). |
| `title` | no | Business name (RU ok). |
| `description` | no | Description from PDF. |
| `type` | no | Source type token for `profile.type_map` (see §3). Empty only if PDF has no type. |
| `required` | no | `true` / `false` only if PDF states obligation; else **empty**. |
| `pk` | no | `true` / `false` only if PDF states primary/key; else **empty**. |

Rules:

- Dedup key: `(entity, name)`.
- Lookup/FK attributes remain attributes; do not drop them when also modeling a relationship.
- Broken hyphenation from PDF extraction (`MoexApplicatio` + `nSource`) must be
  repaired to the obvious system identifier when unambiguous; if ambiguous → `gaps.md`, do not guess.

### 2.3 `Relationships.csv`

```
name,source,target,source_role,target_role,source_card,target_card,identifying
```

| Column | Required in row | Semantics |
|--------|-----------------|-----------|
| `name` | **yes** | Stable relationship id (`TradeClient`, `AccountPrimaryContact`). Unique. |
| `source` | **yes** | `Entities.name` of source. |
| `target` | **yes** | `Entities.name` of target. |
| `source_role` | no | Role name on source side if stated. |
| `target_role` | no | Role name on target side if stated. |
| `source_card` | no | Cardinality grammar §4. Empty if not stated. |
| `target_card` | no | Cardinality grammar §4. Empty if not stated. |
| `identifying` | no | `true` / `false` only if stated; else empty. |

**Emit a relationship row only when** source entity, target entity, and a
relationship fact are explicit in the PDF **and** you can name it without
invention. If cardinality is missing, you may still emit the row with empty
card columns **only when** the PDF clearly states a relationship between two
named entities; if only a lookup type is listed without a clear association
direction, put the fact in `gaps.md` instead.

### 2.4 `PhysicalObjects.csv`

```
name,title,description,object_kind,qualified_name,technology,system_ref,direction,native_schema_ref
```

| Column | Required in row | Semantics |
|--------|-----------------|-----------|
| `name` | **yes** | Technical physical object id (`EmployeeReadDto`, `client_changed_topic`). |
| `title` | no | Display title. |
| `description` | **yes** (ingest) | Must be grounded in PDF text. |
| `object_kind` | **yes** (ingest) | Enum §5.1 — only if PDF supports the choice without stretching. |
| `qualified_name` | **yes** (ingest) | Stable technical qualifier (topic name, API path, table FQN) **from PDF**. |
| `technology` | **yes** (ingest) | Technology string **from PDF** (e.g. `Apache Kafka`, `REST`). |
| `system_ref` | **yes** (ingest) | IT system ref **only if present in PDF** (e.g. `eam:system/…`). **Never invent.** |
| `direction` | **yes** (ingest) | Enum §5.2 — only if stated or unambiguously labeled in PDF. |
| `native_schema_ref` | **yes** (ingest) | URI/ref to native schema **from PDF**. **Never invent.** |

**Critical:** if any ingest-required column cannot be filled from the PDF,
**do not write the row**. List the candidate object in `gaps.md` with missing
fields named.

### 2.5 `PhysicalFields.csv`

```
object,name,description,native_name,native_type,required,schema_path
```

| Column | Required in row | Semantics |
|--------|-----------------|-----------|
| `object` | **yes** | Must equal a written `PhysicalObjects.name`. |
| `name` | **yes** | Field technical name. |
| `description` | no | From PDF. |
| `native_name` | no | Wire/DB name if different; else empty (ingest may default to `name`). |
| `native_type` | **yes** (ingest) | Native type string from PDF (`uuid`, `string`, `date-time`). |
| `required` | no | `true` / `false` if stated; else empty. |
| `schema_path` | no | JSON path / column path if stated (e.g. `/payload/client_id`). |

Do not emit fields for physical objects that were omitted due to incompleteness.

### 2.6 `Mappings.csv`

```
name,source,target,mapping_type,mapping_cardinality
```

| Column | Required in row | Semantics |
|--------|-----------------|-----------|
| `name` | **yes** | Unique mapping id. |
| `source` | **yes** | Ref token §6. |
| `target` | **yes** | Ref token §6. |
| `mapping_type` | no | Enum §5.3. Empty → ingest default `field_mapping` (only leave empty when PDF does not specify; do not invent other types). |
| `mapping_cardinality` | no | Enum §5.4. Empty → ingest default `one_to_one`. |

Emit **only** when the PDF explicitly asserts correspondence between the two
sides. Name similarity alone is insufficient.

---

## 3. Logical `type` tokens (`Attributes.type`)

Prefer keys present in `profile.yaml` → `type_map` (case-insensitive match in
ingest). Canonical template keys include:

`VARCHAR`, `NVARCHAR`, `CHAR`, `TEXT`, `STRING`, `NUMBER`, `INTEGER`, `INT`,
`BIGINT`, `DECIMAL`, `NUMERIC`, `FLOAT`, `DOUBLE`, `BOOLEAN`, `BOOL`, `DATE`,
`DATETIME`, `TIMESTAMP`, `TIME`, `BINARY`, `BLOB`, `URI`, `UUID`, `IDENTIFIER`,
`PK`

PDF → token guidance (only when PDF type is clear):

| PDF wording examples | Preferred token |
|----------------------|-----------------|
| Строка (N символов), string | `VARCHAR` |
| Логическое, boolean | `BOOLEAN` |
| Дата, date | `DATE` |
| Дата и время, datetime, date-time | `DATETIME` |
| Число / decimal / number (fractional) | `DECIMAL` |
| integer / int / bigint | `INTEGER` or `BIGINT` if specified |
| uuid | `UUID` |
| Справочник / enum / lookup | keep attribute; type `VARCHAR` only if PDF treats it as string code; else leave type as source token or empty + gap note |

If the PDF type cannot be mapped confidently to a `type_map` key, write the
**source type string as-is** and add a `gaps.md` line. Do not silently invent
a different token.

---

## 4. Cardinality grammar

Accepted by ingest when non-empty:

- `N` (exact, e.g. `1`)
- `N..M` (e.g. `0..1`, `1..1`)
- `N..*` or `N..n` / `N..N` (unbounded upper)

Invalid strings cause mapper errors — leave empty rather than guess.

---

## 5. Enumerations (DAMS)

Use these literals **exactly** when a value is written.

### 5.1 `object_kind` (`PhysicalObjectKindEnum`)

`database`, `schema`, `table`, `view`, `column`, `api`, `endpoint`, `payload`,
`topic`, `queue`, `message`, `file`, `dataset`, `pipeline`

### 5.2 `direction` (`FlowDirectionEnum`)

`inbound`, `outbound`, `internal`, `bidirectional`

### 5.3 `mapping_type` (`MappingTypeEnum`)

`semantic_equivalence`, `specialization`, `implementation`, `field_mapping`,
`transformation`, `aggregation`, `derivation`

### 5.4 `mapping_cardinality` (`MappingCardinalityEnum`)

`one_to_one`, `one_to_many`, `many_to_one`, `many_to_many`

---

## 6. Mapping reference tokens

Each of `Mappings.source` / `Mappings.target` is one token, or several joined
with `|` (no spaces required around `|`, but trim each part).

Allowed forms:

| Form | Resolves to |
|------|-------------|
| `EntityName` | logical entity |
| `EntityName.attrName` | logical attribute |
| `ObjectName` | physical object |
| `ObjectName.fieldName` | physical field |

Unresolved refs → mapper error → must fix or remove the mapping row.

---

## 7. Boolean cells

When filled, use lowercase `true` / `false`.

Ingest also treats as true: `1`, `yes`, `y`, `x`, `pk` (case-insensitive).
Prefer explicit `true`/`false` for clarity.

Empty boolean/pk/required → ingest `false`. That is allowed under the
no-invention policy (absence ≠ assertion of false in the business sense;
document uncertainty in `gaps.md` when important).

---

## 8. `gaps.md` requirements

Create/update `gaps.md` in the output directory every run.

Minimum structure:

```markdown
# ER-dictionary gaps

## Unmapped / incomplete physical objects
- ...

## Relationships not emitted (missing cardinality / unclear direction)
- ...

## Type ambiguities
- ...

## Name conflicts across PDFs
- ...

## Other
- ...
```

Every omitted PhysicalObject candidate must list which required columns were
missing. Every skipped inventable-looking value must state why it was not filled.

---

## 9. Structural validation checklist (must pass before ingest)

1. Headers equal §2 exactly (spelling + order).
2. `Entities.name` unique; non-empty.
3. Every `Attributes.entity` ∈ Entities; `(entity,name)` unique.
4. Every `Relationships.source`/`target` ∈ Entities; `name` unique when file present.
5. Every `PhysicalFields.object` ∈ PhysicalObjects written rows.
6. Every mapping token resolves per §6.
7. No `Conceptual.csv`.
8. No fabricated `system_ref` / `native_schema_ref` / cardinalities / mappings.

Then run ingest validation (see playbook). Delivery is forbidden if mapper or
LinkML validation reports errors.
