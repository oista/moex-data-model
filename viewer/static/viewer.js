(() => {
  const modules = JSON.parse(document.getElementById("publication-data").textContent);
  const searchIndex = JSON.parse(document.getElementById("search-index").textContent);

  const moduleNav = document.getElementById("module-nav");
  const content = document.getElementById("content");
  const searchInput = document.getElementById("global-search");
  const searchResults = document.getElementById("search-results");

  let currentModuleId = null;
  let selectedItemId = null;
  const PAGE_SIZE = 100;
  const openGroups = new Set();

  function parseHash() {
    const raw = (location.hash || "").replace(/^#/, "");
    const params = new URLSearchParams(raw);
    return {
      module: params.get("module"),
      section: params.get("section"),
      item: params.get("item"),
    };
  }

  function setHash({ module, section, item }) {
    const params = new URLSearchParams();
    if (module) params.set("module", module);
    if (section) params.set("section", section);
    if (item) params.set("item", item);
    const next = params.toString();
    if (location.hash.replace(/^#/, "") !== next) {
      location.hash = next;
    }
  }

  function moduleKey(moduleId) {
    const exact = modules.find((m) => m.module_id === moduleId);
    if (exact) return exact.module_id;
    const short = modules.find(
      (m) => m.module_id.endsWith(":" + moduleId) || m.module_id.endsWith(moduleId)
    );
    return short ? short.module_id : moduleId;
  }

  function shortModule(moduleId) {
    const parts = moduleId.split(":");
    return parts[parts.length - 1];
  }

  function escapeHtml(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function cellValue(item, col) {
    if (col === "id") return item.id;
    if (col === "title") return item.title ?? "";
    if (col === "description") return item.description ?? "";
    if (col === "name") return item.attributes?.name ?? item.title ?? item.id;
    const v = item.attributes?.[col];
    if (Array.isArray(v)) return v.join(", ");
    if (v === null || v === undefined) return "";
    if (typeof v === "object") return JSON.stringify(v);
    return String(v);
  }

  function explorerSection(mod) {
    return (mod.sections || []).find((s) => s.type === "explorer") || null;
  }

  function findExplorerItem(section, itemId) {
    if (!section || !itemId) return null;
    for (const group of section.items || []) {
      // Package/group nodes are hierarchy-only — never open as a detail card
      for (const child of group.children || []) {
        if (child.id === itemId) return { item: child, group };
        for (const gc of child.children || []) {
          if (gc.id === itemId) return { item: gc, group, parent: child };
        }
      }
    }
    return null;
  }

  function collectExplorerIds(section) {
    const ids = new Set();
    (section.items || []).forEach((g) => {
      (g.children || []).forEach((c) => ids.add(c.id));
    });
    return ids;
  }

  function fiboItemExists(itemId) {
    const fibo = modules.find((m) => m.module_id.includes("fibo"));
    if (!fibo) return false;
    for (const sec of fibo.sections || []) {
      if (sec.type !== "glossary") continue;
      if ((sec.items || []).some((i) => i.id === itemId)) return true;
    }
    return false;
  }

  function renderModuleNav(focus) {
    moduleNav.innerHTML = "";
    modules.forEach((mod) => {
      const wrap = document.createElement("div");
      wrap.className = "nav-module";
      const active = mod.module_id === currentModuleId;
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "module-btn" + (active ? " active" : "");
      btn.innerHTML = `<span class="module-icon">${escapeHtml(mod.icon || "📄")}</span>
        <span>${escapeHtml(mod.title)}</span>
        <span class="badge">${mod.sections.length}</span>`;
      btn.addEventListener("click", () => {
        const expl = explorerSection(mod);
        setHash({
          module: shortModule(mod.module_id),
          section: expl ? expl.id : (mod.sections[0] && mod.sections[0].id),
        });
        showModule(mod.module_id, { section: expl ? expl.id : null });
      });
      wrap.appendChild(btn);

      if (active) {
        const expl = explorerSection(mod);
        if (expl) {
          const tree = document.createElement("div");
          tree.className = "nav-explorer";
          (expl.items || []).forEach((group) => {
            const gId = group.id;
            // Keep group open if selected item is inside
            if (focus?.item && (group.children || []).some((c) => c.id === focus.item)) {
              openGroups.add(gId);
            }
            const open = openGroups.has(gId);
            const gWrap = document.createElement("div");
            gWrap.className = "nav-group";
            const gBtn = document.createElement("button");
            gBtn.type = "button";
            gBtn.className = "nav-group-btn";
            gBtn.innerHTML = `<span class="tree-toggle">${open ? "▼" : "▶"}</span>
              <span>${escapeHtml(group.title || group.id)}</span>
              <span class="badge">${(group.children || []).length}</span>`;
            const kids = document.createElement("div");
            kids.className = "nav-group-children";
            kids.hidden = !open;
            gBtn.addEventListener("click", (e) => {
              e.stopPropagation();
              if (openGroups.has(gId)) openGroups.delete(gId);
              else openGroups.add(gId);
              renderModuleNav({ item: selectedItemId });
            });
            (group.children || []).forEach((child) => {
              const cBtn = document.createElement("button");
              cBtn.type = "button";
              cBtn.className =
                "nav-item-btn" + (child.id === selectedItemId ? " active" : "");
              const kind = child.attributes?.kind || "class";
              cBtn.innerHTML = `<span class="nav-kind">${escapeHtml(kind === "enum" ? "E" : "C")}</span>
                <span>${escapeHtml(child.title || child.id)}</span>`;
              cBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                setHash({
                  module: shortModule(mod.module_id),
                  section: expl.id,
                  item: child.id,
                });
                showModule(mod.module_id, { section: expl.id, item: child.id });
              });
              kids.appendChild(cBtn);
            });
            gWrap.appendChild(gBtn);
            gWrap.appendChild(kids);
            tree.appendChild(gWrap);
          });
          wrap.appendChild(tree);
        }

        const secondary = document.createElement("div");
        secondary.className = "nav-secondary";
        (mod.sections || [])
          .filter((s) => s.type !== "explorer")
          .forEach((sec) => {
            const sBtn = document.createElement("button");
            sBtn.type = "button";
            sBtn.className =
              "nav-section-btn" +
              (focus?.section === sec.id && !focus?.item ? " active" : "");
            sBtn.textContent = sec.title;
            sBtn.addEventListener("click", (e) => {
              e.stopPropagation();
              selectedItemId = null;
              setHash({
                module: shortModule(mod.module_id),
                section: sec.id,
              });
              showModule(mod.module_id, { section: sec.id });
            });
            secondary.appendChild(sBtn);
          });
        wrap.appendChild(secondary);
      }

      moduleNav.appendChild(wrap);
    });
  }

  function showModule(moduleId, focus) {
    currentModuleId = moduleKey(moduleId);
    const mod = modules.find((m) => m.module_id === currentModuleId);
    if (!mod) {
      content.innerHTML = `<p class="muted">Module not found.</p>`;
      return;
    }

    const expl = explorerSection(mod);
    // Explorer groups stay collapsed by default (openGroups starts empty)

    selectedItemId = focus?.item || null;
    renderModuleNav(focus);

    content.innerHTML = "";
    const crumb = document.createElement("div");
    crumb.className = "breadcrumb muted";

    // Explorer item detail takes priority
    if (expl && focus?.item) {
      const found = findExplorerItem(expl, focus.item);
      if (found) {
        const path = [mod.title];
        if (found.group) path.push(found.group.title || found.group.id);
        path.push(found.item.title || found.item.id);
        crumb.textContent = path.join(" / ");
        content.appendChild(crumb);
        content.appendChild(renderExplorerDetail(mod, expl, found.item, found.group));
        return;
      }
    }

    // Secondary section (or overview) as single focus
    if (focus?.section && (!expl || focus.section !== expl.id || !focus.item)) {
      const section = mod.sections.find((s) => s.id === focus.section);
      if (section && section.type !== "explorer") {
        crumb.textContent = `${mod.title} / ${section.title}`;
        content.appendChild(crumb);
        content.appendChild(renderSection(mod, section));
        return;
      }
    }

    // Default landing for explorer module: package overview (not empty intro)
    if (expl) {
      crumb.textContent = mod.title;
      content.appendChild(crumb);
      const header = document.createElement("div");
      header.className = "module-header";
      header.innerHTML = `<h1>${escapeHtml(mod.icon || "")} ${escapeHtml(mod.title)}</h1>
        <p class="muted">${escapeHtml(mod.description || "")}</p>
        <p>Пакеты схемы спецификации (тело LinkML). Выберите класс слева или ниже.</p>`;
      content.appendChild(header);

      const grid = document.createElement("div");
      grid.className = "explorer-landing";
      (expl.items || []).forEach((group) => {
        const panel = document.createElement("section");
        panel.className = "explorer-package";
        const kids = group.children || [];
        const classes = kids.filter((c) => (c.attributes?.kind || "class") === "class");
        const enums = kids.filter((c) => c.attributes?.kind === "enum");
        panel.innerHTML = `<h2>${escapeHtml(group.title || group.id)}
          <span class="muted">${classes.length} classes${enums.length ? ", " + enums.length + " enums" : ""}</span></h2>`;
        const list = document.createElement("div");
        list.className = "explorer-class-list";
        kids.forEach((child) => {
          const btn = document.createElement("button");
          btn.type = "button";
          btn.className = "spec-link";
          const kind = child.attributes?.kind || "class";
          btn.textContent = (kind === "enum" ? "E · " : "") + (child.title || child.id);
          btn.title = child.description || "";
          btn.addEventListener("click", () => {
            openGroups.add(group.id);
            setHash({
              module: shortModule(mod.module_id),
              section: expl.id,
              item: child.id,
            });
            showModule(mod.module_id, { section: expl.id, item: child.id });
          });
          list.appendChild(btn);
        });
        panel.appendChild(list);
        grid.appendChild(panel);
      });
      content.appendChild(grid);
      return;
    }

    // Modules without explorer: show all sections (previous behaviour)
    const header = document.createElement("div");
    header.className = "module-header";
    header.innerHTML = `<h1>${escapeHtml(mod.icon || "")} ${escapeHtml(mod.title)}</h1>
      <p class="muted">${escapeHtml(mod.description || "")}</p>`;
    content.appendChild(header);
    mod.sections.forEach((section) => {
      content.appendChild(renderSection(mod, section));
    });
    if (focus?.section) {
      const el = content.querySelector(`[data-section-id="${CSS.escape(focus.section)}"]`);
      if (el) {
        el.classList.remove("collapsed");
        el.scrollIntoView({ behavior: "smooth", block: "start" });
        if (focus.item) highlightItem(el, focus.item);
      }
    }
  }

  function highlightItem(sectionEl, itemId) {
    const row = sectionEl.querySelector(`[data-item-id="${CSS.escape(itemId)}"]`);
    if (row) {
      row.classList.add("highlight");
      row.scrollIntoView({ behavior: "smooth", block: "center" });
      setTimeout(() => row.classList.remove("highlight"), 2500);
    }
  }

  function renderExplorerDetail(mod, expl, item, group) {
    const card = document.createElement("article");
    card.className = "detail-card";
    const kind = item.attributes?.kind || "class";
    const abstract = item.attributes?.abstract;
    const fromSchema = item.attributes?.from_schema || item.attributes?.schema_key || "";
    const known = collectExplorerIds(expl);

    const badges = [];
    if (kind) badges.push(`<span class="badge-pill">${escapeHtml(kind)}</span>`);
    if (abstract) badges.push(`<span class="badge-pill">abstract</span>`);
    if (item.attributes?.expressed_in) {
      badges.push(`<span class="badge-pill">expressed in ${escapeHtml(item.attributes.expressed_in)}</span>`);
    }

    card.innerHTML = `
      <header class="detail-head">
        <h1>${escapeHtml(item.title || item.id)}</h1>
        <div class="badge-row">${badges.join("")}</div>
        <p class="muted">${escapeHtml(fromSchema)}</p>
      </header>
      <p class="detail-desc">${escapeHtml(item.description || "No description.")}</p>
    `;

    if (kind === "class") {
      const inh = document.createElement("section");
      inh.className = "detail-block";
      inh.innerHTML = `<h2>Inheritance</h2>`;
      const list = document.createElement("div");
      list.className = "link-row";
      const isA = item.attributes?.is_a;
      if (isA) {
        list.appendChild(makeSpecLink(mod, expl, isA, known, "is_a"));
      } else {
        list.appendChild(document.createTextNode("No parent (root / mixin)"));
      }
      const mixins = item.attributes?.mixins || [];
      if (mixins.length) {
        const mLabel = document.createElement("div");
        mLabel.className = "muted";
        mLabel.style.marginTop = "8px";
        mLabel.textContent = "mixins:";
        list.appendChild(mLabel);
        mixins.forEach((m) => list.appendChild(makeSpecLink(mod, expl, m, known, "mixin")));
      }
      inh.appendChild(list);
      card.appendChild(inh);

      const slots = item.attributes?.slots || [];
      const slotBlock = document.createElement("section");
      slotBlock.className = "detail-block";
      slotBlock.innerHTML = `<h2>Slots (${slots.length})</h2>`;
      if (!slots.length) {
        slotBlock.innerHTML += `<p class="muted">No induced slots.</p>`;
      } else {
        const table = document.createElement("table");
        table.className = "data-table detail-slots";
        table.innerHTML = `<thead><tr>
          <th>name</th><th>range</th><th>required</th><th>multivalued</th><th>description</th>
        </tr></thead>`;
        const tbody = document.createElement("tbody");
        slots.forEach((slot) => {
          const tr = document.createElement("tr");
          const rangeTd = document.createElement("td");
          if (slot.range && known.has(slot.range)) {
            rangeTd.appendChild(makeSpecLink(mod, expl, slot.range, known));
          } else if (slot.name === "glossary_term_refs" && fiboItemExists(slot.range)) {
            rangeTd.appendChild(makeFiboLink(slot.range));
          } else {
            rangeTd.textContent = slot.range || "";
          }
          // glossary_term_refs: show slot name; if FIBO has matching terms user navigates via search
          const nameTd = document.createElement("td");
          nameTd.textContent = slot.name || "";
          if (slot.name === "glossary_term_refs") {
            nameTd.innerHTML =
              `${escapeHtml(slot.name)} <span class="muted">(ontology refs — link when id matches FIBO)</span>`;
          }
          tr.appendChild(nameTd);
          tr.appendChild(rangeTd);
          const req = document.createElement("td");
          req.textContent = slot.required ? "yes" : "";
          tr.appendChild(req);
          const multi = document.createElement("td");
          multi.textContent = slot.multivalued ? "yes" : "";
          tr.appendChild(multi);
          const desc = document.createElement("td");
          desc.textContent = slot.description || "";
          tr.appendChild(desc);
          tbody.appendChild(tr);
        });
        table.appendChild(tbody);
        const scroll = document.createElement("div");
        scroll.className = "table-scroll";
        scroll.appendChild(table);
        slotBlock.appendChild(scroll);
      }
      card.appendChild(slotBlock);
    }

    if (kind === "enum") {
      const vals = document.createElement("section");
      vals.className = "detail-block";
      vals.innerHTML = `<h2>Permissible values</h2>`;
      const ul = document.createElement("ul");
      (item.children || []).forEach((v) => {
        const li = document.createElement("li");
        li.innerHTML = `<strong>${escapeHtml(v.title || v.id)}</strong>
          <span class="muted"> — ${escapeHtml(v.description || "")}</span>`;
        ul.appendChild(li);
      });
      vals.appendChild(ul);
      card.appendChild(vals);
    }

    return card;
  }

  function makeSpecLink(mod, expl, name, known, label) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "spec-link";
    btn.textContent = label ? `${label}: ${name}` : name;
    if (known.has(name)) {
      btn.addEventListener("click", () => {
        setHash({
          module: shortModule(mod.module_id),
          section: expl.id,
          item: name,
        });
        showModule(mod.module_id, { section: expl.id, item: name });
      });
    } else {
      btn.disabled = true;
      btn.classList.add("disabled");
    }
    return btn;
  }

  function makeFiboLink(itemId) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "spec-link";
    btn.textContent = `FIBO: ${itemId}`;
    btn.addEventListener("click", () => {
      setHash({ module: "fibo", section: "glossary", item: itemId });
      showModule("moex:module:fibo", { section: "glossary", item: itemId });
    });
    return btn;
  }

  function renderSection(mod, section) {
    const wrap = document.createElement("section");
    wrap.className = "section" + (section.default_collapsed ? " collapsed" : "");
    wrap.dataset.sectionId = section.id;
    wrap.dataset.sectionType = section.type;

    const head = document.createElement("div");
    head.className = "section-head";
    head.innerHTML = `<h2>${escapeHtml(section.title)}</h2><span class="muted">${escapeHtml(section.type)}</span>`;
    head.addEventListener("click", () => {
      wrap.classList.toggle("collapsed");
      setHash({ module: shortModule(mod.module_id), section: section.id });
    });
    wrap.appendChild(head);

    const body = document.createElement("div");
    body.className = "section-body";
    if (section.description) {
      const d = document.createElement("p");
      d.className = "section-desc";
      d.textContent = section.description;
      body.appendChild(d);
    }

    switch (section.type) {
      case "markdown-doc":
        body.insertAdjacentHTML(
          "beforeend",
          `<div class="markdown-body">${section.content || ""}</div>`
        );
        break;
      case "key-value":
        body.appendChild(renderKeyValue(section));
        break;
      case "tree":
        body.appendChild(renderTree(mod, section));
        break;
      case "glossary":
        body.appendChild(renderGlossary(mod, section));
        break;
      case "explorer":
        body.insertAdjacentHTML(
          "beforeend",
          `<p class="muted">Use the left sidebar to explore schema packages.</p>`
        );
        break;
      default:
        body.appendChild(renderTable(mod, section));
        break;
    }
    wrap.appendChild(body);
    return wrap;
  }

  function renderKeyValue(section) {
    const dl = document.createElement("dl");
    dl.className = "kv-list";
    section.items.forEach((item) => {
      const dt = document.createElement("dt");
      dt.textContent = item.title || item.id;
      const dd = document.createElement("dd");
      dd.textContent = item.attributes?.value ?? item.description ?? "";
      dl.appendChild(dt);
      dl.appendChild(dd);
    });
    return dl;
  }

  function renderTable(mod, section) {
    const root = document.createElement("div");
    const columns = section.columns?.length ? section.columns : inferColumns(section.items);

    const state = {
      sortCol: section.sort_by || null,
      sortDir: section.sort_order || "asc",
      filters: {},
      page: 0,
      query: "",
    };

    const toolbar = document.createElement("div");
    toolbar.className = "section-toolbar";
    const filterSelects = document.createElement("div");
    filterSelects.className = "chips";
    (section.filterable || []).forEach((col) => {
      const values = [
        ...new Set(section.items.map((i) => cellValue(i, col)).filter(Boolean)),
      ].sort();
      const sel = document.createElement("select");
      sel.innerHTML =
        `<option value="">${escapeHtml(col)}: all</option>` +
        values.map((v) => `<option value="${escapeHtml(v)}">${escapeHtml(v)}</option>`).join("");
      sel.addEventListener("change", () => {
        if (sel.value) state.filters[col] = sel.value;
        else delete state.filters[col];
        state.page = 0;
        paint();
      });
      filterSelects.appendChild(sel);
    });
    const q = document.createElement("input");
    q.type = "search";
    q.placeholder = "Filter rows…";
    q.addEventListener("input", () => {
      state.query = q.value.trim().toLowerCase();
      state.page = 0;
      paint();
    });
    toolbar.appendChild(filterSelects);
    toolbar.appendChild(q);
    const chips = document.createElement("div");
    chips.className = "chips";
    toolbar.appendChild(chips);
    root.appendChild(toolbar);

    const scroll = document.createElement("div");
    scroll.className = "table-scroll";
    const table = document.createElement("table");
    table.className = "data-table";
    scroll.appendChild(table);
    root.appendChild(scroll);
    const pager = document.createElement("div");
    pager.className = "pager";
    root.appendChild(pager);

    function filtered() {
      let rows = section.items.slice();
      Object.entries(state.filters).forEach(([col, val]) => {
        rows = rows.filter((r) => cellValue(r, col) === val);
      });
      if (state.query) {
        rows = rows.filter(
          (r) =>
            columns.some((c) => cellValue(r, c).toLowerCase().includes(state.query)) ||
            (r.description || "").toLowerCase().includes(state.query)
        );
      }
      if (state.sortCol) {
        const col = state.sortCol;
        const dir = state.sortDir === "asc" ? 1 : -1;
        rows.sort(
          (a, b) =>
            cellValue(a, col).localeCompare(cellValue(b, col), undefined, { numeric: true }) * dir
        );
      }
      return rows;
    }

    function paint() {
      chips.innerHTML = "";
      Object.entries(state.filters).forEach(([col, val]) => {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "chip";
        chip.innerHTML = `${escapeHtml(col)}=${escapeHtml(val)} <span class="x">×</span>`;
        chip.addEventListener("click", () => {
          delete state.filters[col];
          paint();
        });
        chips.appendChild(chip);
      });

      const rows = filtered();
      const pages = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
      if (state.page >= pages) state.page = pages - 1;
      const slice = rows.slice(state.page * PAGE_SIZE, (state.page + 1) * PAGE_SIZE);

      const thead = `<thead><tr>${columns
        .map(
          (c) =>
            `<th data-col="${escapeHtml(c)}">${escapeHtml(c)}${
              state.sortCol === c ? (state.sortDir === "asc" ? " ▲" : " ▼") : ""
            }</th>`
        )
        .join("")}</tr></thead>`;

      const tbody = `<tbody>${slice
        .map((item) => {
          const cells = columns
            .map((c) => {
              const raw = cellValue(item, c);
              const long = raw.length > 160;
              const text = long
                ? `<span class="long-text clamped" data-full="${escapeHtml(raw)}">${escapeHtml(
                    raw.slice(0, 160)
                  )}…</span>
               <button type="button" class="expand-btn">more</button>`
                : `<span>${escapeHtml(raw)}</span>`;
              return `<td>${text}<span class="cell-actions"><button type="button" class="copy-btn" data-copy="${escapeHtml(
                raw
              )}">copy</button></span></td>`;
            })
            .join("");
          return `<tr data-item-id="${escapeHtml(item.id)}">${cells}</tr>`;
        })
        .join("")}</tbody>`;

      table.innerHTML = thead + tbody;
      table.querySelectorAll("th").forEach((th) => {
        th.addEventListener("click", () => {
          const col = th.dataset.col;
          if (state.sortCol === col) state.sortDir = state.sortDir === "asc" ? "desc" : "asc";
          else {
            state.sortCol = col;
            state.sortDir = "asc";
          }
          paint();
        });
      });
      table.querySelectorAll(".copy-btn").forEach((btn) => {
        btn.addEventListener("click", (e) => {
          e.stopPropagation();
          navigator.clipboard?.writeText(btn.dataset.copy || "");
        });
      });
      table.querySelectorAll(".expand-btn").forEach((btn) => {
        btn.addEventListener("click", (e) => {
          e.stopPropagation();
          const span = btn.previousElementSibling;
          span.classList.toggle("clamped");
          if (!span.classList.contains("clamped")) span.textContent = span.dataset.full;
          else span.textContent = span.dataset.full.slice(0, 160) + "…";
          btn.textContent = span.classList.contains("clamped") ? "more" : "less";
        });
      });

      if (section.type === "enum-table") {
        slice.forEach((item) => {
          if (!item.children?.length) return;
          const tr = table.querySelector(`tr[data-item-id="${CSS.escape(item.id)}"]`);
          if (!tr) return;
          const sub = document.createElement("tr");
          sub.innerHTML = `<td colspan="${columns.length}"><div class="muted">values: ${item.children
            .map((c) => escapeHtml(c.title || c.id))
            .join(", ")}</div></td>`;
          tr.after(sub);
        });
      }

      pager.innerHTML = `<span class="muted">${rows.length} rows</span>`;
      if (pages > 1) {
        const prev = document.createElement("button");
        prev.type = "button";
        prev.textContent = "Prev";
        prev.disabled = state.page === 0;
        prev.addEventListener("click", () => {
          state.page--;
          paint();
        });
        const next = document.createElement("button");
        next.type = "button";
        next.textContent = "Next";
        next.disabled = state.page >= pages - 1;
        next.addEventListener("click", () => {
          state.page++;
          paint();
        });
        pager.appendChild(prev);
        pager.appendChild(document.createTextNode(` ${state.page + 1} / ${pages} `));
        pager.appendChild(next);
      }
    }

    paint();
    return root;
  }

  function inferColumns(items) {
    const cols = new Set(["name", "title", "description"]);
    items.slice(0, 20).forEach((it) => {
      Object.keys(it.attributes || {}).forEach((k) => {
        if (k !== "slots" && k !== "kind") cols.add(k);
      });
    });
    return [...cols].filter((c) => items.some((i) => cellValue(i, c)));
  }

  function renderGlossary(mod, section) {
    const root = document.createElement("div");
    const toolbar = document.createElement("div");
    toolbar.className = "section-toolbar";
    const alpha = document.createElement("div");
    alpha.className = "alpha-index";
    const list = document.createElement("div");
    list.className = "glossary-list";
    const state = { filters: {}, query: "" };

    (section.filterable || []).forEach((col) => {
      const values = [
        ...new Set(section.items.map((i) => cellValue(i, col)).filter(Boolean)),
      ].sort();
      const sel = document.createElement("select");
      sel.innerHTML =
        `<option value="">${escapeHtml(col)}: all</option>` +
        values.map((v) => `<option value="${escapeHtml(v)}">${escapeHtml(v)}</option>`).join("");
      sel.addEventListener("change", () => {
        if (sel.value) state.filters[col] = sel.value;
        else delete state.filters[col];
        paint();
      });
      toolbar.appendChild(sel);
    });

    const filter = document.createElement("input");
    filter.type = "search";
    filter.placeholder = "Search terms…";
    filter.addEventListener("input", () => {
      state.query = filter.value.trim().toLowerCase();
      paint();
    });
    toolbar.appendChild(filter);
    root.appendChild(toolbar);
    root.appendChild(alpha);
    root.appendChild(list);

    function letterOf(item) {
      const t = (item.title || item.attributes?.label || item.id || "?").trim();
      return t.charAt(0).toUpperCase();
    }

    function paint() {
      let items = section.items.slice();
      Object.entries(state.filters).forEach(([col, val]) => {
        items = items.filter((r) => cellValue(r, col) === val);
      });
      if (state.query) {
        const q = state.query;
        items = items.filter(
          (i) =>
            (i.title || "").toLowerCase().includes(q) ||
            (i.description || "").toLowerCase().includes(q) ||
            (i.attributes?.label || "").toLowerCase().includes(q) ||
            (i.attributes?.definition || "").toLowerCase().includes(q) ||
            (i.id || "").toLowerCase().includes(q)
        );
      }
      items.sort((a, b) => (a.title || a.id).localeCompare(b.title || b.id));
      const letters = [...new Set(items.map(letterOf))].sort();
      alpha.innerHTML = letters
        .map((L) => `<a href="#letter-${escapeHtml(L)}">${escapeHtml(L)}</a>`)
        .join(" ");
      list.innerHTML = "";
      let current = null;
      items.forEach((item) => {
        const L = letterOf(item);
        if (L !== current) {
          current = L;
          const h = document.createElement("div");
          h.className = "glossary-letter";
          h.id = `letter-${L}`;
          h.textContent = L;
          list.appendChild(h);
        }
        const card = document.createElement("div");
        card.className = "glossary-card";
        card.dataset.itemId = item.id;
        const title = item.attributes?.label || item.title || item.id;
        const def = item.attributes?.definition || item.description || "";
        const domain = item.attributes?.source_domain || "";
        card.innerHTML = `<h3>${escapeHtml(title)}</h3>
          <p>${escapeHtml(def)}</p>
          <div class="muted">${escapeHtml(item.id)}${domain ? " · " + escapeHtml(domain) : ""}</div>`;
        card.addEventListener("click", () => {
          setHash({
            module: shortModule(mod.module_id),
            section: section.id,
            item: item.id,
          });
        });
        list.appendChild(card);
      });
    }
    paint();
    return root;
  }

  function renderTree(mod, section) {
    const layout = document.createElement("div");
    layout.className = "tree-layout";
    const nodes = document.createElement("div");
    nodes.className = "tree-nodes";
    const details = document.createElement("aside");
    details.className = "tree-details muted";
    details.textContent = "Select a node";
    layout.appendChild(nodes);
    layout.appendChild(details);

    function showDetails(item, path) {
      details.classList.remove("muted");
      details.innerHTML = `<h3>${escapeHtml(item.title || item.id)}</h3>
        <p>${escapeHtml(item.description || "")}</p>
        <div class="muted">Path: ${escapeHtml(path.join(" / "))}</div>`;
    }

    function makeNode(item, depth, path) {
      const wrap = document.createElement("div");
      wrap.className = "tree-node";
      const hasKids = item.children && item.children.length;
      const open = depth < 2;
      const row = document.createElement("div");
      const toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = "tree-toggle";
      toggle.textContent = hasKids ? (open ? "▼" : "▶") : "·";
      const label = document.createElement("button");
      label.type = "button";
      label.className = "tree-label";
      label.textContent = item.title || item.id;
      row.appendChild(toggle);
      row.appendChild(label);
      wrap.appendChild(row);
      const kids = document.createElement("div");
      kids.className = "children";
      if (!open) kids.hidden = true;
      if (hasKids) {
        item.children.forEach((c) =>
          kids.appendChild(makeNode(c, depth + 1, path.concat(item.title || item.id)))
        );
        toggle.addEventListener("click", () => {
          kids.hidden = !kids.hidden;
          toggle.textContent = kids.hidden ? "▶" : "▼";
        });
      }
      label.addEventListener("click", () => {
        showDetails(item, path.concat(item.title || item.id));
        setHash({
          module: shortModule(mod.module_id),
          section: section.id,
          item: item.id,
        });
      });
      wrap.appendChild(kids);
      return wrap;
    }

    section.items.forEach((item) => nodes.appendChild(makeNode(item, 0, [])));
    return layout;
  }

  function runSearch(q) {
    const query = q.trim().toLowerCase();
    if (!query) {
      searchResults.classList.add("hidden");
      searchResults.innerHTML = "";
      return;
    }
    const hits = searchIndex
      .filter(
        (h) =>
          (h.title || "").toLowerCase().includes(query) ||
          (h.description || "").toLowerCase().includes(query)
      )
      .slice(0, 40);

    if (!hits.length) {
      searchResults.innerHTML = `<div class="search-hit muted">No results</div>`;
      searchResults.classList.remove("hidden");
      return;
    }

    const groups = { module: [], section: [], item: [] };
    hits.forEach((h) => groups[h.kind]?.push(h));
    searchResults.innerHTML = "";
    ["module", "section", "item"].forEach((kind) => {
      if (!groups[kind].length) return;
      const title = document.createElement("div");
      title.className = "muted";
      title.style.padding = "6px 12px";
      title.textContent = kind + "s";
      searchResults.appendChild(title);
      groups[kind].forEach((h) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "search-hit";
        const labeled = escapeHtml(h.title).replace(
          new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "ig"),
          "<mark>$1</mark>"
        );
        btn.innerHTML = `${labeled}<div class="muted">${escapeHtml(h.module_id)}${
          h.section_id ? " / " + escapeHtml(h.section_id) : ""
        }</div>`;
        btn.addEventListener("click", () => {
          searchResults.classList.add("hidden");
          setHash({
            module: shortModule(h.module_id),
            section: h.section_id || null,
            item: h.item_id || null,
          });
          showModule(h.module_id, { section: h.section_id, item: h.item_id });
        });
        searchResults.appendChild(btn);
      });
    });
    searchResults.classList.remove("hidden");
  }

  searchInput.addEventListener("input", () => runSearch(searchInput.value));
  document.addEventListener("click", (e) => {
    if (!searchResults.contains(e.target) && e.target !== searchInput) {
      searchResults.classList.add("hidden");
    }
  });

  document.getElementById("btn-theme").addEventListener("click", () => {
    const html = document.documentElement;
    const next = html.dataset.theme === "dark" ? "light" : "dark";
    html.dataset.theme = next;
    localStorage.setItem("moex-viewer-theme", next);
  });
  document.getElementById("btn-expand").addEventListener("click", () => {
    const mod = modules.find((m) => m.module_id === currentModuleId);
    const expl = mod && explorerSection(mod);
    if (expl) {
      (expl.items || []).forEach((g) => openGroups.add(g.id));
      renderModuleNav({ item: selectedItemId });
    }
    content.querySelectorAll(".section").forEach((s) => s.classList.remove("collapsed"));
  });
  document.getElementById("btn-collapse").addEventListener("click", () => {
    openGroups.clear();
    renderModuleNav({ item: selectedItemId });
    content.querySelectorAll(".section").forEach((s) => s.classList.add("collapsed"));
  });
  document.getElementById("btn-copy-link").addEventListener("click", () => {
    navigator.clipboard?.writeText(location.href);
  });

  const savedTheme = localStorage.getItem("moex-viewer-theme");
  if (savedTheme) document.documentElement.dataset.theme = savedTheme;

  function applyRoute() {
    const { module, section, item } = parseHash();
    if (module) {
      showModule(moduleKey(module), { section, item });
    } else if (modules[0]) {
      const expl = explorerSection(modules[0]);
      setHash({
        module: shortModule(modules[0].module_id),
        section: expl ? expl.id : null,
      });
      showModule(modules[0].module_id, { section: expl ? expl.id : null });
    } else {
      renderModuleNav();
      content.innerHTML = `<p class="muted">No publication modules found.</p>`;
    }
  }

  window.addEventListener("hashchange", applyRoute);
  applyRoute();
})();
