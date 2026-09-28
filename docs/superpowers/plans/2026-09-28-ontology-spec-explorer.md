# Ontology Spec explorer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Give Spec ontology modules (FIBO first, Ontology Catalog second) a DAMS-style `explorer`: domain folders in the left nav, nested `subClassOf` trees, and rich class cards with definitions in the main pane — without removing existing glossary/hierarchy/cards/backlinks sections.

**Architecture:** Reuse `type: explorer` and `PublicationItem`. CSV/JSON normalizers emit domain `group` roots whose children are nested class trees. Viewer generalizes `nav-explorer` to arbitrary depth and branches `renderExplorerDetail` for ontology attributes (`iri`, `definition_ru`, …). DAMS LinkML explorer stays flat under schema packages.

**Tech Stack:** Python normalizers (`apps/viewer`), ontology-catalog `publication_export`, vanilla JS/CSS viewer, pytest, static `publish.yaml` manifests.

**Spec:** `docs/superpowers/specs/2026-09-28-ontology-spec-explorer-design.md`

## Global Constraints

- Layout matches DAMS explorer: nav left, card main — no right-hand tree panel for explorer.
- Hybrid nav: top-level domain/ontology folders; inside — asserted parent/child tree.
- Keep glossary, hierarchy (`tree`), entity-table cards, backlinks; add explorer alongside.
- No new section type name; extend `explorer` only.
- Do not change DAMS schema-package explorer semantics (flat class/enum children).
- Preview/catalog data only; no live RDF/reasoning in the viewer.
- Optional card fields degrade gracefully when missing.

## File structure

| File | Responsibility |
|------|----------------|
| `apps/viewer/src/moex_publication_viewer/normalizers/helpers.py` | `items_to_domain_explorer()` — group by domain + nest by parent |
| `apps/viewer/src/moex_publication_viewer/normalizers/csv_normalizer.py` | Call helper when `section.type == "explorer"` |
| `packages/ontology/publish.yaml` | Add FIBO `explorer` section |
| `apps/viewer/static/viewer.js` | Deep nav, deep find/collect, ontology card renderer |
| `apps/viewer/static/viewer.css` | Nested nav indent / ontology card tweaks if needed |
| `packages/ontology-catalog/.../publication_export.py` | Emit `ontology_explorer.json` |
| `packages/ontology-catalog/publish.yaml` | Add catalog `explorer` section |
| `apps/viewer/tests/test_normalizers.py` | CSV explorer nesting tests |
| `apps/viewer/tests/test_build.py` | Smoke: FIBO (then catalog) has explorer |

---

### Task 1: CSV → domain explorer helper

**Files:**
- Modify: `apps/viewer/src/moex_publication_viewer/normalizers/helpers.py`
- Modify: `apps/viewer/src/moex_publication_viewer/normalizers/csv_normalizer.py`
- Test: `apps/viewer/tests/test_normalizers.py`

**Interfaces:**
- Consumes: existing `PublicationItem`, `items_to_tree` pattern, `records_to_items`
- Produces: `items_to_domain_explorer(items, *, domain_attr="source_domain", parent_attr="parent_local_name") -> list[PublicationItem]` where each root has `attributes.kind == "group"` and nested class children

- [x] **Step 1: Write the failing test**

Add to `apps/viewer/tests/test_normalizers.py`:

