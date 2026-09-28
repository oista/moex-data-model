"""Replace class/enum detail rendering with Atlas tabbed cards."""
from pathlib import Path

NEW = r'''
    const badges = [];
    if (kind) badges.push(`<span class="badge-pill">${escapeHtml(kind)}</span>`);
    if (abstract) badges.push(`<span class="badge-pill">abstract</span>`);
    if (isMixin) badges.push(`<span class="badge-pill">mixin</span>`);
    // Keep at most 3 badges in the header row (ADR)
    const headerBadges = badges.slice(0, 3);

    const titleBadge =
      kind === "class"
        ? `<span class="nav-kind ${classKindClassNames(item.attributes)}" aria-hidden="true">C</span> `
        : kind === "enum"
          ? `<span class="nav-kind" aria-hidden="true">E</span> `
          : "";

    card.innerHTML = `
      <header class="detail-head">
        <h1>${titleBadge}${escapeHtml(item.title || item.id)}</h1>
        <div class="badge-row">${headerBadges.join("")}</div>
        <p class="muted">${escapeHtml(fromSchema)}</p>
      </header>
      <p class="detail-desc">${escapeHtml(item.description || "No description.")}</p>
    `;

    function findSourceFileId() {
      const key = item.attributes?.schema_key || item.attributes?.source_file || "";
      if (!key) return null;
      let hit = null;
      walkExplorerItems(expl, (node) => {
        if (hit) return;
        if (node.attributes?.kind !== "source_file") return;
        const path = String(node.attributes?.path || node.title || node.id);
        if (
          path.endsWith(key) ||
          path.includes(key) ||
          node.id.includes(key) ||
          (node.title || "") === key
        ) {
          hit = node.id;
        }
      });
      return hit;
    }

    function openSourceFile() {
      const fileId = findSourceFileId();
      if (!fileId) return;
      const node = nodeForModule(mod.module_id);
      setHash({
        node: node ? node.id : null,
        module: shortModule(mod.module_id),
        section: expl.id,
        item: fileId,
      });
      showModule(mod.module_id, { section: expl.id, item: fileId });
    }

    function renderSourceTab(panel) {
      const fileId = findSourceFileId();
      const sec = document.createElement("section");
      sec.className = "detail-block";
      sec.innerHTML = `<h2>Source</h2>`;
      const dl = document.createElement("dl");
      dl.className = "detail-meta definition-list";
      if (item.attributes?.schema_key) {
        appendMetaRow(dl, "schema_key", String(item.attributes.schema_key));
      }
      if (item.attributes?.from_schema) {
        appendMetaRow(dl, "from_schema", String(item.attributes.from_schema));
      }
      if (item.attributes?.source_file) {
        appendMetaRow(dl, "source_file", String(item.attributes.source_file));
      }
      sec.appendChild(dl);
      if (fileId) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "spec-link";
        btn.textContent = "Open specification file";
        btn.addEventListener("click", openSourceFile);
        sec.appendChild(btn);
      } else {
        const empty = document.createElement("p");
        empty.className = "muted";
        empty.textContent = "No linked specification file in this publication.";
        sec.appendChild(empty);
      }
      panel.appendChild(sec);
    }

    if (kind === "class") {
      const slots = item.attributes?.slots || [];
      const declared = new Set(item.attributes?.declared_slots || []);
      (item.attributes?.attributes_inline || []).forEach((n) => declared.add(n));

      mountTabs(card, [
        {
          id: "overview",
          label: "Overview",
          render(panel) {
            const def = document.createElement("section");
            def.className = "detail-block";
            def.setAttribute("data-renderer", "definition");
            def.innerHTML = `<h2>Definition</h2>
              <p class="detail-desc">${escapeHtml(item.description || "No description.")}</p>`;
            panel.appendChild(def);

            const meta = document.createElement("section");
            meta.className = "detail-block";
            meta.innerHTML = `<h2>Identity</h2>`;
            const dl = document.createElement("dl");
            dl.className = "detail-meta definition-list";
            const classUri = item.attributes?.class_uri;
            if (classUri) {
              const uriSpan = document.createElement("code");
              uriSpan.className = "middle-ellipsis";
              uriSpan.title = classUri;
              uriSpan.textContent = classUri;
              appendMetaRow(dl, "class_uri", uriSpan);
            }
            if (item.attributes?.from_schema) {
              appendMetaRow(dl, "package", String(item.attributes.from_schema));
            }
            if (item.attributes?.schema_key) {
              appendMetaRow(dl, "schema_key", String(item.attributes.schema_key));
            }
            const isA = item.attributes?.is_a;
            if (isA) {
              const wrap = document.createElement("span");
              wrap.appendChild(makeSpecLink(mod, expl, isA, known, "parent"));
              appendMetaRow(dl, "parent", wrap);
            } else if (isMixin) {
              appendMetaRow(dl, "parent", "mixin (no is_a)");
            }
            meta.appendChild(dl);
            panel.appendChild(meta);
          },
        },
        {
          id: "attributes",
          label: "Attributes",
          count: slots.length,
          render(panel) {
            const slotBlock = document.createElement("section");
            slotBlock.className = "detail-block";
            slotBlock.setAttribute("data-renderer", "properties-table");
            slotBlock.innerHTML = `<h2>Attributes</h2>`;
            if (!slots.length) {
              slotBlock.innerHTML += `<p class="muted">No attributes defined for this class.</p>`;
              panel.appendChild(slotBlock);
              return;
            }
            const table = document.createElement("table");
            table.className = "data-table detail-slots";
            table.innerHTML = `<thead><tr>
              <th>Attribute</th><th>Type</th><th>Required</th><th>Multiple</th>
              <th>Declared</th><th>Description</th>
            </tr></thead>`;
            const tbody = document.createElement("tbody");
            slots.forEach((slot) => {
              const tr = document.createElement("tr");
              const nameTd = document.createElement("td");
              nameTd.textContent = slot.name || "";
              const rangeTd = document.createElement("td");
              if (slot.range && known.has(slot.range)) {
                rangeTd.appendChild(makeSpecLink(mod, expl, slot.range, known));
              } else if (slot.name === "glossary_term_refs" && fiboItemExists(slot.range)) {
                rangeTd.appendChild(makeFiboLink(slot.range));
              } else {
                rangeTd.textContent = slot.range || "";
              }
              tr.appendChild(nameTd);
              tr.appendChild(rangeTd);
              [["required", slot.required], ["multivalued", slot.multivalued]].forEach(([, flag]) => {
                const td = document.createElement("td");
                td.textContent = yesBlank(flag) || "No";
                tr.appendChild(td);
              });
              const declTd = document.createElement("td");
              declTd.textContent = declared.has(slot.name) ? "Yes" : (slot.inherited ? "Inherited" : "");
              tr.appendChild(declTd);
              const desc = document.createElement("td");
              desc.textContent = slot.description || "";
              tr.appendChild(desc);
              tbody.appendChild(tr);
            });
            table.appendChild(tbody);
            const scroll = document.createElement("div");
            scroll.className = "table-scroll data-table-shell";
            scroll.appendChild(table);
            slotBlock.appendChild(scroll);
            panel.appendChild(slotBlock);
          },
        },
        {
          id: "relations",
          label: "Relations",
          render(panel) {
            const inh = document.createElement("section");
            inh.className = "detail-block";
            inh.innerHTML = `<h2>Inheritance</h2>`;
            const list = document.createElement("div");
            list.className = "link-row";
            const isA = item.attributes?.is_a;
            if (isA) {
              list.appendChild(makeSpecLink(mod, expl, isA, known, "is_a"));
            } else if (isMixin) {
              list.appendChild(document.createTextNode("mixin (no is_a)"));
            } else {
              list.appendChild(document.createTextNode("No parent"));
            }
            const mixins = item.attributes?.mixins || [];
            if (mixins.length) {
              const mLabel = document.createElement("div");
              mLabel.className = "muted mixin-label";
              mLabel.textContent = "mixins:";
              list.appendChild(mLabel);
              mixins.forEach((m) => list.appendChild(makeSpecLink(mod, expl, m, known, "mixin")));
            }
            inh.appendChild(list);
            panel.appendChild(inh);

            const ranges = document.createElement("section");
            ranges.className = "detail-block";
            ranges.innerHTML = `<h2>Typed references</h2>`;
            const row = document.createElement("div");
            row.className = "link-row";
            const seen = new Set();
            slots.forEach((slot) => {
              if (!slot.range || seen.has(slot.range)) return;
              if (!known.has(slot.range) && !(slot.name === "glossary_term_refs" && fiboItemExists(slot.range))) {
                return;
              }
              seen.add(slot.range);
              if (known.has(slot.range)) {
                row.appendChild(makeSpecLink(mod, expl, slot.range, known));
              } else {
                row.appendChild(makeFiboLink(slot.range));
              }
            });
            if (!row.childNodes.length) {
              ranges.innerHTML += `<p class="muted">No outbound type references.</p>`;
            } else {
              ranges.appendChild(row);
            }
            panel.appendChild(ranges);
          },
        },
        {
          id: "source",
          label: "Source",
          render: renderSourceTab,
        },
      ], { initial: "overview" });
      return card;
    }

    if (kind === "enum") {
      const members = item.children || [];
      mountTabs(card, [
        {
          id: "overview",
          label: "Overview",
          render(panel) {
            const meta = document.createElement("section");
            meta.className = "detail-block";
            meta.innerHTML = `<h2>Identity</h2>`;
            const dl = document.createElement("dl");
            dl.className = "detail-meta definition-list";
            if (item.attributes?.from_schema) {
              appendMetaRow(dl, "package", String(item.attributes.from_schema));
            }
            if (item.attributes?.schema_key) {
              appendMetaRow(dl, "schema_key", String(item.attributes.schema_key));
            }
            appendMetaRow(dl, "members", String(members.length));
            meta.appendChild(dl);
            panel.appendChild(meta);
          },
        },
        {
          id: "members",
          label: "Members",
          count: members.length,
          render(panel) {
            const vals = document.createElement("section");
            vals.className = "detail-block";
            vals.innerHTML = `<h2>Permissible values</h2>`;
            if (!members.length) {
              vals.innerHTML += `<p class="muted">No values defined.</p>`;
              panel.appendChild(vals);
              return;
            }
            const ul = document.createElement("ul");
            ul.className = "detail-name-list";
            members.forEach((v) => {
              const li = document.createElement("li");
              li.innerHTML = `<strong>${escapeHtml(v.title || v.id)}</strong>
                <span class="muted"> — ${escapeHtml(v.description || "")}</span>`;
              ul.appendChild(li);
            });
            vals.appendChild(ul);
            panel.appendChild(vals);
          },
        },
        {
          id: "source",
          label: "Source",
          render: renderSourceTab,
        },
      ], { initial: "overview" });
      return card;
    }

    return card;
  }

  function makeSpecLink'''

p = Path(__file__).resolve().parents[1] / "static" / "viewer.js"
t = p.read_text(encoding="utf-8")
# Unique to LinkML class/enum card inside renderExplorerDetail
marker = '    if (treeRoot) badges.push(`<span class="badge-pill">tree_root</span>`);'
idx = t.index(marker)
# Walk back to the badges = [] that precedes treeRoot in this function
start = t.rindex("    const badges = [];", 0, idx)
end = t.index("  function makeSpecLink", start)
slice_ = t[start:end]
assert "Slots (induced)" in slice_, "expected induced slots block in replaced region"
assert "function renderOntologyExplorerDetail" not in slice_
assert "function renderSourceFileDetail" not in slice_
# NEW ends with "  function makeSpecLink" — keep original signature after name
assert NEW.rstrip().endswith("function makeSpecLink")
t2 = t[:start] + NEW + t[end + len("  function makeSpecLink") :]
assert "function renderSourceFileDetail" in t2
assert "function renderOntologyExplorerDetail" in t2
assert "function renderYamlFold" in t2
assert "mountTabs(card" in t2
assert "Slots (induced)" not in t2
p.write_text(t2, encoding="utf-8")
print("replaced", end - start, "chars; new len", len(t2))
print("ok")
