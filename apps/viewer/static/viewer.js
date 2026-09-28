(() => {
  const modules = JSON.parse(document.getElementById("publication-data").textContent);
  const catalogRaw = JSON.parse(
    document.getElementById("architecture-catalog").textContent
  );
  const catalogNodes = (catalogRaw && catalogRaw.nodes) || [];
  const searchIndex = JSON.parse(document.getElementById("search-index").textContent);
  const viewerConfig = (() => {
    const el = document.getElementById("viewer-config");
    if (!el) return {};
    try {
      return JSON.parse(el.textContent);
    } catch {
      return {};
    }
  })();

  const DEFAULT_CLASS_COLORS = {
    roles: { plain: "#3d8f6e", mixin: "#3d6eb5", abstract: "#2e8fad" },
    corner: { has_mixins: "#3d6eb5" },
  };
  const classKindColors = {
    roles: {
      ...DEFAULT_CLASS_COLORS.roles,
      ...(viewerConfig.class_kind_colors?.roles || {}),
    },
    corner: {
      ...DEFAULT_CLASS_COLORS.corner,
      ...(viewerConfig.class_kind_colors?.corner || {}),
    },
  };

  (function applyClassKindCssVars() {
    const root = document.documentElement;
    root.style.setProperty("--class-color-plain", classKindColors.roles.plain);
    root.style.setProperty("--class-color-mixin", classKindColors.roles.mixin);
    root.style.setProperty("--class-color-abstract", classKindColors.roles.abstract);
    root.style.setProperty(
      "--class-color-has-mixins",
      classKindColors.corner.has_mixins || classKindColors.roles.mixin
    );
  })();

  function classRole(attrs) {
    if (!attrs || attrs.kind === "enum") return null;
    if (attrs.mixin) return "mixin";
    if (attrs.abstract) return "abstract";
    return "plain";
  }

  function classHasMixins(attrs) {
    const mixins = attrs?.mixins;
    return Array.isArray(mixins) && mixins.length > 0;
  }

  function classKindClassNames(attrs) {
    const role = classRole(attrs);
    if (!role) return "";
    let cls = `kind-${role}`;
    if (classHasMixins(attrs)) cls += " has-mixins-corner";
    return cls;
  }

  const moduleNav = document.getElementById("module-nav");
  const content = document.getElementById("content");
  const searchInput = document.getElementById("global-search");
  const searchResults = document.getElementById("search-results");

  let currentModuleId = null;
  let currentNodeId = null;
  let selectedItemId = null;
  const PAGE_SIZE = 100;
  const openGroups = new Set();

  function parseHash() {
    const raw = (location.hash || "").replace(/^#/, "");
    const params = new URLSearchParams(raw);
    return {
      node: params.get("node"),
      module: params.get("module"),
      section: params.get("section"),
      item: params.get("item"),
    };
  }

  function setHash({ node, module, section, item }) {
    const params = new URLSearchParams();
    if (node) params.set("node", node);
    if (module) params.set("module", module);
    if (section) params.set("section", section);
    if (item) params.set("item", item);
    const next = params.toString();
    if (location.hash.replace(/^#/, "") !== next) {
      location.hash = next;
    }
  }

  function catalogNode(id) {
    return catalogNodes.find((n) => n.id === id) || null;
  }

  function nodeForModule(moduleId) {
    const full = moduleKey(moduleId);
    return catalogNodes.find((n) => n.module_id === full) || null;
  }

  function implementationsOf(specId) {
    return catalogNodes
      .filter((n) => n.role === "specification_implementation" && n.conforms_to === specId)
      .sort((a, b) => (a.order || 0) - (b.order || 0) || a.title.localeCompare(b.title));
  }

  function rootSpecifications() {
    return catalogNodes
      .filter((n) => n.role === "reference_specification")
      .sort((a, b) => (a.order || 0) - (b.order || 0) || a.title.localeCompare(b.title));
  }

  function unattachedImplementations() {
    return catalogNodes
      .filter((n) => n.role === "specification_implementation" && !n.conforms_to)
      .sort((a, b) => (a.order || 0) - (b.order || 0) || a.title.localeCompare(b.title));
  }

  function otherModules() {
    const linked = new Set(
      catalogNodes.map((n) => n.module_id).filter(Boolean)
    );
    return modules.filter((m) => !linked.has(m.module_id));
  }

  function defaultFocusForModule(mod) {
    if (!mod) return {};
    const expl = explorerSection(mod);
    return {
      section: expl ? expl.id : (mod.sections[0] && mod.sections[0].id) || null,
    };
  }

  function navigateToNode(node, focus) {
    currentNodeId = node.id;
    if (node.module_id) {
      const mod = modules.find((m) => m.module_id === node.module_id);
      const f = focus || defaultFocusForModule(mod);
      setHash({
        node: node.id,
        module: shortModule(node.module_id),
        section: f.section || null,
        item: f.item || null,
      });
      showModule(node.module_id, f);
      return;
    }
    setHash({ node: node.id });
    showCatalogCard(node);
  }

  function navigateToModule(moduleId, focus) {
    const node = nodeForModule(moduleId);
    if (node) {
      navigateToNode(node, focus);
      return;
    }
    currentNodeId = null;
    const mod = modules.find((m) => m.module_id === moduleKey(moduleId));
    const f = focus || defaultFocusForModule(mod);
    setHash({
      module: shortModule(moduleKey(moduleId)),
      section: f.section || null,
      item: f.item || null,
    });
    showModule(moduleId, f);
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

  function walkExplorerItems(section, visit) {
    function walk(nodes, group, ancestors) {
      for (const node of nodes || []) {
        visit(node, group, ancestors);
        const nextGroup =
          node.attributes?.kind === "group" ? node : group;
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

  function countExplorerClasses(node) {
    let n = 0;
    walkExplorerItems({ items: node.children || [] }, (child) => {
      const k = child.attributes?.kind;
      if (k === "group" || k === "enum_value") return;
      n += 1;
    });
    return n;
  }

  function descendantHasId(node, itemId) {
    if (!itemId || !node) return false;
    if (node.id === itemId) return true;
    return (node.children || []).some((c) => descendantHasId(c, itemId));
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

  function appendPublicationSubtree(wrap, mod, focus) {
    const expl = explorerSection(mod);
    if (expl) {
      const tree = document.createElement("div");
      tree.className = "nav-explorer";

      if (focus?.item) {
        const focused = findExplorerItem(expl, focus.item);
        if (focused) {
          (focused.ancestors || []).forEach((a) => openGroups.add(a.id));
          if (focused.group) openGroups.add(focused.group.id);
          openGroups.add(focused.item.id);
        }
      }

      function openExplorerItem(itemId) {
        const node = nodeForModule(mod.module_id);
        setHash({
          node: node ? node.id : null,
          module: shortModule(mod.module_id),
          section: expl.id,
          item: itemId,
        });
        if (node) currentNodeId = node.id;
        showModule(mod.module_id, { section: expl.id, item: itemId });
      }

      function appendNavClassNode(parentEl, node, depth) {
        const hasKids = node.children && node.children.length;
        const open = openGroups.has(node.id);
        const wrapNode = document.createElement("div");
        wrapNode.className = "nav-tree-node";
        if (depth) wrapNode.style.marginLeft = `${Math.min(depth, 6) * 8}px`;

        const row = document.createElement("div");
        row.className = "nav-tree-row";

        const toggle = document.createElement("button");
        toggle.type = "button";
        toggle.className = "tree-toggle";
        toggle.textContent = hasKids ? (open ? "▼" : "▶") : "·";
        toggle.addEventListener("click", (e) => {
          e.stopPropagation();
          if (!hasKids) return;
          if (openGroups.has(node.id)) openGroups.delete(node.id);
          else openGroups.add(node.id);
          renderModuleNav({ item: selectedItemId, section: expl.id });
        });

        const label = document.createElement("button");
        label.type = "button";
        label.className =
          "nav-item-btn" + (node.id === selectedItemId ? " active" : "");
        const kind = node.attributes?.kind || "class";
        const kindClasses =
          kind === "class" ? classKindClassNames(node.attributes) : "";
        const mark =
          kind === "enum" ? "E" : kind === "individual" ? "I" : "C";
        label.innerHTML = `<span class="nav-kind ${kindClasses}">${escapeHtml(mark)}</span>
          <span>${escapeHtml(node.title || node.id)}</span>`;
        label.addEventListener("click", (e) => {
          e.stopPropagation();
          if (hasKids) openGroups.add(node.id);
          openExplorerItem(node.id);
        });

        row.appendChild(toggle);
        row.appendChild(label);
        wrapNode.appendChild(row);

        if (hasKids) {
          const kids = document.createElement("div");
          kids.className = "nav-tree-children";
          kids.hidden = !open;
          node.children.forEach((c) =>
            appendNavClassNode(kids, c, depth + 1)
          );
          wrapNode.appendChild(kids);
        }
        parentEl.appendChild(wrapNode);
      }

      (expl.items || []).forEach((group) => {
        const gId = group.id;
        if (focus?.item && descendantHasId(group, focus.item)) {
          openGroups.add(gId);
        }
        const open = openGroups.has(gId);
        const gWrap = document.createElement("div");
        gWrap.className = "nav-group";
        const gBtn = document.createElement("button");
        gBtn.type = "button";
        gBtn.className =
          "nav-group-btn" + (gId === selectedItemId ? " active" : "");
        const toggle = document.createElement("span");
        toggle.className = "tree-toggle";
        toggle.textContent = open ? "▼" : "▶";
        toggle.addEventListener("click", (e) => {
          e.stopPropagation();
          if (openGroups.has(gId)) openGroups.delete(gId);
          else openGroups.add(gId);
          renderModuleNav({ item: selectedItemId, section: expl.id });
        });
        const titleSpan = document.createElement("span");
        titleSpan.textContent = group.title || group.id;
        const badge = document.createElement("span");
        badge.className = "badge";
        const classCount =
          group.attributes?.class_count ?? countExplorerClasses(group);
        badge.textContent = String(classCount);
        gBtn.appendChild(toggle);
        gBtn.appendChild(titleSpan);
        gBtn.appendChild(badge);
        const kids = document.createElement("div");
        kids.className = "nav-group-children";
        kids.hidden = !open;
        gBtn.addEventListener("click", (e) => {
          e.stopPropagation();
          openGroups.add(gId);
          openExplorerItem(gId);
        });
        (group.children || []).forEach((child) => {
          appendNavClassNode(kids, child, 0);
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
          const node = nodeForModule(mod.module_id);
          if (node) currentNodeId = node.id;
          // Hash only — hashchange → applyRoute → showModule (avoid double render)
          setHash({
            node: node ? node.id : null,
            module: shortModule(mod.module_id),
            section: sec.id,
          });
        });
        secondary.appendChild(sBtn);
      });
    if (secondary.childNodes.length) wrap.appendChild(secondary);
  }

  function makeCatalogBtn(node, { nested } = {}) {
    const active = node.id === currentNodeId;
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className =
      (nested ? "nav-impl-btn" : "module-btn") + (active ? " active" : "");
    const roleLabel =
      node.role === "reference_specification" ? "Spec" : "Impl";
    btn.innerHTML = `<span class="role-pill">${roleLabel}</span>
      <span>${escapeHtml(node.title)}</span>
      ${node.version ? `<span class="badge">${escapeHtml(node.version)}</span>` : ""}`;
    btn.addEventListener("click", () => navigateToNode(node));
    return btn;
  }

  function renderModuleNav(focus) {
    moduleNav.innerHTML = "";

    if (!catalogNodes.length) {
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
        btn.addEventListener("click", () => navigateToModule(mod.module_id));
        wrap.appendChild(btn);
        if (active) appendPublicationSubtree(wrap, mod, focus);
        moduleNav.appendChild(wrap);
      });
      return;
    }

    rootSpecifications().forEach((spec) => {
      const wrap = document.createElement("div");
      wrap.className = "nav-module";
      wrap.appendChild(makeCatalogBtn(spec));

      const impls = implementationsOf(spec.id);
      if (impls.length) {
        const kids = document.createElement("div");
        kids.className = "nav-impl-children";
        impls.forEach((impl) => kids.appendChild(makeCatalogBtn(impl, { nested: true })));
        wrap.appendChild(kids);
      }

      const activeHere =
        currentNodeId === spec.id ||
        impls.some((i) => i.id === currentNodeId) ||
        (spec.module_id && spec.module_id === currentModuleId);
      if (activeHere && spec.module_id && currentNodeId === spec.id) {
        const mod = modules.find((m) => m.module_id === spec.module_id);
        if (mod) appendPublicationSubtree(wrap, mod, focus);
      } else if (
        activeHere &&
        currentNodeId &&
        catalogNode(currentNodeId)?.module_id === currentModuleId &&
        catalogNode(currentNodeId)?.conforms_to === spec.id
      ) {
        const mod = modules.find((m) => m.module_id === currentModuleId);
        if (mod) appendPublicationSubtree(wrap, mod, focus);
      }

      moduleNav.appendChild(wrap);
    });

    const orphans = unattachedImplementations();
    if (orphans.length) {
      const label = document.createElement("div");
      label.className = "nav-group-label muted";
      label.textContent = "Implementations without specification";
      moduleNav.appendChild(label);
      orphans.forEach((impl) => {
        const wrap = document.createElement("div");
        wrap.className = "nav-module";
        wrap.appendChild(makeCatalogBtn(impl));
        if (currentNodeId === impl.id && impl.module_id) {
          const mod = modules.find((m) => m.module_id === impl.module_id);
          if (mod) appendPublicationSubtree(wrap, mod, focus);
        }
        moduleNav.appendChild(wrap);
      });
    }

    const others = otherModules();
    if (others.length) {
      const label = document.createElement("div");
      label.className = "nav-group-label muted";
      label.textContent = "Other publications";
      moduleNav.appendChild(label);
      others.forEach((mod) => {
        const wrap = document.createElement("div");
        wrap.className = "nav-module";
        const active = mod.module_id === currentModuleId && !currentNodeId;
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "module-btn" + (active ? " active" : "");
        btn.innerHTML = `<span class="module-icon">${escapeHtml(mod.icon || "📄")}</span>
          <span>${escapeHtml(mod.title)}</span>
          <span class="badge">${mod.sections.length}</span>`;
        btn.addEventListener("click", () => navigateToModule(mod.module_id));
        wrap.appendChild(btn);
        if (mod.module_id === currentModuleId && !currentNodeId) {
          appendPublicationSubtree(wrap, mod, focus);
        }
        moduleNav.appendChild(wrap);
      });
    }
  }

  function renderArchitectureCrumb(node) {
    const crumb = document.createElement("div");
    crumb.className = "breadcrumb";
    if (!node) {
      crumb.classList.add("muted");
      return crumb;
    }
    const parts = [];
    if (node.role === "specification_implementation" && node.conforms_to) {
      const parent = catalogNode(node.conforms_to);
      if (parent) {
        const link = document.createElement("button");
        link.type = "button";
        link.className = "crumb-link";
        link.textContent = parent.title;
        link.addEventListener("click", () => navigateToNode(parent));
        parts.push(link);
      }
    }
    const current = document.createElement("span");
    current.className = "muted";
    current.textContent = node.title;
    parts.push(current);

    parts.forEach((el, i) => {
      if (i > 0) {
        const sep = document.createElement("span");
        sep.className = "muted";
        sep.textContent = " / ";
        crumb.appendChild(sep);
      }
      crumb.appendChild(el);
    });
    return crumb;
  }

  function renderImplementationsBlock(spec) {
    const block = document.createElement("section");
    block.className = "arch-block";
    const impls = implementationsOf(spec.id);
    block.innerHTML = `<h2>Implementations</h2>`;
    if (!impls.length) {
      const empty = document.createElement("p");
      empty.className = "muted";
      empty.textContent = "No implementations registered for this specification.";
      block.appendChild(empty);
      return block;
    }
    const list = document.createElement("div");
    list.className = "impl-list";
    impls.forEach((impl) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "spec-link";
      btn.innerHTML = `<strong>${escapeHtml(impl.title)}</strong>${
        impl.version ? ` <span class="muted">${escapeHtml(impl.version)}</span>` : ""
      }`;
      btn.addEventListener("click", () => navigateToNode(impl));
      list.appendChild(btn);
    });
    block.appendChild(list);
    return block;
  }

  function findOntologyCatalogHit(nodeId) {
    const catalogMod = modules.find((m) => m.module_id.includes("ontology-catalog"));
    if (!catalogMod) return null;
    for (const sec of catalogMod.sections || []) {
      const hit = (sec.items || []).find((i) => i.id === nodeId);
      if (hit) return { module: catalogMod, section: sec, item: hit };
    }
    return null;
  }

  function showCatalogCard(node) {
    currentModuleId = null;
    selectedItemId = null;
    renderModuleNav();
    content.innerHTML = "";
    content.appendChild(renderArchitectureCrumb(node));

    const card = document.createElement("article");
    card.className = "detail-card";
    const badges = [
      `<span class="badge-pill">${
        node.role === "reference_specification" ? "Specification" : "Implementation"
      }</span>`,
    ];
    if (node.expressed_in) {
      badges.push(
        `<span class="badge-pill">expressed in ${escapeHtml(node.expressed_in)}</span>`
      );
    }
    if (node.version) {
      badges.push(`<span class="badge-pill">${escapeHtml(node.version)}</span>`);
    }
    card.innerHTML = `
      <header class="detail-head">
        <h1>${escapeHtml(node.title)}</h1>
        <div class="badge-row">${badges.join("")}</div>
        <p class="muted">${escapeHtml(node.id)}</p>
      </header>
      <p class="detail-desc">${escapeHtml(node.description || "No publication body for this node yet.")}</p>
    `;
    content.appendChild(card);

    if (node.role === "reference_specification") {
      content.appendChild(renderImplementationsBlock(node));
    }

    const hit = findOntologyCatalogHit(node.id);
    if (hit) {
      const linkBlock = document.createElement("section");
      linkBlock.className = "arch-block";
      linkBlock.innerHTML = `<h2>Related publication</h2>`;
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "spec-link";
      btn.textContent = `Open in ${hit.module.title}`;
      btn.addEventListener("click", () => {
        currentNodeId = null;
        navigateToModule(hit.module.module_id, {
          section: hit.section.id,
          item: hit.item.id,
        });
      });
      linkBlock.appendChild(btn);
      content.appendChild(linkBlock);
    }
  }

  function prependArchitectureChrome(mod, focus) {
    const node =
      (currentNodeId && catalogNode(currentNodeId)) || nodeForModule(mod.module_id);
    if (!node) return null;

    const chrome = document.createElement("div");
    chrome.className = "arch-chrome";
    chrome.appendChild(renderArchitectureCrumb(node));

    const meta = document.createElement("div");
    meta.className = "arch-meta";
    const badges = [
      `<span class="badge-pill">${
        node.role === "reference_specification" ? "Specification" : "Implementation"
      }</span>`,
    ];
    if (node.expressed_in) {
      badges.push(
        `<span class="badge-pill">expressed in ${escapeHtml(node.expressed_in)}</span>`
      );
    }
    meta.innerHTML = `<div class="badge-row">${badges.join("")}</div>`;
    chrome.appendChild(meta);

    if (
      node.role === "reference_specification" &&
      !focus?.item &&
      (!focus?.section || focus.section === explorerSection(mod)?.id)
    ) {
      chrome.appendChild(renderImplementationsBlock(node));
    }
    return chrome;
  }

  function showModule(moduleId, focus) {
    currentModuleId = moduleKey(moduleId);
    const mod = modules.find((m) => m.module_id === currentModuleId);
    if (!mod) {
      content.innerHTML = `<p class="muted">Module not found.</p>`;
      return;
    }

    if (!currentNodeId || catalogNode(currentNodeId)?.module_id !== currentModuleId) {
      const linked = nodeForModule(currentModuleId);
      if (linked) currentNodeId = linked.id;
    }

    const expl = explorerSection(mod);
    selectedItemId = focus?.item || null;
    renderModuleNav(focus);

    content.innerHTML = "";
    const chrome = prependArchitectureChrome(mod, focus);
    if (chrome) content.appendChild(chrome);

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
        if (focus.item) highlightItem(content, focus.item);
        return;
      }
    }

    // Default landing for explorer module: package overview (not empty intro)
    if (expl) {
      crumb.textContent = mod.title;
      content.appendChild(crumb);
      const header = document.createElement("div");
      header.className = "module-header";
      const ontoExpl =
        (expl.tags || []).includes("ontology") ||
        (expl.tags || []).includes("fibo");
      const landingHint = ontoExpl
        ? "Домены и иерархия классов. Выберите класс слева или ниже."
        : "Пакеты схемы спецификации (тело LinkML). Выберите класс слева или ниже.";
      header.innerHTML = `<h1>${escapeHtml(mod.icon || "")} ${escapeHtml(mod.title)}</h1>
        <p class="muted">${escapeHtml(mod.description || "")}</p>
        <p>${landingHint}</p>`;
      content.appendChild(header);

      const grid = document.createElement("div");
      grid.className = "explorer-landing";
      (expl.items || []).forEach((group) => {
        const panel = document.createElement("section");
        panel.className = "explorer-package";
        const kids = group.children || [];
        const classes = kids.filter((c) => (c.attributes?.kind || "class") === "class");
        const enums = kids.filter((c) => c.attributes?.kind === "enum");
        const h2 = document.createElement("h2");
        const titleBtn = document.createElement("button");
        titleBtn.type = "button";
        titleBtn.className = "package-title-link";
        titleBtn.textContent = group.title || group.id;
        titleBtn.title = group.attributes?.purpose || group.description || "";
        titleBtn.addEventListener("click", () => {
          openGroups.add(group.id);
          const node = nodeForModule(mod.module_id);
          setHash({
            node: node ? node.id : null,
            module: shortModule(mod.module_id),
            section: expl.id,
            item: group.id,
          });
          showModule(mod.module_id, { section: expl.id, item: group.id });
        });
        const countSpan = document.createElement("span");
        countSpan.className = "muted";
        const totalClasses =
          group.attributes?.class_count ?? countExplorerClasses(group);
        countSpan.textContent = ontoExpl
          ? `${totalClasses} classes`
          : `${classes.length} classes${enums.length ? ", " + enums.length + " enums" : ""}`;
        h2.appendChild(titleBtn);
        h2.appendChild(document.createTextNode(" "));
        h2.appendChild(countSpan);
        panel.appendChild(h2);
        const list = document.createElement("div");
        list.className = "explorer-class-list";
        kids.forEach((child) => {
          const btn = document.createElement("button");
          btn.type = "button";
          const kind = child.attributes?.kind || "class";
          const role = kind === "class" ? classRole(child.attributes) : null;
          btn.className = "spec-link explorer-chip" + (role ? ` kind-${role}` : "");
          if (kind === "class") {
            btn.innerHTML = `<span class="nav-kind ${classKindClassNames(child.attributes)}">C</span>
              <span>${escapeHtml(child.title || child.id)}</span>`;
          } else if (kind === "enum") {
            btn.innerHTML = `<span class="nav-kind">E</span>
              <span>${escapeHtml(child.title || child.id)}</span>`;
          } else {
            btn.textContent = child.title || child.id;
          }
          btn.title = child.description || "";
          btn.addEventListener("click", () => {
            openGroups.add(group.id);
            const node = nodeForModule(mod.module_id);
            setHash({
              node: node ? node.id : null,
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

  function yesBlank(value) {
    return value ? "yes" : "";
  }

  function appendMetaRow(dl, term, valueNode) {
    if (valueNode == null || valueNode === "") return;
    const dt = document.createElement("dt");
    dt.textContent = term;
    const dd = document.createElement("dd");
    if (typeof valueNode === "string") {
      dd.textContent = valueNode;
    } else {
      dd.appendChild(valueNode);
    }
    dl.appendChild(dt);
    dl.appendChild(dd);
  }

  function isOntologyExplorerItem(item, section) {
    if (item?.attributes?.iri) return true;
    const tags = section?.tags || [];
    return tags.includes("ontology") || tags.includes("fibo");
  }

  function splitRefList(value) {
    if (value == null || value === "") return [];
    if (Array.isArray(value)) return value.map(String).filter(Boolean);
    return String(value)
      .split(/\s*\|\s*|\s*,\s*/)
      .map((s) => s.trim())
      .filter(Boolean);
  }

  function renderOntologyExplorerDetail(mod, expl, item) {
    const card = document.createElement("article");
    card.className = "detail-card";
    const attrs = item.attributes || {};
    const kind = attrs.kind || "class";
    const labelRu = attrs.label_ru || "";
    const aliases = attrs.aliases || "";
    const aliasBit = labelRu || (typeof aliases === "string" ? aliases : "");
    const titleExtra = aliasBit
      ? ` <span class="muted">(${escapeHtml(String(aliasBit))})</span>`
      : "";
    const badges = [];
    if (kind) badges.push(`<span class="badge-pill">${escapeHtml(kind)}</span>`);
    if (attrs.deprecated === true || attrs.deprecated === "true") {
      badges.push(`<span class="badge-pill">deprecated</span>`);
    }
    card.innerHTML = `
      <header class="detail-head">
        <h1>${escapeHtml(item.title || item.id)}${titleExtra}</h1>
        <div class="badge-row">${badges.join("")}</div>
        <p class="muted">${escapeHtml(attrs.source_domain || attrs.ontology_id || "")}</p>
      </header>
    `;

    const defBlock = document.createElement("section");
    defBlock.className = "detail-block";
    defBlock.innerHTML = `<h2>Definition</h2>`;
    const defEn = document.createElement("p");
    defEn.className = "detail-desc";
    defEn.textContent = item.description || attrs.definition || "No definition.";
    defBlock.appendChild(defEn);
    if (attrs.definition_ru) {
      const defRu = document.createElement("p");
      defRu.className = "detail-desc muted";
      defRu.textContent = String(attrs.definition_ru);
      defBlock.appendChild(defRu);
    }
    card.appendChild(defBlock);

    const idBlock = document.createElement("section");
    idBlock.className = "detail-block";
    idBlock.innerHTML = `<h2>Identity</h2>`;
    const dl = document.createElement("dl");
    dl.className = "detail-meta";
    if (attrs.iri) {
      const code = document.createElement("code");
      code.textContent = String(attrs.iri);
      appendMetaRow(dl, "iri", code);
    }
    if (attrs.curie) appendMetaRow(dl, "curie", String(attrs.curie));
    if (attrs.local_name) appendMetaRow(dl, "local_name", String(attrs.local_name));
    if (attrs.source_domain) {
      appendMetaRow(dl, "source_domain", String(attrs.source_domain));
    }
    if (attrs.ontology_id) {
      appendMetaRow(dl, "ontology_id", String(attrs.ontology_id));
    }
    if (dl.children.length) {
      idBlock.appendChild(dl);
      card.appendChild(idBlock);
    }

    const known = collectExplorerIds(expl);
    const parents = splitRefList(attrs.parents?.length ? attrs.parents : attrs.parent_local_name);
    const children = splitRefList(attrs.children);
    // Prefer live tree children when nested under explorer
    const treeKids = (item.children || []).map((c) => c.id);
    const childIds = treeKids.length ? treeKids : children;

    const tax = document.createElement("section");
    tax.className = "detail-block";
    tax.innerHTML = `<h2>Taxonomy</h2>`;
    const taxList = document.createElement("div");
    taxList.className = "link-row";
    if (parents.length) {
      const pLabel = document.createElement("div");
      pLabel.className = "muted mixin-label";
      pLabel.textContent = "parents:";
      taxList.appendChild(pLabel);
      parents.forEach((p) =>
        taxList.appendChild(makeSpecLink(mod, expl, p, known, "parent"))
      );
    } else {
      taxList.appendChild(document.createTextNode("No parent in preview"));
    }
    if (childIds.length) {
      const cLabel = document.createElement("div");
      cLabel.className = "muted mixin-label";
      cLabel.textContent = "children:";
      taxList.appendChild(cLabel);
      childIds.forEach((c) =>
        taxList.appendChild(makeSpecLink(mod, expl, c, known, "child"))
      );
    }
    tax.appendChild(taxList);
    card.appendChild(tax);

    const domains = splitRefList(attrs.domain);
    const ranges = splitRefList(attrs.range);
    if (domains.length || ranges.length) {
      const prop = document.createElement("section");
      prop.className = "detail-block";
      prop.innerHTML = `<h2>Property</h2>`;
      const pdl = document.createElement("dl");
      pdl.className = "detail-meta";
      if (domains.length) appendMetaRow(pdl, "domain", domains.join(", "));
      if (ranges.length) appendMetaRow(pdl, "range", ranges.join(", "));
      prop.appendChild(pdl);
      card.appendChild(prop);
    }

    if (attrs.replaced_by) {
      const life = document.createElement("section");
      life.className = "detail-block";
      life.innerHTML = `<h2>Lifecycle</h2>`;
      const ldl = document.createElement("dl");
      ldl.className = "detail-meta";
      appendMetaRow(ldl, "replaced_by", String(attrs.replaced_by));
      life.appendChild(ldl);
      card.appendChild(life);
    }

    const bl = attrs.backlinks;
    if (bl !== undefined && bl !== null && bl !== "" && bl !== 0 && bl !== "0") {
      const back = document.createElement("section");
      back.className = "detail-block";
      back.innerHTML = `<h2>Backlinks</h2>
        <p class="detail-desc">${escapeHtml(String(bl))}</p>`;
      card.appendChild(back);
    }

    return card;
  }

  function renderExplorerDetail(mod, expl, item, group) {
    const card = document.createElement("article");
    card.className = "detail-card";
    const kind = item.attributes?.kind || "class";
    const abstract = item.attributes?.abstract;
    const isMixin = item.attributes?.mixin;
    const treeRoot = item.attributes?.tree_root;
    const fromSchema = item.attributes?.from_schema || item.attributes?.schema_key || "";
    const known = collectExplorerIds(expl);

    if (kind === "group") {
      const purpose = item.attributes?.purpose || item.description || "";
      const structureWhy = item.attributes?.structure_why || "";
      const classCount = item.attributes?.class_count ?? 0;
      const enumCount = item.attributes?.enum_count ?? 0;
      const groupBadge = item.attributes?.ontology_id
        ? "ontology"
        : item.attributes?.source_domain
          ? "domain"
          : "package";
      card.innerHTML = `
        <header class="detail-head">
          <h1>${escapeHtml(item.title || item.id)}</h1>
          <div class="badge-row"><span class="badge-pill">${groupBadge}</span></div>
          <p class="muted">${escapeHtml(item.attributes?.source_file || item.attributes?.schema_key || item.attributes?.ontology_id || item.attributes?.source_domain || "")}</p>
        </header>
      `;

      const purposeBlock = document.createElement("section");
      purposeBlock.className = "detail-block";
      purposeBlock.innerHTML = `<h2>Зачем</h2>
        <p class="detail-desc">${escapeHtml(purpose || "No description.")}</p>`;
      card.appendChild(purposeBlock);

      if (structureWhy) {
        const whyBlock = document.createElement("section");
        whyBlock.className = "detail-block";
        whyBlock.innerHTML = `<h2>Почему такая структура</h2>
          <p class="detail-desc">${escapeHtml(structureWhy)}</p>`;
        card.appendChild(whyBlock);
      }

      const meta = document.createElement("section");
      meta.className = "detail-block";
      meta.innerHTML = `<h2>Пакет</h2>`;
      const dl = document.createElement("dl");
      dl.className = "detail-meta";
      if (item.attributes?.schema_key) {
        appendMetaRow(dl, "schema_key", String(item.attributes.schema_key));
      }
      if (item.attributes?.source_file) {
        appendMetaRow(dl, "source_file", String(item.attributes.source_file));
      }
      appendMetaRow(dl, "classes", String(classCount));
      appendMetaRow(dl, "enums", String(enumCount));
      meta.appendChild(dl);
      card.appendChild(meta);

      const members = item.children || [];
      const memberBlock = document.createElement("section");
      memberBlock.className = "detail-block";
      memberBlock.innerHTML = `<h2>Состав (${members.length})</h2>`;
      if (!members.length) {
        memberBlock.innerHTML += `<p class="muted">Пустой пакет.</p>`;
      } else {
        const list = document.createElement("div");
        list.className = "explorer-class-list";
        members.forEach((child) => {
          const btn = document.createElement("button");
          btn.type = "button";
          const childKind = child.attributes?.kind || "class";
          const role = childKind === "class" ? classRole(child.attributes) : null;
          btn.className = "spec-link explorer-chip" + (role ? ` kind-${role}` : "");
          if (childKind === "class") {
            btn.innerHTML = `<span class="nav-kind ${classKindClassNames(child.attributes)}">C</span>
              <span>${escapeHtml(child.title || child.id)}</span>`;
          } else if (childKind === "enum") {
            btn.innerHTML = `<span class="nav-kind">E</span>
              <span>${escapeHtml(child.title || child.id)}</span>`;
          } else {
            btn.textContent = child.title || child.id;
          }
          btn.title = child.description || "";
          btn.addEventListener("click", () => {
            openGroups.add(item.id);
            const node = nodeForModule(mod.module_id);
            setHash({
              node: node ? node.id : null,
              module: shortModule(mod.module_id),
              section: expl.id,
              item: child.id,
            });
            showModule(mod.module_id, { section: expl.id, item: child.id });
          });
          list.appendChild(btn);
        });
        memberBlock.appendChild(list);
      }
      card.appendChild(memberBlock);
      return card;
    }

    if (kind !== "enum" && isOntologyExplorerItem(item, expl)) {
      return renderOntologyExplorerDetail(mod, expl, item);
    }

    const badges = [];
    if (kind) badges.push(`<span class="badge-pill">${escapeHtml(kind)}</span>`);
    if (abstract) badges.push(`<span class="badge-pill">abstract</span>`);
    if (isMixin) badges.push(`<span class="badge-pill">mixin</span>`);
    if (treeRoot) badges.push(`<span class="badge-pill">tree_root</span>`);

    const role = kind === "class" ? classRole(item.attributes) : null;
    const titleClass = role
      ? `class-title-colored kind-${role}`
      : "";
    const titleBadge =
      kind === "class"
        ? `<span class="nav-kind ${classKindClassNames(item.attributes)}" aria-hidden="true">C</span> `
        : kind === "enum"
          ? `<span class="nav-kind" aria-hidden="true">E</span> `
          : "";

    card.innerHTML = `
      <header class="detail-head">
        <h1 class="${titleClass}">${titleBadge}${escapeHtml(item.title || item.id)}</h1>
        <div class="badge-row">${badges.join("")}</div>
        <p class="muted">${escapeHtml(fromSchema)}</p>
      </header>
      <p class="detail-desc">${escapeHtml(item.description || "No description.")}</p>
    `;

    if (kind === "class") {
      const meta = document.createElement("section");
      meta.className = "detail-block";
      meta.innerHTML = `<h2>LinkML</h2>`;
      const dl = document.createElement("dl");
      dl.className = "detail-meta";
      const classUri = item.attributes?.class_uri;
      if (classUri) {
        const uriSpan = document.createElement("code");
        uriSpan.textContent = classUri;
        appendMetaRow(dl, "class_uri", uriSpan);
      }
      if (item.attributes?.from_schema) {
        appendMetaRow(dl, "from_schema", String(item.attributes.from_schema));
      }
      if (item.attributes?.schema_key) {
        appendMetaRow(dl, "schema_key", String(item.attributes.schema_key));
      }
      if (dl.children.length) {
        meta.appendChild(dl);
        card.appendChild(meta);
      }

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
      card.appendChild(inh);

      const declared = item.attributes?.declared_slots || [];
      const inlineAttrs = item.attributes?.attributes_inline || [];
      const declaredBlock = document.createElement("section");
      declaredBlock.className = "detail-block";
      declaredBlock.innerHTML = `<h2>declared slots</h2>`;
      if (!declared.length && !inlineAttrs.length) {
        declaredBlock.innerHTML += `<p class="muted">None (all slots inherited).</p>`;
      } else {
        const ul = document.createElement("ul");
        ul.className = "detail-name-list";
        declared.forEach((name) => {
          const li = document.createElement("li");
          li.innerHTML = `<code>${escapeHtml(name)}</code>`;
          ul.appendChild(li);
        });
        inlineAttrs.forEach((name) => {
          const li = document.createElement("li");
          li.innerHTML = `<code>${escapeHtml(name)}</code> <span class="muted">attributes</span>`;
          ul.appendChild(li);
        });
        declaredBlock.appendChild(ul);
      }
      card.appendChild(declaredBlock);

      const slots = item.attributes?.slots || [];
      const slotBlock = document.createElement("section");
      slotBlock.className = "detail-block";
      slotBlock.innerHTML = `<h2>Slots (induced) (${slots.length})</h2>`;
      if (!slots.length) {
        slotBlock.innerHTML += `<p class="muted">No induced slots.</p>`;
      } else {
        const table = document.createElement("table");
        table.className = "data-table detail-slots";
        table.innerHTML = `<thead><tr>
          <th>name</th><th>range</th><th>required</th><th>multivalued</th>
          <th>identifier</th><th>inlined</th><th>inherited</th><th>description</th>
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
          const nameTd = document.createElement("td");
          nameTd.textContent = slot.name || "";
          if (slot.name === "glossary_term_refs") {
            nameTd.innerHTML =
              `${escapeHtml(slot.name)} <span class="muted">(ontology refs — link when id matches FIBO)</span>`;
          }
          tr.appendChild(nameTd);
          tr.appendChild(rangeTd);
          [["required", slot.required], ["multivalued", slot.multivalued],
           ["identifier", slot.identifier], ["inlined", slot.inlined],
           ["inherited", slot.inherited]].forEach(([, flag]) => {
            const td = document.createElement("td");
            td.textContent = yesBlank(flag);
            tr.appendChild(td);
          });
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

      const slotUsage = item.attributes?.slot_usage || {};
      const usageNames = Object.keys(slotUsage);
      if (usageNames.length) {
        const usageBlock = document.createElement("section");
        usageBlock.className = "detail-block";
        usageBlock.innerHTML = `<h2>slot_usage</h2>`;
        const table = document.createElement("table");
        table.className = "data-table detail-slots";
        table.innerHTML = `<thead><tr><th>slot</th><th>overrides</th></tr></thead>`;
        const tbody = document.createElement("tbody");
        usageNames.sort().forEach((slotName) => {
          const tr = document.createElement("tr");
          const nameTd = document.createElement("td");
          nameTd.innerHTML = `<code>${escapeHtml(slotName)}</code>`;
          const ovTd = document.createElement("td");
          ovTd.innerHTML = `<code>${escapeHtml(JSON.stringify(slotUsage[slotName]))}</code>`;
          tr.appendChild(nameTd);
          tr.appendChild(ovTd);
          tbody.appendChild(tr);
        });
        table.appendChild(tbody);
        const scroll = document.createElement("div");
        scroll.className = "table-scroll";
        scroll.appendChild(table);
        usageBlock.appendChild(scroll);
        card.appendChild(usageBlock);
      }
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
        const node = nodeForModule(mod.module_id);
        setHash({
          node: node ? node.id : currentNodeId,
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
      const node = nodeForModule("moex:module:fibo");
      currentNodeId = node ? node.id : null;
      setHash({
        node: node ? node.id : null,
        module: "fibo",
        section: "glossary",
        item: itemId,
      });
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
      // Collapse only — do not setHash (would re-render and hide the body permanently
      // when already focused on this section).
      wrap.classList.toggle("collapsed");
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
          `<p class="muted">Use the left sidebar to explore this module.</p>`
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

  function parentMeta(item, section) {
    const raw =
      (item.attributes?.parent_local_name || "").trim() ||
      (item.attributes?.parents || "").trim().split(/\s*\|\s*/)[0] ||
      "";
    if (!raw) return null;
    // Prefer local_name match; also allow full IRI id (catalog glossary)
    const parentItem =
      section.items.find((i) => i.id === raw) ||
      section.items.find((i) => (i.attributes?.local_name || "") === raw) ||
      section.items.find((i) => (i.attributes?.curie || "") === raw);
    if (parentItem) {
      return {
        id: parentItem.id,
        label: parentItem.attributes?.label || parentItem.title || parentItem.id,
        inSection: true,
      };
    }
    // External / not in preview: show local name only
    const short = raw.includes("/") ? raw.replace(/\/$/, "").split("/").pop() : raw;
    return { id: raw, label: short || raw, inSection: false };
  }

  function findTreePath(items, targetId, path) {
    const trail = path || [];
    for (const item of items || []) {
      const next = trail.concat(item);
      if (item.id === targetId) return next;
      if (item.children && item.children.length) {
        const found = findTreePath(item.children, targetId, next);
        if (found) return found;
      }
    }
    return null;
  }

  function replaceHashQuiet({ node, module, section, item }) {
    const params = new URLSearchParams();
    if (node) params.set("node", node);
    if (module) params.set("module", module);
    if (section) params.set("section", section);
    if (item) params.set("item", item);
    const next = "#" + params.toString();
    if (location.hash !== next) {
      history.replaceState(null, "", next);
    }
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
            (i.attributes?.label_ru || "").toLowerCase().includes(q) ||
            (i.attributes?.definition || "").toLowerCase().includes(q) ||
            (i.attributes?.definition_ru || "").toLowerCase().includes(q) ||
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
        const en = item.attributes?.label || item.title || item.id;
        const ru = (item.attributes?.label_ru || "").trim();
        const title = ru ? `${en} (${ru})` : en;
        const defEn = item.attributes?.definition || item.description || "";
        const defRu = (item.attributes?.definition_ru || "").trim();
        const domain = item.attributes?.source_domain || "";
        card.innerHTML = `<h3>${escapeHtml(title)}</h3>
          <p>${escapeHtml(defEn)}</p>
          ${defRu ? `<p class="muted">${escapeHtml(defRu)}</p>` : ""}
          <div class="muted">${escapeHtml(item.id)}${domain ? " · " + escapeHtml(domain) : ""}</div>`;
        const parentRow = parentMeta(item, section);
        if (parentRow) {
          const parentLine = document.createElement("div");
          parentLine.className = "glossary-parent";
          parentLine.appendChild(document.createTextNode("extends "));
          if (parentRow.inSection) {
            const link = document.createElement("button");
            link.type = "button";
            link.className = "glossary-parent-link";
            link.textContent = parentRow.label;
            link.addEventListener("click", (e) => {
              e.stopPropagation();
              setHash({
                node: nodeForModule(mod.module_id)?.id || currentNodeId,
                module: shortModule(mod.module_id),
                section: section.id,
                item: parentRow.id,
              });
            });
            parentLine.appendChild(link);
          } else {
            const span = document.createElement("span");
            span.className = "muted";
            span.textContent = parentRow.label;
            parentLine.appendChild(span);
          }
          card.appendChild(parentLine);
        }
        card.addEventListener("click", () => {
          setHash({
            node: nodeForModule(mod.module_id)?.id || currentNodeId,
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

    const focusPath = selectedItemId
      ? findTreePath(section.items, selectedItemId)
      : null;
    const expandIds = new Set(
      focusPath ? focusPath.map((i) => i.id) : []
    );

    function showDetails(item, path) {
      details.classList.remove("muted");
      details.innerHTML = `<h3>${escapeHtml(item.title || item.id)}</h3>
        <p>${escapeHtml(item.description || "")}</p>
        <div class="muted">Path: ${escapeHtml(path.join(" / "))}</div>`;
    }

    function makeNode(item, depth, path) {
      const wrap = document.createElement("div");
      wrap.className = "tree-node";
      wrap.dataset.itemId = item.id;
      const hasKids = item.children && item.children.length;
      const open = depth < 2 || expandIds.has(item.id);
      const row = document.createElement("div");
      const toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = "tree-toggle";
      toggle.textContent = hasKids ? (open ? "▼" : "▶") : "·";
      const label = document.createElement("button");
      label.type = "button";
      label.className =
        "tree-label" + (item.id === selectedItemId ? " active" : "");
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
        const crumbPath = path.concat(item.title || item.id);
        showDetails(item, crumbPath);
        selectedItemId = item.id;
        nodes.querySelectorAll(".tree-label.active").forEach((el) => {
          el.classList.remove("active");
        });
        label.classList.add("active");
        // Update URL without hashchange → no full re-render / expand reset
        replaceHashQuiet({
          node: nodeForModule(mod.module_id)?.id || currentNodeId,
          module: shortModule(mod.module_id),
          section: section.id,
          item: item.id,
        });
      });
      wrap.appendChild(kids);
      return wrap;
    }

    section.items.forEach((item) => nodes.appendChild(makeNode(item, 0, [])));
    if (focusPath && focusPath.length) {
      const leaf = focusPath[focusPath.length - 1];
      showDetails(
        leaf,
        focusPath.map((i) => i.title || i.id)
      );
    }
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

    const groups = { module: [], section: [], item: [], catalog: [] };
    hits.forEach((h) => groups[h.kind]?.push(h));
    searchResults.innerHTML = "";
    ["catalog", "module", "section", "item"].forEach((kind) => {
      if (!groups[kind].length) return;
      const title = document.createElement("div");
      title.className = "muted";
      title.style.padding = "6px 12px";
      title.textContent = kind === "catalog" ? "architecture" : kind + "s";
      searchResults.appendChild(title);
      groups[kind].forEach((h) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "search-hit";
        const labeled = escapeHtml(h.title).replace(
          new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "ig"),
          "<mark>$1</mark>"
        );
        const subtitle =
          h.kind === "catalog"
            ? h.node_id || ""
            : `${h.module_id}${h.section_id ? " / " + h.section_id : ""}`;
        btn.innerHTML = `${labeled}<div class="muted">${escapeHtml(subtitle)}</div>`;
        btn.addEventListener("click", () => {
          searchResults.classList.add("hidden");
          if (h.kind === "catalog" && h.node_id) {
            const node = catalogNode(h.node_id);
            if (node) navigateToNode(node);
            return;
          }
          if (h.module_id) navigateToModule(h.module_id, {
            section: h.section_id,
            item: h.item_id,
          });
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
    const { node, module, section, item } = parseHash();
    if (node) {
      const catalogEntry = catalogNode(node);
      if (catalogEntry) {
        currentNodeId = catalogEntry.id;
        if (catalogEntry.module_id) {
          showModule(catalogEntry.module_id, { section, item });
        } else {
          showCatalogCard(catalogEntry);
        }
        return;
      }
    }
    if (module) {
      const linked = nodeForModule(moduleKey(module));
      currentNodeId = linked ? linked.id : null;
      showModule(moduleKey(module), { section, item });
      return;
    }
    const firstSpec = rootSpecifications()[0];
    if (firstSpec) {
      navigateToNode(firstSpec);
      return;
    }
    if (modules[0]) {
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