```python
def test_csv_explorer_groups_by_domain_and_nests_parents(tmp_path: Path):
    p = tmp_path / "onto.csv"
    p.write_text(
        "local_name,label,definition,definition_ru,label_ru,parent_local_name,source_domain,iri\n"
        "RootA,Root A,def A,опр A,Корень A,,FND,https://ex/RootA\n"
        "ChildA,Child A,def CA,опр CA,Дитя A,RootA,FND,https://ex/ChildA\n"
        "RootB,Root B,def B,,, ,BE,https://ex/RootB\n"
        "Cross,Cross,def X,,,RootA,BE,https://ex/Cross\n",
        encoding="utf-8",
    )
    sec = _section(
        type="explorer",
        source={"format": "csv", "path": "onto.csv"},
        key_column="local_name",
        tags=["ontology", "fibo"],
    )
    out = CsvNormalizer().normalize(sec, p)
    assert out.type == "explorer"
    groups = {g.id: g for g in out.items}
    assert set(groups) == {"group:FND", "group:BE"}
    assert all(g.attributes.get("kind") == "group" for g in out.items)
    fnd = groups["group:FND"]
    assert fnd.title == "FND"
    assert [c.id for c in fnd.children] == ["RootA"]
    assert [c.id for c in fnd.children[0].children] == ["ChildA"]
    child = fnd.children[0].children[0]
    assert child.attributes.get("kind") == "class"
    assert child.description == "def CA"
    assert child.attributes.get("definition_ru") == "опр CA"
    assert child.attributes.get("iri") == "https://ex/ChildA"
    be = groups["group:BE"]
    # Cross parent RootA is other domain → treat as root in BE
    be_ids = {c.id for c in be.children}
    assert be_ids == {"RootB", "Cross"}
```

- [x] **Step 2: Run test to verify it fails**

Run: `python -m pytest apps/viewer/tests/test_normalizers.py::test_csv_explorer_groups_by_domain_and_nests_parents -v`

Expected: FAIL (explorer path not implemented / no groups)

- [x] **Step 3: Implement helper + CSV branch**

In `helpers.py` add:

```python
def items_to_domain_explorer(
    items: list[PublicationItem],
    *,
    domain_attr: str = "source_domain",
    parent_attr: str = "parent_local_name",
) -> list[PublicationItem]:
    """Group flat items by domain_attr; nest by parent_attr within each domain."""
    by_domain: dict[str, list[PublicationItem]] = {}
    for item in items:
        raw = (item.attributes or {}).get(domain_attr)
        domain = str(raw).strip() if raw not in (None, "") else "unknown"
        enriched = item.model_copy(
            update={
                "attributes": {
                    **(item.attributes or {}),
                    "kind": (item.attributes or {}).get("kind") or "class",
                }
            }
        )
        by_domain.setdefault(domain, []).append(enriched)

    groups: list[PublicationItem] = []
    for domain in sorted(by_domain.keys()):
        domain_items = by_domain[domain]
        tree = items_to_tree(domain_items, parent_attr=parent_attr)
        groups.append(
            PublicationItem(
                id=f"group:{domain}",
                title=domain,
                description=f"Ontology domain {domain}",
                attributes={
                    "kind": "group",
                    "source_domain": domain,
                    "purpose": f"Classes in domain {domain} (preview).",
                    "class_count": len(domain_items),
                    "enum_count": 0,
                },
                children=tree,
            )
        )
    return groups
```

In `csv_normalizer.py` after `records_to_items`:

```python
        items = records_to_items(rows, key_column=section.key_column)
        if section.type == "tree":
            items = items_to_tree(items)
        elif section.type == "explorer":
            from moex_publication_viewer.normalizers.helpers import items_to_domain_explorer

            items = items_to_domain_explorer(items)
```

(Prefer a top-level import of `items_to_domain_explorer` next to `items_to_tree` instead of inline import.)

- [x] **Step 4: Run test to verify it passes**

Run: `python -m pytest apps/viewer/tests/test_normalizers.py::test_csv_explorer_groups_by_domain_and_nests_parents -v`

Expected: PASS

- [x] **Step 5: Commit**

```bash
git add apps/viewer/src/moex_publication_viewer/normalizers/helpers.py \
  apps/viewer/src/moex_publication_viewer/normalizers/csv_normalizer.py \
  apps/viewer/tests/test_normalizers.py
git commit -m "feat(viewer): CSV explorer groups by domain with nested parents"
```

---

### Task 2: FIBO manifest explorer section

**Files:**
- Modify: `packages/ontology/publish.yaml`
- Modify: `apps/viewer/tests/test_build.py`

**Interfaces:**
- Consumes: Task 1 CSV explorer normalization
- Produces: FIBO module section `id: explorer`, `type: explorer`, same preview CSV

- [x] **Step 1: Add section to publish.yaml**

Insert as the **first** section (so explorer is primary), keep glossary + hierarchy:

