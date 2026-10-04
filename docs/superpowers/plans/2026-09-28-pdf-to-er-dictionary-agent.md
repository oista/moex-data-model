# PDF → ER-dictionary agent docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship durable agent playbook + model contract so a filling agent can turn heterogeneous PDFs into valid ER-dictionary CSVs.

**Architecture:** Two markdown artifacts under `docs/agents/`: normative column/ref contract, and a step-by-step playbook that mandates contract checks plus ingest validation before delivery.

**Tech Stack:** Markdown docs; target CSV layout of `moex_standard_linkml` ER-dictionary ingest; DAMS enums from `moex-types.yaml`.

## Global Constraints

- Spec: `docs/superpowers/specs/2026-09-28-pdf-to-er-dictionary-agent-design.md`
- No Conceptual sheet; system names in `name`; no invented values
- Sheets: Entities, Attributes, Relationships, PhysicalObjects, PhysicalFields, Mappings
- Output path for filling runs: `packages/standard-linkml/tests/fixtures/er-dictionary`

---

### Task 1: Model contract artifact

**Files:**
- Create: `docs/agents/er-dictionary-model-contract.md`

- [x] Write full column headers, requiredness, enums, ref rules, type_map notes, gaps rules
- [x] Cross-check against fixture `profile.yaml` and DAMS `PhysicalObjectKindEnum` / `FlowDirectionEnum` / mapping enums

### Task 2: Agent playbook

**Files:**
- Create: `docs/agents/pdf-to-er-dictionary.md`

- [x] Write workflow, PDF classification, extraction rules, pre-delivery gate, ingest command
- [x] Link to model contract as sole structural authority
- [x] Include OKITA default PDF path and fixture overwrite warning

### Task 3: Spec status

**Files:**
- Modify: `docs/superpowers/specs/2026-09-28-pdf-to-er-dictionary-agent-design.md`

- [x] Set status to approved / implemented for docs deliverable
