# Agent playbook: PDF → ER-dictionary CSV

**Role:** You are a filling agent. You read PDF documents that describe data
structures and produce ER-dictionary CSV files for MOEX DAMS ingest via
`moex_standard_linkml`.

**You do not** change ingest Python code, DAMS schemas, or invent business /
EAM identifiers.

**Normative structure:** always open and obey  
[`er-dictionary-model-contract.md`](./er-dictionary-model-contract.md)  
before writing any CSV. If unsure about a column — re-read the contract; do
not improvise.

**Design context:**  
`docs/superpowers/specs/2026-09-28-pdf-to-er-dictionary-agent-design.md`

---

## 0. Mission parameters

| Parameter | Value |
|-----------|--------|
| Default PDF input | `F:\!PASSPORT\!H_DATASC\!Data Architecture\MOEX_DataModel\OKITA\pdf solutions` |
| CSV output | `packages/standard-linkml/tests/fixtures/er-dictionary/` |
| Sheets to fill | Entities, Attributes, Relationships, DataCarriers, PhysicalFields, Mappings |
| Sheets forbidden | Conceptual |
| Naming | System/technical names in `name`; RU business text in `title` / `description` |
| Missing data | **Do not invent.** Leave empty or omit the row; record in `gaps.md` |

**Warning:** writing into the fixture directory replaces the pilot
`TradingClient` / `Trade` sample. Package tests may fail until updated — that
is expected for this mission; note it in your final report.

---

## 1. Mandatory bootstrap (do this first)

1. Read [`er-dictionary-model-contract.md`](./er-dictionary-model-contract.md) fully.
2. Read existing `profile.yaml` in the output directory (column aliases + `type_map`).
3. Skim fixture examples only as format samples — **do not** copy pilot domain data into a new solution model.
4. List all `*.pdf` in the input directory.
5. Prepare empty working tables in memory (or temp files) matching contract headers.
6. Create/clear `gaps.md` skeleton per contract §8.

Stop if the contract file is missing.

---

## 2. Extract text from PDFs

For each PDF:

1. Extract text (and tables if your tools support table extraction).
2. Preserve page/section markers in notes when useful for `gaps.md` citations.
3. Repair obvious PDF line-break damage inside **system identifiers** only when
   unambiguous (`MoexApplicatio` + `nSource` → `MoexApplicationSource`).
   If two repairs are plausible → keep fragments in `gaps.md`, do not pick.
4. If a PDF is image-only / OCR fails → record in `gaps.md` and continue with others.

Expected heterogeneity (real OKITA samples):

| Pattern | Example signals |
|---------|-----------------|
| CRM entity sheet | Title `Клиент (Account)`; blocks «Параметры объекта», «Атрибуты объекта»; columns «Бизнес-название», «Системное название», «Тип атрибута», «Обязательность» |
| Domain / logical model | «Логическая модель данных», tables of business entities + attribute matrices with Type / FK / Обязательность |
| API / connector | OpenAPI-like endpoints, `Request Body` / `Response`, DTO names, JSON field lists |
| Non-structural | Glossary, principles, container diagrams without fields → usually no CSV rows |

A single PDF may contain more than one pattern. Classify **by section**, not only by file.

---

## 3. Classification → sheet routing

### 3.1 CRM entity sheet → logical

For each object block:

1. **Entity**
   - `name` = system name (`Account`, `Contact`, `Lead`)
   - `title` = business name (`Клиент`, `Контакт`)
   - `description` = from «Параметры» / surrounding text if present; else empty
   - `conceptual_ref` = empty
2. **Attributes** — one row per attribute with a recoverable system name
   - `entity` = entity `name`
   - `name` = system attribute name
   - `title` = business attribute name
   - `description` = description column if present
   - `type` = per contract §3
   - `required` / `pk` = only if explicitly stated; else empty
3. **Relationships**
   - When type is «Справочник» and target entity system name is explicit
     (`Контакт (Contact)` → target `Contact`):
     - Emit relationship **only if** association is clearly an entity link and you
       can set `source`/`target` without guessing direction.
     - Prefer `source` = owning entity, `target` = lookup entity when the attribute
       sits on the owning entity.
     - Cardinality / roles: fill only if stated; otherwise empty columns **or**
       skip the relationship and gap it (see contract §2.3 — when direction is unclear, gap).
   - Do **not** invent `0..*` / `1` defaults.

### 3.2 Domain / logical model → logical

1. Entity list tables → `Entities` (`name` = technical entity id as printed:
   `Organization`, `Person`, …).
2. Per-entity attribute tables → `Attributes`.
3. FK notes (`typeId` FK → `OrganizationType`):
   - Always keep the FK attribute row if the attribute exists.
   - Add `Relationships` only when cardinality (or an explicit association
     statement) is present; otherwise gap the relationship.

Ignore pure glossary definitions that do not define fields.

### 3.3 API / connector → physical (+ rare mappings)

1. Treat a documented DTO / resource / topic as a **candidate** DataCarrier.
2. Write `DataCarriers` **only if every ingest-required column** is present
   in the PDF (contract §2.4):  
   `name, description, asset_kind, qualified_name, technology, system_ref, direction, structure_ref`
3. Typical grounded fills (examples — use only when text supports them):
   - `asset_kind=api` or `endpoint` / `payload` when document is an API
   - `qualified_name` = server URL + path, or DTO name if that is the only
     stable qualifier **printed**
   - `technology` = e.g. `REST` if stated
   - `structure_ref` = schema URL if printed
   - `system_ref` / `direction` — **only if printed**; otherwise omit entire object