```yaml
  - id: explorer
    title: Class explorer
    description: Domains and asserted subClassOf tree (preview) with full class cards
    type: explorer
    source:
      format: csv
      path: publications/fibo_glossary.preview.csv
    key_column: local_name
    tags:
      - fibo
      - preview
      - ontology
```

- [x] **Step 2: Extend build smoke asserts**

In `test_build_tmp_repo` / golden path that loads real FIBO (same place as `assert "glossary" in fibo["sections"]`):

```python
    assert "explorer" in fibo["sections"]
    assert "group:FND" in html or "group:BE" in html
```

- [x] **Step 3: Run tests**

Run:

```bash
python -m pytest apps/viewer/tests/test_normalizers.py apps/viewer/tests/test_build.py -q
```

Expected: PASS (build embeds FIBO explorer groups)

- [x] **Step 4: Commit**

```bash
git add packages/ontology/publish.yaml apps/viewer/tests/test_build.py
git commit -m "feat(fibo): add ontology explorer section to publication manifest"
```

---

### Task 3: Nested explorer navigation (viewer.js)

**Files:**
- Modify: `apps/viewer/static/viewer.js` (`findExplorerItem`, `collectExplorerIds`, `appendPublicationSubtree` / nav-explorer)
- Modify: `apps/viewer/static/viewer.css` (nested indent under `.nav-group-children` if needed)
- Test: `apps/viewer/tests/test_build.py` (string smoke for recursive helpers)

**Interfaces:**
- Consumes: explorer items with `group → class → class…` depth
- Produces: sidebar that expands/collapses nested class nodes; hash still `#…&section=explorer&item=<id>`

- [x] **Step 1: Deep find + collect**

Replace shallow walks with recursive helpers:

```javascript
  function walkExplorerItems(section, visit) {
    function walk(nodes, group, ancestors) {
      for (const node of nodes || []) {
        visit(node, group, ancestors);
        const nextGroup = (node.attributes?.kind === "group") ? node : group;
        walk(node.children, nextGroup, ancestors.concat(node));
      }
    }
    walk(section?.items || [], null, []);
  }

  function findExplorerItem(section, itemId) {
    if (!section || !itemId) return null;
    let found = null;
    walkExplorerItems(section, (node, group, ancestors) => {
      if (node.id === itemId && !found) {
        found = { item: node, group, ancestors };
      }
    });
    return found;
  }

  function collectExplorerIds(section) {
    const ids = new Set();
    walkExplorerItems(section, (node) => {
      if (node.attributes?.kind !== "group") ids.add(node.id);
    });
    return ids;
  }
```

Update `makeSpecLink` / inheritance links to keep working with deep ids (already use `collectExplorerIds`).

- [x] **Step 2: Recursive nav under each group**

In `appendPublicationSubtree`, when rendering `group.children`, do not assume leaves. For each child:

- If `child.children?.length`, render a nested collapsible row (toggle + label button) similar to group, using a `Set` of open node ids (reuse `openGroups` keyed by any id, or add `openNavIds`).
- Auto-open ancestors when `focus.item` is under them (extend the existing `openGroups.add` condition to walk descendants).
- Badge count: for groups keep total descendant classes, or `child.children.length` for intermediate nodes — prefer **direct children count** for toggles, group badge = recursive class count.

Minimal recursive renderer sketch:

```javascript
      function appendNavNode(parentEl, node, expl, mod, depth) {
        const hasKids = node.children && node.children.length;
        const isGroup = node.attributes?.kind === "group";
        // group button already handled at top; this handles class nodes
        const row = document.createElement("div");
        row.className = "nav-tree-node";
        row.style.marginLeft = depth ? `${depth * 8}px` : "0";
        // toggle + label buttons; on label click setHash section=expl.id item=node.id
        // if hasKids, render children container with hidden=!openNavIds.has(node.id)
        parentEl.appendChild(row);
      }
```

Keep DAMS behaviour: groups with only flat class/enum children still work (depth 0 under group).

- [x] **Step 3: CSS for nested nav**

Add if missing:

