# Glossary: «Связи» tab (pinned picker + See also results)

Status: Draft for review  
Date: 2026-10-05  
Scope: `apps/viewer` UI for universal glossary sections (`type: glossary`)  
Related: [ADR-027](../../adr/ADR-027-glossary-term-relations.md), existing tabs Overview / Список / Иерархия

## 1. Goal

Add a fourth glossary tab **Связи** where the user picks one or more terms
(checkbox + pin) and sees the **associative (See also)** neighbourhood of the
selection in a lower panel.

Non-goals (v1):

- Hierarchy / definition-cascade edges in the results panel (those stay on
  **Иерархия** and on the term card Taxonomy / definition blocks).
- Assignment / mapping / `glossary_term_refs` in the results panel.
- Authoring or persisting a `related` field on glossary CSV/JSON (glossary
  remains a view; links come from existing `attributes.see_also`).
- Projecting new See also for ontology (object properties) or model glossary
  (`Relationship`) — out of band; empty results are acceptable until those
  projections exist.
- Persisting selection in the URL or across module/section navigation.
- Resizable splitter between panels.

## 2. UX

Layout: one tab panel, two stacked panes (~45% / ~55% height), each with its
own scroll. No drag handle in v1.

### 2.1 Upper pane (picker)

- Same columns, search, column filters, and pagination behaviour as **Список**.
- First column: checkbox per row.
- **Pinning:** checked rows stay visible at the top of the pane and are
  **excluded** from search/filter matching for the unpinned pool. Clearing
  search does not uncheck them. Unchecking returns the row to the normal list.
- **Pagination:** `PAGE_SIZE` applies only to the unpinned pool. Pinned rows
  are always rendered above the current unpinned page and do not consume
  page slots.
- Multi-select is a **set** (order of check does not matter for results;
  display order of pinned rows follows the Список sort among pinned ids).
- Row / term-link navigation matches Список (open term page / deep-link).

### 2.2 Lower pane (results)

- Empty until at least one term is checked:  
  `Отметьте термины сверху, чтобы увидеть связанные.`
- After selection: table like Список for the **union** of resolvable
  `see_also` neighbours of all checked terms, **excluding** the checked
  terms themselves.
- Extra column **Связь**: human-readable edge label(s), e.g.
  `SelectedTerm → range:owned_by`. If one neighbour is reached from several
  selected terms, keep **one row** and list all such labels (comma-separated
  or equivalent compact text).
- No checkboxes in the lower pane.
- Checked but no resolvable neighbours:  
  `Нет ассоциативных связей у выбранных терминов.`
- Unresolvable targets (not found in the same glossary section) are omitted
  from the table (same spirit as a disabled chip on the term card).

### 2.3 Relation family

Results use **only** ADR-027 associative links: `item.attributes.see_also`.
Do not mix in taxonomy parents/children or definition-source dependents.

## 3. Data

- Read `see_also` entries already attached at publication build
  (`spec_glossary_tree` for LinkML / dams; ontology preview may be `[]`).
- Resolve each entry via existing glossary helpers (`relTargetId`,
  `resolveItemInGlossary` / canonical id).
- Selection state: in-memory `Set` of item ids for the lifetime of the tab
  instance; reset when the section is re-rendered (module/section change).

## 4. Implementation approach

**Separate renderer** (do not extend `renderTable` with checkbox/pin options
in v1 — keeps Список stable).

| Piece | Responsibility |
|---|---|
| `renderGlossary` | Add tab `{ id: "relations", label: "Связи", render → renderGlossaryRelations }` |
| `renderGlossaryRelations` | Split layout, selection Set, paint upper + lower |
| Upper table | Dedicated paint path: Список columns + checkbox + pinned block |
| Lower table | Neighbour items + **Связь** column |
| Shared helpers | Reuse `pickGlossaryListColumns`, `cellValue`, term link formatting, `relTargetId` / `relLabel` |
| CSS | Vertical split container under the relations tabpanel; pane overflow |

Helper `collectGlossarySeeAlsoNeighbours(section, selectedIds)` →
`Map<targetItemId, Array<{ fromId, rel }>>`, dropping unresolved targets and
ids that are themselves selected.

## 5. Testing

Extend static JS contract tests (same style as
`test_js_glossary_section_tabs_and_term_links` in `test_atlas_polish.py`):

- `renderGlossary` includes `id: "relations"` and label `Связи`.
- `renderGlossaryRelations` (or equivalent) exists.
- `collectGlossarySeeAlsoNeighbours` exists; contract assertions cover
  union semantics, exclusion of selected ids, and use of `see_also` only.
- Empty-state copy strings present in JS.
- CSS class(es) for the split layout present in assembled CSS.

No publication rebuild or ADR change required for this wave.

## 6. Acceptance

On `moex.dams` → Глоссарий → Связи:

1. Upper pane looks like Список with checkboxes and fits roughly half height.
2. Checking A pins A; search for B still shows A pinned; checking B keeps both.
3. Lower pane lists See also neighbours of A ∪ B with a **Связь** column.
4. Unchecking removes that term’s contribution from the lower pane.
5. On a glossary with empty `see_also`, empty-neighbour message appears after
   selection.

## 7. Follow-ups (out of scope)

- Family filter chips if results later include more than See also.
- Resizable splitter; URL-persisted selection.
- Model / ontology See also projection work (native graphs → `see_also`).