4. Fields of request/response DTOs → `PhysicalFields` for objects you actually wrote.
5. `Mappings` — only if the document explicitly maps API fields to logical
   entities/attributes. Name similarity (`inn` vs `MoexINN`) is **not** enough.

### 3.4 Merge across PDFs

- Produce **one** CSV set for the whole batch.
- Dedup keys: entity `name`; `(entity, attr)`; relationship `name`; physical
  `name`; `(object, field)`; mapping `name`.
- On conflict: keep the first completed row; document the conflict in `gaps.md`
  with both sources.

---

## 4. Writing CSV files

1. Delete or avoid creating `Conceptual.csv`.
2. Write headers **exactly** as in the contract (order matters).
3. Write data rows UTF-8 CSV.
4. Update `gaps.md` continuously as you skip items.
5. Optionally update `profile.yaml` **metadata** (`package_title`,
   `package_description`, `solution_slug`, …) only when those identities are
   explicit in the PDFs. Do **not** invent `solution_ref` / `domain_ref` /
   `eam:system/…`. Keep sheet column mappings unchanged unless the operator
   asks.

Boolean/empty policy: see contract §7. Prefer blank over fabricated `false`
when the PDF is silent; blank is acceptable for ingest.

---

## 5. Pre-delivery gate (blocking)

You **must not** present results as complete until all steps pass.

### 5.1 Contract self-check

Re-open the contract and verify:

- [ ] Headers 1:1 for every written file
- [ ] No Conceptual file
- [ ] All referential integrity rules (contract §9)
- [ ] No invented `system_ref`, `structure_ref`, cardinalities, or mappings
- [ ] Every incomplete physical candidate is in `gaps.md` with missing columns listed
- [ ] Spot-check ≥3 attributes and ≥1 entity against PDF text

### 5.2 Ingest validation

From repo root (venv must already exist; if not, run
`packages/standard-linkml/scripts/check.ps1` setup or create venv per package README):

```powershell
packages/standard-linkml/.venv/Scripts/python -m moex_standard_linkml.ingest.cli ingest `
  --workbook packages/standard-linkml/tests/fixtures/er-dictionary `
  --profile packages/standard-linkml/tests/fixtures/er-dictionary/profile.yaml `
  --schema model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml `
  --out $env:TEMP/er-dictionary-ingest-check
```

Pass criteria:

- Command exits successfully
- No mapper errors
- `{name}.validation.txt` does not report validation failure

On failure:

1. Read errors.
2. Fix CSV **only** with values grounded in PDFs, **or** remove the offending
   row and move the fact to `gaps.md`.
3. Re-run §5.1–5.2.
4. Never “fix” by inventing refs to silence the validator.

### 5.3 Delivery report (required in the agent reply)

Include:

1. PDF files processed + classification per file
2. Counts: entities, attributes, relationships, technical asset (DataCarrier)s, fields, mappings
3. Path to `gaps.md` + top residual risks
4. Ingest command result (pass/fail + path to `validation.txt`)
5. Explicit statement: “Contract checklist passed” or list failures

If ingest cannot pass because PDFs lack required physical columns, it is
valid to deliver logical CSVs only (empty/absent optional physical sheets),
with physical candidates fully listed in `gaps.md`, and ingest still green.

---

## 6. Worked mapping sketches (non-normative)

### 6.1 CRM attribute row

PDF: business «ИНН», system `MoexINN`, type «Строка (50 символов)»,
обязательность «По условию».

```csv
Account,MoexINN,ИНН,,VARCHAR,,
```

(`required` empty because “по условию” ≠ unconditional true; note in gaps if needed.)

### 6.2 Logical model attribute

PDF: `Organization.id` bigint, обязательность Да, описание «MCDB ID».

```csv
Organization,id,id,Уникальный идентификатор (MCDB ID),BIGINT,true,true
```

(`pk=true` only if PDF marks it as identifier/PK; here “Уникальный идентификатор” may justify `pk=true` — if the PDF does not say primary key, leave `pk` empty and put “possible PK” in gaps.)

### 6.3 API field without system_ref

PDF documents `EmployeeReadDto.rowId: uuid` but no EAM system CURIE and no
schema URI → **do not** write DataCarriers/PhysicalFields; gap:

```markdown
## Unmapped / incomplete technical asset (DataCarrier)s
- EmployeeReadDto (API Docsvision): missing system_ref, structure_ref, direction; has fields rowId, id1c, accountName, email
```

---

## 7. Anti-patterns (fail the review)

- Adding columns like `notes`, `source_pdf`, `enum_values` into CSV
- Using Russian or translit as `Entities.name` when a system name exists
- Creating `Conceptual.csv` “to be helpful”
- Filling `system_ref=eam:system/UNKNOWN` or similar
- Inferring mappings because names look similar
- Defaulting all cardinalities to `0..*` / `1`
- Declaring success without running ingest validate
- Quietly changing contract headers to match a spreadsheet export

---

## 8. Operator overrides

If the human explicitly supplies missing values (EAM system CURIE, direction,
schema URI) in the chat, you may fill those cells **and** cite the human
message in `gaps.md` under “Operator-provided values”. That is not invention.

Without an explicit human value — leave empty / omit row.