```css
.nav-explorer .nav-tree-node { display: flex; flex-direction: column; gap: 2px; }
.nav-explorer .nav-tree-children { display: flex; flex-direction: column; gap: 2px; }
.nav-explorer .nav-tree-children[hidden] { display: none; }
```

- [x] **Step 4: Smoke test**

In `test_build.py` or a small JS-presence assert:

```python
    js = (repo / "apps" / "viewer" / "static" / "viewer.js").read_text(encoding="utf-8")
    assert "walkExplorerItems" in js
```

Run: `python -m pytest apps/viewer/tests/test_build.py -q`

Expected: PASS

- [x] **Step 5: Commit**

```bash
git add apps/viewer/static/viewer.js apps/viewer/static/viewer.css apps/viewer/tests/test_build.py
git commit -m "feat(viewer): nested ontology trees in explorer sidebar"
```

---

### Task 4: Rich ontology class card

**Files:**
- Modify: `apps/viewer/static/viewer.js` (`renderExplorerDetail`)
- Modify: `apps/viewer/static/viewer.css` (optional `.detail-desc-ru`, definition blocks)

**Interfaces:**
- Consumes: explorer item with ontology attributes (`iri` and/or section tags `ontology`/`fibo`)
- Produces: main-pane card with definitions + metadata; DAMS path unchanged when `iri` absent and LinkML slots present

- [x] **Step 1: Detection helper**

```javascript
  function isOntologyExplorerItem(item, section) {
    if (item?.attributes?.iri) return true;
    const tags = section?.tags || [];
    return tags.includes("ontology") || tags.includes("fibo");
  }
```

At start of class rendering in `renderExplorerDetail` (after group branch), if `isOntologyExplorerItem(item, expl)` and `kind !== "enum"`, call `renderOntologyExplorerDetail(mod, expl, item)` and return.

- [x] **Step 2: Implement `renderOntologyExplorerDetail`**

Render `article.detail-card` with:

1. Header: title `label` or `item.title`; if `label_ru` or `aliases`, show `(…)`  
2. Badges: `kind`, `deprecated`  
3. Block **Definition**: `item.description` / `definition`; muted second paragraph for `definition_ru`  
4. Block **Identity** (`dl.detail-meta`): `iri` as `<code>`, `curie`, `source_domain` / `ontology_id`  
5. Block **Taxonomy**: parents / children — split `parents`/`children` attributes if string (`" | "` or comma), else arrays; each id → `makeSpecLink` when in `collectExplorerIds(expl)`, else muted text  
6. Block **Property** (only if domain/range present)  
7. Block **Lifecycle** if `replaced_by`  
8. Block **Backlinks** if `backlinks` truthy (number or list)

Do **not** render LinkML slots table for ontology items.

- [x] **Step 3: Domain group card**

Existing `kind === "group"` branch already shows purpose + members. For ontology groups, member list should include nested roots (top-level children only is OK) with chips that navigate by id. Ensure `purpose` from Task 1 shows. No DAMS `structure_why` required.

- [x] **Step 4: Manual + smoke**

Rebuild viewer:

```bash
python -m moex_publication_viewer.cli build --root .
```

Open Spec → FIBO → domain FND/BE → class with definition → confirm EN+RU definitions and IRI. Confirm glossary/hierarchy still in secondary nav.

Add assert:

```python
    assert "renderOntologyExplorerDetail" in js or "definition_ru" in js
```

- [x] **Step 5: Commit**

```bash
git add apps/viewer/static/viewer.js apps/viewer/static/viewer.css
git commit -m "feat(viewer): rich ontology class cards in explorer"
```

---

### Task 5: Ontology Catalog explorer export (increment 2)

**Files:**
- Modify: `packages/ontology-catalog/src/moex_ontology/publication_export.py`
- Modify: `packages/ontology-catalog/publish.yaml`
- Create/update: `packages/ontology-catalog/publications/ontology_explorer.json` (preview)
- Test: catalog package tests if present; else `apps/viewer/tests/test_normalizers.py` JSON explorer load

**Interfaces:**
- Consumes: `get_entity`, `get_hierarchy`, `list_entities`, `OntologyEntityCard`
- Produces: JSON array of group `PublicationItem`-shaped dicts for `JsonNormalizer` + `type: explorer`

