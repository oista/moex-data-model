(() => {
  const modules = JSON.parse(document.getElementById("publication-data").textContent);
  const searchIndex = JSON.parse(document.getElementById("search-index").textContent);

  const moduleNav = document.getElementById("module-nav");
  const content = document.getElementById("content");
  const searchInput = document.getElementById("global-search");
  const searchResults = document.getElementById("search-results");

  let currentModuleId = null;
  const PAGE_SIZE = 100;

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
    // Accept full module_id or short suffix after last ':'
    const exact = modules.find((m) => m.module_id === moduleId);
    if (exact) return exact.module_id;
    const short = modules.find((m) => m.module_id.endsWith(":" + moduleId) || m.module_id.endsWith(moduleId));
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

  function renderModuleNav() {
    moduleNav.innerHTML = "";
    modules.forEach((mod) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "module-btn" + (mod.module_id === currentModuleId ? " active" : "");
      btn.dataset.moduleId = mod.module_id;
      btn.innerHTML = `<span class="module-icon">${escapeHtml(mod.icon || "📄")}</span>
        <span>${escapeHtml(mod.title)}</span>
        <span class="badge">${mod.sections.length}</span>`;
      btn.addEventListener("click", () => {
        setHash({ module: shortModule(mod.module_id) });
        showModule(mod.module_id);
      });
      moduleNav.appendChild(btn);
    });
  }

  function showModule(moduleId, focus) {
    currentModuleId = moduleKey(moduleId);
    renderModuleNav();
    const mod = modules.find((m) => m.module_id === currentModuleId);
    if (!mod) {
      content.innerHTML = `<p class="muted">Module not found.</p>`;
      return;
    }
    content.innerHTML = "";
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
        if (focus.item) {
          highlightItem(el, focus.item);
        }
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
        body.insertAdjacentHTML("beforeend", `<div class="markdown-body">${section.content || ""}</div>`);
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
    const columns = section.columns?.length
      ? section.columns
      : inferColumns(section.items);

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
      const values = [...new Set(section.items.map((i) => cellValue(i, col)).filter(Boolean))].sort();
      const sel = document.createElement("select");
      sel.innerHTML = `<option value="">${escapeHtml(col)}: all</option>` +
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
        rows = rows.filter((r) =>
          columns.some((c) => cellValue(r, c).toLowerCase().includes(state.query)) ||
          (r.description || "").toLowerCase().includes(state.query)
        );
      }
      if (state.sortCol) {
        const col = state.sortCol;
        const dir = state.sortDir === "asc" ? 1 : -1;
        rows.sort((a, b) => cellValue(a, col).localeCompare(cellValue(b, col), undefined, { numeric: true }) * dir);
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

      const thead = `<thead><tr>${columns.map((c) =>
        `<th data-col="${escapeHtml(c)}">${escapeHtml(c)}${state.sortCol === c ? (state.sortDir === "asc" ? " ▲" : " ▼") : ""}</th>`
      ).join("")}</tr></thead>`;

      const tbody = `<tbody>${slice.map((item) => {
        const cells = columns.map((c) => {
          const raw = cellValue(item, c);
          const long = raw.length > 160;
          const text = long
            ? `<span class="long-text clamped" data-full="${escapeHtml(raw)}">${escapeHtml(raw.slice(0, 160))}…</span>
               <button type="button" class="expand-btn">more</button>`
            : `<span>${escapeHtml(raw)}</span>`;
          return `<td>${text}<span class="cell-actions"><button type="button" class="copy-btn" data-copy="${escapeHtml(raw)}">copy</button></span></td>`;
        }).join("");
        return `<tr data-item-id="${escapeHtml(item.id)}" id="item-${escapeHtml(shortModule(mod.module_id))}-${escapeHtml(section.id)}-${escapeHtml(item.id)}">${cells}</tr>`;
      }).join("")}</tbody>`;

      table.innerHTML = thead + tbody;
      table.querySelectorAll("th").forEach((th) => {
        th.addEventListener("click", () => {
          const col = th.dataset.col;
          if (state.sortCol === col) state.sortDir = state.sortDir === "asc" ? "desc" : "asc";
          else { state.sortCol = col; state.sortDir = "asc"; }
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
      table.querySelectorAll("tr[data-item-id]").forEach((tr) => {
        tr.addEventListener("click", () => {
          setHash({
            module: shortModule(mod.module_id),
            section: section.id,
            item: tr.dataset.itemId,
          });
        });
      });

      // enum children expand: show nested values under description col if enum-table
      if (section.type === "enum-table") {
        slice.forEach((item) => {
          if (!item.children?.length) return;
          const tr = table.querySelector(`tr[data-item-id="${CSS.escape(item.id)}"]`);
          if (!tr) return;
          const sub = document.createElement("tr");
          sub.innerHTML = `<td colspan="${columns.length}"><div class="muted">values: ${
            item.children.map((c) => escapeHtml(c.title || c.id)).join(", ")
          }</div></td>`;
          tr.after(sub);
        });
      }

      pager.innerHTML = `<span class="muted">${rows.length} rows</span>`;
      if (pages > 1) {
        const prev = document.createElement("button");
        prev.type = "button";
        prev.textContent = "Prev";
        prev.disabled = state.page === 0;
        prev.addEventListener("click", () => { state.page--; paint(); });
        const next = document.createElement("button");
        next.type = "button";
        next.textContent = "Next";
        next.disabled = state.page >= pages - 1;
        next.addEventListener("click", () => { state.page++; paint(); });
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
      Object.keys(it.attributes || {}).forEach((k) => cols.add(k));
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
      const values = [...new Set(section.items.map((i) => cellValue(i, col)).filter(Boolean))].sort();
      const sel = document.createElement("select");
      sel.innerHTML = `<option value="">${escapeHtml(col)}: all</option>` +
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
        items = items.filter((i) =>
          (i.title || "").toLowerCase().includes(q) ||
          (i.description || "").toLowerCase().includes(q) ||
          (i.attributes?.label || "").toLowerCase().includes(q) ||
          (i.attributes?.definition || "").toLowerCase().includes(q) ||
          (i.id || "").toLowerCase().includes(q)
        );
      }
      items.sort((a, b) => (a.title || a.id).localeCompare(b.title || b.id));
      const letters = [...new Set(items.map(letterOf))].sort();
      alpha.innerHTML = letters.map((L) => `<a href="#letter-${escapeHtml(L)}">${escapeHtml(L)}</a>`).join(" ");
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
          setHash({ module: shortModule(mod.module_id), section: section.id, item: item.id });
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
        <div class="muted">Path: ${escapeHtml(path.join(" / "))}</div>
        <dl>${Object.entries(item.attributes || {}).map(([k, v]) =>
          `<dt>${escapeHtml(k)}</dt><dd>${escapeHtml(Array.isArray(v) ? v.join(", ") : v)}</dd>`
        ).join("")}</dl>`;
    }

    function makeNode(item, depth, path) {
      const wrap = document.createElement("div");
      wrap.className = "tree-node";
      wrap.dataset.itemId = item.id;
      const row = document.createElement("div");
      const hasKids = item.children && item.children.length;
      const open = depth < 2;
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
        item.children.forEach((c) => kids.appendChild(makeNode(c, depth + 1, path.concat(item.title || item.id))));
        toggle.addEventListener("click", () => {
          kids.hidden = !kids.hidden;
          toggle.textContent = kids.hidden ? "▶" : "▼";
        });
      }
      label.addEventListener("click", () => {
        nodes.querySelectorAll(".tree-label.active").forEach((el) => el.classList.remove("active"));
        label.classList.add("active");
        showDetails(item, path.concat(item.title || item.id));
        setHash({ module: shortModule(mod.module_id), section: section.id, item: item.id });
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
    const hits = searchIndex.filter((h) =>
      (h.title || "").toLowerCase().includes(query) ||
      (h.description || "").toLowerCase().includes(query)
    ).slice(0, 40);

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
        btn.innerHTML = `${labeled}<div class="muted">${escapeHtml(h.module_id)}${h.section_id ? " / " + escapeHtml(h.section_id) : ""}</div>`;
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
    content.querySelectorAll(".section").forEach((s) => s.classList.remove("collapsed"));
  });
  document.getElementById("btn-collapse").addEventListener("click", () => {
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
      setHash({ module: shortModule(modules[0].module_id) });
      showModule(modules[0].module_id);
    } else {
      renderModuleNav();
      content.innerHTML = `<p class="muted">No publication modules found.</p>`;
    }
  }

  window.addEventListener("hashchange", applyRoute);
  renderModuleNav();
  applyRoute();
})();