- [x] **Step 1: Export function**

In `publication_export.py`, build nested explorer:

- Group entities by `ontology_id`
- Within each ontology, nest classes using asserted parents that share the same `ontology_id` (mirror `items_to_tree` logic on dicts, or build `PublicationItem`-like dicts then nest)
- Each node attributes include full card fields: `kind`, `iri`, `curie`, `aliases` (joined or list), `definition` as description, `parents`, `children`, `deprecated`, `replaced_by`, `domain`, `range`, `backlinks` count
- Write `ontology_explorer.json`

```python
def _entities_to_explorer(entities, *, index, provider, bindings) -> list[dict[str, Any]]:
    # group by ontology_id; for each entity attach parent iri from card.parents
    # nest; wrap groups id=f"group:{ontology_id}"
    ...
```

Call from `export_preview_json` and add to `written`.

- [x] **Step 2: Regenerate preview JSON**

Run the package’s existing rebuild/export CLI (same command used for other `publications/*.json` — check `packages/ontology-catalog/README.md` / `publish.yaml` header). Commit updated `ontology_explorer.json`.

- [x] **Step 3: Manifest section**

```yaml
  - id: explorer
    title: Entity explorer
    description: Ontologies and asserted class hierarchy with entity cards
    type: explorer
    source:
      format: json
      path: publications/ontology_explorer.json
    key_column: id
    tags:
      - ontology
      - catalog
```

Place first among sections; keep catalog/entities/hierarchy/cards/backlinks.

- [x] **Step 4: JsonNormalizer**

No special-case required if JSON is already nested group dicts with `children` — `records_to_items` / `dict_to_item` already recurse. Verify with a tiny unit test loading fixture JSON as `type: explorer`.

- [x] **Step 5: Build smoke**

```python
    # if ontology-catalog module present in registry:
    cat = next((m for m in registry["modules"] if "ontology-catalog" in m["module_id"]), None)
    if cat:
        assert "explorer" in cat["sections"]
```

Run: `python -m pytest apps/viewer/tests -q`

Expected: PASS

- [x] **Step 6: Commit**

```bash
git add packages/ontology-catalog/src/moex_ontology/publication_export.py \
  packages/ontology-catalog/publish.yaml \
  packages/ontology-catalog/publications/ontology_explorer.json \
  apps/viewer/tests/test_normalizers.py apps/viewer/tests/test_build.py
git commit -m "feat(ontology-catalog): export explorer JSON for Spec viewer"
```

---

### Task 6: End-to-end verification

**Files:** none new (verify only)

- [x] **Step 1: Full viewer tests**

```bash
python -m pytest apps/viewer/tests -q
```

Expected: all PASS

- [x] **Step 2: Rebuild dist**

```bash
python -m moex_publication_viewer.cli build --root .
```

Expected: exit 0; `apps/viewer/dist/index.html` contains `group:FND` and FIBO explorer section

- [x] **Step 3: Manual checklist**

1. Spec → FIBO → explorer domain folder opens purpose card  
2. Nested class under parent selectable  
3. Card shows definition + definition_ru + iri  
4. Secondary nav: Glossary + Class hierarchy still work  
5. Spec → Ontology Catalog → explorer (after Task 5)  
6. DAMS explorer still flat packages + LinkML slots card  

- [x] **Step 4: Commit** only if dist is tracked and intentionally updated; otherwise leave dist untracked per repo convention.

---

## Plan self-review

| Spec requirement | Task |
|------------------|------|
| DAMS-like layout (nav left, card main) | 3, 4 (reuse explorer shell) |
| Both modules, FIBO first | 2 then 5 |
| Hybrid domain + subClassOf | 1, 3, 5 |
| Keep existing sections | 2, 5 (add alongside) |
| Rich card + definitions | 4, 5 export fields |
| Extend explorer, no new type | 1–5 |
| DAMS unchanged | 3 depth-compatible; LinkML path untouched |
| Verification | 1–2 tests, 6 e2e |

No TBD placeholders. Helper name `items_to_domain_explorer` consistent across tasks. Attribute `iri` is the ontology-card detector used in Tasks 4–5.
