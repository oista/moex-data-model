(() => {
  let modules = JSON.parse(document.getElementById("publication-data").textContent);
  const catalogRaw = JSON.parse(
    document.getElementById("architecture-catalog").textContent
  );
  const catalogNodes = (catalogRaw && catalogRaw.nodes) || [];
  let searchIndex = JSON.parse(document.getElementById("search-index").textContent);
  const viewerConfig = (() => {
    const el = document.getElementById("viewer-config");
    if (!el) return {};
    try {
      return JSON.parse(el.textContent);
    } catch {
      return {};
    }
  })();

  const PREFS_STORAGE_KEY = "moex-viewer-prefs";
  const LEGACY_THEME_KEY = "moex-viewer-theme";
  const displayCatalog = viewerConfig.display || {};
  const sidebarSiblings = Array.isArray(viewerConfig.sidebar_siblings)
    ? viewerConfig.sidebar_siblings
    : [];
  const displaySettings = Array.isArray(displayCatalog.settings)
    ? displayCatalog.settings
    : [];
  const catalogDefaults = { ...(displayCatalog.defaults || {}) };
  displaySettings.forEach((s) => {
    if (s && s.key != null && catalogDefaults[s.key] === undefined) {
      catalogDefaults[s.key] = s.default;
    }
  });

  let prefsMemory = null;
  let systemThemeMql = null;

  function safeStorageGet(key) {
    try {
      return localStorage.getItem(key);
    } catch {
      return null;
    }
  }

  function safeStorageSet(key, value) {
    try {
      localStorage.setItem(key, value);
      return true;
    } catch {
      return false;
    }
  }

  function safeStorageRemove(key) {
    try {
      localStorage.removeItem(key);
    } catch {
      /* ignore */
    }
  }

  function settingMeta(key) {
    return displaySettings.find((s) => s.key === key) || null;
  }

  function coercePrefValue(key, value) {
    const meta = settingMeta(key);
    if (!meta) return undefined;
    const stype = meta.type;
    if (stype === "bool") return !!value;
    if (stype === "choice") {
      const options = meta.options || [];
      if (value == null || !options.includes(value)) return meta.default;
      return value;
    }
    if (stype === "multi-from-data") {
      if (!Array.isArray(value)) return Array.isArray(meta.default) ? [...meta.default] : [];
      return value.map(String);
    }
    return value;
  }

  function readStoredPrefs() {
    const raw = safeStorageGet(PREFS_STORAGE_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch {
      return null;
    }
  }

  function migrateLegacyTheme(overlay) {
    const legacy = safeStorageGet(LEGACY_THEME_KEY);
    if (!legacy) return overlay;
    const next = { ...(overlay || {}) };
    if (next["appearance.theme"] == null && ["light", "dark"].includes(legacy)) {
      next["appearance.theme"] = legacy;
    }
    return next;
  }

  function mergePrefs(overlay) {
    const merged = { ...catalogDefaults };
    const src = migrateLegacyTheme(overlay || {});
    Object.keys(src).forEach((key) => {
      if (key === "version") return;
      if (!settingMeta(key) && catalogDefaults[key] === undefined) return;
      const coerced = coercePrefValue(key, src[key]);
      if (coerced !== undefined) merged[key] = coerced;
    });
    return merged;
  }

  function loadPrefs() {
    const stored = readStoredPrefs();
    const overlay = stored && typeof stored === "object" ? stored : null;
    prefsMemory = mergePrefs(overlay);
    return prefsMemory;
  }

  function persistPrefs() {
    const payload = {
      version: displayCatalog.version || 1,
      ...prefsMemory,
    };
    safeStorageSet(PREFS_STORAGE_KEY, JSON.stringify(payload));
    // Keep legacy key in sync for older bookmarks / external tools.
    if (prefsMemory["appearance.theme"] === "light" || prefsMemory["appearance.theme"] === "dark") {
      safeStorageSet(LEGACY_THEME_KEY, prefsMemory["appearance.theme"]);
    }
  }

  function getPref(key) {
    if (!prefsMemory) loadPrefs();
    return prefsMemory[key];
  }

  function setPref(key, value) {
    if (!prefsMemory) loadPrefs();
    const coerced = coercePrefValue(key, value);
    if (coerced === undefined) return;
    prefsMemory[key] = coerced;
    persistPrefs();
  }

  function setPrefs(patch) {
    if (!prefsMemory) loadPrefs();
    Object.keys(patch || {}).forEach((key) => {
      const coerced = coercePrefValue(key, patch[key]);
      if (coerced !== undefined) prefsMemory[key] = coerced;
    });
    persistPrefs();
  }

  function resetPrefs() {
    prefsMemory = { ...catalogDefaults };
    persistPrefs();
    safeStorageRemove(LEGACY_THEME_KEY);
  }

  function exportPrefsJson() {
    return JSON.stringify(
      { version: displayCatalog.version || 1, ...prefsMemory },
      null,
      2
    );
  }

  function importPrefsJson(text) {
    const data = JSON.parse(text);
    if (!data || typeof data !== "object") throw new Error("Invalid prefs JSON");
    prefsMemory = mergePrefs(data);
    persistPrefs();
  }

  function resolvedTheme(pref) {
    const theme = pref || getPref("appearance.theme") || "light";
    if (theme === "system") {
      try {
        return window.matchMedia("(prefers-color-scheme: dark)").matches
          ? "dark"
          : "light";
      } catch {
        return "light";
      }
    }
    return theme === "dark" ? "dark" : "light";
  }

  function applyPalette(name) {
    const root = document.documentElement;
    const paletteName = name || getPref("appearance.palette") || "default";
    root.dataset.palette = paletteName;
    // YAML remains source of truth for the default palette values.
    if (paletteName === "default" && viewerConfig.class_kind_colors?.roles) {
      const roles = viewerConfig.class_kind_colors.roles;
      const corner = viewerConfig.class_kind_colors.corner || {};
      root.style.setProperty("--class-color-plain", roles.plain);
      root.style.setProperty("--class-color-mixin", roles.mixin);
      root.style.setProperty("--class-color-abstract", roles.abstract);
      root.style.setProperty("--class-color-enum", roles.enum);
      root.style.setProperty(
        "--class-color-has-mixins",
        corner.has_mixins || roles.mixin
      );
    } else {
      ["plain", "mixin", "abstract", "enum", "has-mixins"].forEach((k) => {
        root.style.removeProperty(`--class-color-${k}`);
      });
    }
  }

  function applyAppearancePrefs() {
    const root = document.documentElement;
    const themePref = getPref("appearance.theme") || "light";
    root.dataset.theme = resolvedTheme(themePref);
    root.dataset.density = getPref("appearance.density") || "comfortable";
    applyPalette(getPref("appearance.palette") || "default");

    if (systemThemeMql) {
      try {
        systemThemeMql.removeEventListener("change", onSystemThemeChange);
      } catch {
        try {
          systemThemeMql.removeListener(onSystemThemeChange);
        } catch {
          /* ignore */
        }
      }
      systemThemeMql = null;
    }
    if (themePref === "system") {
      try {
        systemThemeMql = window.matchMedia("(prefers-color-scheme: dark)");
        if (systemThemeMql.addEventListener) {
          systemThemeMql.addEventListener("change", onSystemThemeChange);
        } else if (systemThemeMql.addListener) {
          systemThemeMql.addListener(onSystemThemeChange);
        }
      } catch {
        systemThemeMql = null;
      }
    }
  }

  function onSystemThemeChange() {
    if (getPref("appearance.theme") === "system") {
      document.documentElement.dataset.theme = resolvedTheme("system");
    }
  }

  /** Strip ADR mentions from displayed copy; publication data is unchanged. */
  function stripAdrRefs(s) {
    if (s == null) return "";
    return String(s)
      .replace(
        /\s*[\(（]\s*ADR[-–]?\s*\d{3}(?:\s*[/,]\s*(?:ADR[-–]?)?\d{3})*\s*[\)）]/gi,
        ""
      )
      .replace(/\bADR[-–]?\d{3}(?:\s*[/,]\s*(?:ADR[-–]?)?\d{3})*/gi, "")
      .replace(/\s{2,}/g, " ")
      .replace(/\s+([.,;:])/g, "$1")
      .trim();
  }

  function displayText(s) {
    if (s == null) return "";
    const text = String(s);
    return getPref("text.hide_adr_refs") ? stripAdrRefs(text) : text;
  }

  function collectSectionRoots(mod) {
    const roots = new Set();
    const expl = explorerSection(mod);
    function walk(nodes) {
      (nodes || []).forEach((n) => {
        const root = n?.attributes?.section_root;
        if (root) roots.add(String(root));
        walk(n.children);
      });
    }
    if (expl) walk(expl.items);
    return [...roots].sort();
  }

  function collectAllSectionRoots() {
    const roots = new Set();
    modules.forEach((m) => collectSectionRoots(m).forEach((r) => roots.add(r)));
    return [...roots].sort();
  }

  function filterGlossaryFolderChildren(folder, view) {
    const kids = folder.children || [];
    if (view === "flat-az") {
      return {
        ...folder,
        children: kids.filter((c) => c.attributes?.kind === "section_ref"),
      };
    }
    if (view === "by-definition-site") {
      return {
        ...folder,
        children: kids.filter((c) => c.attributes?.kind !== "section_ref"),
      };
    }
    return folder;
  }

  function filterExplorerItemsForPrefs(items) {
    const hidden = new Set(getPref("navigation.hidden_roots") || []);
    const showGlossaryFolder = getPref("glossary.show_overview_folder") !== false;
    const glossaryView = getPref("glossary.view") || "by-definition-site";
    return (items || [])
      .filter((g) => {
        const root = g.attributes?.section_root;
        if (root && hidden.has(String(root))) return false;
        return true;
      })
      .map((g) => {
        if (g.attributes?.section_root !== "overview" && g.id !== "group:overview") {
          return g;
        }
        let children = (g.children || []).filter((c) => {
          if (c.id === "group:overview-glossary" && !showGlossaryFolder) return false;
          return true;
        });
        children = children.map((c) =>
          c.id === "group:overview-glossary"
            ? filterGlossaryFolderChildren(c, glossaryView)
            : c
        );
        return { ...g, children };
      });
  }

  loadPrefs();
  applyAppearancePrefs();

  function classRole(attrs) {
    if (!attrs) return null;
    if (attrs.kind === "enum") return "enum";
    if (attrs.kind && attrs.kind !== "class") return null;
    if (attrs.mixin) return "mixin";
    if (attrs.abstract) return "abstract";
    return "plain";
  }

  function classHasMixins(attrs) {
    const mixins = attrs?.mixins;
    return Array.isArray(mixins) && mixins.length > 0;
  }

  function classKindClassNames(attrs, { corner = true } = {}) {
    const role = classRole(attrs);
    if (!role) return "";
    let cls = `kind-${role}`;
    if (corner && role !== "enum" && classHasMixins(attrs)) cls += " has-mixins-corner";
    return cls;
  }

  function sectionMajorityRole(children) {
    const counts = { plain: 0, mixin: 0, abstract: 0, enum: 0 };
    let total = 0;
    (children || []).forEach((child) => {
      const role = classRole(child?.attributes);
      if (!role || !(role in counts)) return;
      counts[role] += 1;
      total += 1;
    });
    if (!total) {
      return { role: "plain", count: 0, total: 0, tied: false };
    }
    let bestRole = "plain";
    let bestCount = -1;
    let tied = false;
    Object.keys(counts).forEach((role) => {
      const n = counts[role];
      if (n > bestCount) {
        bestRole = role;
        bestCount = n;
        tied = false;
      } else if (n === bestCount && n > 0) {
        tied = true;
      }
    });
    if (tied || bestCount <= 0) {
      return { role: "plain", count: bestCount, total, tied: true };
    }
    return { role: bestRole, count: bestCount, total, tied: false };
  }

  function isSchemaPackageGroup(attrs) {
    if (!attrs || attrs.kind !== "group") return false;
    if (attrs.section_root || attrs.group_style === "section_folder") return false;
    return !!(attrs.schema_key || attrs.source_domain || attrs.ontology_id);
  }

  function sectionMajorityGlyphHtml(node) {
    const kids = node?.children || [];
    const majority = sectionMajorityRole(kids);
    const role = majority.role || "plain";
    const letter = role === "enum" ? "E" : "C";
    const tip = majority.tied || !majority.total
      ? "mixed"
      : `mostly ${role} (${majority.count}/${majority.total})`;
    return `<span class="nav-kind-section" title="${escapeHtml(tip)}" aria-hidden="true"><span class="nav-kind kind-${role}">${letter}</span></span>`;
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

  function catalogOpenKey(nodeId) {
    return `catalog:${nodeId}`;
  }

  function bodyModuleForCatalogNode(node) {
    if (!node) return null;
    // Spec body is always the Spec publication module — never swap to Impl
    // (seamless nest: Impl sections live under implementation_ref children).
    if (node.role === "reference_specification") {
      if (node.module_id) {
        return modules.find((m) => m.module_id === node.module_id) || null;
      }
      return null;
    }
    if (node.module_id) {
      return modules.find((m) => m.module_id === node.module_id) || null;
    }
    return null;
  }

  function navigateToNode(node, focus) {
    currentNodeId = node.id;
    openGroups.add(catalogOpenKey(node.id));
    if (node.role === "specification_implementation" && node.conforms_to) {
      openGroups.add(catalogOpenKey(node.conforms_to));
      openGroups.add("group:implementations");
      openGroups.add(node.id);
    }
    if (node.module_id) {
      const mod = modules.find((m) => m.module_id === node.module_id);
      // Spec: identity landing (no section). Impl / explicit focus: module default.
      let f = focus;
      if (f === undefined) {
        f =
          node.role === "reference_specification"
            ? {}
            : defaultFocusForModule(mod);
      }
      // Expand focus folder on navigate (not on every renderModuleNav).
      if (f && f.item) openGroups.add(f.item);
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
    const parts = String(moduleId || "").split(":");
    return parts[parts.length - 1];
  }

  function itemHref({ node, module, section, item }) {
    const params = new URLSearchParams();
    if (node) params.set("node", node);
    if (module) params.set("module", module);
    if (section) params.set("section", section);
    if (item) params.set("item", item);
    const base = String(location.href || "").split("#")[0];
    const q = params.toString();
    return q ? `${base}#${q}` : base;
  }

  function setContentWide(on) {
    if (!content) return;
    content.classList.toggle("content--wide", !!on);
  }

  let linkIndex = null;

  function ensureLinkIndex() {
    if (linkIndex) return linkIndex;
    const byId = new Map();
    const byKey = new Map();

    function put(target, id, name, short, sectionId) {
      if (id && !byId.has(id)) byId.set(id, target);
      if (id) byKey.set(`${short}:${sectionId}:${id}`, target);
      if (name) byKey.set(`${short}:${sectionId}:${name}`, target);
    }

    modules.forEach((mod) => {
      const short = shortModule(mod.module_id);
      const node = nodeForModule(mod.module_id);
      const nodeId = node ? node.id : null;
      (mod.sections || []).forEach((sec) => {
        if (sec.type === "explorer") {
          walkExplorerItems(sec, (nodeItem) => {
            const kind = nodeItem.attributes?.kind;
            if (!kind || kind === "group" || kind === "section_ref") return;
            const target = {
              module: short,
              section: sec.id,
              item: nodeItem.id,
              node: nodeId,
              card: true,
            };
            put(
              target,
              nodeItem.id,
              nodeItem.attributes?.name || nodeItem.title,
              short,
              sec.id
            );
          });
          return;
        }
        const card = !!sec.instance_of || !!sec.attributes?.term_cards;
        (sec.items || []).forEach((item) => {
          const target = {
            module: short,
            section: sec.id,
            item: item.id,
            node: nodeId,
            card,
          };
          put(target, item.id, item.attributes?.name || item.title, short, sec.id);
          (item.children || []).forEach((ch) => {
            // Nested attribute/field ids resolve to the parent entity card.
            if (ch.id) {
              if (!byId.has(ch.id)) byId.set(ch.id, target);
              byKey.set(`${short}:${sec.id}:${ch.id}`, target);
            }
          });
        });
      });
    });

    linkIndex = {
      resolve(raw, preferredMod) {
        if (raw === null || raw === undefined || raw === "") return null;
        const s = String(raw).trim();
        if (!s) return null;
        if (preferredMod) {
          const short = shortModule(preferredMod.module_id);
          for (const sec of preferredMod.sections || []) {
            const hit = byKey.get(`${short}:${sec.id}:${s}`);
            if (hit) return hit;
          }
        }
        return byId.get(s) || null;
      },
    };
    return linkIndex;
  }

  function escapeHtml(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function isEmojiIcon(value) {
    const s = String(value ?? "");
    if (!s) return false;
    try {
      return /\p{Extended_Pictographic}/u.test(s);
    } catch {
      return /[\uD800-\uDBFF][\uDC00-\uDFFF]/.test(s);
    }
  }

  function displayIcon(icon, fallback = "") {
    if (!icon || isEmojiIcon(icon)) return fallback;
    return String(icon);
  }

  const LEVEL_GLYPHS = new Set(["cdm", "ldm", "pdm"]);
  const SECTION_ID_NAV_GLYPH = {
    conceptual: "cdm",
    "conceptual-erd": "cdm",
    logical: "ldm",
    "logical-erd": "ldm",
    physical: "pdm",
    "physical-erd": "pdm",
    glossary: "glossary",
    "relation-terms": "glossary",
    vocabularies: "glossary",
    "implementations-glossary": "glossary",
    "artifact-model-body": "source_file",
    "artifact-envelope": "source_file",
    "artifact-relation-terms": "source_file",
    "artifact-vocabularies": "source_file",
  };
  const KIND_LETTER = {
    enum: "E",
    individual: "I",
    source_file: "F",
    requirements: "R",
    requirement: "R",
    implementation_ref: "M",
    section_ref: "S",
    group: "G",
    glossary: "G",
    class: "C",
  };

  function resolveNavGlyph(attrs, extras) {
    const a = attrs || {};
    const x = extras || {};
    const explicit = String(a.nav_glyph || "").trim().toLowerCase();
    if (LEVEL_GLYPHS.has(explicit) || KIND_LETTER[explicit]) return explicit;

    const sectionCode = String(a.requirement_section || "").trim().toUpperCase();
    if (
      a.group_style === "section_folder" &&
      (sectionCode === "CDM" || sectionCode === "LDM" || sectionCode === "PDM")
    ) {
      return sectionCode.toLowerCase();
    }

    const sectionId = String(
      a.section_id || x.sectionId || a.target_section_id || ""
    ).trim();
    if (SECTION_ID_NAV_GLYPH[sectionId]) return SECTION_ID_NAV_GLYPH[sectionId];

    const sectionType = String(a.section_type || x.type || "")
      .trim()
      .toLowerCase();
    const pubKind = String(a.publication_kind || x.publicationKind || "")
      .trim()
      .toLowerCase();
    if (sectionType === "glossary" || pubKind === "glossary") return "glossary";

    const kind = String(a.kind || x.kind || "class");
    return KIND_LETTER[kind] ? kind : "class";
  }

  function folderShapeSvg() {
    return `<svg class="nav-kind-folder-shape" viewBox="0 0 24 20" aria-hidden="true" focusable="false"><path class="outline" d="M4.2 7.6V5.45A2.05 2.05 0 0 1 6.25 3.4h6.35L14.85 7.6h3.05A2.05 2.05 0 0 1 19.95 9.65v6.25A2.05 2.05 0 0 1 17.9 17.95H6.25A2.05 2.05 0 0 1 4.2 15.9V7.6Z"/><rect class="tab-slot" x="5.95" y="5.05" width="6.05" height="1.2" rx="0.6"/></svg>`;
  }

  function folderMarkHtml(extraClass, innerHtml) {
    const cls = extraClass ? ` ${extraClass}` : "";
    return `<span class="nav-kind nav-kind-folder${cls}" aria-hidden="true">${folderShapeSvg()}${innerHtml || ""}</span>`;
  }

  function yamlFileSvg() {
    return `<svg class="nav-kind-yaml-shape" viewBox="0 0 80 89" fill="none" aria-hidden="true" focusable="false"><g stroke="#ff6641" stroke-width="5.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.8 35.4V18.2A8.2 8.2 0 0 1 23 10h27.6L66.2 23.6v11.8"/><path d="M50.6 10v13.6h15.6"/><path d="M24.2 21.6h24.8M24.2 28.8h20.2M24.2 36h13.6"/><rect x="6.6" y="37.2" width="66.8" height="23.4" rx="8.4"/><path d="M14.8 60.6v10.6A8.2 8.2 0 0 0 23 79.4h34.2A8.2 8.2 0 0 0 65.4 71.2V60.6"/><path d="M26.8 66.4h26.4M31.2 73.6h17.6"/></g><text x="40" y="53.4" text-anchor="middle" fill="#ff6641" font-family="Segoe UI, Arial, Helvetica, sans-serif" font-size="12" font-weight="700">yaml</text></svg>`;
  }

  function yamlFileMarkHtml() {
    return `<span class="nav-kind nav-kind-yaml" aria-hidden="true">${yamlFileSvg()}</span>`;
  }

  const REQUIREMENT_STATUS = {
    draft: { label: "Черновик", cls: "draft" },
    proposed: { label: "На согласовании", cls: "proposed" },
    approved: { label: "Утверждено", cls: "approved" },
    rejected: { label: "Отклонено", cls: "inactive" },
    deprecated: { label: "Устарело", cls: "inactive" },
    superseded: { label: "Заменено", cls: "inactive" },
  };

  function requirementStatusInfo(raw) {
    const key = String(raw || "").trim().toLowerCase();
    if (REQUIREMENT_STATUS[key]) return { key, ...REQUIREMENT_STATUS[key] };
    return { key: key || "draft", label: key || REQUIREMENT_STATUS.draft.label, cls: "draft" };
  }

  function requirementsFileSvg() {
    // font-size 52 in viewBox 80×89 ≈ 9.5px at 14×16 slot (matches .nav-kind letters)
    // Stroke/fill via currentColor → --nav-requirements-accent on .nav-kind-requirements
    return `<svg class="nav-kind-requirements-shape" viewBox="0 0 80 89" fill="none" aria-hidden="true" focusable="false"><g stroke="currentColor" stroke-width="5.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.8 18.2A8.2 8.2 0 0 1 23 10h27.6L66.2 23.6v47.6A8.2 8.2 0 0 1 58 79.4H23A8.2 8.2 0 0 1 14.8 71.2V18.2Z"/><path d="M50.6 10v13.6h15.6"/></g><text x="40" y="54" text-anchor="middle" dominant-baseline="central" fill="currentColor" font-family="Segoe UI, Arial, Helvetica, sans-serif" font-size="52" font-weight="700">R</text></svg>`;
  }

  function requirementsFileMarkHtml() {
    return `<span class="nav-kind nav-kind-requirements" aria-hidden="true">${requirementsFileSvg()}</span>`;
  }

  function requirementMarkHtml(status, opts) {
    const info = requirementStatusInfo(status);
    const o = opts || {};
    const title = escapeHtml(info.label);
    const aria = o.ariaHidden === false ? "" : ' aria-hidden="true"';
    return `<span class="nav-kind nav-kind-requirement-status req-status--${info.cls}" title="${title}"${aria}>R</span>`;
  }

  function navGlyphHtml(glyph, slot, opts) {
    const g = String(glyph || "").toLowerCase();
    const s = slot || "menu";
    const o = opts || {};
    if (g === "source_file") return yamlFileMarkHtml();
    if (g === "requirements") return requirementsFileMarkHtml();
    if (LEVEL_GLYPHS.has(g)) {
      const label = g.toUpperCase();
      const plaque = `<span class="nav-glyph nav-glyph--${g} nav-glyph--menu" aria-hidden="true">${label}</span>`;
      if (s === "folder") {
        return folderMarkHtml(
          `nav-kind-folder--level nav-kind-folder--${g}`,
          `<span class="nav-kind-folder-letter">${escapeHtml(label.charAt(0))}</span>`
        );
      }
      if (s === "menu") return plaque;
      return `<span class="nav-glyph nav-glyph--${g} nav-glyph--${s}" aria-hidden="true">${label}</span>`;
    }
    const letter = KIND_LETTER[g] || String(o.letter || "C");
    const kindClasses = o.kindClasses || "";
    const implClass = g === "implementation_ref" ? " nav-kind--impl" : "";
    const glossaryClass = g === "glossary" ? " nav-kind--glossary" : "";
    return `<span class="nav-kind ${kindClasses}${implClass}${glossaryClass}" aria-hidden="true">${escapeHtml(letter)}</span>`;
  }

  function chevronSvg(direction) {
    if (direction === "down") {
      return `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
    }
    return `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m9 18 6-6-6-6" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  }

  function setTreeToggle(el, { open = false, leaf = false } = {}) {
    el.className = "tree-toggle" + (leaf ? " is-leaf" : "");
    el.type = "button";
    if (leaf) {
      el.innerHTML = "";
      el.tabIndex = -1;
      el.setAttribute("aria-hidden", "true");
      return;
    }
    el.innerHTML = chevronSvg(open ? "down" : "right");
    el.setAttribute("aria-hidden", "false");
    el.setAttribute("aria-label", open ? "Collapse" : "Expand");
  }

  function shortcutModKey() {
    const p = navigator.platform || "";
    const ua = navigator.userAgent || "";
    return /Mac|iPhone|iPad|iPod/i.test(p) || /Mac OS/i.test(ua) ? "⌘" : "Ctrl";
  }

  function mountTabs(container, tabs, { initial } = {}) {
    const list = document.createElement("div");
    list.className = "tabs";
    list.setAttribute("role", "tablist");
    const panels = document.createElement("div");
    panels.className = "tabpanels";
    let activeId = initial || tabs[0]?.id;
    const tabButtons = [];

    function select(id) {
      activeId = id;
      tabButtons.forEach((btn) => {
        const on = btn.dataset.tabId === id;
        btn.setAttribute("aria-selected", on ? "true" : "false");
        btn.tabIndex = on ? 0 : -1;
      });
      panels.querySelectorAll("[data-tabpanel]").forEach((panel) => {
        panel.hidden = panel.dataset.tabpanel !== id;
      });
    }

    tabs.forEach((tab, index) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "tab";
      btn.setAttribute("role", "tab");
      btn.dataset.tabId = tab.id;
      btn.id = `tab-${tab.id}`;
      btn.setAttribute("aria-controls", `tabpanel-${tab.id}`);
      const countHtml =
        tab.count != null
          ? ` <span class="tab-count">${escapeHtml(String(tab.count))}</span>`
          : "";
      btn.innerHTML = `${escapeHtml(tab.label)}${countHtml}`;
      btn.addEventListener("click", () => select(tab.id));
      btn.addEventListener("keydown", (e) => {
        if (e.key !== "ArrowRight" && e.key !== "ArrowLeft" && e.key !== "Home" && e.key !== "End") {
          return;
        }
        e.preventDefault();
        let next = index;
        if (e.key === "ArrowRight") next = (index + 1) % tabs.length;
        if (e.key === "ArrowLeft") next = (index - 1 + tabs.length) % tabs.length;
        if (e.key === "Home") next = 0;
        if (e.key === "End") next = tabs.length - 1;
        tabButtons[next].focus();
        select(tabs[next].id);
      });
      tabButtons.push(btn);
      list.appendChild(btn);

      const panel = document.createElement("div");
      panel.className = "tabpanel";
      panel.setAttribute("role", "tabpanel");
      panel.dataset.tabpanel = tab.id;
      panel.id = `tabpanel-${tab.id}`;
      panel.setAttribute("aria-labelledby", `tab-${tab.id}`);
      tab.render(panel);
      panels.appendChild(panel);
    });

    container.appendChild(list);
    container.appendChild(panels);
    select(activeId);
    return { select, list, panels };
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

  function indexExplorerClasses(expl) {
    const byId = new Map();
    walkExplorerItems(expl, (node) => {
      const kind = node.attributes?.kind || "class";
      if (kind === "class") byId.set(node.id, node);
    });
    return byId;
  }

  function collectClassAncestors(item, byId) {
    const out = [];
    const seen = new Set();
    function walk(node) {
      if (!node) return;
      const parentName = node.attributes?.is_a;
      if (parentName && byId.has(parentName) && !seen.has(parentName)) {
        seen.add(parentName);
        out.push(byId.get(parentName));
        walk(byId.get(parentName));
      }
      (node.attributes?.mixins || []).forEach((m) => {
        if (!byId.has(m) || seen.has(m)) return;
        seen.add(m);
        out.push(byId.get(m));
        walk(byId.get(m));
      });
    }
    walk(item);
    return out;
  }

  function collectClassDescendants(classId, byId) {
    const childrenOf = new Map();
    byId.forEach((node) => {
      const parents = [];
      if (node.attributes?.is_a) parents.push(node.attributes.is_a);
      (node.attributes?.mixins || []).forEach((m) => parents.push(m));
      parents.forEach((p) => {
        if (!childrenOf.has(p)) childrenOf.set(p, []);
        childrenOf.get(p).push(node.id);
      });
    });
    const out = [];
    const seen = new Set();
    function walk(id) {
      (childrenOf.get(id) || []).forEach((childId) => {
        if (seen.has(childId)) return;
        seen.add(childId);
        const node = byId.get(childId);
        if (!node) return;
        out.push(node);
        walk(childId);
      });
    }
    walk(classId);
    out.sort((a, b) =>
      String(a.title || a.id).localeCompare(String(b.title || b.id))
    );
    return out;
  }

  function collectClassInstances(className) {
    if (!className) return [];
    return modules.flatMap((m) =>
      (m.sections || [])
        .filter((s) => s.instance_of === className && s.type !== "explorer")
        .flatMap((s) =>
          (s.items || []).map((row) => ({ mod: m, section: s, item: row }))
        )
    );
  }

  function itSolutionModuleIds() {
    const dams = modules.find(
      (m) =>
        m.module_id === "moex:module:dams" || shortModule(m.module_id) === "dams"
    );
    if (!dams) return [];
    const expl = explorerSection(dams);
    if (!expl) return [];
    const found = findExplorerItem(expl, "group:implementations-it-solutions");
    if (!found) return [];
    const options = [];
    (found.item.children || []).forEach((child) => {
      if (child.attributes?.kind !== "implementation_ref") return;
      const mid =
        child.attributes.module_id || child.attributes.target_module_id;
      if (!mid) return;
      options.push({
        moduleId: mid,
        title: child.title || child.id,
        id: child.id,
      });
    });
    return options;
  }

  function appendExplorerClassChips(
    listEl,
    members,
    { mod, expl, openGroupId, nested } = {}
  ) {
    // nested: render is_a / subClassOf children as an indented tree, not flat chips.
    if (nested) listEl.classList.add("explorer-class-tree");
    (members || []).forEach((child) => {
      const btn = document.createElement("button");
      btn.type = "button";
      const childKind = child.attributes?.kind || "class";
      const role =
        childKind === "class" || childKind === "enum"
          ? classRole(child.attributes)
          : null;
      btn.className = "spec-link explorer-chip" + (role ? ` kind-${role}` : "");
      if (childKind === "class") {
        btn.innerHTML = `<span class="nav-kind ${classKindClassNames(child.attributes)}">C</span>
          <span>${escapeHtml(child.title || child.id)}</span>`;
      } else if (childKind === "enum") {
        btn.innerHTML = `<span class="nav-kind ${classKindClassNames(child.attributes)}">E</span>
          <span>${escapeHtml(child.title || child.id)}</span>`;
      } else if (childKind === "requirement") {
        btn.innerHTML = `${requirementMarkHtml(child.attributes?.lifecycle_status)}
          <span>${escapeHtml(child.title || child.id)}</span>`;
      } else if (childKind === "source_file") {
        btn.innerHTML = `${yamlFileMarkHtml()}
          <span>${escapeHtml(child.title || child.id)}</span>`;
      } else {
        btn.textContent = child.title || child.id;
      }
      btn.title = child.description || "";
      btn.addEventListener("click", () => {
        if (openGroupId) openGroups.add(openGroupId);
        if (child.attributes?.kind === "implementation_ref") {
          openGroups.add(child.id);
        } else {
          const found = findExplorerItem(expl, child.id);
          if (found?.group) openGroups.add(found.group.id);
        }
        const node = nodeForModule(mod.module_id);
        setHash({
          node: node ? node.id : null,
          module: shortModule(mod.module_id),
          section: expl.id,
          item: child.id,
        });
        if (node) currentNodeId = node.id;
        showModule(mod.module_id, {
          section: expl.id,
          item: child.id,
        });
      });
      listEl.appendChild(btn);
      if (nested && childKind === "class") {
        const subclasses = (child.children || []).filter(
          (c) => (c.attributes?.kind || "class") === "class"
        );
        if (subclasses.length) {
          const sub = document.createElement("div");
          sub.className = "explorer-class-subtree";
          appendExplorerClassChips(sub, subclasses, {
            mod,
            expl,
            openGroupId,
            nested,
          });
          listEl.appendChild(sub);
        }
      }
    });
  }

  function appendExplorerCompositionBlock(
    card,
    title,
    members,
    { mod, expl, openGroupId, emptyMessage }
  ) {
    const block = document.createElement("section");
    block.className = "detail-block";
    block.innerHTML = `<h2>${escapeHtml(title)} (${members.length})</h2>`;
    if (!members.length) {
      block.innerHTML += `<p class="muted">${escapeHtml(emptyMessage)}</p>`;
    } else {
      const list = document.createElement("div");
      list.className = "explorer-class-list";
      appendExplorerClassChips(list, members, {
        mod,
        expl,
        openGroupId,
        nested: true,
      });
      block.appendChild(list);
    }
    card.appendChild(block);
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

  function collectNestedSectionIds(nodes, out) {
    const ids = out || new Set();
    (nodes || []).forEach((node) => {
      const a = node.attributes || {};
      if (a.section_id) ids.add(a.section_id);
      if (Array.isArray(a.member_ids)) {
        a.member_ids.forEach((mid) => {
          if (typeof mid !== "string") return;
          if (mid.startsWith("section:")) ids.add(mid.slice("section:".length));
          else if (!mid.includes(":")) ids.add(mid);
        });
      }
      collectNestedSectionIds(node.children, ids);
    });
    return ids;
  }

  function appendPublicationSubtree(wrap, mod, focus) {
    const expl = explorerSection(mod);
    const nestedSectionIds = expl
      ? collectNestedSectionIds(expl.items)
      : new Set();
    const orphanSections = (mod.sections || []).filter(
      (s) => s.type !== "explorer" && !nestedSectionIds.has(s.id)
    );

    if (expl) {
      const tree = document.createElement("div");
      tree.className = "nav-explorer";

      // Fold publication sections not already linked from explorer into a
      // top-level Overview group (no flat .nav-secondary orphans).
      let explorerItems = expl.items || [];
      if (orphanSections.length) {
        const overviewExisting = explorerItems.find(
          (g) => g.attributes?.section_root === "overview"
        );
        const orphanRefs = orphanSections.map((sec) => {
          const attrs = {
            kind: "section_ref",
            section_id: sec.id,
            description:
              sec.description || `Open publication section «${sec.title}».`,
          };
          if (sec.type) attrs.section_type = sec.type;
          if (sec.kind) attrs.publication_kind = sec.kind;
          // Spec chrome: only DAMS level plaques (cdm/ldm/pdm). Glossary is plain
          // text like Overview peers — keep glossary glyph for impl nav only.
          if (
            SECTION_ID_NAV_GLYPH[sec.id] &&
            SECTION_ID_NAV_GLYPH[sec.id] !== "glossary"
          ) {
            attrs.nav_glyph = SECTION_ID_NAV_GLYPH[sec.id];
          }
          return {
            id: `section:${sec.id}`,
            title: sec.title,
            description:
              sec.description || `Open publication section «${sec.title}».`,
            attributes: attrs,
            children: [],
          };
        });
        orphanRefs.forEach((r) => nestedSectionIds.add(r.attributes.section_id));
        if (overviewExisting) {
          const mergedKids = [
            ...(overviewExisting.children || []),
            ...orphanRefs.filter(
              (r) =>
                !(overviewExisting.children || []).some(
                  (c) => c.attributes?.section_id === r.attributes.section_id
                )
            ),
          ];
          explorerItems = explorerItems.map((g) =>
            g.id === overviewExisting.id
              ? { ...g, children: mergedKids }
              : g
          );
        } else {
          openGroups.add("group:overview");
          explorerItems = [
            {
              id: "group:overview",
              title: "Overview",
              description: "Publication sections for this module.",
              attributes: {
                kind: "group",
                section_root: "overview",
                purpose: "Sections not otherwise nested under the explorer.",
                member_ids: orphanRefs.map((r) => r.id),
              },
              children: orphanRefs,
            },
            ...explorerItems,
          ];
        }
      }

      if (focus?.item) {
        const focused =
          findExplorerItem({ items: explorerItems }, focus.item) ||
          findExplorerItem(expl, focus.item);
        if (focused) {
          // Open ancestors/group so the selected item is visible; do not
          // force-open the item itself (label click / chevron toggles children).
          (focused.ancestors || []).forEach((a) => openGroups.add(a.id));
          if (focused.group && focused.group.id !== focus.item) {
            openGroups.add(focused.group.id);
          }
        }
      }

      function openPublicationSection(sectionId, targetModuleId) {
        selectedItemId = null;
        const mid = targetModuleId || mod.module_id;
        const node = nodeForModule(mid) || nodeForModule(mod.module_id);
        if (node) currentNodeId = node.id;
        // Keep parent Spec expanded when opening a nested Impl section.
        if (node?.conforms_to) {
          openGroups.add(catalogOpenKey(node.conforms_to));
        }
        if (node?.role === "specification_implementation") {
          openGroups.add(catalogOpenKey(node.id));
          openGroups.add("group:implementations");
          openGroups.add(node.id);
        }
        setHash({
          node: node ? node.id : null,
          module: shortModule(mid),
          section: sectionId,
        });
        showModule(mid, { section: sectionId });
      }

      function openExplorerItem(itemId) {
        const found =
          findExplorerItem({ items: explorerItems }, itemId) ||
          findExplorerItem(expl, itemId);
        const attrs = found?.item?.attributes || {};
        if (attrs.kind === "section_ref" && attrs.section_id) {
          if (found?.group) openGroups.add(found.group.id);
          // Expand parent implementation_ref when nested under it.
          if (found?.ancestors) {
            found.ancestors.forEach((a) => openGroups.add(a.id));
          }
          openPublicationSection(
            attrs.section_id,
            attrs.target_module_id || null
          );
          return;
        }
        // implementation_ref: select item → description card (expand children in tree)
        if (attrs.kind === "implementation_ref") {
          openGroups.add(itemId);
          openGroups.add("group:implementations");
        }
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

      function appendNavClassNode(parentEl, node, depth, opts) {
        const hasKids = node.children && node.children.length;
        const open = openGroups.has(node.id);
        const wrapNode = document.createElement("div");
        wrapNode.className = "nav-tree-node";
        wrapNode.style.setProperty("--tree-level", String(depth || 0));

        const row = document.createElement("div");
        row.className = "nav-tree-row";

        const toggle = document.createElement("button");
        toggle.type = "button";
        toggle.className = "tree-toggle";
        setTreeToggle(toggle, { open, leaf: !hasKids });
        toggle.addEventListener("click", (e) => {
          e.stopPropagation();
          if (!hasKids) return;
          if (openGroups.has(node.id)) openGroups.delete(node.id);
          else openGroups.add(node.id);
          renderModuleNav({
            item: selectedItemId,
            section: focus?.section || expl.id,
          });
        });

        const sectionActive =
          !focus?.item &&
          !!focus?.section &&
          node.attributes?.kind === "section_ref" &&
          node.attributes?.section_id === focus.section;
        const label = document.createElement("button");
        label.type = "button";
        label.className =
          "nav-item-btn" +
          (node.id === selectedItemId || sectionActive ? " active" : "");
        label.setAttribute("data-tree-node", "");
        label.setAttribute("data-node-id", node.id);
        label.setAttribute("data-node-type", node.attributes?.kind || "class");
        label.setAttribute("data-depth", String(depth || 0));
        if (node.id === selectedItemId || sectionActive) {
          label.setAttribute("aria-current", "page");
        }
        if (hasKids) label.setAttribute("aria-expanded", open ? "true" : "false");
        const kind = node.attributes?.kind || "class";
        const kindClasses =
          kind === "class" || kind === "enum"
            ? classKindClassNames(node.attributes)
            : "";
        const isSectionFolder =
          kind === "group" && node.attributes?.group_style === "section_folder";
        const isPackageGroup = isSchemaPackageGroup(node.attributes);
        const sectionCode = String(
          node.attributes?.requirement_section || ""
        ).trim();
        const glyph = resolveNavGlyph(node.attributes, { kind });
        // Spec top-level peers (e.g. Глоссарий next to Overview/Classes) use plain
        // chrome like nav-group rows — no letter/glyph. Impl trees keep glyphs.
        const omitGlyph = !!(opts && opts.omitGlyph);
        let markHtml;
        if (omitGlyph) {
          markHtml = "";
        } else if (isSectionFolder) {
          if (LEVEL_GLYPHS.has(glyph)) {
            markHtml = navGlyphHtml(glyph, "folder", {
              folderCode: sectionCode || glyph,
            });
          } else if (glyph === "source_file") {
            markHtml = yamlFileMarkHtml();
          } else {
            const codeHtml = sectionCode
              ? `<span class="nav-kind-folder-code">${escapeHtml(sectionCode.slice(0, 3))}</span>`
              : "";
            markHtml = folderMarkHtml("", codeHtml);
          }
        } else if (isPackageGroup) {
          markHtml = sectionMajorityGlyphHtml(node);
        } else if (kind === "requirement") {
          markHtml = requirementMarkHtml(node.attributes?.lifecycle_status, {
            ariaHidden: false,
          });
        } else if (LEVEL_GLYPHS.has(glyph)) {
          markHtml = navGlyphHtml(glyph, "menu");
        } else {
          markHtml = navGlyphHtml(glyph, "menu", { kindClasses });
        }
        label.innerHTML = `${markHtml}
          <span class="tree-label">${escapeHtml(node.title || node.id)}</span>`;
        if (kind === "requirement") {
          const st = requirementStatusInfo(node.attributes?.lifecycle_status);
          label.title = `${node.title || node.id} — ${st.label}`;
        } else {
          label.title = isSectionFolder && sectionCode
            ? `${sectionCode} — ${node.title || node.id}`
            : node.title || node.id;
        }
        label.addEventListener("click", (e) => {
          e.stopPropagation();
          if (hasKids) {
            // Symmetric: first click expands, second click on same parent collapses
            if (node.id === selectedItemId && openGroups.has(node.id)) {
              openGroups.delete(node.id);
            } else {
              openGroups.add(node.id);
            }
          }
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

      explorerItems = filterExplorerItemsForPrefs(explorerItems);

      explorerItems.forEach((group) => {
        // Top-level section_ref (e.g. moex.dams «Глоссарий») — leaf, not a folder.
        // Match peer groups: no kind/glyph icon at this hierarchy level.
        if (group.attributes?.kind === "section_ref") {
          appendNavClassNode(tree, group, 0, { omitGlyph: true });
          return;
        }
        const gId = group.id;
        // Default: open Классы when no item focus — also when landing on
        // explorer via section_ref (focus.section === explorer.id).
        const landingOnExplorer =
          !focus?.item &&
          (!focus?.section || focus.section === expl.id);
        if (
          landingOnExplorer &&
          gId === "group:classes" &&
          !explorerItems.some((g) => openGroups.has(g.id))
        ) {
          openGroups.add(gId);
          // Single package under Classes (e.g. moex.dsp): open it too.
          const pkgKids = (group.children || []).filter(
            (c) => c.attributes?.kind === "group"
          );
          if (pkgKids.length === 1) openGroups.add(pkgKids[0].id);
        }
        // Auto-open only when a descendant is focused, not the group itself
        if (
          focus?.item &&
          focus.item !== gId &&
          descendantHasId(group, focus.item)
        ) {
          openGroups.add(gId);
        }
        const open = openGroups.has(gId);
        const gWrap = document.createElement("div");
        gWrap.className =
          "nav-group" +
          (group.attributes?.section_root === "implementations"
            ? " nav-implementations"
            : "");
        const overviewRootActive =
          group.attributes?.section_root === "overview" &&
          !focus?.item &&
          focus?.section === "overview";
        const gBtn = document.createElement("button");
        gBtn.type = "button";
        gBtn.className =
          "nav-group-btn" +
          (gId === selectedItemId || overviewRootActive ? " active" : "");
        const toggle = document.createElement("span");
        toggle.className = "tree-toggle";
        setTreeToggle(toggle, { open, leaf: false });
        toggle.addEventListener("click", (e) => {
          e.stopPropagation();
          if (openGroups.has(gId)) openGroups.delete(gId);
          else openGroups.add(gId);
          renderModuleNav({
            item: selectedItemId,
            section: focus?.section || expl.id,
          });
        });
        const titleSpan = document.createElement("span");
        titleSpan.textContent = group.title || group.id;
        const groupGlyph = resolveNavGlyph(group.attributes);
        const badge = document.createElement("span");
        badge.className = "badge";
        const sectionRoot = group.attributes?.section_root;
        let badgeCount;
        if (sectionRoot === "spec-files") {
          badgeCount =
            group.attributes?.file_count ?? (group.children || []).length;
        } else if (
          sectionRoot === "requirements" ||
          sectionRoot === "requirements-conceptual" ||
          sectionRoot === "requirements-conceptual-list" ||
          sectionRoot === "requirements-it-solutions" ||
          sectionRoot === "requirements-list" ||
          sectionRoot === "requirements-publication" ||
          sectionRoot === "requirements-publication-list"
        ) {
          badgeCount =
            group.attributes?.requirement_count ??
            (group.children || []).reduce(
              (n, c) =>
                n +
                ((c.attributes?.kind === "requirement"
                  ? 1
                  : (c.children || []).length) || 0),
              0
            );
        } else if (
          sectionRoot === "requirements-it-spec" ||
          sectionRoot === "requirements-conceptual-spec" ||
          sectionRoot === "requirements-model-example" ||
          sectionRoot === "requirements-publication-spec"
        ) {
          badgeCount =
            group.attributes?.file_count ?? (group.children || []).length;
        } else if (sectionRoot === "implementations") {
          badgeCount =
            group.attributes?.impl_count ?? (group.children || []).length;
        } else if (sectionRoot === "overview") {
          badgeCount = (group.children || []).length;
        } else {
          badgeCount =
            group.attributes?.class_count ?? countExplorerClasses(group);
        }
        badge.textContent = String(badgeCount);
        gBtn.appendChild(toggle);
        if (LEVEL_GLYPHS.has(groupGlyph)) {
          gBtn.insertAdjacentHTML("beforeend", navGlyphHtml(groupGlyph, "menu"));
        }
        gBtn.appendChild(titleSpan);
        gBtn.appendChild(badge);
        const kids = document.createElement("div");
        kids.className = "nav-group-children";
        kids.hidden = !open;
        gBtn.addEventListener("click", (e) => {
          e.stopPropagation();
          if (gId === selectedItemId && openGroups.has(gId)) {
            openGroups.delete(gId);
          } else {
            openGroups.add(gId);
          }
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
      return;
    }

    // No explorer: sections are the primary tree (not a bolted secondary strip)
    if (orphanSections.length) {
      const tree = document.createElement("div");
      tree.className = "nav-explorer";
      orphanSections.forEach((sec) => {
        const sBtn = document.createElement("button");
        sBtn.type = "button";
        sBtn.className =
          "nav-section-btn" +
          (focus?.section === sec.id && !focus?.item ? " active" : "");
        sBtn.setAttribute("data-tree-node", "");
        const secGlyph =
          SECTION_ID_NAV_GLYPH[sec.id] ||
          resolveNavGlyph(
            { section_id: sec.id, nav_glyph: sec.nav_glyph },
            { type: sec.type, publicationKind: sec.kind }
          );
        // Spec section list: level plaques only; glossary matches plain siblings.
        if (LEVEL_GLYPHS.has(secGlyph)) {
          sBtn.innerHTML = `${navGlyphHtml(secGlyph, "menu")} <span>${escapeHtml(sec.title)}</span>`;
        } else {
          sBtn.textContent = sec.title;
        }
        sBtn.addEventListener("click", (e) => {
          e.stopPropagation();
          selectedItemId = null;
          const node = nodeForModule(mod.module_id);
          if (node) currentNodeId = node.id;
          setHash({
            node: node ? node.id : null,
            module: shortModule(mod.module_id),
            section: sec.id,
          });
        });
        tree.appendChild(sBtn);
      });
      wrap.appendChild(tree);
    }
  }

  function openSidebarSectionRef(attrs) {
    selectedItemId = null;
    const mid = attrs.target_module_id;
    if (!mid || !attrs.section_id) return;
    const node = nodeForModule(mid);
    if (node) {
      currentNodeId = node.id;
      if (node.conforms_to) {
        openGroups.add(catalogOpenKey(node.conforms_to));
      }
      if (node.role === "specification_implementation") {
        openGroups.add(catalogOpenKey(node.id));
        openGroups.add("group:implementations");
        openGroups.add(node.id);
      }
    }
    setHash({
      node: node ? node.id : null,
      module: shortModule(mid),
      section: attrs.section_id,
    });
    showModule(mid, { section: attrs.section_id });
  }

  function appendSidebarSiblingNav(parentEl, sibling, focus) {
    const mKey = `sidebar:${sibling.id}`;
    const open = openGroups.has(mKey);
    const kids = sibling.children || [];
    const wrap = document.createElement("div");
    wrap.className = "nav-module";
    const row = document.createElement("div");
    row.className = "nav-tree-row nav-catalog-row";
    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "tree-toggle";
    setTreeToggle(toggle, { open, leaf: !kids.length });
    toggle.addEventListener("click", (e) => {
      e.stopPropagation();
      if (!kids.length) return;
      if (openGroups.has(mKey)) openGroups.delete(mKey);
      else openGroups.add(mKey);
      renderModuleNav(focus);
    });
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "module-btn";
    btn.innerHTML = `<span>${escapeHtml(sibling.title)}</span>
      <span class="badge">${kids.length}</span>`;
    btn.addEventListener("click", () => {
      if (openGroups.has(mKey)) openGroups.delete(mKey);
      else openGroups.add(mKey);
      renderModuleNav(focus);
    });
    row.appendChild(toggle);
    row.appendChild(btn);
    wrap.appendChild(row);
    if (open && kids.length) {
      const body = document.createElement("div");
      body.className = "nav-catalog-body";
      const tree = document.createElement("div");
      tree.className = "nav-explorer";
      kids.forEach((child) => {
        const leafWrap = document.createElement("div");
        leafWrap.className = "nav-tree-node";
        leafWrap.style.setProperty("--tree-level", "0");
        const leafRow = document.createElement("div");
        leafRow.className = "nav-tree-row";
        const leafToggle = document.createElement("button");
        leafToggle.type = "button";
        leafToggle.className = "tree-toggle is-leaf";
        setTreeToggle(leafToggle, { open: false, leaf: true });
        const attrs = child.attributes || {};
        const sectionActive =
          !focus?.item &&
          !!focus?.section &&
          attrs.kind === "section_ref" &&
          attrs.section_id === focus.section &&
          attrs.target_module_id &&
          shortModule(attrs.target_module_id) === shortModule(currentModuleId);
        const label = document.createElement("button");
        label.type = "button";
        label.className = "nav-item-btn" + (sectionActive ? " active" : "");
        label.setAttribute("data-tree-node", "");
        const glyph = resolveNavGlyph(attrs, { kind: attrs.kind });
        label.innerHTML = `${navGlyphHtml(glyph, "menu")}
          <span class="tree-label">${escapeHtml(child.title || child.id)}</span>`;
        label.addEventListener("click", (e) => {
          e.stopPropagation();
          openGroups.add(mKey);
          if (attrs.kind === "section_ref") openSidebarSectionRef(attrs);
        });
        leafRow.appendChild(leafToggle);
        leafRow.appendChild(label);
        leafWrap.appendChild(leafRow);
        tree.appendChild(leafWrap);
      });
      body.appendChild(tree);
      wrap.appendChild(body);
    }
    parentEl.appendChild(wrap);
  }

  function appendSidebarSiblingsAfter(parentEl, afterModuleId, focus) {
    sidebarSiblings
      .filter((s) => s && s.after_module_id === afterModuleId)
      .forEach((s) => appendSidebarSiblingNav(parentEl, s, focus));
  }

  function appendCatalogNav(parentEl, node, focus) {
    const bodyMod = bodyModuleForCatalogNode(node);
    const hasBody = !!bodyMod;
    const cKey = catalogOpenKey(node.id);
    const open = openGroups.has(cKey);
    const selected =
      node.id === currentNodeId && !selectedItemId;

    const wrap = document.createElement("div");
    wrap.className = "nav-module";

    const row = document.createElement("div");
    row.className = "nav-tree-row nav-catalog-row";

    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "tree-toggle";
    setTreeToggle(toggle, { open, leaf: !hasBody });
    toggle.addEventListener("click", (e) => {
      e.stopPropagation();
      if (!hasBody) return;
      if (openGroups.has(cKey)) openGroups.delete(cKey);
      else openGroups.add(cKey);
      renderModuleNav({
        item: selectedItemId,
        section: focus?.section || null,
      });
    });

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "module-btn" + (selected ? " active" : "");
    const roleLabel =
      node.role === "reference_specification" ? "Spec" : "Impl";
    const roleClass =
      node.role === "reference_specification"
        ? "role-pill role-pill--spec"
        : "role-pill role-pill--impl";
    const titleClass =
      node.role === "reference_specification" ? "nav-spec-title" : "";
    btn.innerHTML = `<span class="${roleClass}">${roleLabel}</span>
      <span class="${titleClass}">${escapeHtml(node.title)}</span>
      ${node.version ? `<span class="badge">${escapeHtml(node.version)}</span>` : ""}`;
    btn.addEventListener("click", () => {
      if (
        hasBody &&
        node.id === currentNodeId &&
        !selectedItemId &&
        openGroups.has(cKey)
      ) {
        openGroups.delete(cKey);
        renderModuleNav({
          item: selectedItemId,
          section: focus?.section || null,
        });
        return;
      }
      if (hasBody) openGroups.add(cKey);
      navigateToNode(node);
    });

    row.appendChild(toggle);
    row.appendChild(btn);
    wrap.appendChild(row);

    if (open && bodyMod) {
      const body = document.createElement("div");
      body.className = "nav-catalog-body";
      appendPublicationSubtree(body, bodyMod, focus);
      wrap.appendChild(body);
    }
    parentEl.appendChild(wrap);
  }

  function renderModuleNav(focus) {
    moduleNav.innerHTML = "";

    if (!catalogNodes.length) {
      modules.forEach((mod) => {
        const wrap = document.createElement("div");
        wrap.className = "nav-module";
        const active = mod.module_id === currentModuleId;
        const mKey = `module:${mod.module_id}`;
        const open = openGroups.has(mKey) || active;
        const row = document.createElement("div");
        row.className = "nav-tree-row nav-catalog-row";
        const toggle = document.createElement("button");
        toggle.type = "button";
        toggle.className = "tree-toggle";
        setTreeToggle(toggle, { open, leaf: false });
        toggle.addEventListener("click", (e) => {
          e.stopPropagation();
          if (openGroups.has(mKey)) openGroups.delete(mKey);
          else openGroups.add(mKey);
          renderModuleNav(focus);
        });
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "module-btn" + (active && !selectedItemId ? " active" : "");
        btn.innerHTML = `${displayIcon(mod.icon) ? `<span class="module-icon">${escapeHtml(displayIcon(mod.icon))}</span> ` : ""}<span>${escapeHtml(mod.title)}</span>
          <span class="badge">${mod.sections.length}</span>`;
        btn.addEventListener("click", () => {
          openGroups.add(mKey);
          navigateToModule(mod.module_id);
        });
        row.appendChild(toggle);
        row.appendChild(btn);
        wrap.appendChild(row);
        if (open && active) appendPublicationSubtree(wrap, mod, focus);
        moduleNav.appendChild(wrap);
        appendSidebarSiblingsAfter(moduleNav, mod.module_id, focus);
      });
      return;
    }

    rootSpecifications().forEach((spec) => {
      appendCatalogNav(moduleNav, spec, focus);
    });

    const orphans = unattachedImplementations();
    if (orphans.length) {
      const label = document.createElement("div");
      label.className = "nav-group-label muted";
      label.textContent = "Implementations without specification";
      moduleNav.appendChild(label);
      orphans.forEach((impl) => appendCatalogNav(moduleNav, impl, focus));
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
        const mKey = `module:${mod.module_id}`;
        const open = openGroups.has(mKey) || active;
        const row = document.createElement("div");
        row.className = "nav-tree-row nav-catalog-row";
        const toggle = document.createElement("button");
        toggle.type = "button";
        toggle.className = "tree-toggle";
        setTreeToggle(toggle, { open, leaf: false });
        toggle.addEventListener("click", (e) => {
          e.stopPropagation();
          if (openGroups.has(mKey)) openGroups.delete(mKey);
          else openGroups.add(mKey);
          renderModuleNav(focus);
        });
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "module-btn" + (active && !selectedItemId ? " active" : "");
        btn.innerHTML = `${displayIcon(mod.icon) ? `<span class="module-icon">${escapeHtml(displayIcon(mod.icon))}</span> ` : ""}<span>${escapeHtml(mod.title)}</span>
          <span class="badge">${mod.sections.length}</span>`;
        btn.addEventListener("click", () => {
          openGroups.add(mKey);
          navigateToModule(mod.module_id);
        });
        row.appendChild(toggle);
        row.appendChild(btn);
        wrap.appendChild(row);
        if (open && active) appendPublicationSubtree(wrap, mod, focus);
        moduleNav.appendChild(wrap);
        appendSidebarSiblingsAfter(moduleNav, mod.module_id, focus);
      });
    }
    bindPublicationTreeKeyboard();
  }

  function visibleNavTargets() {
    return Array.from(
      moduleNav.querySelectorAll("[data-tree-node], .module-btn, .nav-group-btn, .nav-section-btn, .nav-impl-btn")
    ).filter((el) => {
      if (el.disabled) return false;
      const style = window.getComputedStyle(el);
      if (style.display === "none" || style.visibility === "hidden") return false;
      let p = el.parentElement;
      while (p && p !== moduleNav) {
        if (p.hidden) return false;
        p = p.parentElement;
      }
      return true;
    });
  }

  function bindPublicationTreeKeyboard() {
    const targets = visibleNavTargets();
    targets.forEach((el, i) => {
      el.tabIndex = i === 0 || el.classList.contains("active") || el.getAttribute("aria-current") === "page" ? 0 : -1;
    });
    const current =
      targets.find((el) => el.getAttribute("aria-current") === "page" || el.classList.contains("active")) ||
      targets[0];
    if (current) {
      targets.forEach((el) => {
        el.tabIndex = el === current ? 0 : -1;
      });
    }

    targets.forEach((el) => {
      if (el.dataset.treeKeysBound === "1") return;
      el.dataset.treeKeysBound = "1";
      el.addEventListener("keydown", (e) => {
        const list = visibleNavTargets();
        const idx = list.indexOf(el);
        if (idx < 0) return;

        const focusAt = (i) => {
          const next = list[i];
          if (!next) return;
          list.forEach((n) => {
            n.tabIndex = -1;
          });
          next.tabIndex = 0;
          next.focus();
        };

        if (e.key === "ArrowDown") {
          e.preventDefault();
          focusAt(Math.min(list.length - 1, idx + 1));
          return;
        }
        if (e.key === "ArrowUp") {
          e.preventDefault();
          focusAt(Math.max(0, idx - 1));
          return;
        }
        if (e.key === "Home") {
          e.preventDefault();
          focusAt(0);
          return;
        }
        if (e.key === "End") {
          e.preventDefault();
          focusAt(list.length - 1);
          return;
        }
        if (e.key === "ArrowRight") {
          e.preventDefault();
          const toggle = el.closest(".nav-tree-row")?.querySelector(".tree-toggle:not(.is-leaf)");
          if (toggle && el.getAttribute("aria-expanded") === "false") {
            toggle.click();
          } else {
            focusAt(Math.min(list.length - 1, idx + 1));
          }
          return;
        }
        if (e.key === "ArrowLeft") {
          e.preventDefault();
          const toggle = el.closest(".nav-tree-row")?.querySelector(".tree-toggle:not(.is-leaf)");
          if (toggle && el.getAttribute("aria-expanded") === "true") {
            toggle.click();
          } else {
            const parentRow = el.closest(".nav-tree-node")?.parentElement?.closest(".nav-tree-node");
            const parentBtn = parentRow?.querySelector("[data-tree-node], .nav-group-btn");
            if (parentBtn) {
              list.forEach((n) => {
                n.tabIndex = -1;
              });
              parentBtn.tabIndex = 0;
              parentBtn.focus();
            }
          }
          return;
        }
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          el.click();
          // Selecting a leaf must not collapse its branch (handled in click handlers).
          requestAnimationFrame(() => {
            const h1 = content.querySelector("h1");
            if (h1) {
              h1.setAttribute("tabindex", "-1");
              h1.focus();
            }
            announce(h1 ? h1.textContent.trim() : "Opened");
          });
        }
      });
    });
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
    openGroups.add(catalogOpenKey(node.id));
    renderModuleNav();
    content.innerHTML = "";
    content.appendChild(renderArchitectureCrumb(node));
    const { card, block } = renderCatalogIdentityCard(node, null);
    content.appendChild(card);
    if (block) content.appendChild(block);

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

    // When an object card is open, keep chrome to breadcrumb only (avoid badge duplication).
    if (!focus?.item) {
      const meta = document.createElement("div");
      meta.className = "arch-meta muted";
      const role =
        node.role === "reference_specification" ? "Specification" : "Implementation";
      const bits = [role];
      if (node.expressed_in) bits.push(node.expressed_in);
      if (node.version) bits.push(node.version);
      meta.textContent = bits.join(" · ");
      chrome.appendChild(meta);
    }

    if (
      node.role === "reference_specification" &&
      !focus?.item &&
      focus?.section &&
      focus.section === explorerSection(mod)?.id
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
      setContentWide(false);
      return;
    }

    if (!currentNodeId || catalogNode(currentNodeId)?.module_id !== currentModuleId) {
      const linked = nodeForModule(currentModuleId);
      if (linked) currentNodeId = linked.id;
    }

    const linkedNode = currentNodeId ? catalogNode(currentNodeId) : nodeForModule(currentModuleId);
    if (linkedNode) {
      openGroups.add(catalogOpenKey(linkedNode.id));
      if (linkedNode.conforms_to) {
        openGroups.add(catalogOpenKey(linkedNode.conforms_to));
      }
    }

    const expl = explorerSection(mod);
    selectedItemId = focus?.item || null;
    renderModuleNav(focus);

    content.innerHTML = "";
    setContentWide(false);
    const chrome = prependArchitectureChrome(mod, focus);
    if (chrome) content.appendChild(chrome);

    const crumb = document.createElement("div");
    crumb.className = "breadcrumb muted";

    // Catalog identity landing (Spec/Impl selected, no section/item focus)
    if (linkedNode && !focus?.item && !focus?.section) {
      crumb.textContent = linkedNode.title;
      content.appendChild(crumb);
      const { card, block } = renderCatalogIdentityCard(linkedNode, mod);
      content.appendChild(card);
      if (block) content.appendChild(block);
      return;
    }

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

    // Instance card for entity-table rows with instance_of,
    // or term card for aggregated implementations glossary (term_cards).
    if (focus?.section && focus?.item) {
      const section = mod.sections.find((s) => s.id === focus.section);
      if (section && section.type !== "explorer") {
        const row = findSectionItem(section, focus.item);
        if (row && section.attributes?.term_cards) {
          crumb.textContent = `${mod.title} / ${section.title} / ${row.title || row.id}`;
          content.appendChild(crumb);
          content.appendChild(renderImplTermDetail(mod, section, row));
          return;
        }
        if (row && section.instance_of) {
          crumb.textContent = `${mod.title} / ${section.title} / ${row.title || row.id}`;
          content.appendChild(crumb);
          content.appendChild(renderInstanceDetail(mod, section, row));
          return;
        }
      }
    }

    // Secondary section (or overview) as single focus
    if (focus?.section && (!expl || focus.section !== expl.id || !focus.item)) {
      const section = mod.sections.find((s) => s.id === focus.section);
      if (section && section.type === "source-file") {
        setContentWide(false);
        crumb.textContent = `${mod.title} / ${section.title}`;
        content.appendChild(crumb);
        content.appendChild(renderSourceFileSection(mod, section));
        return;
      }
      if (section && section.type !== "explorer") {
        const isWide =
          section.type === "entity-table" ||
          section.type === "enum-table" ||
          section.type === "markdown-doc" ||
          section.type === "glossary" ||
          section.type === "mermaid-diagram";
        setContentWide(isWide);
        crumb.textContent = `${mod.title} / ${section.title}`;
        content.appendChild(crumb);
        content.appendChild(renderSection(mod, section, { forceOpen: true }));
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
      header.innerHTML = `<h1>${escapeHtml(displayIcon(mod.icon) ? displayIcon(mod.icon) + " " : "")}${escapeHtml(mod.title)}</h1>
        <p class="muted">${escapeHtml(displayText(mod.description || ""))}</p>
        <p>${landingHint}</p>`;
      content.appendChild(header);

      const kpi = document.createElement("div");
      kpi.className = "kpi-strip";
      const groups = expl.items || [];
      const classTotal = groups.reduce(
        (n, g) => n + (g.attributes?.class_count ?? countExplorerClasses(g)),
        0
      );
      const enumTotal = groups.reduce((n, g) => {
        if (g.attributes?.enum_count != null) return n + g.attributes.enum_count;
        const kids = g.children || [];
        return n + kids.filter((c) => c.attributes?.kind === "enum").length;
      }, 0);
      kpi.innerHTML = `
        <div class="kpi-card"><div class="kpi-value">${groups.length}</div><div class="kpi-label">Groups</div></div>
        <div class="kpi-card"><div class="kpi-value">${classTotal}</div><div class="kpi-label">Classes</div></div>
        <div class="kpi-card"><div class="kpi-value">${enumTotal}</div><div class="kpi-label">Enumerations</div></div>
        <div class="kpi-card"><div class="kpi-value">${escapeHtml(mod.version || "—")}</div><div class="kpi-label">Version</div></div>`;
      content.appendChild(kpi);

      const grid = document.createElement("div");
      grid.className = "explorer-landing";
      // LinkML spec roots wrap packages under group:classes — show each package
      // with its is_a hierarchy instead of one flat «Classes» panel of package chips.
      const landingGroups = [];
      filterExplorerItemsForPrefs(expl.items || []).forEach((group) => {
        const pkgs = (group.children || []).filter(
          (c) => c.attributes?.kind === "group"
        );
        if (
          !ontoExpl &&
          group.attributes?.section_root === "classes" &&
          pkgs.length
        ) {
          pkgs.forEach((p) => landingGroups.push(p));
        } else {
          landingGroups.push(group);
        }
      });
      landingGroups.forEach((group) => {
        const panel = document.createElement("section");
        panel.className = "explorer-package";
        const kids = group.children || [];
        const enums = kids.filter((c) => c.attributes?.kind === "enum");
        const h2 = document.createElement("h2");
        const titleBtn = document.createElement("button");
        titleBtn.type = "button";
        titleBtn.className = "package-title-link";
        titleBtn.textContent = group.title || group.id;
        titleBtn.title = displayText(
          group.attributes?.purpose || group.description || ""
        );
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
        const enumCount = group.attributes?.enum_count ?? enums.length;
        countSpan.textContent = ontoExpl
          ? `${totalClasses} classes`
          : `${totalClasses} classes${enumCount ? ", " + enumCount + " enums" : ""}`;
        h2.appendChild(titleBtn);
        h2.appendChild(document.createTextNode(" "));
        h2.appendChild(countSpan);
        panel.appendChild(h2);
        const list = document.createElement("div");
        list.className = "explorer-class-list";
        appendExplorerClassChips(list, kids, {
          mod,
          expl,
          openGroupId: group.id,
          nested: !ontoExpl,
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
    header.innerHTML = `<h1>${escapeHtml(displayIcon(mod.icon) ? displayIcon(mod.icon) + " " : "")}${escapeHtml(mod.title)}</h1>
      <p class="muted">${escapeHtml(mod.description || "")}</p>`;
    const chipRow = document.createElement("div");
    chipRow.className = "module-meta-chips";
    appendModuleProfileChips(chipRow, mod);
    if (chipRow.childNodes.length) header.appendChild(chipRow);
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

  function appendModuleProfileChips(container, mod) {
    const chips = [];
    if (mod.implementation_profile) {
      chips.push(["implementation_profile", mod.implementation_profile]);
    }
    if (mod.dams_model_level) {
      chips.push(["dams_model_level", mod.dams_model_level]);
    }
    if (mod.conformance_status) {
      chips.push(["conformance", mod.conformance_status]);
    }
    chips.forEach(([kind, value]) => {
      const span = document.createElement("span");
      const slug = String(value).toLowerCase().replace(/[^a-z0-9-]+/g, "-");
      span.className = `status-chip status-chip--${slug}`;
      if (kind === "dams_model_level") {
        span.classList.add("status-chip--dams-level");
      }
      if (kind === "implementation_profile") {
        span.classList.add("status-chip--impl-profile");
      }
      if (String(value).toLowerCase() === "draft-conformant") {
        span.classList.add("status-chip--draft-conformant");
      }
      span.textContent = `${kind}: ${value}`;
      container.appendChild(span);
    });
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

  function isGlossaryViewItem(item) {
    return Boolean(item?.attributes?.glossary_view);
  }

  function splitRefList(value) {
    if (value == null || value === "") return [];
    if (Array.isArray(value)) return value.map(String).filter(Boolean);
    return String(value)
      .split(/\s*\|\s*|\s*,\s*/)
      .map((s) => s.trim())
      .filter(Boolean);
  }

  function canonicalGlossaryId(id) {
    const raw = String(id || "");
    return raw.startsWith("glossary:") ? raw.slice("glossary:".length) : raw;
  }

  function resolveGlossaryNavId(canonicalId, known) {
    const cid = canonicalGlossaryId(canonicalId);
    if (!cid) return null;
    const prefixed = "glossary:" + cid;
    if (known && known.has(prefixed)) return prefixed;
    if (known && known.has(cid)) return cid;
    return null;
  }

  function relTargetId(entry) {
    if (entry == null) return "";
    if (typeof entry === "string") return entry;
    return String(entry.id || entry.target_ref || "");
  }

  function relLabel(entry) {
    if (entry == null) return "";
    if (typeof entry === "string") return entry;
    const id = relTargetId(entry);
    const rel = entry.rel ? String(entry.rel) : "";
    return rel ? `${id} (${rel})` : id;
  }

  function appendAdr027RelationBlocks(card, mod, item, navCtx) {
    /** Taxonomy / See also / Assignment / Origin — ADR-027 term card contract. */
    if (getPref("glossary.show_relation_blocks") === false) return;
    const attrs = item.attributes || {};
    const known = navCtx.known || new Set();
    const sectionId = navCtx.sectionId;
    const expl = navCtx.expl;

    function makeTermChip(targetId, label) {
      const display = label || canonicalGlossaryId(targetId) || targetId;
      const navId = resolveGlossaryNavId(targetId, known);
      if (!navId) {
        const span = document.createElement("span");
        span.className = "spec-link disabled glossary-rel-chip";
        span.textContent = display;
        return span;
      }
      const node = nodeForModule(mod.module_id);
      const href = itemHref({
        node: node ? node.id : currentNodeId,
        module: shortModule(mod.module_id),
        section: expl ? expl.id : sectionId,
        item: expl ? navId : canonicalGlossaryId(navId),
      });
      return makeBlankAnchor(href, display, "spec-link glossary-rel-chip");
    }

    // Taxonomy
    let parents = Array.isArray(attrs.taxonomy_parents) ? attrs.taxonomy_parents : [];
    let children = Array.isArray(attrs.taxonomy_children) ? attrs.taxonomy_children : [];
    if (!parents.length) {
      const fallbackParent =
        (attrs.parent_local_name || "").trim() ||
        (attrs.is_a || "").trim() ||
        "";
      if (fallbackParent) parents = [{ id: fallbackParent, rel: "parent" }];
      const mixins = Array.isArray(attrs.mixins) ? attrs.mixins : [];
      mixins.forEach((m) => parents.push({ id: String(m), rel: "mixin" }));
    }
    const tax = document.createElement("section");
    tax.className = "detail-block glossary-adr027-taxonomy";
    tax.innerHTML = `<h2>Taxonomy</h2>`;
    const taxRow = document.createElement("div");
    taxRow.className = "link-row";
    if (attrs.defined_in) {
      const defined = document.createElement("div");
      defined.className = "muted";
      defined.textContent = `defined in: ${attrs.defined_in}`;
      tax.appendChild(defined);
    }
    if (attrs.is_a_chain && attrs.is_a_chain.length) {
      const chain = document.createElement("div");
      chain.className = "muted glossary-isa-chain";
      chain.textContent = `is_a chain: ${attrs.is_a_chain.join(" ← ")}`;
      tax.appendChild(chain);
    }
    if (attrs.definition_depth != null && attrs.definition_depth !== "") {
      const depth = document.createElement("div");
      depth.className = "muted";
      depth.textContent = `depth: ${attrs.definition_depth}`;
      tax.appendChild(depth);
    }
    if (parents.length) {
      const pLabel = document.createElement("div");
      pLabel.className = "muted mixin-label";
      pLabel.textContent = "parents:";
      taxRow.appendChild(pLabel);
      parents.forEach((p) =>
        taxRow.appendChild(makeTermChip(relTargetId(p), relLabel(p)))
      );
    } else {
      taxRow.appendChild(document.createTextNode("No parents"));
    }
    if (children.length) {
      const cLabel = document.createElement("div");
      cLabel.className = "muted mixin-label";
      cLabel.textContent = "children:";
      taxRow.appendChild(cLabel);
      children.forEach((c) =>
        taxRow.appendChild(makeTermChip(relTargetId(c), relLabel(c)))
      );
    }
    tax.appendChild(taxRow);
    card.appendChild(tax);

    // See also (associative only — never parent/child)
    const seeAlso = Array.isArray(attrs.see_also) ? attrs.see_also : [];
    const see = document.createElement("section");
    see.className = "detail-block glossary-adr027-see-also";
    see.innerHTML = `<h2>See also</h2>`;
    if (!seeAlso.length) {
      const empty = document.createElement("p");
      empty.className = "muted";
      empty.textContent = "No associative links in this coverage.";
      see.appendChild(empty);
    } else {
      const row = document.createElement("div");
      row.className = "link-row";
      seeAlso.forEach((entry) =>
        row.appendChild(makeTermChip(relTargetId(entry), relLabel(entry)))
      );
      see.appendChild(row);
    }
    card.appendChild(see);

    // Assignment / mapping (equivalence family — separate heading)
    const assignments = []
      .concat(attrs.related_glossary_terms || [])
      .concat(attrs.glossary_term_refs || [])
      .concat(attrs.external_class_refs || []);
    if (assignments.length) {
      const asg = document.createElement("section");
      asg.className = "detail-block glossary-adr027-assignment";
      asg.innerHTML = `<h2>Assignment / mapping</h2>`;
      const row = document.createElement("div");
      row.className = "link-row";
      assignments.forEach((entry) => {
        const id = relTargetId(entry) || String(entry);
        const span = document.createElement("span");
        span.className = "spec-link disabled glossary-rel-chip";
        const mk = entry && entry.match_kind ? ` [${entry.match_kind}]` : "";
        span.textContent = id + mk;
        row.appendChild(span);
      });
      asg.appendChild(row);
      card.appendChild(asg);
    }

    // Origin (not genesis_kind)
    const origin = (attrs.origin || "").trim();
    if (origin) {
      const orig = document.createElement("section");
      orig.className = "detail-block glossary-adr027-origin";
      orig.innerHTML = `<h2>Origin</h2>`;
      const badge = document.createElement("span");
      badge.className = "glossary-origin-badge";
      badge.setAttribute("data-origin", origin);
      badge.textContent = origin;
      orig.appendChild(badge);
      if (attrs.source_release) {
        const rel = document.createElement("span");
        rel.className = "muted";
        rel.style.marginLeft = "8px";
        rel.textContent = String(attrs.source_release);
        orig.appendChild(rel);
      }
      card.appendChild(orig);
    }
  }

  function renderGlossaryTermDetail(mod, expl, item) {
    const card = document.createElement("article");
    card.className = "detail-card content-card";
    card.setAttribute("data-publication-item", "");
    card.setAttribute("data-module-id", mod.module_id || "");
    card.setAttribute("data-section-id", expl.id || "");
    card.setAttribute("data-item-id", item.id);
    card.setAttribute("data-item-type", item.attributes?.kind || "class");
    const attrs = item.attributes || {};
    const kind = attrs.kind || "class";
    const labelRu = (attrs.label_ru || "").trim();
    const titleExtra = labelRu
      ? ` <span class="muted">(${escapeHtml(labelRu)})</span>`
      : "";
    const badges = [];
    if (kind) badges.push(`<span class="badge-pill">${escapeHtml(kind)}</span>`);
    if (attrs.origin) {
      badges.push(
        `<span class="badge-pill glossary-origin-badge" data-origin="${escapeHtml(String(attrs.origin))}">${escapeHtml(String(attrs.origin))}</span>`
      );
    }
    card.innerHTML = `
      <header class="detail-head">
        <h1>${escapeHtml(item.title || item.id)}${titleExtra}</h1>
        <div class="badge-row">${badges.slice(0, 4).join("")}</div>
        <p class="muted">${escapeHtml(attrs.defined_in || attrs.source_domain || attrs.schema_key || "")}</p>
      </header>
    `;
    const defBlock = document.createElement("section");
    defBlock.className = "detail-block";
    defBlock.setAttribute("data-renderer", "definition");
    defBlock.innerHTML = `<h2>Definition</h2>`;
    const defEn = document.createElement("p");
    defEn.className = "detail-desc";
    defEn.textContent =
      displayText(item.description || attrs.definition || "No definition.");
    defBlock.appendChild(defEn);
    if (attrs.definition_ru) {
      const defRu = document.createElement("p");
      defRu.className = "detail-desc muted";
      defRu.textContent = displayText(String(attrs.definition_ru));
      defBlock.appendChild(defRu);
    }
    card.appendChild(defBlock);

    const known = collectExplorerIds(expl);
    appendAdr027RelationBlocks(card, mod, item, {
      known,
      expl,
      sectionId: expl.id,
    });
    return card;
  }

  function renderOntologyExplorerDetail(mod, expl, item) {
    const card = document.createElement("article");
    card.className = "detail-card content-card";
    card.setAttribute("data-publication-item", "");
    card.setAttribute("data-module-id", mod.module_id || "");
    card.setAttribute("data-section-id", expl.id || "");
    card.setAttribute("data-item-id", item.id);
    card.setAttribute("data-item-type", item.attributes?.kind || "class");
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
        <div class="badge-row">${badges.slice(0, 3).join("")}</div>
        <p class="muted">${escapeHtml(attrs.source_domain || attrs.ontology_id || "")}</p>
      </header>
    `;

    const defBlock = document.createElement("section");
    defBlock.className = "detail-block";
    defBlock.setAttribute("data-renderer", "definition");
    defBlock.innerHTML = `<h2>Definition</h2>`;
    const defEn = document.createElement("p");
    defEn.className = "detail-desc";
    defEn.textContent =
      displayText(item.description || attrs.definition || "No definition.");
    defBlock.appendChild(defEn);
    if (attrs.definition_ru) {
      const ruHead = document.createElement("h3");
      ruHead.className = "muted";
      ruHead.style.fontSize = "var(--font-sm)";
      ruHead.style.fontWeight = "600";
      ruHead.textContent = "Русское определение";
      defBlock.appendChild(ruHead);
      const defRu = document.createElement("p");
      defRu.className = "detail-desc";
      defRu.textContent = displayText(String(attrs.definition_ru));
      defBlock.appendChild(defRu);
    }
    card.appendChild(defBlock);

    const idBlock = document.createElement("section");
    idBlock.className = "detail-block";
    idBlock.innerHTML = `<h2>Identity</h2>`;
    const dl = document.createElement("dl");
    dl.className = "detail-meta definition-list";
    if (attrs.iri) {
      const wrap = document.createElement("span");
      wrap.style.display = "inline-flex";
      wrap.style.alignItems = "center";
      wrap.style.gap = "8px";
      wrap.style.minWidth = "0";
      const code = document.createElement("code");
      code.className = "middle-ellipsis";
      code.title = String(attrs.iri);
      code.textContent = String(attrs.iri);
      const copyBtn = document.createElement("button");
      copyBtn.type = "button";
      copyBtn.className = "copy-btn";
      copyBtn.setAttribute("aria-label", "Copy IRI");
      copyBtn.textContent = "Copy";
      copyBtn.addEventListener("click", () => {
        navigator.clipboard?.writeText(String(attrs.iri)).then(
          () => announce("IRI copied"),
          () => announce("Copy failed")
        );
      });
      wrap.appendChild(code);
      wrap.appendChild(copyBtn);
      appendMetaRow(dl, "iri", wrap);
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

  function highlightYamlLine(line) {
    const m = line.match(/^(\s*)([^:#\s][^:]*)(:)(.*)$/);
    if (m) {
      return (
        escapeHtml(m[1]) +
        `<span class="yaml-key">${escapeHtml(m[2])}</span>` +
        escapeHtml(m[3]) +
        escapeHtml(m[4])
      );
    }
    return escapeHtml(line);
  }

  function renderYamlFold(text) {
    const root = document.createElement("div");
    root.className = "yaml-fold";
    const lines = String(text || "").split("\n");
    const nodes = lines.map((line, index) => ({
      line,
      index,
      indent: (line.match(/^ */)?.[0] || "").length,
      children: [],
    }));
    const stack = [{ indent: -1, children: [] }];
    nodes.forEach((node) => {
      while (stack.length > 1 && node.indent <= stack[stack.length - 1].indent) {
        stack.pop();
      }
      stack[stack.length - 1].children.push(node);
      const trimmed = node.line.trim();
      const canNest =
        trimmed &&
        !trimmed.startsWith("#") &&
        /:\s*(#.*)?$/.test(trimmed) &&
        !/: .+$/.test(trimmed.replace(/\s+#.*$/, ""));
      if (canNest) stack.push(node);
    });

    function renderNodes(list, into) {
      list.forEach((node) => {
        const row = document.createElement("div");
        row.className = "yaml-line";
        const hasKids = node.children && node.children.length;
        if (hasKids) {
          const toggle = document.createElement("button");
          toggle.type = "button";
          toggle.className = "yaml-fold-toggle";
          toggle.textContent = "−";
          const block = document.createElement("div");
          block.className = "yaml-fold-block";
          toggle.addEventListener("click", () => {
            const collapsed = block.hidden;
            block.hidden = !collapsed;
            toggle.textContent = collapsed ? "−" : "+";
          });
          row.appendChild(toggle);
          const code = document.createElement("code");
          code.innerHTML = highlightYamlLine(node.line);
          row.appendChild(code);
          into.appendChild(row);
          renderNodes(node.children, block);
          into.appendChild(block);
        } else {
          const spacer = document.createElement("span");
          spacer.className = "yaml-fold-spacer";
          spacer.textContent = "·";
          row.appendChild(spacer);
          const code = document.createElement("code");
          code.innerHTML = highlightYamlLine(node.line);
          row.appendChild(code);
          into.appendChild(row);
        }
      });
    }

    renderNodes(stack[0].children, root);
    return root;
  }

  function renderRequirementDetail(item) {
    const card = document.createElement("article");
    card.className = "detail-card requirement-card";
    const attrs = item.attributes || {};
    const code = attrs.code || item.title || item.id;
    const level = attrs.requirement_level || "";
    const section = attrs.requirement_section || "";
    const title = attrs.title || attrs.name || "";
    const statusInfo = requirementStatusInfo(attrs.lifecycle_status);
    const reqGlyph = resolveNavGlyph(attrs);
    const levelSection =
      String(section).toUpperCase() === "LDM" ||
      String(section).toUpperCase() === "PDM"
        ? String(section).toLowerCase()
        : "";
    const cardGlyph = LEVEL_GLYPHS.has(reqGlyph)
      ? reqGlyph
      : levelSection || (level === "conceptual_model" ? "cdm" : "");
    const titleBadge = LEVEL_GLYPHS.has(cardGlyph)
      ? navGlyphHtml(cardGlyph, "card")
      : requirementMarkHtml(attrs.lifecycle_status);
    const statusChipClass = `req-status-chip req-status--${statusInfo.cls}`;
    let statusChipHtml = `<span class="${statusChipClass}">${escapeHtml(statusInfo.label)}</span>`;
    if (statusInfo.key === "superseded" && attrs.superseded_by_item) {
      const targetId = String(attrs.superseded_by_item);
      const damsMod =
        modules.find(
          (m) =>
            m.module_id === "moex:module:dams" || shortModule(m.module_id) === "dams"
        ) || null;
      const explSec = damsMod ? explorerSection(damsMod) : null;
      const node = damsMod ? nodeForModule(damsMod.module_id) : null;
      const href = itemHref({
        node: node ? node.id : currentNodeId,
        module: damsMod ? shortModule(damsMod.module_id) : "dams",
        section: explSec ? explSec.id : null,
        item: targetId,
      });
      statusChipHtml = `<a class="${statusChipClass}" href="${escapeHtml(href)}" title="${escapeHtml(String(attrs.superseded_by || targetId))}">${escapeHtml(statusInfo.label)}</a>`;
    } else if (statusInfo.key === "superseded" && attrs.superseded_by) {
      statusChipHtml = `<span class="${statusChipClass}" title="${escapeHtml(String(attrs.superseded_by))}">${escapeHtml(statusInfo.label)}</span>`;
    }
    card.innerHTML = `
      <header class="detail-head">
        <h1>${titleBadge}${escapeHtml(String(code))}${statusChipHtml}</h1>
        <div class="badge-row">
          <span class="badge-pill">requirement</span>
          ${section && !LEVEL_GLYPHS.has(cardGlyph) ? `<span class="badge-pill">${escapeHtml(String(section))}</span>` : ""}
          ${level ? `<span class="badge-pill">${escapeHtml(String(level))}</span>` : ""}
        </div>
        <p class="muted">${escapeHtml(title)}</p>
      </header>
      <section class="detail-block">
        <h2>Формулировка</h2>
        <p class="detail-desc requirement-statement">${escapeHtml(attrs.statement || "—")}</p>
      </section>
    `;

    const checks = Array.isArray(attrs.formal_checks) ? attrs.formal_checks : [];
    const checkBlock = document.createElement("section");
    checkBlock.className = "detail-block";
    checkBlock.innerHTML = `<h2>Формальные проверки (${checks.length})</h2>`;
    if (!checks.length) {
      checkBlock.innerHTML += `<p class="muted">Нет проверок.</p>`;
    } else {
      const table = document.createElement("table");
      table.className = "data-table requirement-checks";
      table.innerHTML = `<thead><tr>
        <th>check_id</th><th>kind</th><th>target</th><th>severity</th><th>diagnostic</th>
      </tr></thead>`;
      const tbody = document.createElement("tbody");
      checks.forEach((ch) => {
        const tr = document.createElement("tr");
        const target = [ch.target_class, ch.target_slot, ch.target_path]
          .filter(Boolean)
          .join(" · ");
        tr.innerHTML = `
          <td><code>${escapeHtml(String(ch.check_id || ""))}</code></td>
          <td>${escapeHtml(String(ch.kind || ""))}</td>
          <td>${escapeHtml(target)}</td>
          <td>${escapeHtml(String(ch.severity || ""))}</td>
          <td><code>${escapeHtml(String(ch.diagnostic_code || ""))}</code></td>
        `;
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      const scroll = document.createElement("div");
      scroll.className = "table-scroll data-table-shell";
      scroll.appendChild(table);
      checkBlock.appendChild(scroll);
    }
    card.appendChild(checkBlock);

    const meta = document.createElement("section");
    meta.className = "detail-block";
    meta.innerHTML = `<h2>Метаданные</h2>`;
    const dl = document.createElement("dl");
    dl.className = "detail-meta";
    if (attrs.element_id) appendMetaRow(dl, "element_id", String(attrs.element_id));
    if (attrs.lifecycle_status) {
      appendMetaRow(dl, "lifecycle_status", String(attrs.lifecycle_status));
    }
    if (attrs.description) appendMetaRow(dl, "description", String(attrs.description));
    meta.appendChild(dl);
    card.appendChild(meta);
    return card;
  }

  function sourceFileItemFromSection(section) {
    const raw = (section.items || [])[0] || {};
    const attrs = { ...(raw.attributes || {}) };
    if (!attrs.kind) attrs.kind = "source_file";
    if (!attrs.path && section.source_path) attrs.path = section.source_path;
    return {
      id: raw.id || `file:${section.id}`,
      title: section.title || raw.title || attrs.file_name || section.id,
      description: section.description || raw.description || attrs.description || "",
      attributes: attrs,
    };
  }

  function renderSourceFileSection(mod, section) {
    const item = sourceFileItemFromSection(section);
    // Minimal explorer stub so dependency deep-links stay no-ops when refs empty.
    const explStub = { id: section.id, items: section.items || [] };
    return renderSourceFileDetail(mod, explStub, item);
  }

  function renderSourceFileDetail(mod, expl, item) {
    const card = document.createElement("article");
    card.className = "detail-card content-card";
    card.setAttribute("data-publication-item", "");
    card.setAttribute("data-item-id", item.id);
    card.setAttribute("data-item-type", "source_file");
    const attrs = item.attributes || {};
    const version = attrs.version || "";
    const refsOut = Array.isArray(attrs.refs_out) ? attrs.refs_out : [];
    const refsIn = Array.isArray(attrs.refs_in) ? attrs.refs_in : [];
    const fileName = String(attrs.file_name || attrs.path || "")
      .replace(/\\/g, "/")
      .split("/")
      .filter(Boolean)
      .pop();
    const heading =
      item.title && fileName && item.title !== fileName
        ? `${item.title} [${fileName}]`
        : item.title || fileName || item.id;
    card.innerHTML = `
      <header class="detail-head">
        <h1>${yamlFileMarkHtml()}${escapeHtml(heading)}</h1>
        <div class="badge-row">
          <span class="badge-pill">YAML</span>
          ${version ? `<span class="badge-pill">${escapeHtml(String(version))}</span>` : ""}
        </div>
        <p class="muted">${escapeHtml(attrs.path || "")}</p>
      </header>
      <p class="detail-desc">${escapeHtml(displayText(attrs.description || item.description || "No description."))}</p>
    `;

    function fillRefList(container, title, refs) {
      const sec = document.createElement("section");
      sec.className = "detail-block";
      sec.innerHTML = `<h2>${escapeHtml(title)} (${refs.length})</h2>`;
      if (!refs.length) {
        sec.innerHTML += `<p class="muted">None.</p>`;
        container.appendChild(sec);
        return;
      }
      const ul = document.createElement("div");
      ul.className = "impl-list";
      refs.forEach((refId) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "spec-link";
        const found = findExplorerItem(expl, refId);
        btn.textContent = found?.item?.title || refId;
        btn.addEventListener("click", () => {
          const node = nodeForModule(mod.module_id);
          setHash({
            node: node ? node.id : null,
            module: shortModule(mod.module_id),
            section: expl.id,
            item: refId,
          });
          showModule(mod.module_id, { section: expl.id, item: refId });
        });
        ul.appendChild(btn);
      });
      sec.appendChild(ul);
      container.appendChild(sec);
    }

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
          if (attrs.path) appendMetaRow(dl, "path", String(attrs.path));
          if (version) appendMetaRow(dl, "version", String(version));
          appendMetaRow(dl, "imports", String(refsOut.length));
          appendMetaRow(dl, "imported_by", String(refsIn.length));
          meta.appendChild(dl);
          panel.appendChild(meta);
        },
      },
      {
        id: "dependencies",
        label: "Dependencies",
        count: refsOut.length + refsIn.length,
        render(panel) {
          fillRefList(panel, "Imports", refsOut);
          fillRefList(panel, "Imported by", refsIn);
        },
      },
      {
        id: "source",
        label: "Source",
        render(panel) {
          const body = document.createElement("section");
          body.className = "detail-block";
          body.setAttribute("data-renderer", "source-code");
          body.innerHTML = `<h2>Source</h2>`;
          body.appendChild(renderYamlFold(attrs.text || ""));
          panel.appendChild(body);
        },
      },
    ], { initial: "overview" });
    return card;
  }

  function renderImplementationRefDetail(item) {
    const card = document.createElement("article");
    card.className = "detail-card";
    const attrs = item.attributes || {};
    const cat = catalogNode(attrs.catalog_node_id || item.id);
    const desc =
      item.description ||
      attrs.description ||
      cat?.description ||
      `Registered implementation conforming to ${attrs.conforms_to || "specification"}.`;
    const kidCount = (item.children || []).length;
    card.innerHTML = `
      <header class="detail-head">
        <h1>${escapeHtml(item.title || item.id)}</h1>
        <div class="badge-row">
          <span class="badge-pill">implementation</span>
          ${attrs.version ? `<span class="badge-pill">${escapeHtml(String(attrs.version))}</span>` : ""}
          ${kidCount ? `<span class="badge-pill">${kidCount} sections</span>` : ""}
        </div>
        <p class="muted">${escapeHtml(attrs.catalog_node_id || item.id)}</p>
      </header>
      <p class="detail-desc">${escapeHtml(desc)}</p>
    `;
    if (kidCount) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "spec-link";
      btn.textContent = "Reveal sections";
      btn.addEventListener("click", () => {
        openGroups.add("group:implementations");
        openGroups.add(item.id);
        const first = item.children[0];
        const targetMod =
          first?.attributes?.target_module_id || attrs.module_id;
        const sectionId =
          first?.attributes?.section_id || first?.attributes?.target_section_id;
        if (targetMod && sectionId) {
          const node = catalogNode(attrs.catalog_node_id || item.id);
          if (node?.conforms_to) {
            openGroups.add(catalogOpenKey(node.conforms_to));
          }
          if (node) currentNodeId = node.id;
          setHash({
            node: node ? node.id : null,
            module: shortModule(targetMod),
            section: sectionId,
          });
          showModule(targetMod, { section: sectionId });
          return;
        }
        renderModuleNav({
          item: item.id,
          section: explorerSection(modules.find((m) => m.module_id === currentModuleId))
            ?.id,
        });
      });
      card.appendChild(btn);
    }
    return card;
  }

  function renderCatalogIdentityCard(node, mod) {
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
    const desc =
      node.description ||
      mod?.description ||
      "No description for this architecture node yet.";
    card.innerHTML = `
      <header class="detail-head">
        <h1>${escapeHtml(node.title)}</h1>
        <div class="badge-row">${badges.join("")}</div>
        <p class="muted">${escapeHtml(node.id)}</p>
      </header>
      <p class="detail-desc">${escapeHtml(desc)}</p>
    `;
    if (node.role === "reference_specification") {
      const block = renderImplementationsBlock(node);
      return { card, block };
    }
    return { card, block: null };
  }

  function renderExplorerDetail(mod, expl, item, group) {
    const card = document.createElement("article");
    card.className = "detail-card content-card";
    card.setAttribute("data-publication-item", "");
    card.setAttribute("data-module-id", mod.module_id || "");
    card.setAttribute("data-section-id", expl.id || "");
    card.setAttribute("data-item-id", item.id);
    card.setAttribute("data-item-type", item.attributes?.kind || "class");
    const kind = item.attributes?.kind || "class";
    const abstract = item.attributes?.abstract;
    const isMixin = item.attributes?.mixin;
    const treeRoot = item.attributes?.tree_root;
    const fromSchema = item.attributes?.from_schema || item.attributes?.schema_key || "";
    const known = collectExplorerIds(expl);

    if (kind === "source_file") {
      return renderSourceFileDetail(mod, expl, item);
    }
    if (kind === "requirement") {
      return renderRequirementDetail(item);
    }
    if (kind === "implementation_ref") {
      return renderImplementationRefDetail(item);
    }
    if (isGlossaryViewItem(item)) {
      return renderGlossaryTermDetail(mod, expl, item);
    }

    if (kind === "group") {
      const purpose = displayText(item.attributes?.purpose || item.description || "");
      const structureWhy = displayText(item.attributes?.structure_why || "");
      const classCount = item.attributes?.class_count ?? 0;
      const enumCount = item.attributes?.enum_count ?? 0;
      const sectionRoot = item.attributes?.section_root;
      const groupBadge = sectionRoot
        ? "section"
        : item.attributes?.ontology_id
          ? "ontology"
          : item.attributes?.source_domain
            ? "domain"
            : "package";
      const groupLevelGlyph = resolveNavGlyph(item.attributes);
      let groupTitleBadge = "";
      if (LEVEL_GLYPHS.has(groupLevelGlyph)) {
        groupTitleBadge = navGlyphHtml(groupLevelGlyph, "card");
      } else if (isSchemaPackageGroup(item.attributes)) {
        groupTitleBadge = sectionMajorityGlyphHtml(item);
      }
      card.innerHTML = `
        <header class="detail-head">
          <h1>${groupTitleBadge}${escapeHtml(item.title || item.id)}</h1>
          <div class="badge-row"><span class="badge-pill">${groupBadge}</span></div>
          <p class="muted">${escapeHtml(item.attributes?.source_file || item.attributes?.schema_key || item.attributes?.ontology_id || item.attributes?.source_domain || sectionRoot || "")}</p>
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
      meta.innerHTML = `<h2>${sectionRoot ? "Раздел" : "Пакет"}</h2>`;
      const dl = document.createElement("dl");
      dl.className = "detail-meta";
      if (item.attributes?.schema_key) {
        appendMetaRow(dl, "schema_key", String(item.attributes.schema_key));
      }
      if (item.attributes?.source_file) {
        appendMetaRow(dl, "source_file", String(item.attributes.source_file));
      }
      if (sectionRoot === "spec-files") {
        appendMetaRow(
          dl,
          "files",
          String(item.attributes?.file_count ?? (item.children || []).length)
        );
      } else if (sectionRoot === "requirements") {
        appendMetaRow(
          dl,
          "requirements",
          String(item.attributes?.requirement_count ?? 0)
        );
        appendMetaRow(
          dl,
          "minimal_files",
          String(item.attributes?.file_count ?? 0)
        );
      } else if (
        sectionRoot === "requirements-list" ||
        sectionRoot === "requirements-it-spec" ||
        sectionRoot === "requirements-it-solutions" ||
        sectionRoot === "requirements-model-example" ||
        sectionRoot === "requirements-conceptual" ||
        sectionRoot === "requirements-conceptual-list" ||
        sectionRoot === "requirements-conceptual-spec" ||
        sectionRoot === "requirements-publication" ||
        sectionRoot === "requirements-publication-list" ||
        sectionRoot === "requirements-publication-spec"
      ) {
        if (item.attributes?.requirement_count != null) {
          appendMetaRow(
            dl,
            "requirements",
            String(item.attributes.requirement_count)
          );
        }
        if (item.attributes?.file_count != null) {
          appendMetaRow(dl, "files", String(item.attributes.file_count));
        }
      } else if (sectionRoot === "implementations") {
        appendMetaRow(
          dl,
          "implementations",
          String(item.attributes?.impl_count ?? (item.children || []).length)
        );
      } else if (!sectionRoot) {
        appendMetaRow(dl, "classes", String(classCount));
        appendMetaRow(dl, "enums", String(enumCount));
      } else if (sectionRoot === "classes") {
        appendMetaRow(dl, "classes", String(classCount));
        appendMetaRow(dl, "enums", String(enumCount));
      }
      meta.appendChild(dl);
      card.appendChild(meta);

      const members = item.children || [];
      appendExplorerCompositionBlock(card, "Состав", members, {
        mod,
        expl,
        openGroupId: item.id,
        emptyMessage: "Пустой пакет.",
      });
      return card;
    }

    if (kind !== "enum" && isOntologyExplorerItem(item, expl)) {
      return renderOntologyExplorerDetail(mod, expl, item);
    }


    const badges = [];
    if (kind === "enum") {
      badges.push(`<span class="badge-pill badge-kind-enum">enum</span>`);
    } else if (kind) {
      badges.push(`<span class="badge-pill">${escapeHtml(kind)}</span>`);
    }
    if (abstract) badges.push(`<span class="badge-pill">abstract</span>`);
    if (isMixin) badges.push(`<span class="badge-pill badge-kind-mixin">mixin</span>`);
    if (kind === "class" && classHasMixins(item.attributes)) {
      badges.push(`<span class="badge-pill badge-kind-mixin">has mixin</span>`);
    }
    // Keep at most 4 badges in the header row (class/abstract/mixin/has mixin)
    const headerBadges = badges.slice(0, 4);

    const titleBadge =
      kind === "class"
        ? `<span class="nav-kind ${classKindClassNames(item.attributes)}" aria-hidden="true">C</span> `
        : kind === "enum"
          ? `<span class="nav-kind ${classKindClassNames(item.attributes)}" aria-hidden="true">E</span> `
          : "";

    card.innerHTML = `
      <header class="detail-head">
        <h1>${titleBadge}${escapeHtml(item.title || item.id)}</h1>
        <div class="badge-row">${headerBadges.join("")}</div>
        <p class="muted">${escapeHtml(fromSchema)}</p>
      </header>
      <p class="detail-desc">${escapeHtml(displayText(item.description || "No description."))}</p>
    `;

    function findSourceFileId() {
      const key = item.attributes?.schema_key || item.attributes?.source_file || "";
      if (!key) return null;
      let hit = null;
      walkExplorerItems(expl, (node) => {
        if (hit) return;
        if (node.attributes?.kind !== "source_file") return;
        const path = String(node.attributes?.path || node.title || node.id);
        const fileName = String(node.attributes?.file_name || "");
        if (
          path.endsWith(key) ||
          path.includes(key) ||
          node.id.includes(key) ||
          fileName === key ||
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
      const classById = indexExplorerClasses(expl);
      const ancestors = collectClassAncestors(item, classById);
      const descendants = collectClassDescendants(item.id, classById);
      const instances = collectClassInstances(item.id);

      function renderObjectsTab(panel) {
        const body = document.createElement("section");
        body.className = "detail-block";
        body.innerHTML = `<h2>Objects</h2>`;
        if (!instances.length) {
          body.innerHTML += `<p class="muted">No instances of this class in compiled publications.</p>`;
          panel.appendChild(body);
          return;
        }

        const itSolutions = itSolutionModuleIds();
        const toolbar = document.createElement("div");
        toolbar.className = "section-toolbar";
        const filterSelects = document.createElement("div");
        filterSelects.className = "chips";
        const sel = document.createElement("select");
        sel.innerHTML =
          `<option value="">IT solution: all</option>` +
          itSolutions
            .map(
              (opt) =>
                `<option value="${escapeHtml(opt.moduleId)}">${escapeHtml(
                  opt.title
                )}</option>`
            )
            .join("");
        filterSelects.appendChild(sel);
        toolbar.appendChild(filterSelects);
        body.appendChild(toolbar);

        const listHost = document.createElement("div");
        body.appendChild(listHost);

        function paintObjects() {
          listHost.innerHTML = "";
          const filterMid = sel.value;
          const visible = filterMid
            ? instances.filter((hit) => hit.mod.module_id === filterMid)
            : instances;
          if (!visible.length) {
            const empty = document.createElement("p");
            empty.className = "muted";
            empty.textContent = filterMid
              ? "No instances in the selected IT solution."
              : "No instances of this class in compiled publications.";
            listHost.appendChild(empty);
            return;
          }
          const byMod = new Map();
          visible.forEach((hit) => {
            const key = hit.mod.module_id;
            if (!byMod.has(key)) byMod.set(key, { mod: hit.mod, hits: [] });
            byMod.get(key).hits.push(hit);
          });
          byMod.forEach(({ mod: pubMod, hits }) => {
            const group = document.createElement("div");
            group.className = "objects-pub-group";
            const h3 = document.createElement("h3");
            h3.textContent = `${pubMod.title || pubMod.module_id} (${hits.length})`;
            group.appendChild(h3);
            const list = document.createElement("div");
            list.className = "explorer-class-list";
            hits.forEach(({ mod: hitMod, section, item: row }) => {
              const btn = document.createElement("button");
              btn.type = "button";
              btn.className = "spec-link explorer-chip";
              const label =
                row.attributes?.name || row.title || row.id;
              btn.innerHTML = `<span>${escapeHtml(label)}</span>`;
              btn.title = row.id;
              btn.addEventListener("click", () => {
                const node = nodeForModule(hitMod.module_id);
                setHash({
                  node: node ? node.id : null,
                  module: shortModule(hitMod.module_id),
                  section: section.id,
                  item: row.id,
                });
                if (node) currentNodeId = node.id;
                showModule(hitMod.module_id, {
                  section: section.id,
                  item: row.id,
                });
              });
              list.appendChild(btn);
            });
            group.appendChild(list);
            listHost.appendChild(group);
          });
        }

        sel.addEventListener("change", paintObjects);
        paintObjects();
        panel.appendChild(body);
      }

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
          id: "objects",
          label: "Objects",
          count: instances.length,
          render: renderObjectsTab,
        },
        {
          id: "source",
          label: "Source",
          render: renderSourceTab,
        },
      ], { initial: "overview" });

      appendExplorerCompositionBlock(card, "Состав", ancestors, {
        mod,
        expl,
        emptyMessage: "Нет родителей.",
      });
      appendExplorerCompositionBlock(card, "Наследники", descendants, {
        mod,
        expl,
        emptyMessage: "Нет наследников.",
      });
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

  function makeBlankAnchor(href, text, className) {
    const a = document.createElement("a");
    a.className = className || "spec-link";
    a.href = href;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    a.textContent = text;
    return a;
  }

  function makeSpecLink(mod, expl, name, known, label) {
    const text = label ? `${label}: ${name}` : name;
    if (!known.has(name)) {
      const span = document.createElement("span");
      span.className = "spec-link disabled";
      span.textContent = text;
      return span;
    }
    const node = nodeForModule(mod.module_id);
    const href = itemHref({
      node: node ? node.id : currentNodeId,
      module: shortModule(mod.module_id),
      section: expl.id,
      item: name,
    });
    return makeBlankAnchor(href, text, "spec-link");
  }

  function makeFiboLink(itemId) {
    const node = nodeForModule("moex:module:fibo");
    const href = itemHref({
      node: node ? node.id : null,
      module: "fibo",
      section: "glossary",
      item: itemId,
    });
    return makeBlankAnchor(href, `FIBO: ${itemId}`, "spec-link");
  }

  function findDamsClassItem(className) {
    if (!className) return null;
    const dams = modules.find(
      (m) => m.module_id === "moex:module:dams" || shortModule(m.module_id) === "dams"
    );
    if (!dams) return null;
    const expl = explorerSection(dams);
    if (!expl) return null;
    const found = findExplorerItem(expl, className);
    return found ? { mod: dams, expl, item: found.item } : null;
  }

  function findSectionItem(section, itemId) {
    if (!section || !itemId) return null;
    return (section.items || []).find((it) => it.id === itemId) || null;
  }

  function renderLinkedValue(raw, mod) {
    const target = ensureLinkIndex().resolve(raw, mod);
    if (!target || !target.card) {
      const span = document.createElement("span");
      span.textContent = String(raw ?? "");
      return span;
    }
    const href = itemHref(target);
    return makeBlankAnchor(href, String(raw), "table-item-link");
  }

  function appendMetaValue(dl, label, valueNode) {
    const dt = document.createElement("dt");
    dt.textContent = label;
    const dd = document.createElement("dd");
    if (typeof valueNode === "string") dd.textContent = valueNode;
    else if (valueNode) dd.appendChild(valueNode);
    else dd.textContent = "—";
    dl.appendChild(dt);
    dl.appendChild(dd);
  }

  function renderNestedAttributesTable(nestedItems, emptyMessage) {
    const slotBlock = document.createElement("section");
    slotBlock.className = "detail-block";
    slotBlock.setAttribute("data-renderer", "properties-table");
    slotBlock.innerHTML = `<h2>Attributes</h2>`;
    if (!nestedItems.length) {
      slotBlock.innerHTML += `<p class="muted">${escapeHtml(emptyMessage || "No attributes defined.")}</p>`;
      return slotBlock;
    }
    const table = document.createElement("table");
    table.className = "data-table detail-slots";
    table.innerHTML = `<thead><tr>
      <th>Attribute</th><th>Type</th><th>Required</th><th>Multiple</th>
      <th>Declared</th><th>Description</th>
    </tr></thead>`;
    const tbody = document.createElement("tbody");
    nestedItems.forEach((slot) => {
      const attrs = slot.attributes || {};
      const tr = document.createElement("tr");
      const nameTd = document.createElement("td");
      nameTd.textContent = attrs.name || slot.title || slot.id || "";
      const rangeTd = document.createElement("td");
      rangeTd.textContent = attrs.logical_type || attrs.native_type || attrs.range || "";
      tr.appendChild(nameTd);
      tr.appendChild(rangeTd);
      [["required", attrs.required], ["multivalued", attrs.multivalued]].forEach(([, flag]) => {
        const td = document.createElement("td");
        td.textContent = yesBlank(flag) || "No";
        tr.appendChild(td);
      });
      const declTd = document.createElement("td");
      declTd.textContent = "Yes";
      tr.appendChild(declTd);
      const desc = document.createElement("td");
      desc.textContent = slot.description || attrs.description || "";
      tr.appendChild(desc);
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    const scroll = document.createElement("div");
    scroll.className = "table-scroll data-table-shell";
    scroll.appendChild(table);
    slotBlock.appendChild(scroll);
    return slotBlock;
  }

  function implGlossaryTermHref(mod, section, termId) {
    if (!termId || !section) return null;
    const hit = resolveItemInGlossary(section, termId);
    if (!hit) return null;
    return itemHref({
      module: shortModule(mod.module_id),
      section: section.id,
      item: hit.id,
      node: nodeForModule(mod.module_id)?.id || currentNodeId,
    });
  }

  function appendImplTermLink(parent, mod, section, termId, label) {
    const href = implGlossaryTermHref(mod, section, termId);
    const text = label || termId || "—";
    if (!href) {
      const span = document.createElement("span");
      span.className = "muted";
      span.textContent = text;
      parent.appendChild(span);
      return;
    }
    parent.appendChild(makeBlankAnchor(href, text, "spec-link"));
  }

  function renderImplTermDetail(mod, section, item) {
    const attrs = item.attributes || {};
    const card = document.createElement("article");
    card.className = "detail-card content-card";
    card.setAttribute("data-publication-item", "");
    card.setAttribute("data-module-id", mod.module_id || "");
    card.setAttribute("data-section-id", section.id || "");
    card.setAttribute("data-item-id", item.id);
    card.setAttribute("data-item-type", "impl-term");
    card.setAttribute("data-instance-of", attrs.instance_of || "");

    const level = String(attrs.model_level || "").trim();
    const solution = String(attrs.solution || "").trim();
    const mode = String(attrs.definition_mode || "").trim();
    const kind = String(attrs.kind || "").trim();
    const badges = [];
    if (level) {
      badges.push(
        `<span class="badge-pill glossary-level-badge" data-level="${escapeHtml(level)}">${escapeHtml(level)}</span>`
      );
    }
    if (kind) badges.push(`<span class="badge-pill">${escapeHtml(kind)}</span>`);
    if (mode) {
      badges.push(
        `<span class="badge-pill glossary-mode-badge" data-mode="${escapeHtml(mode)}">${escapeHtml(mode)}</span>`
      );
    }
    if (attrs.redundant_override) {
      badges.push(`<span class="badge-pill glossary-redundant-badge">redundant override</span>`);
    }
    card.innerHTML = `
      <header class="detail-head">
        <h1>${escapeHtml(item.title || item.id)}</h1>
        <div class="badge-row">${badges.join("")}</div>
        <p class="muted">${escapeHtml(
          [solution, level, attrs.source_item_id || item.id].filter(Boolean).join(" · ")
        )}</p>
      </header>
    `;

    function linkToSourceElement(elementId) {
      if (!elementId) return null;
      // Prefer a glossary row that carries this source_item_id.
      const bySource = (section.items || []).find(
        (i) =>
          i.attributes?.source_item_id === elementId ||
          i.id === elementId ||
          String(i.id).endsWith(":" + elementId)
      );
      if (bySource) {
        return {
          href: itemHref({
            module: shortModule(mod.module_id),
            section: section.id,
            item: bySource.id,
            node: nodeForModule(mod.module_id)?.id || currentNodeId,
          }),
          label: bySource.title || elementId,
        };
      }
      return null;
    }

    function renderDefinitionTab(panel) {
      const def = document.createElement("section");
      def.className = "detail-block";
      def.setAttribute("data-renderer", "definition");
      def.innerHTML = `<h2>Определение</h2>
        <p class="detail-desc">${escapeHtml(
          displayText(item.description || attrs.definition || "No definition.")
        )}</p>`;
      panel.appendChild(def);

      const override = document.createElement("section");
      override.className = "detail-block";
      override.innerHTML = `<h2>Переопределение</h2>`;
      const dl = document.createElement("dl");
      dl.className = "detail-meta definition-list";
      appendMetaRow(dl, "режим", mode || "—");
      const sourceId = attrs.definition_source;
      if (sourceId) {
        const linked = linkToSourceElement(String(sourceId));
        if (linked) {
          appendMetaValue(
            dl,
            "источник",
            makeBlankAnchor(linked.href, linked.label, "spec-link")
          );
        } else {
          appendMetaRow(dl, "источник", String(sourceId));
        }
      } else {
        appendMetaRow(dl, "источник", "—");
      }
      if (attrs.definition_rationale) {
        appendMetaRow(dl, "rationale", String(attrs.definition_rationale));
      }
      if (attrs.definition_diagnostic) {
        appendMetaRow(dl, "диагностика", String(attrs.definition_diagnostic));
      }
      if (attrs.redundant_override) {
        appendMetaRow(
          dl,
          "избыточное переопределение",
          "собственный текст совпадает с эталонным (ADR-025)"
        );
      }
      override.appendChild(dl);
      panel.appendChild(override);

      const ownText =
        displayText(item.description || attrs.definition || "").trim();
      const refText = displayText(attrs.reference_definition || "").trim();
      if (ownText || refText) {
        const cmp = document.createElement("section");
        cmp.className = "detail-block";
        cmp.innerHTML = `<h2>Сравнение с эталоном</h2>`;
        const table = document.createElement("table");
        table.className = "data-table";
        table.innerHTML = `<thead><tr><th>Собственный текст</th><th>Эталонный (из концепта / источника)</th></tr></thead>
          <tbody><tr>
            <td>${escapeHtml(ownText || "—")}</td>
            <td>${escapeHtml(refText || "—")}</td>
          </tr></tbody>`;
        const scroll = document.createElement("div");
        scroll.className = "table-scroll data-table-shell";
        scroll.appendChild(table);
        cmp.appendChild(scroll);
        panel.appendChild(cmp);
      }

      const scoped = Array.isArray(attrs.scoped_definitions)
        ? attrs.scoped_definitions
        : [];
      const scopedBlock = document.createElement("section");
      scopedBlock.className = "detail-block";
      scopedBlock.innerHTML = `<h2>Scoped definitions</h2>`;
      if (!scoped.length) {
        scopedBlock.innerHTML += `<p class="muted">Нет scoped definitions.</p>`;
      } else {
        const table = document.createElement("table");
        table.className = "data-table";
        table.innerHTML = `<thead><tr>
          <th>scope_ref</th><th>relation</th><th>text</th><th>rationale</th>
        </tr></thead>`;
        const tbody = document.createElement("tbody");
        scoped.forEach((sd) => {
          if (!sd || typeof sd !== "object") return;
          const tr = document.createElement("tr");
          tr.innerHTML = `<td>${escapeHtml(String(sd.scope_ref || ""))}</td>
            <td>${escapeHtml(String(sd.relation_to_reference || ""))}</td>
            <td>${escapeHtml(String(sd.text || ""))}</td>
            <td>${escapeHtml(String(sd.rationale || ""))}</td>`;
          tbody.appendChild(tr);
        });
        table.appendChild(tbody);
        const scroll = document.createElement("div");
        scroll.className = "table-scroll data-table-shell";
        scroll.appendChild(table);
        scopedBlock.appendChild(scroll);
      }
      panel.appendChild(scopedBlock);
    }

    function renderChainTab(panel) {
      const cascade = document.createElement("section");
      cascade.className = "detail-block";
      cascade.innerHTML = `<h2>Каскад CDM → LDM</h2>`;
      const parents = Array.isArray(attrs.taxonomy_parents)
        ? attrs.taxonomy_parents
        : [];
      const children = Array.isArray(attrs.taxonomy_children)
        ? attrs.taxonomy_children
        : [];
      if (!parents.length && !children.length) {
        cascade.innerHTML += `<p class="muted">Нет связей каскада для этого термина.</p>`;
      } else {
        const row = document.createElement("div");
        row.className = "link-row";
        if (parents.length) {
          const lab = document.createElement("div");
          lab.className = "muted mixin-label";
          lab.textContent = "родители:";
          row.appendChild(lab);
          parents.forEach((p) => {
            const tid = relTargetId(p);
            const hit = resolveItemInGlossary(section, tid);
            appendImplTermLink(
              row,
              mod,
              section,
              tid,
              hit ? `${hit.title || tid} (${p.rel || "parent"})` : relLabel(p)
            );
          });
        }
        if (children.length) {
          const lab = document.createElement("div");
          lab.className = "muted mixin-label";
          lab.textContent = "дети / реализации:";
          row.appendChild(lab);
          children.forEach((c) => {
            const tid = relTargetId(c);
            const hit = resolveItemInGlossary(section, tid);
            appendImplTermLink(
              row,
              mod,
              section,
              tid,
              hit ? `${hit.title || tid} (${c.rel || "child"})` : relLabel(c)
            );
          });
        }
        cascade.appendChild(row);
      }
      panel.appendChild(cascade);

      const same = Array.isArray(attrs.see_also) ? attrs.see_also : [];
      const sameBlock = document.createElement("section");
      sameBlock.className = "detail-block";
      sameBlock.innerHTML = `<h2>Тот же концепт в других решениях</h2>`;
      if (!same.length) {
        sameBlock.innerHTML += `<p class="muted">Нет дубликатов в других реализациях.</p>`;
      } else {
        const row = document.createElement("div");
        row.className = "link-row";
        same.forEach((entry) => {
          const tid = relTargetId(entry);
          const hit = resolveItemInGlossary(section, tid);
          const sol = hit?.attributes?.solution || "";
          appendImplTermLink(
            row,
            mod,
            section,
            tid,
            hit
              ? `${hit.title || tid}${sol ? " · " + sol : ""}`
              : tid
          );
        });
        sameBlock.appendChild(row);
      }
      panel.appendChild(sameBlock);

      const ext = Array.isArray(attrs.external_class_refs)
        ? attrs.external_class_refs
        : [];
      const extBlock = document.createElement("section");
      extBlock.className = "detail-block";
      extBlock.innerHTML = `<h2>Внешние соответствия</h2>`;
      if (!ext.length) {
        extBlock.innerHTML += `<p class="muted">Нет external_class_refs.</p>`;
      } else {
        const row = document.createElement("div");
        row.className = "link-row";
        ext.forEach((entry) => {
          const span = document.createElement("span");
          span.className = "spec-link disabled glossary-rel-chip";
          const id = relTargetId(entry) || String(entry);
          const mk = entry && entry.match_kind ? ` [${entry.match_kind}]` : "";
          span.textContent = id + mk;
          row.appendChild(span);
        });
        extBlock.appendChild(row);
      }
      panel.appendChild(extBlock);
    }

    function renderImplTab(panel) {
      const meta = document.createElement("section");
      meta.className = "detail-block";
      meta.innerHTML = `<h2>Реализация</h2>`;
      const dl = document.createElement("dl");
      dl.className = "detail-meta definition-list";
      appendMetaRow(dl, "решение", solution || "—");
      appendMetaRow(dl, "уровень", level || "—");
      appendMetaRow(dl, "element_id", String(attrs.source_item_id || item.id));
      if (attrs.entity_tier) appendMetaRow(dl, "entity_tier", String(attrs.entity_tier));
      if (attrs.genesis_kind) appendMetaRow(dl, "genesis_kind", String(attrs.genesis_kind));
      if (attrs.lifecycle_status) {
        appendMetaRow(dl, "lifecycle_status", String(attrs.lifecycle_status));
      }
      const aliases = attrs.aliases;
      if (Array.isArray(aliases) && aliases.length) {
        appendMetaRow(dl, "aliases", aliases.map(String).join(", "));
      } else if (aliases) {
        appendMetaRow(dl, "aliases", String(aliases));
      }
      meta.appendChild(dl);
      panel.appendChild(meta);

      const links = document.createElement("section");
      links.className = "detail-block";
      links.innerHTML = `<h2>Ссылки</h2>`;
      const row = document.createElement("div");
      row.className = "link-row";
      const implMid = attrs.impl_module_id;
      const implSec = attrs.impl_section_id;
      const sourceId = attrs.source_item_id;
      if (implMid && implSec && sourceId) {
        const node = nodeForModule(implMid);
        const href = itemHref({
          node: node ? node.id : currentNodeId,
          module: shortModule(implMid),
          section: implSec,
          item: sourceId,
        });
        row.appendChild(
          makeBlankAnchor(href, "Карточка сущности в реализации", "spec-link")
        );
      }
      if (implMid) {
        const node = nodeForModule(implMid);
        const href = itemHref({
          node: node ? node.id : null,
          module: shortModule(implMid),
          section: null,
          item: null,
        });
        row.appendChild(
          makeBlankAnchor(
            href,
            `Модуль: ${solution || shortModule(implMid)}`,
            "spec-link"
          )
        );
      }
      if (!row.childNodes.length) {
        links.innerHTML += `<p class="muted">Нет ссылок на реализацию.</p>`;
      } else {
        links.appendChild(row);
      }
      panel.appendChild(links);
    }

    mountTabs(
      card,
      [
        {
          id: "definition",
          label: "Определение",
          render: renderDefinitionTab,
        },
        {
          id: "chain",
          label: "Цепочка",
          render: renderChainTab,
        },
        {
          id: "implementation",
          label: "Реализация",
          render: renderImplTab,
        },
      ],
      { initial: "definition" }
    );
    return card;
  }

  function renderInstanceDetail(mod, section, item) {
    const className = section.instance_of;
    const damsClass = findDamsClassItem(className);
    const card = document.createElement("article");
    card.className = "detail-card content-card";
    card.setAttribute("data-publication-item", "");
    card.setAttribute("data-module-id", mod.module_id || "");
    card.setAttribute("data-section-id", section.id || "");
    card.setAttribute("data-item-id", item.id);
    card.setAttribute("data-item-type", "instance");
    card.setAttribute("data-instance-of", className || "");

    const titleBadge = `<span class="nav-kind kind-plain" aria-hidden="true">C</span> `;
    card.innerHTML = `
      <header class="detail-head">
        <h1>${titleBadge}${escapeHtml(item.title || item.attributes?.name || item.id)}</h1>
        <div class="badge-row"><span class="badge-pill">${escapeHtml(className || "instance")}</span></div>
        <p class="muted">${escapeHtml(item.id)}</p>
      </header>
      <p class="detail-desc">${escapeHtml(item.description || "No description.")}</p>
    `;

    const classSlots = damsClass?.item?.attributes?.slots || [];
    const nested = item.children || [];
    const attrs = item.attributes || {};

    function renderSourceTab(panel) {
      const sec = document.createElement("section");
      sec.className = "detail-block";
      sec.innerHTML = `<h2>Source</h2>`;
      const dl = document.createElement("dl");
      dl.className = "detail-meta definition-list";
      appendMetaRow(dl, "module", mod.module_id);
      appendMetaRow(dl, "section", section.id);
      appendMetaRow(dl, "instance_of", className || "—");
      if (mod.manifest_path) appendMetaRow(dl, "manifest", String(mod.manifest_path));
      sec.appendChild(dl);
      panel.appendChild(sec);
    }

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
          if (damsClass) {
            const typeLink = makeSpecLink(
              damsClass.mod,
              damsClass.expl,
              className,
              new Set([className]),
              "type"
            );
            appendMetaValue(dl, "type", typeLink);
          } else {
            appendMetaRow(dl, "type", className || "—");
          }
          appendMetaRow(dl, "element_id", item.id);
          appendMetaRow(dl, "name", String(attrs.name || item.title || ""));
          if (item.title) appendMetaRow(dl, "title", String(item.title));
          // Class-template slots with scalar values on the instance
          classSlots.forEach((slot) => {
            const sn = slot.name;
            if (!sn || sn === "attributes" || sn === "physical_fields" || sn === "description") {
              return;
            }
            if (!(sn in attrs) || attrs[sn] === null || attrs[sn] === undefined || attrs[sn] === "") {
              return;
            }
            const val = attrs[sn];
            if (Array.isArray(val)) {
              const wrap = document.createElement("span");
              wrap.className = "link-row";
              val.forEach((v, i) => {
                if (i) wrap.appendChild(document.createTextNode(", "));
                wrap.appendChild(renderLinkedValue(v, mod));
              });
              appendMetaValue(dl, sn, wrap);
            } else if (typeof val !== "object") {
              const asRef = /_refs?$/.test(sn) || sn.endsWith("_ref");
              appendMetaValue(dl, sn, asRef ? renderLinkedValue(val, mod) : String(val));
            }
          });
          meta.appendChild(dl);
          panel.appendChild(meta);
        },
      },
      {
        id: "attributes",
        label: "Attributes",
        count: nested.length || classSlots.length,
        render(panel) {
          if (nested.length) {
            panel.appendChild(
              renderNestedAttributesTable(nested, "No attributes defined for this entity.")
            );
            return;
          }
          // Fall back to class slot template with instance values
          const slotBlock = document.createElement("section");
          slotBlock.className = "detail-block";
          slotBlock.setAttribute("data-renderer", "properties-table");
          slotBlock.innerHTML = `<h2>Attributes</h2>`;
          const valueSlots = classSlots.filter((s) => {
            const sn = s.name;
            return sn && sn in attrs && attrs[sn] !== null && attrs[sn] !== undefined && attrs[sn] !== "";
          });
          if (!valueSlots.length) {
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
          valueSlots.forEach((slot) => {
            const tr = document.createElement("tr");
            const nameTd = document.createElement("td");
            nameTd.textContent = slot.name || "";
            const rangeTd = document.createElement("td");
            rangeTd.textContent = slot.range || typeof attrs[slot.name];
            tr.appendChild(nameTd);
            tr.appendChild(rangeTd);
            [["required", slot.required], ["multivalued", slot.multivalued]].forEach(([, flag]) => {
              const td = document.createElement("td");
              td.textContent = yesBlank(flag) || "No";
              tr.appendChild(td);
            });
            const declTd = document.createElement("td");
            declTd.textContent = "Yes";
            tr.appendChild(declTd);
            const desc = document.createElement("td");
            const v = attrs[slot.name];
            desc.textContent = Array.isArray(v) ? v.join(", ") : String(v);
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
          const ranges = document.createElement("section");
          ranges.className = "detail-block";
          ranges.innerHTML = `<h2>Typed references</h2>`;
          const row = document.createElement("div");
          row.className = "link-row";
          const refKeys = [
            "conceptual_entity_refs",
            "context_ref",
            "key_attribute_refs",
            "source_entity_ref",
            "target_entity_ref",
            "relation_term_ref",
            "parent_concept_ref",
          ];
          let any = false;
          refKeys.forEach((key) => {
            const val = attrs[key];
            if (val === null || val === undefined || val === "") return;
            const list = Array.isArray(val) ? val : [val];
            list.forEach((v) => {
              const target = ensureLinkIndex().resolve(v, mod);
              if (!target || !target.card) return;
              any = true;
              const a = makeBlankAnchor(itemHref(target), `${key}: ${v}`, "spec-link");
              row.appendChild(a);
            });
          });
          if (!any) {
            ranges.innerHTML += `<p class="muted">No outbound type references.</p>`;
          } else {
            ranges.appendChild(row);
          }
          panel.appendChild(ranges);

          if (damsClass) {
            const inh = document.createElement("section");
            inh.className = "detail-block";
            inh.innerHTML = `<h2>Inheritance</h2>`;
            const list = document.createElement("div");
            list.className = "link-row";
            list.appendChild(
              makeSpecLink(
                damsClass.mod,
                damsClass.expl,
                className,
                new Set([className]),
                "instance_of"
              )
            );
            inh.appendChild(list);
            panel.appendChild(inh);
          }
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

  function renderSection(mod, section, opts) {
    const forceOpen = !!(opts && opts.forceOpen);
    const wrap = document.createElement("section");
    wrap.className =
      "section" + (section.default_collapsed && !forceOpen ? " collapsed" : "");
    wrap.dataset.sectionId = section.id;
    wrap.dataset.sectionType = section.type;

    const head = document.createElement("div");
    head.className = "section-head";
    const sectionGlyph =
      SECTION_ID_NAV_GLYPH[section.id] ||
      resolveNavGlyph(
        { nav_glyph: section.nav_glyph, section_id: section.id },
        { type: section.type, publicationKind: section.kind }
      );
    // Content section heads: level plaques only. Glossary matches plain sections
    // under specifications; impl nav trees still use glossary glyphs in the menu.
    const sectionBadge = LEVEL_GLYPHS.has(sectionGlyph)
      ? navGlyphHtml(sectionGlyph, "card")
      : "";
    head.innerHTML = `${sectionBadge}<h2>${escapeHtml(section.title)}</h2><span class="muted">${escapeHtml(section.type)}</span>`;
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

    if (
      section.kind === "external-specification-scope" ||
      (section.tags || []).includes("scope-areas")
    ) {
      const note = document.createElement("aside");
      note.className = "scope-disclaimer";
      note.setAttribute("role", "note");
      note.textContent =
        "Scope is a search and interest boundary over an external specification. " +
        "Included areas (e.g. FIBO FND/BE) do not import those domains or select all of their terms.";
      body.appendChild(note);
    }

    if (section.kind === "documentation" && (section.items || []).length) {
      body.appendChild(renderPackageDocs(section));
      wrap.appendChild(body);
      return wrap;
    }

    switch (section.type) {
      case "markdown-doc":
        body.insertAdjacentHTML(
          "beforeend",
          `<div class="markdown-body">${section.content || ""}</div>`
        );
        break;
      case "mermaid-diagram":
        body.appendChild(renderMermaidDiagram(mod, section));
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
      case "source-file":
        body.appendChild(renderSourceFileSection(mod, section));
        break;
      case "explorer":
        body.insertAdjacentHTML(
          "beforeend",
          `<p class="muted">Use the left sidebar to explore this module.</p>`
        );
        break;
      default:
        if (!appendClassesHierarchyTabs(body, mod, section)) {
          body.appendChild(renderTable(mod, section));
        }
        break;
    }
    wrap.appendChild(body);
    return wrap;
  }

  // moex.dams "All classes": flat table (as before) + Hierarchy tab that shows
  // the whole class tree the same way the explorer "Состав" block draws it.
  function appendClassesHierarchyTabs(body, mod, section) {
    if (
      shortModule(mod.module_id) !== "dams" ||
      section.kind !== "classes" ||
      section.type !== "entity-table"
    ) {
      return false;
    }
    const expl = explorerSection(mod);
    const classesRoot = (expl?.items || []).find(
      (g) => g.attributes?.section_root === "classes"
    );
    if (!classesRoot) return false;

    mountTabs(
      body,
      [
        {
          id: "overview",
          label: "Overview",
          render(panel) {
            panel.appendChild(renderTable(mod, section));
          },
        },
        {
          id: "hierarchy",
          label: "Hierarchy",
          render(panel) {
            const packages = classesRoot.children || [];
            if (!packages.length) {
              panel.innerHTML = `<p class="muted">Нет классов.</p>`;
              return;
            }
            packages.forEach((pkg) => {
              appendExplorerCompositionBlock(panel, pkg.title || pkg.id, pkg.children || [], {
                mod,
                expl,
                openGroupId: pkg.id,
                emptyMessage: "Пустой пакет.",
              });
            });
          },
        },
      ],
      { initial: "overview" }
    );
    return true;
  }

  function renderPackageDocs(section) {
    const panel = document.createElement("div");
    panel.className = "package-docs";
    panel.setAttribute("data-ui", "package-docs");

    const toc = document.createElement("nav");
    toc.className = "doc-toc";
    toc.setAttribute("aria-label", "Package documentation");

    const page = document.createElement("div");
    page.className = "markdown-body doc-page";
    page.innerHTML = section.content || "";

    function markCurrent(btn) {
      toc.querySelectorAll("[aria-current]").forEach((el) => el.removeAttribute("aria-current"));
      if (btn) btn.setAttribute("aria-current", "page");
    }

    function addNode(parent, item) {
      const kids = item.children || [];
      if (item.attributes?.kind === "group" && kids.length) {
        const group = document.createElement("div");
        group.className = "doc-toc-group";
        const label = document.createElement("p");
        label.className = "doc-toc-heading";
        label.textContent = item.title || item.id;
        group.appendChild(label);
        kids.forEach((child) => addNode(group, child));
        parent.appendChild(group);
        return;
      }
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "doc-toc-item";
      btn.textContent = item.title || item.id;
      btn.dataset.docId = item.id;
      btn.addEventListener("click", () => {
        page.innerHTML = item.attributes?.content || "";
        markCurrent(btn);
      });
      parent.appendChild(btn);
    }

    (section.items || []).forEach((item) => addNode(toc, item));
    const firstBtn = toc.querySelector(".doc-toc-item");
    markCurrent(firstBtn);

    panel.appendChild(toc);
    panel.appendChild(page);
    return panel;
  }

  function resolveErdClickTarget(clickmap, el) {
    if (!clickmap || !el) return null;
    let node = el;
    while (node && node !== document && node.nodeType === 1) {
      const id = String(node.getAttribute?.("id") || "");
      const dataId = String(node.getAttribute?.("data-id") || "");
      const hay = `${id} ${dataId}`;
      // Edges first: mermaid edge ids embed entity-… substrings.
      const edgeMatch = hay.match(
        /id_entity-([A-Za-z0-9_]+)-\d+_entity-([A-Za-z0-9_]+)-\d+/
      );
      if (edgeMatch || node.getAttribute?.("data-edge") === "true") {
        const edges = clickmap.edges || [];
        if (edgeMatch) {
          const targetName = edgeMatch[1];
          const sourceName = edgeMatch[2];
          const hit =
            edges.find(
              (e) => e.source === sourceName && e.target === targetName
            ) ||
            edges.find(
              (e) => e.source === targetName && e.target === sourceName
            );
          if (hit?.element_id) {
            return {
              element_id: hit.element_id,
              section_id: hit.section_id || "relationships",
              kind: "edge",
            };
          }
        }
      }
      // Standalone entity node ids look like entity-LegalEntity-3 (no id_entity_…_entity).
      const entityMatch = hay.match(/(?:^|[^_])entity-([A-Za-z0-9_]+)-\d+(?:$|[^_])/);
      if (entityMatch && !hay.includes("id_entity-")) {
        const entry = (clickmap.entities || {})[entityMatch[1]];
        if (entry?.element_id) {
          return {
            element_id: entry.element_id,
            section_id: entry.section_id || "conceptual",
            kind: "entity",
          };
        }
      }
      // Relationship labels are often <text> without entity ids — match by label.
      if (node.tagName === "text" || node.tagName === "tspan") {
        const label = String(node.textContent || "").trim();
        if (label) {
          const hit = (clickmap.edges || []).find((e) => e.label === label);
          if (hit?.element_id) {
            return {
              element_id: hit.element_id,
              section_id: hit.section_id || "relationships",
              kind: "edge",
            };
          }
        }
      }
      node = node.parentElement || node.parentNode;
    }
    return null;
  }

  function erdNodeKey(node) {
    return String(node.element_id || node.name || "");
  }

  function erdEdgeKey(edge) {
    return String(edge.element_id || edge.id || "");
  }

  function measureErdNode(node) {
    const cols = node.columns || [];
    const headerH = 36;
    const rowH = 22;
    const pad = 10;
    let maxType = 48;
    let maxName = 80;
    let maxComment = 60;
    cols.forEach((c) => {
      maxType = Math.max(maxType, String(c.type || "").length * 7);
      maxName = Math.max(maxName, String(c.name || "").length * 7.2);
      maxComment = Math.max(maxComment, Math.min(220, String(c.comment || "").length * 6.5));
    });
    const titleW = Math.max(
      String(node.title || "").length * 7.5,
      String(node.name || "").length * 6.5
    );
    const width = Math.max(220, Math.min(420, Math.max(titleW + 40, maxType + maxName + maxComment + 70)));
    const height = headerH + Math.max(1, cols.length) * rowH + pad;
    return { width, height, headerH, rowH, maxType, maxName };
  }

  function erdNodeCenter(pos, metrics) {
    return {
      x: pos.x + metrics.width / 2,
      y: pos.y + metrics.height / 2,
    };
  }

  function erdAnchorOnSide(pos, metrics, side) {
    const cx = pos.x + metrics.width / 2;
    const cy = pos.y + metrics.height / 2;
    if (side === "left") return { x: pos.x, y: cy };
    if (side === "right") return { x: pos.x + metrics.width, y: cy };
    if (side === "top") return { x: cx, y: pos.y };
    return { x: cx, y: pos.y + metrics.height };
  }

  function erdPickSides(sp, sm, tp, tm) {
    const sc = erdNodeCenter(sp, sm);
    const tc = erdNodeCenter(tp, tm);
    const dx = tc.x - sc.x;
    const dy = tc.y - sc.y;
    if (Math.abs(dx) >= Math.abs(dy)) {
      return dx >= 0 ? ["right", "left"] : ["left", "right"];
    }
    return dy >= 0 ? ["bottom", "top"] : ["top", "bottom"];
  }

  function orthogonalErdPath(x1, y1, x2, y2, bend, side1, side2) {
    if (bend && Number.isFinite(bend.x) && Number.isFinite(bend.y)) {
      // Route via bend with orthogonal segments from each end.
      if (side1 === "left" || side1 === "right") {
        return `M ${x1} ${y1} L ${bend.x} ${y1} L ${bend.x} ${y2} L ${x2} ${y2}`;
      }
      return `M ${x1} ${y1} L ${x1} ${bend.y} L ${x2} ${bend.y} L ${x2} ${y2}`;
    }
    const verticalStart = side1 === "top" || side1 === "bottom";
    if (verticalStart) {
      const midY = (y1 + y2) / 2;
      return `M ${x1} ${y1} L ${x1} ${midY} L ${x2} ${midY} L ${x2} ${y2}`;
    }
    const midX = (x1 + x2) / 2;
    return `M ${x1} ${y1} L ${midX} ${y1} L ${midX} ${y2} L ${x2} ${y2}`;
  }

  const ERD_LOCAL_EDGE_PX = 720;

  function erdEdgeIsLocal(sp, sm, tp, tm, limit) {
    const sc = erdNodeCenter(sp, sm);
    const tc = erdNodeCenter(tp, tm);
    const man = Math.abs(sc.x - tc.x) + Math.abs(sc.y - tc.y);
    return man <= (Number.isFinite(limit) ? limit : ERD_LOCAL_EDGE_PX);
  }

  function renderErdScene(mod, section, scene, layout, onSelect) {
    const wrap = document.createElement("div");
    wrap.className = "erd-scene-wrap";
    wrap.setAttribute("data-ui", "erd-scene");

    const state = {
      layout: JSON.parse(JSON.stringify(layout || { version: 1, nodes: {}, edges: {} })),
      layoutPath: String((section.attributes || {}).erd_layout_path || ""),
      layoutHash: String((section.attributes || {}).erd_layout_hash || ""),
      panX: 0,
      panY: 0,
      scale: 1,
      selectedNode: null,
      selectedEdge: null,
      edgeMode:
        String(scene.profile || "") === "conceptual" ||
        (scene.edges || []).length >= 24
          ? "local"
          : "all",
      editMode: false,
      dirty: false,
      dragging: false,
      dragMoved: false,
      dragRaf: 0,
    };

    const tools = document.createElement("div");
    tools.className = "erd-scene-toolbar";

    const btnEdit = document.createElement("button");
    btnEdit.type = "button";
    btnEdit.className = "erd-tool-btn";
    btnEdit.textContent = "Правка";
    const btnSave = document.createElement("button");
    btnSave.type = "button";
    btnSave.className = "erd-tool-btn";
    btnSave.textContent = "Сохранить layout";
    btnSave.disabled = true;
    const btnDownload = document.createElement("button");
    btnDownload.type = "button";
    btnDownload.className = "erd-tool-btn";
    btnDownload.textContent = "Скачать layout.json";
    const btnEdges = document.createElement("button");
    btnEdges.type = "button";
    btnEdges.className = "erd-tool-btn";
    function syncEdgeModeBtn() {
      const local = state.edgeMode === "local";
      btnEdges.textContent = local ? "Все связи" : "Ближние связи";
      btnEdges.classList.toggle("is-active", local);
      btnEdges.title = local
        ? "Показаны короткие связи; дальние — у выбранной сущности"
        : "Скрыть дальние hop'ы, которые оставляют подписи в пустом месте";
    }
    syncEdgeModeBtn();
    btnEdges.addEventListener("click", () => {
      state.edgeMode = state.edgeMode === "local" ? "all" : "local";
      syncEdgeModeBtn();
      redraw();
    });
    const colorInput = document.createElement("input");
    colorInput.type = "color";
    colorInput.className = "erd-color-input";
    colorInput.title = "Цвет выбранной таблицы";
    colorInput.disabled = true;
    const status = document.createElement("span");
    status.className = "muted";
    status.style.fontSize = "var(--font-sm)";

    tools.appendChild(btnEdit);
    tools.appendChild(btnSave);
    tools.appendChild(btnDownload);
    tools.appendChild(btnEdges);
    tools.appendChild(colorInput);
    tools.appendChild(status);
    wrap.appendChild(tools);

    const NS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(NS, "svg");
    svg.classList.add("erd-scene");
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", "ER diagram");
    wrap.appendChild(svg);

    const defs = document.createElementNS(NS, "defs");
    const markerSpecs = [
      ["onlyOne", "M0,0 L0,12 M4,0 L4,12"],
      ["zeroOrOne", "M8,6 m-3,0 a3,3 0 1,0 6,0 a3,3 0 1,0 -6,0 M0,0 L0,12"],
      ["oneOrMore", "M0,6 L8,0 L8,12 Z M12,0 L12,12"],
      ["zeroOrMore", "M14,6 m-3,0 a3,3 0 1,0 6,0 a3,3 0 1,0 -6,0 M0,6 L8,0 L8,12 Z"],
    ];
    markerSpecs.forEach(([name, d]) => {
      ["Start", "End"].forEach((side) => {
        const m = document.createElementNS(NS, "marker");
        m.setAttribute("id", `erd-m-${name}-${side}`);
        m.setAttribute("viewBox", "0 0 18 12");
        m.setAttribute("refX", side === "End" ? "18" : "0");
        m.setAttribute("refY", "6");
        m.setAttribute("markerWidth", "12");
        m.setAttribute("markerHeight", "10");
        m.setAttribute("orient", "auto");
        const p = document.createElementNS(NS, "path");
        p.setAttribute("d", d);
        p.setAttribute("fill", "none");
        p.setAttribute("stroke", "var(--erd-edge)");
        p.setAttribute("stroke-width", "1.25");
        m.appendChild(p);
        defs.appendChild(m);
      });
    });
    svg.appendChild(defs);

    const rootG = document.createElementNS(NS, "g");
    rootG.classList.add("erd-scene-root");
    svg.appendChild(rootG);
    const edgesG = document.createElementNS(NS, "g");
    edgesG.classList.add("erd-edges");
    const nodesG = document.createElementNS(NS, "g");
    nodesG.classList.add("erd-nodes");
    rootG.appendChild(edgesG);
    rootG.appendChild(nodesG);

    const nodeMetrics = {};
    (scene.nodes || []).forEach((n) => {
      nodeMetrics[erdNodeKey(n)] = measureErdNode(n);
    });

    function nodePos(key) {
      const p = (state.layout.nodes || {})[key];
      if (p) return { x: Number(p.x) || 0, y: Number(p.y) || 0, color: p.color };
      return { x: 40, y: 40, color: null };
    }

    function applyTransform() {
      rootG.setAttribute(
        "transform",
        `translate(${state.panX},${state.panY}) scale(${state.scale})`
      );
    }

    function markDirty() {
      state.dirty = true;
      btnSave.disabled = !state.editMode;
      status.textContent = state.editMode ? "есть несохранённые изменения" : "";
    }

    function markerUrl(kind, side) {
      const k = kind || "onlyOne";
      return `url(#erd-m-${k}-${side})`;
    }

    function redraw() {
      edgesG.replaceChildren();
      nodesG.replaceChildren();
      const byName = {};
      (scene.nodes || []).forEach((n) => {
        byName[n.name] = n;
      });

      (scene.edges || []).forEach((edge) => {
        const srcNode = byName[edge.source];
        const tgtNode = byName[edge.target];
        if (!srcNode || !tgtNode) return;
        const sk = erdNodeKey(srcNode);
        const tk = erdNodeKey(tgtNode);
        const sp = nodePos(sk);
        const tp = nodePos(tk);
        const sm = nodeMetrics[sk];
        const tm = nodeMetrics[tk];
        const [side1, side2] = erdPickSides(sp, sm, tp, tm);
        const a1 = erdAnchorOnSide(sp, sm, side1);
        const a2 = erdAnchorOnSide(tp, tm, side2);
        const x1 = a1.x;
        const y1 = a1.y;
        const x2 = a2.x;
        const y2 = a2.y;
        const ek = erdEdgeKey(edge);
        const focused =
          state.selectedNode === sk ||
          state.selectedNode === tk ||
          state.selectedEdge === ek;
        const local = erdEdgeIsLocal(sp, sm, tp, tm);
        const distant = state.edgeMode === "local" && !focused && !local;
        if (distant) return;
        const edgeLayout = (state.layout.edges || {})[ek] || {};
        const bend = (edgeLayout.points && edgeLayout.points[0]) || null;
        const path = document.createElementNS(NS, "path");
        path.setAttribute(
          "d",
          orthogonalErdPath(x1, y1, x2, y2, bend, side1, side2)
        );
        path.classList.add("erd-edge-path");
        if (state.selectedEdge === ek) path.classList.add("is-selected");
        path.setAttribute("marker-start", markerUrl(edge.source_cardinality, "Start"));
        path.setAttribute("marker-end", markerUrl(edge.target_cardinality, "End"));
        path.dataset.edgeId = ek;
        path.addEventListener("click", (ev) => {
          ev.stopPropagation();
          state.selectedEdge = ek;
          state.selectedNode = null;
          colorInput.disabled = true;
          if (typeof onSelect === "function" && edge.element_id) {
            onSelect({
              element_id: edge.element_id,
              section_id: "relationships",
              kind: "edge",
            });
          }
          redraw();
        });
        edgesG.appendChild(path);

        if (edge.label) {
          const lx = bend ? bend.x : (x1 + x2) / 2;
          const ly = bend ? (y1 + y2) / 2 : (y1 + y2) / 2 - 8;
          const labelPos = edgeLayout.label || { x: lx, y: ly };
          const bg = document.createElementNS(NS, "rect");
          bg.classList.add("erd-edge-label-bg");
          const text = document.createElementNS(NS, "text");
          text.classList.add("erd-edge-label");
          text.setAttribute("x", labelPos.x);
          text.setAttribute("y", labelPos.y);
          text.setAttribute("text-anchor", "middle");
          text.textContent = edge.label;
          edgesG.appendChild(bg);
          edgesG.appendChild(text);
          try {
            const bbox = text.getBBox();
            bg.setAttribute("x", bbox.x - 4);
            bg.setAttribute("y", bbox.y - 2);
            bg.setAttribute("width", bbox.width + 8);
            bg.setAttribute("height", bbox.height + 4);
          } catch (_) {
            bg.setAttribute("x", labelPos.x - 30);
            bg.setAttribute("y", labelPos.y - 12);
            bg.setAttribute("width", 60);
            bg.setAttribute("height", 16);
          }
        }

        if (state.editMode) {
          const hx = bend ? bend.x : (x1 + x2) / 2;
          const hy = bend ? bend.y : (y1 + y2) / 2;
          const handle = document.createElementNS(NS, "circle");
          handle.classList.add("erd-edge-handle");
          handle.setAttribute("cx", hx);
          handle.setAttribute("cy", hy);
          handle.dataset.edgeId = ek;
          handle.addEventListener("pointerdown", (ev) => {
            if (ev.button != null && ev.button !== 0) return;
            ev.stopPropagation();
            ev.preventDefault();
            state.dragging = true;
            state.dragMoved = false;
            const pointerId = ev.pointerId;
            const scheduleRedraw = () => {
              if (state.dragRaf) return;
              state.dragRaf = requestAnimationFrame(() => {
                state.dragRaf = 0;
                redraw();
              });
            };
            const move = (e) => {
              if (e.pointerId !== pointerId) return;
              state.dragMoved = true;
              const pt = clientToScene(e.clientX, e.clientY);
              if (!state.layout.edges) state.layout.edges = {};
              state.layout.edges[ek] = {
                ...(state.layout.edges[ek] || {}),
                points: [{ x: Math.round(pt.x), y: Math.round(pt.y) }],
              };
              markDirty();
              scheduleRedraw();
            };
            const up = (e) => {
              if (e.pointerId !== pointerId) return;
              window.removeEventListener("pointermove", move);
              window.removeEventListener("pointerup", up);
              window.removeEventListener("pointercancel", up);
              state.dragging = false;
              if (state.dragRaf) {
                cancelAnimationFrame(state.dragRaf);
                state.dragRaf = 0;
              }
              redraw();
            };
            window.addEventListener("pointermove", move);
            window.addEventListener("pointerup", up);
            window.addEventListener("pointercancel", up);
          });
          edgesG.appendChild(handle);
        }
      });

      (scene.nodes || []).forEach((node) => {
        const key = erdNodeKey(node);
        const m = nodeMetrics[key];
        const pos = nodePos(key);
        const g = document.createElementNS(NS, "g");
        g.classList.add("erd-node");
        if (state.selectedNode === key) g.classList.add("is-selected");
        g.setAttribute("transform", `translate(${pos.x},${pos.y})`);
        g.dataset.nodeKey = key;

        const rect = document.createElementNS(NS, "rect");
        rect.classList.add("erd-node-rect");
        rect.setAttribute("width", m.width);
        rect.setAttribute("height", m.height);
        rect.setAttribute("rx", "6");
        rect.setAttribute("fill", "var(--erd-row-odd)");
        g.appendChild(rect);

        const header = document.createElementNS(NS, "rect");
        header.classList.add("erd-node-header");
        header.setAttribute("width", m.width);
        header.setAttribute("height", m.headerH);
        header.setAttribute("rx", "6");
        if (pos.color) header.setAttribute("fill", pos.color);
        g.appendChild(header);
        // square bottom of header
        const headerFix = document.createElementNS(NS, "rect");
        headerFix.setAttribute("y", m.headerH - 6);
        headerFix.setAttribute("width", m.width);
        headerFix.setAttribute("height", 6);
        headerFix.setAttribute("fill", pos.color || "var(--erd-header-bg)");
        g.appendChild(headerFix);

        const title = document.createElementNS(NS, "text");
        title.classList.add("erd-node-title");
        title.setAttribute("x", 10);
        title.setAttribute("y", 15);
        title.textContent = node.title || node.name;
        g.appendChild(title);
        const name = document.createElementNS(NS, "text");
        name.classList.add("erd-node-name");
        name.setAttribute("x", 10);
        name.setAttribute("y", 28);
        name.textContent = node.name;
        g.appendChild(name);

        const cols = node.columns || [];
        if (!cols.length) {
          const empty = document.createElementNS(NS, "text");
          empty.classList.add("erd-col-comment");
          empty.setAttribute("x", 10);
          empty.setAttribute("y", m.headerH + 16);
          empty.textContent = "—";
          g.appendChild(empty);
        }
        cols.forEach((col, i) => {
          const y = m.headerH + i * m.rowH;
          if (i % 2 === 1) {
            const rowBg = document.createElementNS(NS, "rect");
            rowBg.setAttribute("y", y);
            rowBg.setAttribute("width", m.width);
            rowBg.setAttribute("height", m.rowH);
            rowBg.setAttribute("fill", "var(--erd-row-even)");
            g.appendChild(rowBg);
          }
          const typeT = document.createElementNS(NS, "text");
          typeT.classList.add("erd-col-type");
          typeT.setAttribute("x", 8);
          typeT.setAttribute("y", y + 15);
          typeT.textContent = col.type || "";
          g.appendChild(typeT);
          const nameT = document.createElementNS(NS, "text");
          nameT.classList.add("erd-col-name");
          nameT.setAttribute("x", 8 + Math.min(m.maxType, 90));
          nameT.setAttribute("y", y + 15);
          nameT.textContent = col.name || "";
          g.appendChild(nameT);
          let badgeX = m.width - 8;
          (col.keys || []).slice().reverse().forEach((k) => {
            badgeX -= 22;
            const br = document.createElementNS(NS, "rect");
            br.classList.add("erd-key-badge");
            br.setAttribute("x", badgeX);
            br.setAttribute("y", y + 4);
            br.setAttribute("width", 20);
            br.setAttribute("height", 14);
            br.setAttribute("rx", "3");
            g.appendChild(br);
            const bt = document.createElementNS(NS, "text");
            bt.classList.add("erd-key-badge-text");
            bt.setAttribute("x", badgeX + 10);
            bt.setAttribute("y", y + 14);
            bt.setAttribute("text-anchor", "middle");
            bt.textContent = k;
            g.appendChild(bt);
          });
          if (col.comment) {
            const ct = document.createElementNS(NS, "text");
            ct.classList.add("erd-col-comment");
            ct.setAttribute("x", 8 + Math.min(m.maxType, 90) + Math.min(m.maxName, 120));
            ct.setAttribute("y", y + 15);
            const maxLen = 28;
            const t = String(col.comment);
            ct.textContent = t.length > maxLen ? t.slice(0, maxLen - 1) + "…" : t;
            g.appendChild(ct);
          }
        });

        function selectNode(openDetail) {
          state.selectedNode = key;
          state.selectedEdge = null;
          colorInput.disabled = !state.editMode;
          const c = nodePos(key).color || "#4285F4";
          colorInput.value = /^#[0-9a-fA-F]{6}$/.test(c) ? c : "#4285F4";
          if (openDetail && typeof onSelect === "function" && node.element_id) {
            const profileSec =
              scene.profile === "conceptual"
                ? "conceptual"
                : scene.profile === "physical"
                  ? "physical"
                  : "logical";
            onSelect({
              element_id: node.element_id,
              section_id: profileSec,
              kind: "entity",
            });
          }
        }

        g.addEventListener("click", (ev) => {
          // Drag uses pointer handlers; ignore click after a real drag.
          if (state.dragMoved) {
            state.dragMoved = false;
            ev.stopPropagation();
            return;
          }
          ev.stopPropagation();
          selectNode(true);
          redraw();
        });

        if (state.editMode) {
          g.addEventListener("pointerdown", (ev) => {
            if (ev.button != null && ev.button !== 0) return;
            if (ev.target.closest?.(".erd-edge-handle")) return;
            ev.stopPropagation();
            ev.preventDefault();
            selectNode(false);
            state.dragging = true;
            state.dragMoved = false;
            const pointerId = ev.pointerId;
            const start = clientToScene(ev.clientX, ev.clientY);
            const origin = nodePos(key);
            const scheduleRedraw = () => {
              if (state.dragRaf) return;
              state.dragRaf = requestAnimationFrame(() => {
                state.dragRaf = 0;
                redraw();
              });
            };
            const move = (e) => {
              if (e.pointerId !== pointerId) return;
              const cur = clientToScene(e.clientX, e.clientY);
              const dx = cur.x - start.x;
              const dy = cur.y - start.y;
              if (Math.abs(dx) + Math.abs(dy) > 2) state.dragMoved = true;
              const nx = Math.round(origin.x + dx);
              const ny = Math.round(origin.y + dy);
              if (!state.layout.nodes) state.layout.nodes = {};
              state.layout.nodes[key] = {
                ...(state.layout.nodes[key] || {}),
                x: nx,
                y: ny,
                color: (state.layout.nodes[key] || {}).color || origin.color,
              };
              markDirty();
              // Listeners live on window so full redraw cannot drop capture.
              scheduleRedraw();
            };
            const up = (e) => {
              if (e.pointerId !== pointerId) return;
              window.removeEventListener("pointermove", move);
              window.removeEventListener("pointerup", up);
              window.removeEventListener("pointercancel", up);
              state.dragging = false;
              if (state.dragRaf) {
                cancelAnimationFrame(state.dragRaf);
                state.dragRaf = 0;
              }
              if (!state.dragMoved) selectNode(true);
              redraw();
            };
            window.addEventListener("pointermove", move);
            window.addEventListener("pointerup", up);
            window.addEventListener("pointercancel", up);
            redraw();
          });
        }

        nodesG.appendChild(g);
      });
      applyTransform();
    }

    function clientToScene(clientX, clientY) {
      const rect = svg.getBoundingClientRect();
      const x = (clientX - rect.left - state.panX) / state.scale;
      const y = (clientY - rect.top - state.panY) / state.scale;
      return { x, y };
    }

    function fitToContent() {
      let minX = Infinity;
      let minY = Infinity;
      let maxX = -Infinity;
      let maxY = -Infinity;
      (scene.nodes || []).forEach((node) => {
        const key = erdNodeKey(node);
        const m = nodeMetrics[key];
        const pos = nodePos(key);
        if (!m) return;
        minX = Math.min(minX, pos.x);
        minY = Math.min(minY, pos.y);
        maxX = Math.max(maxX, pos.x + m.width);
        maxY = Math.max(maxY, pos.y + m.height);
      });
      if (!Number.isFinite(minX)) return;
      const pad = 40;
      const contentW = Math.max(1, maxX - minX + pad * 2);
      const contentH = Math.max(1, maxY - minY + pad * 2);
      const vw = Math.max(1, wrap.clientWidth || svg.clientWidth || 800);
      const vh = Math.max(1, wrap.clientHeight || svg.clientHeight || 500);
      const next = Math.min(1.25, Math.max(0.2, Math.min(vw / contentW, vh / contentH)));
      state.scale = next;
      state.panX = (vw - contentW * next) / 2 - (minX - pad) * next;
      state.panY = (vh - contentH * next) / 2 - (minY - pad) * next;
    }

    let panning = false;
    let panOrigin = null;
    svg.addEventListener("pointerdown", (ev) => {
      if (state.dragging) return;
      if (ev.target !== svg && !ev.target.classList?.contains("erd-scene-root")) {
        if (
          ev.target.closest(".erd-node") ||
          ev.target.closest(".erd-edge-path") ||
          ev.target.closest(".erd-edge-handle")
        ) {
          return;
        }
      }
      panning = true;
      wrap.classList.add("is-panning");
      panOrigin = { x: ev.clientX - state.panX, y: ev.clientY - state.panY };
      const pointerId = ev.pointerId;
      const move = (e) => {
        if (!panning || e.pointerId !== pointerId || !panOrigin) return;
        state.panX = e.clientX - panOrigin.x;
        state.panY = e.clientY - panOrigin.y;
        applyTransform();
      };
      const up = (e) => {
        if (e.pointerId !== pointerId) return;
        panning = false;
        wrap.classList.remove("is-panning");
        window.removeEventListener("pointermove", move);
        window.removeEventListener("pointerup", up);
        window.removeEventListener("pointercancel", up);
      };
      window.addEventListener("pointermove", move);
      window.addEventListener("pointerup", up);
      window.addEventListener("pointercancel", up);
    });
    svg.addEventListener(
      "wheel",
      (ev) => {
        ev.preventDefault();
        const delta = ev.deltaY > 0 ? 0.9 : 1.1;
        const next = Math.min(2.5, Math.max(0.15, state.scale * delta));
        const rect = svg.getBoundingClientRect();
        const cx = ev.clientX - rect.left;
        const cy = ev.clientY - rect.top;
        state.panX = cx - ((cx - state.panX) / state.scale) * next;
        state.panY = cy - ((cy - state.panY) / state.scale) * next;
        state.scale = next;
        applyTransform();
      },
      { passive: false }
    );

    btnEdit.addEventListener("click", () => {
      state.editMode = !state.editMode;
      btnEdit.classList.toggle("is-active", state.editMode);
      btnEdit.textContent = state.editMode ? "Просмотр" : "Правка";
      colorInput.disabled = !(state.editMode && state.selectedNode);
      btnSave.disabled = !(state.editMode && state.dirty);
      const canServe = typeof window.__moexCanEditLayout === "function" && window.__moexCanEditLayout();
      if (state.editMode && !canServe) {
        status.textContent = "serve недоступен — используйте «Скачать layout.json»";
      } else {
        status.textContent = state.dirty ? "есть несохранённые изменения" : "";
      }
      redraw();
    });

    colorInput.addEventListener("input", () => {
      if (!state.selectedNode || !state.editMode) return;
      if (!state.layout.nodes) state.layout.nodes = {};
      const prev = state.layout.nodes[state.selectedNode] || nodePos(state.selectedNode);
      state.layout.nodes[state.selectedNode] = {
        x: prev.x,
        y: prev.y,
        color: colorInput.value,
      };
      markDirty();
      redraw();
    });

    btnDownload.addEventListener("click", () => {
      const blob = new Blob(
        [JSON.stringify(state.layout, null, 2) + "\n"],
        { type: "application/json" }
      );
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = (state.layoutPath.split("/").pop() || "layout.json");
      a.click();
      URL.revokeObjectURL(a.href);
    });

    btnSave.addEventListener("click", async () => {
      const token =
        typeof window.__moexGetEditToken === "function"
          ? window.__moexGetEditToken()
          : null;
      if (!token || !state.layoutPath) {
        status.textContent = "Нет serve API — скачайте layout.json";
        return;
      }
      btnSave.disabled = true;
      try {
        const resp = await fetch("/api/layout", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            token,
            path: state.layoutPath,
            layout: state.layout,
            base_hash: state.layoutHash,
          }),
        });
        const data = await resp.json().catch(() => ({}));
        if (resp.status === 409) {
          status.textContent = "Конфликт: layout изменился на диске";
          if (data.current_hash) state.layoutHash = data.current_hash;
          btnSave.disabled = false;
          return;
        }
        if (!resp.ok || !data.ok) {
          status.textContent = data.error || `Ошибка ${resp.status}`;
          btnSave.disabled = false;
          return;
        }
        state.layoutHash = data.new_hash || state.layoutHash;
        state.dirty = false;
        status.textContent = "layout сохранён";
        btnSave.disabled = true;
      } catch (e) {
        status.textContent = e && e.message ? e.message : String(e);
        btnSave.disabled = false;
      }
    });

    redraw();
    fitToContent();
    applyTransform();
    return wrap;
  }

  function renderMermaidDiagram(mod, section) {
    const attrs = section.attributes || {};
    const source = String(attrs.mermaid_source || "");
    const dbmlSource = String(attrs.dbml_source || "");
    const clickmap = attrs.erd_clickmap || null;
    const scene = attrs.erd_scene || null;
    const layout = attrs.erd_layout || null;
    const hasScene = !!(scene && Array.isArray(scene.nodes));
    // SVG may live in attributes.mermaid_svg when scene is primary (payload shrink).
    const svgHtml = String(section.content || attrs.mermaid_svg || "");
    const panel = document.createElement("div");
    panel.className = "erd-panel";
    panel.setAttribute("data-ui", "mermaid-diagram");
    if (clickmap || hasScene) panel.classList.add("erd-panel--interactive");

    const toolbar = document.createElement("div");
    toolbar.className = "erd-toolbar";
    toolbar.setAttribute("role", "tablist");

    const tabDiagram = document.createElement("button");
    tabDiagram.type = "button";
    tabDiagram.className = "erd-tab is-active";
    tabDiagram.setAttribute("data-erd-tab", "diagram");
    tabDiagram.setAttribute("role", "tab");
    tabDiagram.setAttribute("aria-selected", "true");
    tabDiagram.textContent = "Диаграмма";

    const tabMermaid = document.createElement("button");
    tabMermaid.type = "button";
    tabMermaid.className = "erd-tab";
    tabMermaid.setAttribute("data-erd-tab", "mermaid");
    tabMermaid.setAttribute("role", "tab");
    tabMermaid.setAttribute("aria-selected", "false");
    tabMermaid.textContent = "Mermaid";
    if (!hasScene) tabMermaid.hidden = true;

    const tabSource = document.createElement("button");
    tabSource.type = "button";
    tabSource.className = "erd-tab";
    tabSource.setAttribute("data-erd-tab", "source");
    tabSource.setAttribute("role", "tab");
    tabSource.setAttribute("aria-selected", "false");
    tabSource.textContent = "Исходник";

    const tabDbml = document.createElement("button");
    tabDbml.type = "button";
    tabDbml.className = "erd-tab";
    tabDbml.setAttribute("data-erd-tab", "dbml");
    tabDbml.setAttribute("role", "tab");
    tabDbml.setAttribute("aria-selected", "false");
    tabDbml.textContent = "DBML";

    toolbar.appendChild(tabDiagram);
    toolbar.appendChild(tabMermaid);
    toolbar.appendChild(tabSource);
    toolbar.appendChild(tabDbml);

    const bodyRow = document.createElement("div");
    bodyRow.className = "erd-body";

    const canvas = document.createElement("div");
    canvas.className = "erd-canvas";
    canvas.setAttribute("data-erd-pane", "diagram");

    const mermaidCanvas = document.createElement("div");
    mermaidCanvas.className = "erd-canvas is-hidden";
    mermaidCanvas.setAttribute("data-erd-pane", "mermaid");
    mermaidCanvas.hidden = true;

    const detailPane = document.createElement("aside");
    detailPane.className = "erd-detail";
    detailPane.setAttribute("data-erd-detail", "");
    const showDetail = !!(clickmap || hasScene);
    detailPane.hidden = !showDetail;
    if (showDetail) {
      const hint = document.createElement("p");
      hint.className = "muted erd-detail-hint";
      hint.textContent =
        "Кликните сущность или связь на диаграмме, чтобы прочитать определение.";
      detailPane.appendChild(hint);
    }

    function showErdDetail(target) {
      if (!target || !mod) return;
      const sec =
        mod.sections.find((s) => s.id === target.section_id) ||
        mod.sections.find((s) =>
          (s.items || []).some((it) => it.id === target.element_id)
        ) ||
        mod.sections.find((s) =>
          (s.items || []).some((it) => it.id === target.element_id)
        );
      // Broader search across all sections for element_id
      let row = null;
      let hitSec = sec;
      if (hitSec) row = findSectionItem(hitSec, target.element_id);
      if (!row) {
        for (const s of mod.sections || []) {
          const r = findSectionItem(s, target.element_id);
          if (r) {
            row = r;
            hitSec = s;
            break;
          }
        }
      }
      if (!row || !hitSec) return;
      detailPane.replaceChildren();
      const openLink = document.createElement("a");
      openLink.className = "erd-detail-open";
      openLink.href = itemHref({
        module: shortModule(mod.module_id),
        section: hitSec.id,
        item: row.id,
        node: nodeForModule(mod.module_id)?.id || null,
        card: true,
      });
      openLink.textContent = "Открыть карточку";
      detailPane.appendChild(openLink);
      if (hitSec.instance_of) {
        detailPane.appendChild(renderInstanceDetail(mod, hitSec, row));
      } else {
        const fallback = document.createElement("article");
        fallback.className = "detail-card content-card";
        fallback.innerHTML = `<header class="detail-head"><h1>${escapeHtml(
          row.title || row.id
        )}</h1><p class="muted">${escapeHtml(row.id)}</p></header>
          <p class="detail-desc">${escapeHtml(
            row.description || "No description."
          )}</p>`;
        detailPane.appendChild(fallback);
      }
    }

    if (hasScene) {
      try {
        canvas.appendChild(
          renderErdScene(
            mod,
            section,
            scene,
            layout || { version: 1, nodes: {}, edges: {} },
            showErdDetail
          )
        );
      } catch (err) {
        const fail = document.createElement("p");
        fail.className = "error";
        fail.textContent =
          "Не удалось отрисовать диаграмму: " +
          (err && err.message ? err.message : String(err));
        canvas.appendChild(fail);
        if (svgHtml) {
          const svgWrap = document.createElement("div");
          svgWrap.className = "erd-svg";
          svgWrap.innerHTML = svgHtml;
          canvas.appendChild(svgWrap);
        }
      }
    } else if (svgHtml) {
      const svgWrap = document.createElement("div");
      svgWrap.className = "erd-svg";
      if (clickmap) svgWrap.classList.add("erd-svg--clickable");
      svgWrap.innerHTML = svgHtml;
      canvas.appendChild(svgWrap);
    } else {
      const miss = document.createElement("p");
      miss.className = "muted";
      miss.textContent =
        "Нет scene/layout и SVG. Выполните: moex-model diagram --format mermaid --profile logical|physical|conceptual";
      canvas.appendChild(miss);
    }

    // Lazy-mount Mermaid SVG only when that tab is opened (avoids parsing huge SVG up front).
    let mermaidMounted = false;
    function ensureMermaidSvg() {
      if (mermaidMounted) return;
      mermaidMounted = true;
      mermaidCanvas.replaceChildren();
      if (svgHtml) {
        const svgWrap = document.createElement("div");
        svgWrap.className = "erd-svg";
        if (clickmap) svgWrap.classList.add("erd-svg--clickable");
        svgWrap.innerHTML = svgHtml;
        mermaidCanvas.appendChild(svgWrap);
        if (clickmap) {
          mermaidCanvas.addEventListener("click", (ev) => {
            const hit = resolveErdClickTarget(clickmap, ev.target);
            if (!hit) return;
            ev.preventDefault();
            showErdDetail(hit);
          });
        }
      } else {
        const miss = document.createElement("p");
        miss.className = "muted";
        miss.textContent = "Mermaid SVG недоступен.";
        mermaidCanvas.appendChild(miss);
      }
    }
    if (!hasScene) {
      // Fallback path uses canvas; keep Mermaid tab content ready when visible.
      ensureMermaidSvg();
    } else {
      const hint = document.createElement("p");
      hint.className = "muted";
      hint.textContent =
        "Интерактивная диаграмма на вкладке «Диаграмма». SVG не встроен в player (чтобы не раздувать страницу); текст Mermaid — на вкладке «Исходник».";
      mermaidCanvas.appendChild(hint);
    }

    if (!hasScene && clickmap && svgHtml) {
      canvas.addEventListener("click", (ev) => {
        const hit = resolveErdClickTarget(clickmap, ev.target);
        if (!hit) return;
        ev.preventDefault();
        showErdDetail(hit);
      });
    }

    function makeSourcePane(paneName, text) {
      const pane = document.createElement("div");
      pane.className = "erd-source is-hidden";
      pane.setAttribute("data-erd-pane", paneName);
      pane.hidden = true;

      const actions = document.createElement("div");
      actions.className = "erd-source-actions";
      const copyBtn = document.createElement("button");
      copyBtn.type = "button";
      copyBtn.className = "copy-btn";
      copyBtn.textContent = "Copy";
      copyBtn.disabled = !text;
      copyBtn.addEventListener("click", () => {
        if (!text) return;
        navigator.clipboard?.writeText(text).then(
          () => {
            copyBtn.textContent = "Copied";
            setTimeout(() => {
              copyBtn.textContent = "Copy";
            }, 1200);
          },
          () => {}
        );
      });
      actions.appendChild(copyBtn);
      pane.appendChild(actions);

      if (text) {
        const pre = document.createElement("pre");
        pre.className = "erd-source-pre";
        const code = document.createElement("code");
        code.textContent = text;
        pre.appendChild(code);
        pane.appendChild(pre);
      } else {
        const miss = document.createElement("p");
        miss.className = "muted";
        miss.textContent =
          paneName === "dbml"
            ? "DBML не сгенерирован. Выполните moex-model diagram --format dbml --profile logical|physical|conceptual."
            : "Исходник недоступен.";
        pane.appendChild(miss);
      }
      return pane;
    }

    const sourcePane = makeSourcePane("source", source);
    const dbmlPane = makeSourcePane("dbml", dbmlSource);

    function showPane(name) {
      const panes = {
        diagram: { tab: tabDiagram, el: canvas },
        mermaid: { tab: tabMermaid, el: mermaidCanvas },
        source: { tab: tabSource, el: sourcePane },
        dbml: { tab: tabDbml, el: dbmlPane },
      };
      for (const [key, entry] of Object.entries(panes)) {
        if (!entry.tab || entry.tab.hidden) continue;
        const active = key === name;
        entry.tab.classList.toggle("is-active", active);
        entry.tab.setAttribute("aria-selected", active ? "true" : "false");
        entry.el.classList.toggle("is-hidden", !active);
        entry.el.hidden = !active;
      }
      if (showDetail) {
        const isDiagram = name === "diagram" || name === "mermaid";
        detailPane.classList.toggle("is-hidden", !isDiagram);
        detailPane.hidden = !isDiagram;
      }
    }
    tabDiagram.addEventListener("click", () => showPane("diagram"));
    tabMermaid.addEventListener("click", () => {
      if (!hasScene) ensureMermaidSvg();
      showPane("mermaid");
    });
    tabSource.addEventListener("click", () => showPane("source"));
    tabDbml.addEventListener("click", () => showPane("dbml"));

    bodyRow.appendChild(canvas);
    bodyRow.appendChild(mermaidCanvas);
    if (showDetail) bodyRow.appendChild(detailPane);
    panel.appendChild(toolbar);
    panel.appendChild(bodyRow);
    panel.appendChild(sourcePane);
    panel.appendChild(dbmlPane);
    return panel;
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

  function shortIriLabel(iri) {
    const s = String(iri || "");
    if (!s) return "";
    if (s === "REPLACE_WITH_REAL_FIBO_IRI") return "placeholder IRI";
    const hash = s.lastIndexOf("#");
    const slash = s.lastIndexOf("/");
    const cut = Math.max(hash, slash);
    if (cut >= 0 && cut < s.length - 1) return s.slice(cut + 1);
    return s.length > 48 ? "…" + s.slice(-40) : s;
  }

  function isHttpUrl(value) {
    try {
      const u = new URL(String(value));
      return u.protocol === "http:" || u.protocol === "https:";
    } catch {
      return false;
    }
  }

  function statusChipClass(kind, value) {
    const v = String(value || "").toLowerCase();
    if (kind === "decision") {
      if (v === "accepted") return "status-chip status-chip--accepted";
      if (v === "rejected") return "status-chip status-chip--rejected";
      if (v === "deferred") return "status-chip status-chip--deferred";
      if (v === "deprecated") return "status-chip status-chip--deprecated";
      return "status-chip status-chip--candidate";
    }
    if (kind === "review") {
      if (v === "approved") return "status-chip status-chip--approved";
      if (v === "rejected") return "status-chip status-chip--rejected";
      if (v === "superseded") return "status-chip status-chip--deferred";
      return "status-chip status-chip--pending";
    }
    if (kind === "mapping") {
      if (v === "true" || v === "yes") return "status-chip status-chip--approved";
      return "status-chip status-chip--candidate";
    }
    return "status-chip";
  }

  function isLinkableTableColumn(col) {
    if (!col) return false;
    if (col === "name" || col === "title" || col === "is_a" || col === "mixins") return true;
    if (col === "source" || col === "target") return true;
    if (/_refs?$/.test(col)) return true;
    return false;
  }

  function resolveGlossaryTermPageTarget(mod, section, item) {
    if (!mod || !item) return null;
    // Aggregated implementations glossary: always open the term card, never
    // a class explorer card (ADR-025 definition override details).
    if (section?.attributes?.term_cards) {
      return {
        module: shortModule(mod.module_id),
        section: section.id,
        item: item.id,
        node: nodeForModule(mod.module_id)?.id || currentNodeId,
        card: true,
      };
    }
    const cid = canonicalGlossaryId(item.id);
    const name = item.attributes?.name || item.title || cid;
    const byExplorer =
      findExplorerLinkTarget(mod, name) ||
      findExplorerLinkTarget(mod, item.id) ||
      findExplorerLinkTarget(mod, cid);
    if (byExplorer) return byExplorer;

    const expl = explorerSection(mod);
    if (expl) {
      const leafId = "glossary:" + cid;
      const found =
        findExplorerItem(expl, leafId) ||
        findExplorerItem(expl, item.id) ||
        findExplorerItem(expl, cid);
      if (found && isGlossaryViewItem(found.item)) {
        return {
          module: shortModule(mod.module_id),
          section: expl.id,
          item: found.item.id,
          node: nodeForModule(mod.module_id)?.id || currentNodeId,
          card: true,
        };
      }
    }

    return {
      module: shortModule(mod.module_id),
      section: section?.id || "glossary",
      item: item.id,
      node: nodeForModule(mod.module_id)?.id || currentNodeId,
      card: true,
    };
  }

  function findExplorerLinkTarget(mod, nameOrId) {
    const expl = explorerSection(mod);
    if (!expl || !nameOrId) return null;
    const key = String(nameOrId);
    let best = null;
    let bestScore = -1;
    walkExplorerItems(expl, (node, group, ancestors) => {
      const kind = node.attributes?.kind;
      if (kind !== "class" && kind !== "enum" && kind !== "slot") return;
      const name = node.attributes?.name || node.title;
      if (node.id !== key && name !== key) return;
      let score = node.id === key ? 3 : 2;
      const chain = [group, ...(ancestors || [])].filter(Boolean);
      if (
        chain.some(
          (g) =>
            g.id === "group:classes" ||
            g.attributes?.section_root === "classes"
        )
      ) {
        score += 2;
      }
      if (score > bestScore) {
        bestScore = score;
        best = node;
      }
    });
    if (!best) return null;
    return {
      module: shortModule(mod.module_id),
      section: expl.id,
      item: best.id,
      node: nodeForModule(mod.module_id)?.id || currentNodeId,
      card: true,
    };
  }

  function resolveTableCellTarget(mod, section, col, raw, item) {
    if (!raw || !mod) return null;
    const index = ensureLinkIndex();
    if (col === "name" || col === "title") {
      if (section?.attributes?.term_cards) {
        return resolveGlossaryTermPageTarget(mod, section, item);
      }
      if (section?.type === "glossary") {
        return resolveGlossaryTermPageTarget(mod, section, item);
      }
      if (section?.instance_of) {
        return {
          module: shortModule(mod.module_id),
          section: section.id,
          item: item.id,
          node: nodeForModule(mod.module_id)?.id || currentNodeId,
          card: true,
        };
      }
      return (
        findExplorerLinkTarget(mod, raw) ||
        findExplorerLinkTarget(mod, item.id) ||
        null
      );
    }
    if (col === "is_a" || col === "mixins" || col === "range") {
      return findExplorerLinkTarget(mod, raw) || null;
    }
    const hit = index.resolve(raw, mod);
    if (hit && hit.card) return hit;
    // Cross-module / same-module refs may resolve via explorer class name.
    return findExplorerLinkTarget(mod, raw);
  }

  function formatLinkedCellParts(mod, section, col, raw, item) {
    if (raw === null || raw === undefined || raw === "") return null;
    const multi = col === "mixins" || /_refs$/.test(col);
    const parts = multi
      ? String(raw)
          .split(/\s*,\s*/)
          .map((p) => p.trim())
          .filter(Boolean)
      : [String(raw).trim()].filter(Boolean);
    if (!parts.length) return null;
    const linked = parts.map((part) => {
      const target = resolveTableCellTarget(mod, section, col, part, item);
      if (!target) return escapeHtml(part);
      const href = itemHref(target);
      return `<a class="table-item-link" href="${escapeHtml(href)}" target="_blank" rel="noopener noreferrer">${escapeHtml(
        part
      )}</a>`;
    });
    // Only treat as linked cell if at least one part resolved.
    if (!linked.some((html) => html.includes("table-item-link"))) return null;
    return linked.join(", ");
  }

  function formatTableCellHtml(col, raw, item, mod, section) {
    const attrs = item?.attributes || {};
    if (col === "decision" || col === "review_status") {
      const kind = col === "decision" ? "decision" : "review";
      return `<span class="${statusChipClass(kind, raw)}" title="${escapeHtml(raw)}">${escapeHtml(
        raw || "—"
      )}</span>`;
    }
    if (col === "mapping_confirmed") {
      const confirmed = String(raw).toLowerCase() === "true";
      const label = confirmed ? "confirmed mapping" : "not confirmed";
      return `<span class="${statusChipClass("mapping", String(confirmed))}" title="${escapeHtml(
        label
      )}">${escapeHtml(label)}</span>`;
    }
    if (col === "upstream_iri" || col === "iri" || /_iri$/.test(col)) {
      const full = raw || String(attrs.upstream_iri || attrs.iri || "");
      const short = shortIriLabel(full);
      const link =
        isHttpUrl(full) && !full.includes("_placeholder") && full !== "REPLACE_WITH_REAL_FIBO_IRI"
          ? `<a class="iri-ext-link" href="${escapeHtml(full)}" target="_blank" rel="noopener noreferrer" title="Open IRI">↗</a>`
          : "";
      return `<span class="iri-cell"><code class="middle-ellipsis" title="${escapeHtml(
        full
      )}">${escapeHtml(short)}</code>
        <span class="cell-actions">
          <button type="button" class="copy-btn" data-copy="${escapeHtml(full)}" aria-label="Copy full IRI">copy</button>
          ${link}
        </span></span>`;
    }
    if (isLinkableTableColumn(col)) {
      const linkedHtml = formatLinkedCellParts(mod, section, col, raw, item);
      if (linkedHtml) {
        return `${linkedHtml}<span class="cell-actions"><button type="button" class="copy-btn" data-copy="${escapeHtml(
          raw
        )}">copy</button></span>`;
      }
    }
    const long = raw.length > 160;
    const text = long
      ? `<span class="long-text clamped" data-full="${escapeHtml(raw)}">${escapeHtml(
          raw.slice(0, 160)
        )}…</span>
         <button type="button" class="expand-btn">more</button>`
      : `<span>${escapeHtml(raw)}</span>`;
    return `${text}<span class="cell-actions"><button type="button" class="copy-btn" data-copy="${escapeHtml(
      raw
    )}">copy</button></span>`;
  }

  function renderTable(mod, section) {
    const root = document.createElement("div");
    const columns = section.columns?.length ? section.columns : inferColumns(section.items);

    const state = {
      sortCol: section.sort_by || null,
      sortDir: section.sort_order || "asc",
      filters: {},
      page: 0,
      nameQuery: "",
      descQuery: "",
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
    const nameQ = document.createElement("input");
    nameQ.type = "search";
    nameQ.placeholder = "Поиск по имени";
    nameQ.addEventListener("input", () => {
      state.nameQuery = nameQ.value.trim().toLowerCase();
      state.page = 0;
      paint();
    });
    const descQ = document.createElement("input");
    descQ.type = "search";
    descQ.placeholder = "Поиск по описанию";
    descQ.addEventListener("input", () => {
      state.descQuery = descQ.value.trim().toLowerCase();
      state.page = 0;
      paint();
    });
    toolbar.appendChild(filterSelects);
    toolbar.appendChild(nameQ);
    toolbar.appendChild(descQ);
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
      if (state.nameQuery) {
        const q = state.nameQuery;
        rows = rows.filter((r) =>
          [r.title, r.attributes?.name, r.attributes?.label, r.attributes?.label_ru, r.id]
            .some((v) => String(v || "").toLowerCase().includes(q))
        );
      }
      if (state.descQuery) {
        const q = state.descQuery;
        rows = rows.filter((r) =>
          [
            r.description,
            r.attributes?.definition,
            r.attributes?.definition_ru,
          ].some((v) => String(v || "").toLowerCase().includes(q))
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
              return `<td>${formatTableCellHtml(c, raw, item, mod, section)}</td>`;
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

  function glossaryTermLabel(item) {
    if (!item) return "";
    const en = item.attributes?.label || item.title || item.id;
    const ru = (item.attributes?.label_ru || "").trim();
    return ru ? `${en} (${ru})` : en;
  }

  function resolveItemInGlossary(section, raw) {
    const key = String(raw || "").trim();
    if (!key || !section) return null;
    const cid = canonicalGlossaryId(key);
    return (
      (section.items || []).find((i) => i.id === key) ||
      (section.items || []).find((i) => canonicalGlossaryId(i.id) === cid) ||
      (section.items || []).find((i) => (i.attributes?.local_name || "") === key) ||
      (section.items || []).find((i) => (i.attributes?.name || "") === key) ||
      (section.items || []).find((i) => (i.attributes?.curie || "") === key) ||
      null
    );
  }

  /** ADR-027 associative neighbours only (see_also). Union over selected ids. */
  function collectGlossarySeeAlsoNeighbours(section, selectedIds) {
    const selected = selectedIds instanceof Set ? selectedIds : new Set(selectedIds || []);
    const selectedKeys = new Set();
    selected.forEach((id) => {
      selectedKeys.add(String(id));
      selectedKeys.add(canonicalGlossaryId(id));
    });
    const out = new Map();
    selected.forEach((fromId) => {
      const fromItem = resolveItemInGlossary(section, fromId);
      if (!fromItem) return;
      const seeAlso = Array.isArray(fromItem.attributes?.see_also)
        ? fromItem.attributes.see_also
        : [];
      seeAlso.forEach((entry) => {
        const raw = relTargetId(entry);
        if (!raw) return;
        const target = resolveItemInGlossary(section, raw);
        if (!target) return;
        const tid = target.id;
        if (selectedKeys.has(tid) || selectedKeys.has(canonicalGlossaryId(tid))) return;
        const rel =
          entry && typeof entry === "object" && entry.rel ? String(entry.rel) : "";
        if (!out.has(tid)) out.set(tid, []);
        out.get(tid).push({ fromId: fromItem.id, rel });
      });
    });
    return out;
  }

  /** Resolve alignment target across glossary sections (IRI / curie / local_name). */
  function resolveAlignmentAcrossModules(modList, raw) {
    const key = String(raw || "").trim();
    if (!key) return null;
    for (const m of modList || []) {
      for (const sec of m.sections || []) {
        if (sec.type !== "glossary") continue;
        const hit = resolveItemInGlossary(sec, key);
        if (hit) return hit;
        const byIri = (sec.items || []).find(
          (i) =>
            String(i.attributes?.iri || "") === key ||
            String(i.attributes?.upstream_iri || "") === key ||
            String(i.attributes?.curie || "") === key
        );
        if (byIri) return byIri;
      }
    }
    return null;
  }

  function alignmentRelLabel(entry) {
    if (entry && typeof entry === "object") {
      if (entry.rel) return String(entry.rel);
      const mk = entry.match_kind != null ? String(entry.match_kind).trim() : "";
      if (mk) {
        if (/match$/i.test(mk)) return `alignment:${mk}`;
        return `alignment:${mk}Match`;
      }
    }
    return "alignment:related";
  }

  /**
   * ADR-027 equivalence / assignment neighbours (external_class_refs,
   * glossary_term_refs). Unresolved IRIs become stub rows (no silent drop).
   * Returns Map<key, { item, edges, unresolved }>.
   */
  function collectGlossaryAlignmentNeighbours(section, selectedIds, modList) {
    const selected = selectedIds instanceof Set ? selectedIds : new Set(selectedIds || []);
    const selectedKeys = new Set();
    selected.forEach((id) => {
      selectedKeys.add(String(id));
      selectedKeys.add(canonicalGlossaryId(id));
    });
    const out = new Map();

    function addEdge(key, item, fromId, rel, unresolved) {
      if (!key) return;
      if (selectedKeys.has(key) || selectedKeys.has(canonicalGlossaryId(key))) return;
      if (!out.has(key)) {
        out.set(key, { item, edges: [], unresolved: !!unresolved });
      }
      out.get(key).edges.push({ fromId, rel });
    }

    selected.forEach((fromId) => {
      const fromItem = resolveItemInGlossary(section, fromId);
      if (!fromItem) return;
      const attrs = fromItem.attributes || {};
      const refs = []
        .concat(Array.isArray(attrs.external_class_refs) ? attrs.external_class_refs : [])
        .concat(Array.isArray(attrs.glossary_term_refs) ? attrs.glossary_term_refs : []);
      refs.forEach((entry) => {
        const raw = relTargetId(entry);
        if (!raw) return;
        const rel = alignmentRelLabel(entry);
        let target = resolveItemInGlossary(section, raw);
        if (!target) target = resolveAlignmentAcrossModules(modList, raw);
        if (target) {
          if (
            selectedKeys.has(target.id) ||
            selectedKeys.has(canonicalGlossaryId(target.id))
          ) {
            return;
          }
          addEdge(target.id, target, fromItem.id, rel, false);
          return;
        }
        const stub = {
          id: raw,
          title: shortIriLabel(raw) || raw,
          description: "",
          attributes: { kind: "external", iri: raw },
        };
        addEdge(raw, stub, fromItem.id, rel, true);
      });
    });
    return out;
  }

  function glossaryTaxonomyParentIds(item) {
    const attrs = item?.attributes || {};
    if (Array.isArray(attrs.taxonomy_parents) && attrs.taxonomy_parents.length) {
      return attrs.taxonomy_parents.map(relTargetId).filter(Boolean);
    }
    return [
      (attrs.parent_local_name || "").trim(),
      (attrs.is_a || "").trim(),
      (attrs.parent_concept_ref || "").trim(),
    ].filter(Boolean);
  }

  function buildGlossaryChildrenIndex(section) {
    const byParentKey = new Map();
    function add(parentKey, childId) {
      if (!parentKey || !childId) return;
      if (!byParentKey.has(parentKey)) byParentKey.set(parentKey, []);
      const arr = byParentKey.get(parentKey);
      if (!arr.includes(childId)) arr.push(childId);
    }
    (section.items || []).forEach((item) => {
      glossaryTaxonomyParentIds(item).forEach((pid) => {
        add(pid, item.id);
        const parent = resolveItemInGlossary(section, pid);
        if (parent) {
          add(parent.id, item.id);
          add(canonicalGlossaryId(parent.id), item.id);
          if (parent.attributes?.name) add(String(parent.attributes.name), item.id);
          if (parent.attributes?.local_name) {
            add(String(parent.attributes.local_name), item.id);
          }
        }
      });
    });
    return byParentKey;
  }

  function glossaryTaxonomyChildIds(item, childrenIndex) {
    const attrs = item?.attributes || {};
    if (Array.isArray(attrs.taxonomy_children) && attrs.taxonomy_children.length) {
      return attrs.taxonomy_children.map(relTargetId).filter(Boolean);
    }
    const keys = [
      item.id,
      canonicalGlossaryId(item.id),
      attrs.name,
      attrs.local_name,
    ]
      .map((k) => String(k || "").trim())
      .filter(Boolean);
    const out = [];
    keys.forEach((k) => {
      (childrenIndex.get(k) || []).forEach((id) => {
        if (!out.includes(id)) out.push(id);
      });
    });
    return out;
  }

  function glossaryDefinitionDependents(item, section) {
    const id = item.id;
    const cid = canonicalGlossaryId(id);
    return (section.items || []).filter((other) => {
      if (other.id === id) return false;
      const src = String(other.attributes?.definition_source || "").trim();
      if (!src) return false;
      return src === id || src === cid || canonicalGlossaryId(src) === cid;
    });
  }

  function glossaryTermLinkHtml(mod, section, targetIdOrItem) {
    const item =
      typeof targetIdOrItem === "object" && targetIdOrItem
        ? targetIdOrItem
        : resolveItemInGlossary(section, targetIdOrItem);
    if (item) {
      const target = resolveGlossaryTermPageTarget(mod, section, item);
      const href = itemHref(target);
      return `<a class="table-item-link" href="${escapeHtml(href)}" target="_blank" rel="noopener noreferrer">${escapeHtml(
        glossaryTermLabel(item)
      )}</a>`;
    }
    const raw = String(targetIdOrItem || "");
    return raw ? escapeHtml(raw) : "—";
  }

  function pickGlossaryListColumns(section) {
    const candidates = [
      "title",
      "kind",
      "model_level",
      "solution",
      "description",
      "defined_in",
      "origin",
      "source_domain",
      "definition_mode",
      "definition_source",
    ];
    return candidates.filter((c) =>
      (section.items || []).some((i) => Boolean(cellValue(i, c)))
    );
  }

  function renderGlossaryOverview(mod, section) {
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
        const title = glossaryTermLabel(item);
        const defEn = displayText(item.attributes?.definition || item.description || "");
        const defRu = displayText((item.attributes?.definition_ru || "").trim());
        const domain = item.attributes?.source_domain || "";
        const defMode = (item.attributes?.definition_mode || "").trim();
        const kind = (item.attributes?.kind || "").trim();
        const termCards = !!section.attributes?.term_cards;
        const modelLevel = (item.attributes?.model_level || "").trim();
        const solution = (item.attributes?.solution || "").trim();
        const modeBadge = defMode
          ? `<span class="glossary-mode-badge" data-mode="${escapeHtml(defMode)}">${escapeHtml(defMode)}</span>`
          : "";
        const kindBadge = kind
          ? `<span class="glossary-kind-badge">${escapeHtml(kind)}</span>`
          : "";
        const levelBadge =
          termCards && modelLevel
            ? `<span class="glossary-level-badge" data-level="${escapeHtml(modelLevel)}">${escapeHtml(modelLevel)}</span>`
            : "";
        const solutionBadge =
          termCards && solution
            ? `<span class="glossary-solution-badge">${escapeHtml(solution)}</span>`
            : "";
        const origin = (item.attributes?.origin || "").trim();
        const originBadge =
          !termCards && origin
            ? `<span class="glossary-origin-badge" data-origin="${escapeHtml(origin)}">${escapeHtml(origin)}</span>`
            : "";
        const definedIn = (item.attributes?.defined_in || "").trim();
        const metaLine = termCards
          ? [item.attributes?.source_item_id || item.id, solution, modelLevel]
              .filter(Boolean)
              .map((s) => escapeHtml(String(s)))
              .join(" · ")
          : `${escapeHtml(item.id)}${domain ? " · " + escapeHtml(domain) : ""}${
              definedIn ? " · " + escapeHtml(definedIn) : ""
            }`;
        card.innerHTML = `<h3>${escapeHtml(title)} ${levelBadge}${kindBadge}${modeBadge}${solutionBadge}${originBadge}</h3>
          <p>${escapeHtml(defEn)}</p>
          ${defRu ? `<p class="muted">${escapeHtml(defRu)}</p>` : ""}
          <div class="muted">${metaLine}</div>`;
        // ADR-027 blocks (Taxonomy / See also / Assignment / Origin).
        // Skip for aggregated implementations glossary (term_cards).
        // Keep legacy "extends" only when taxonomy_parents is absent.
        if (!termCards) {
          const hasTaxonomyAttrs = Array.isArray(item.attributes?.taxonomy_parents);
          if (!hasTaxonomyAttrs) {
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
          }
          const showAdr027 =
            item.attributes?.glossary_view ||
            item.attributes?.origin ||
            Array.isArray(item.attributes?.taxonomy_parents) ||
            Array.isArray(item.attributes?.see_also);
          if (showAdr027) {
            const known = new Set((section.items || []).map((i) => i.id));
            const expl = explorerSection(mod);
            if (expl) {
              collectExplorerIds(expl).forEach((id) => known.add(id));
            }
            appendAdr027RelationBlocks(card, mod, item, {
              known,
              expl: null,
              sectionId: section.id,
            });
          }
        }
        card.addEventListener("click", (e) => {
          if (e.target.closest("a, button")) return;
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

  function renderGlossaryListTable(mod, section) {
    const columns = pickGlossaryListColumns(section);
    const listSection = {
      ...section,
      type: "glossary",
      columns: columns.length ? columns : ["title", "description"],
    };
    return renderTable(mod, listSection);
  }

  function renderGlossaryHierarchyTable(mod, section) {
    const root = document.createElement("div");
    const items = (section.items || [])
      .slice()
      .sort((a, b) => (a.title || a.id).localeCompare(b.title || b.id));
    const childrenIndex = buildGlossaryChildrenIndex(section);
    let hasAnyLink = false;

    const scroll = document.createElement("div");
    scroll.className = "table-scroll";
    const table = document.createElement("table");
    table.className = "data-table glossary-hierarchy-table";
    const thead = `<thead><tr>
      <th>Term</th>
      <th>Parents</th>
      <th>Children</th>
      <th>Definition source</th>
      <th>Definition dependents</th>
    </tr></thead>`;

    const rows = items
      .map((item) => {
        const parents = glossaryTaxonomyParentIds(item);
        const children = glossaryTaxonomyChildIds(item, childrenIndex);
        const dependents = glossaryDefinitionDependents(item, section);
        const defSource = String(item.attributes?.definition_source || "").trim();
        const defMode = String(item.attributes?.definition_mode || "").trim();
        if (parents.length || children.length || dependents.length || defSource) {
          hasAnyLink = true;
        }
        const parentsHtml = parents.length
          ? parents.map((p) => glossaryTermLinkHtml(mod, section, p)).join(", ")
          : "—";
        const childrenHtml = children.length
          ? children.map((c) => glossaryTermLinkHtml(mod, section, c)).join(", ")
          : "—";
        const modeBadge = defMode
          ? ` <span class="glossary-mode-badge" data-mode="${escapeHtml(defMode)}">${escapeHtml(
              defMode
            )}</span>`
          : "";
        let sourceHtml = "—";
        if (defSource) {
          const selfRef =
            defSource === item.id ||
            defSource === canonicalGlossaryId(item.id) ||
            canonicalGlossaryId(defSource) === canonicalGlossaryId(item.id);
          sourceHtml = selfRef
            ? `${escapeHtml(defSource)}${modeBadge}`
            : `${glossaryTermLinkHtml(mod, section, defSource)}${modeBadge}`;
        }
        const dependentsHtml = dependents.length
          ? dependents.map((d) => glossaryTermLinkHtml(mod, section, d)).join(", ")
          : "—";
        return `<tr data-item-id="${escapeHtml(item.id)}">
          <td>${glossaryTermLinkHtml(mod, section, item)}</td>
          <td>${parentsHtml}</td>
          <td>${childrenHtml}</td>
          <td>${sourceHtml}</td>
          <td>${dependentsHtml}</td>
        </tr>`;
      })
      .join("");

    table.innerHTML = thead + `<tbody>${rows}</tbody>`;
    scroll.appendChild(table);
    if (!hasAnyLink) {
      const empty = document.createElement("p");
      empty.className = "muted";
      empty.textContent =
        "No hierarchy or definition-override links in this glossary.";
      root.appendChild(empty);
    }
    root.appendChild(scroll);
    return root;
  }

  function renderGlossaryRelations(mod, section, opts) {
    const columns = pickGlossaryListColumns(section);
    const cols = columns.length ? columns : ["title", "description"];
    const selected =
      opts && opts.selected instanceof Set ? opts.selected : new Set();
    const onSelectionChange =
      opts && typeof opts.onSelectionChange === "function"
        ? opts.onSelectionChange
        : null;
    const state = {
      sortCol: null,
      sortDir: "asc",
      filters: {},
      page: 0,
      nameQuery: "",
      descQuery: "",
    };

    const layout = document.createElement("div");
    layout.className = "glossary-relations-layout";

    // Toolbar above the split so filter/search rows do not crush the picker table.
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
    const nameQ = document.createElement("input");
    nameQ.type = "search";
    nameQ.placeholder = "Поиск по имени";
    nameQ.addEventListener("input", () => {
      state.nameQuery = nameQ.value.trim().toLowerCase();
      state.page = 0;
      paint();
    });
    const descQ = document.createElement("input");
    descQ.type = "search";
    descQ.placeholder = "Поиск по описанию";
    descQ.addEventListener("input", () => {
      state.descQuery = descQ.value.trim().toLowerCase();
      state.page = 0;
      paint();
    });
    toolbar.appendChild(filterSelects);
    toolbar.appendChild(nameQ);
    toolbar.appendChild(descQ);
    const chips = document.createElement("div");
    chips.className = "chips";
    toolbar.appendChild(chips);

    const upper = document.createElement("div");
    upper.className = "glossary-relations-pane glossary-relations-pane--picker";
    const upperScroll = document.createElement("div");
    upperScroll.className = "table-scroll";
    const upperTable = document.createElement("table");
    upperTable.className = "data-table";
    upperScroll.appendChild(upperTable);
    upper.appendChild(upperScroll);
    const pager = document.createElement("div");
    pager.className = "pager";
    upper.appendChild(pager);

    const lower = document.createElement("div");
    lower.className = "glossary-relations-pane glossary-relations-pane--results";
    const lowerScroll = document.createElement("div");
    lowerScroll.className = "table-scroll";
    const lowerTable = document.createElement("table");
    lowerTable.className = "data-table";
    lowerScroll.appendChild(lowerTable);
    const lowerEmpty = document.createElement("p");
    lowerEmpty.className = "muted glossary-relations-empty";
    lower.appendChild(lowerEmpty);
    lower.appendChild(lowerScroll);

    layout.appendChild(toolbar);
    layout.appendChild(upper);
    layout.appendChild(lower);

    function sortRows(rows) {
      const list = rows.slice();
      if (state.sortCol) {
        const col = state.sortCol;
        const dir = state.sortDir === "asc" ? 1 : -1;
        list.sort(
          (a, b) =>
            cellValue(a, col).localeCompare(cellValue(b, col), undefined, {
              numeric: true,
            }) * dir
        );
      } else {
        list.sort((a, b) =>
          (a.title || a.id).localeCompare(b.title || b.id, undefined, { numeric: true })
        );
      }
      return list;
    }

    function matchesFilters(item) {
      for (const [col, val] of Object.entries(state.filters)) {
        if (cellValue(item, col) !== val) return false;
      }
      if (state.nameQuery) {
        const q = state.nameQuery;
        const hit = [
          item.title,
          item.attributes?.name,
          item.attributes?.label,
          item.attributes?.label_ru,
          item.id,
        ].some((v) => String(v || "").toLowerCase().includes(q));
        if (!hit) return false;
      }
      if (state.descQuery) {
        const q = state.descQuery;
        const hit = [
          item.description,
          item.attributes?.definition,
          item.attributes?.definition_ru,
        ].some((v) => String(v || "").toLowerCase().includes(q));
        if (!hit) return false;
      }
      return true;
    }

    function bindTableChrome(tableEl, onHeaderClick) {
      tableEl.querySelectorAll("th[data-col]").forEach((th) => {
        th.addEventListener("click", () => onHeaderClick(th.dataset.col));
      });
      tableEl.querySelectorAll(".copy-btn").forEach((btn) => {
        btn.addEventListener("click", (e) => {
          e.stopPropagation();
          navigator.clipboard?.writeText(btn.dataset.copy || "");
        });
      });
      tableEl.querySelectorAll(".expand-btn").forEach((btn) => {
        btn.addEventListener("click", (e) => {
          e.stopPropagation();
          const span = btn.previousElementSibling;
          span.classList.toggle("clamped");
          if (!span.classList.contains("clamped")) span.textContent = span.dataset.full;
          else span.textContent = span.dataset.full.slice(0, 160) + "…";
          btn.textContent = span.classList.contains("clamped") ? "more" : "less";
        });
      });
    }

    function rowCellsHtml(item) {
      return cols
        .map((c) => {
          const raw = cellValue(item, c);
          return `<td>${formatTableCellHtml(c, raw, item, mod, section)}</td>`;
        })
        .join("");
    }

    function emptyNeighboursMessage(assocCount, alignCount) {
      let withAssoc = 0;
      let withAlign = 0;
      let hiddenBecauseSelected = 0;
      const selectedKeys = new Set();
      selected.forEach((id) => {
        selectedKeys.add(String(id));
        selectedKeys.add(canonicalGlossaryId(id));
      });
      selected.forEach((fromId) => {
        const fromItem = resolveItemInGlossary(section, fromId);
        const seeAlso = Array.isArray(fromItem?.attributes?.see_also)
          ? fromItem.attributes.see_also
          : [];
        if (seeAlso.length) withAssoc += 1;
        seeAlso.forEach((entry) => {
          const target = resolveItemInGlossary(section, relTargetId(entry));
          if (!target) return;
          if (
            selectedKeys.has(target.id) ||
            selectedKeys.has(canonicalGlossaryId(target.id))
          ) {
            hiddenBecauseSelected += 1;
          }
        });
        const attrs = fromItem?.attributes || {};
        const refs = []
          .concat(Array.isArray(attrs.external_class_refs) ? attrs.external_class_refs : [])
          .concat(Array.isArray(attrs.glossary_term_refs) ? attrs.glossary_term_refs : []);
        if (refs.length) withAlign += 1;
      });
      if (assocCount === 0 && alignCount === 0 && withAlign > 0) {
        return "Нет отображаемых связей эквивалентности у выбранных терминов.";
      }
      if (withAssoc === 0 && withAlign === 0) {
        return (
          "Нет ассоциативных связей и связей эквивалентности у выбранных терминов. " +
          "Иерархия — на вкладке «Иерархия»."
        );
      }
      if (hiddenBecauseSelected > 0 && assocCount === 0 && alignCount === 0) {
        return (
          "Все связанные термины уже входят в выборку. " +
          "Снимите часть отметок, чтобы увидеть их внизу."
        );
      }
      if (withAssoc === 0) {
        return "Нет ассоциативных связей (see also / Relationship) у выбранных терминов.";
      }
      return "Нет ассоциативных связей у выбранных терминов.";
    }

    function paintLower() {
      if (!selected.size) {
        lowerEmpty.hidden = false;
        lowerEmpty.textContent =
          "Отметьте термины сверху, чтобы увидеть связанные.";
        lowerScroll.hidden = true;
        lowerTable.innerHTML = "";
        return;
      }
      const assoc = collectGlossarySeeAlsoNeighbours(section, selected);
      const align = collectGlossaryAlignmentNeighbours(section, selected, modules);
      const byKey = new Map();
      assoc.forEach((edges, tid) => {
        const item = resolveItemInGlossary(section, tid);
        if (!item) return;
        byKey.set(tid, { item, edges: edges.slice(), unresolved: false });
      });
      align.forEach((rec, key) => {
        if (byKey.has(key)) {
          byKey.get(key).edges.push(...rec.edges);
        } else {
          byKey.set(key, {
            item: rec.item,
            edges: rec.edges.slice(),
            unresolved: !!rec.unresolved,
          });
        }
      });
      if (!byKey.size) {
        lowerEmpty.hidden = false;
        lowerEmpty.textContent = emptyNeighboursMessage(assoc.size, align.size);
        lowerScroll.hidden = true;
        lowerTable.innerHTML = "";
        return;
      }
      lowerEmpty.hidden = true;
      lowerScroll.hidden = false;
      const rows = [...byKey.values()];
      const resolved = rows.filter((r) => !r.unresolved).map((r) => r.item);
      const sortedResolved = sortRows(resolved);
      const unresolved = rows
        .filter((r) => r.unresolved)
        .sort((a, b) =>
          (a.item.title || a.item.id).localeCompare(b.item.title || b.item.id, undefined, {
            numeric: true,
          })
        );
      const ordered = sortedResolved
        .map((item) => byKey.get(item.id))
        .concat(unresolved)
        .filter(Boolean);
      const thead = `<thead><tr>${cols
        .map((c) => `<th>${escapeHtml(c)}</th>`)
        .join("")}<th>Связь</th></tr></thead>`;
      const tbody = `<tbody>${ordered
        .map((rec) => {
          const item = rec.item;
          const edges = rec.edges || [];
          const linkText = edges
            .map((e) => {
              const from = resolveItemInGlossary(section, e.fromId);
              const fromLabel = glossaryTermLabel(from) || e.fromId;
              return e.rel ? `${fromLabel} → ${e.rel}` : fromLabel;
            })
            .join(", ");
          const cells = rec.unresolved
            ? cols
                .map((c) => {
                  if (c === "title" || c === "name") {
                    return `<td><span class="spec-link disabled glossary-rel-chip" title="${escapeHtml(
                      item.id
                    )}">${escapeHtml(item.title || item.id)}</span></td>`;
                  }
                  if (c === "description") {
                    return `<td><span class="muted">${escapeHtml(
                      item.id
                    )}</span></td>`;
                  }
                  return `<td>—</td>`;
                })
                .join("")
            : rowCellsHtml(item);
          return `<tr data-item-id="${escapeHtml(item.id)}">${cells}<td>${escapeHtml(
            linkText
          )}</td></tr>`;
        })
        .join("")}</tbody>`;
      lowerTable.innerHTML = thead + tbody;
      bindTableChrome(lowerTable, () => {});
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

      const pinned = sortRows(
        (section.items || []).filter((i) => selected.has(i.id))
      );
      const unpinned = sortRows(
        (section.items || []).filter((i) => !selected.has(i.id) && matchesFilters(i))
      );
      const pages = Math.max(1, Math.ceil(unpinned.length / PAGE_SIZE));
      if (state.page >= pages) state.page = pages - 1;
      const slice = unpinned.slice(
        state.page * PAGE_SIZE,
        (state.page + 1) * PAGE_SIZE
      );

      const headCols = `<th aria-label="Select"></th>${cols
        .map(
          (c) =>
            `<th data-col="${escapeHtml(c)}">${escapeHtml(c)}${
              state.sortCol === c ? (state.sortDir === "asc" ? " ▲" : " ▼") : ""
            }</th>`
        )
        .join("")}`;

      function pickerRow(item, pinnedRow) {
        const checked = selected.has(item.id) ? " checked" : "";
        const cls = pinnedRow ? ' class="glossary-relations-pinned"' : "";
        return `<tr data-item-id="${escapeHtml(item.id)}"${cls}>
          <td><input type="checkbox" class="glossary-relations-check" data-item-id="${escapeHtml(
            item.id
          )}"${checked} /></td>
          ${rowCellsHtml(item)}
        </tr>`;
      }

      upperTable.innerHTML =
        `<thead><tr>${headCols}</tr></thead><tbody>${pinned
          .map((i) => pickerRow(i, true))
          .concat(slice.map((i) => pickerRow(i, false)))
          .join("")}</tbody>`;

      bindTableChrome(upperTable, (col) => {
        if (state.sortCol === col) state.sortDir = state.sortDir === "asc" ? "desc" : "asc";
        else {
          state.sortCol = col;
          state.sortDir = "asc";
        }
        paint();
      });
      upperTable.querySelectorAll(".glossary-relations-check").forEach((cb) => {
        cb.addEventListener("click", (e) => e.stopPropagation());
        cb.addEventListener("change", () => {
          const id = cb.dataset.itemId;
          if (cb.checked) selected.add(id);
          else selected.delete(id);
          state.page = 0;
          paint();
          if (onSelectionChange) onSelectionChange(selected);
        });
      });

      pager.innerHTML = `<span class="muted">${unpinned.length} rows</span>`;
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
        pager.appendChild(
          document.createTextNode(` ${state.page + 1} / ${pages} `)
        );
        pager.appendChild(next);
      }

      paintLower();
    }

    paint();
    return layout;
  }

  function hierarchyGraphIndex(section) {
    const graph = (section.attributes || {}).hierarchy_graph || {};
    const nodes = Array.isArray(graph.nodes) ? graph.nodes : [];
    const edges = Array.isArray(graph.edges) ? graph.edges : [];
    const byId = new Map();
    nodes.forEach((n) => {
      if (n && n.id) byId.set(String(n.id), n);
    });
    // Fall back to glossary items when graph node missing (OWL stubs in items).
    (section.items || []).forEach((item) => {
      if (byId.has(item.id)) return;
      const layer =
        item.attributes?.layer || item.attributes?.model_level || "CDM";
      byId.set(item.id, {
        id: item.id,
        layer,
        title: item.title || item.id,
        name: item.attributes?.name || item.title || item.id,
        solution: item.attributes?.solution || "",
        solution_id: item.attributes?.solution_id || "",
        kind: item.attributes?.kind || "entity",
        description: item.description || "",
      });
    });
    return { byId, edges, nodes: [...byId.values()] };
  }

  /** BFS neighborhood with per-layer hop limits (OWL / CDM / LDM). */
  function collectHierarchyNeighborhood(section, seedIds, hops) {
    const { byId, edges } = hierarchyGraphIndex(section);
    const hop = {
      OWL: Math.max(0, Number(hops?.OWL) || 0),
      CDM: Math.max(0, Number(hops?.CDM) || 0),
      LDM: Math.max(0, Number(hops?.LDM) || 0),
    };
    const adj = new Map();
    edges.forEach((e) => {
      if (!e || !e.source || !e.target) return;
      const s = String(e.source);
      const t = String(e.target);
      if (!adj.has(s)) adj.set(s, []);
      if (!adj.has(t)) adj.set(t, []);
      adj.get(s).push(t);
      adj.get(t).push(s);
    });

    function bandOf(id) {
      const layer = String(byId.get(id)?.layer || "CDM").toUpperCase();
      return layer === "OWL" || layer === "LDM" ? layer : "CDM";
    }

    // Best per-layer depth vector found for each node (sum of depths as score).
    const best = new Map();
    const queue = [];
    (seedIds || []).forEach((id) => {
      const sid = String(id);
      if (!byId.has(sid)) return;
      const depths = { OWL: 0, CDM: 0, LDM: 0 };
      best.set(sid, depths);
      queue.push({ id: sid, depths });
    });

    function score(d) {
      return (d.OWL || 0) + (d.CDM || 0) + (d.LDM || 0);
    }

    while (queue.length) {
      const cur = queue.shift();
      (adj.get(cur.id) || []).forEach((to) => {
        if (!byId.has(to)) return;
        const band = bandOf(to);
        const next = {
          OWL: cur.depths.OWL || 0,
          CDM: cur.depths.CDM || 0,
          LDM: cur.depths.LDM || 0,
        };
        next[band] = (next[band] || 0) + 1;
        if (next[band] > hop[band]) return;
        const prev = best.get(to);
        if (prev && score(prev) <= score(next)) return;
        best.set(to, next);
        queue.push({ id: to, depths: next });
      });
    }

    const nodeIds = new Set(best.keys());
    const outEdges = edges.filter(
      (e) => nodeIds.has(String(e.source)) && nodeIds.has(String(e.target))
    );
    const outNodes = [...nodeIds].map((id) => byId.get(id)).filter(Boolean);
    return { nodes: outNodes, edges: outEdges };
  }

  function hierarchyMermaidNodeId(rawId, used) {
    let base = String(rawId || "n").replace(/[^A-Za-z0-9_]/g, "_");
    if (!/^[A-Za-z_]/.test(base)) base = `n_${base}`;
    let id = base || "n";
    let i = 2;
    while (used.has(id)) {
      id = `${base}_${i}`;
      i += 1;
    }
    used.add(id);
    return id;
  }

  function hierarchyNeighborhoodToMermaid(nodes, edges) {
    const list = Array.isArray(nodes) ? nodes : [];
    const edgeList = Array.isArray(edges) ? edges : [];
    if (!list.length) {
      return (
        "%% Отметьте сущности на вкладке «Связи», чтобы построить схему.\n" +
        "flowchart TB\n"
      );
    }
    const used = new Set();
    const idMap = new Map();
    list.forEach((n) => {
      idMap.set(String(n.id), hierarchyMermaidNodeId(n.id, used));
    });
    function bandOf(n) {
      const layer = String(n.layer || "CDM").toUpperCase();
      return layer === "OWL" || layer === "LDM" ? layer : "CDM";
    }
    function escapeLabel(s) {
      // Mermaid text entities: #quot; → "
      return String(s || "").replace(/"/g, "#quot;");
    }
    const lines = ["flowchart TB"];
    ["OWL", "CDM", "LDM"].forEach((band) => {
      const bandNodes = list.filter((n) => bandOf(n) === band);
      if (!bandNodes.length) return;
      const bySol = new Map();
      bandNodes.forEach((n) => {
        const sid = String(n.solution_id || n.solution || "other");
        if (!bySol.has(sid)) bySol.set(sid, []);
        bySol.get(sid).push(n);
      });
      lines.push(`  subgraph ${band}["${band}"]`);
      for (const [sid, kids] of bySol.entries()) {
        const solLabel = escapeLabel(kids[0]?.solution || sid);
        const solSubId = hierarchyMermaidNodeId(`sol_${band}_${sid}`, used);
        lines.push(`    subgraph ${solSubId}["${solLabel}"]`);
        kids.forEach((n) => {
          const mid = idMap.get(String(n.id));
          const label = escapeLabel(n.title || n.name || n.id);
          lines.push(`      ${mid}["${label}"]`);
        });
        lines.push("    end");
      }
      lines.push("  end");
    });
    edgeList.forEach((e) => {
      const s = idMap.get(String(e.source));
      const t = idMap.get(String(e.target));
      if (!s || !t) return;
      const rel = String(e.rel || "").trim();
      if (rel) {
        lines.push(`  ${s} -->|"${escapeLabel(rel)}"| ${t}`);
      } else {
        lines.push(`  ${s} --> ${t}`);
      }
    });
    return lines.join("\n") + "\n";
  }

  function hierarchyNodeSize(title) {
    const t = String(title || "");
    const w = Math.min(220, Math.max(120, 10 + t.length * 7.2));
    return { width: w, height: 40 };
  }

  function buildElkHierarchyGraph(nodes, edges) {
    const layers = { OWL: [], CDM: [], LDM: [] };
    const nodeBand = new Map();
    nodes.forEach((n) => {
      const layer = String(n.layer || "CDM").toUpperCase();
      const band = layer === "OWL" || layer === "LDM" ? layer : "CDM";
      layers[band].push(n);
      nodeBand.set(n.id, band);
    });
    const bandRank = { OWL: 0, CDM: 1, LDM: 2 };

    function solutionClusters(bandNodes, band) {
      const bySol = new Map();
      bandNodes.forEach((n) => {
        const sid = String(n.solution_id || n.solution || "other");
        if (!bySol.has(sid)) bySol.set(sid, []);
        bySol.get(sid).push(n);
      });
      return [...bySol.entries()].map(([sid, kids]) => {
        const label = kids[0]?.solution || sid;
        return {
          id: `cluster:${band}:${sid}`,
          labels: [{ text: label }],
          layoutOptions: {
            "elk.padding": "[top=28,left=16,bottom=16,right=16]",
          },
          children: kids.map((n) => {
            const size = hierarchyNodeSize(n.title || n.name || n.id);
            return {
              id: n.id,
              width: size.width,
              height: size.height,
              labels: [{ text: n.title || n.name || n.id }],
            };
          }),
        };
      });
    }

    const children = [];
    ["OWL", "CDM", "LDM"].forEach((band) => {
      if (!layers[band].length) return;
      children.push({
        id: `band:${band}`,
        labels: [{ text: band }],
        layoutOptions: {
          "elk.padding": "[top=32,left=20,bottom=20,right=20]",
          "elk.algorithm": "layered",
          "elk.direction": "RIGHT",
        },
        children: solutionClusters(layers[band], band),
      });
    });

    // Orient edges OWL→CDM→LDM so layered DOWN keeps bands top→bottom.
    const elkEdges = edges.map((e, i) => {
      let s = String(e.source);
      let t = String(e.target);
      const sb = bandRank[nodeBand.get(s)] ?? 1;
      const tb = bandRank[nodeBand.get(t)] ?? 1;
      if (sb > tb) {
        const tmp = s;
        s = t;
        t = tmp;
      }
      return {
        id: `e${i}:${e.source}->${e.target}`,
        sources: [s],
        targets: [t],
        labels: e.rel ? [{ text: String(e.rel) }] : [],
      };
    });

    return {
      id: "root",
      layoutOptions: {
        "elk.algorithm": "layered",
        "elk.direction": "DOWN",
        "elk.edgeRouting": "ORTHOGONAL",
        "elk.spacing.nodeNode": "40",
        "elk.layered.spacing.nodeNodeBetweenLayers": "56",
        "elk.hierarchyHandling": "INCLUDE_CHILDREN",
        "elk.padding": "[top=24,left=24,bottom=24,right=24]",
      },
      children,
      edges: elkEdges,
    };
  }

  function flattenElkNodes(node, absX, absY, out) {
    const x = (node.x || 0) + absX;
    const y = (node.y || 0) + absY;
    out.push({
      id: node.id,
      x,
      y,
      width: node.width || 0,
      height: node.height || 0,
      labels: node.labels || [],
      isCompound: !!(node.children && node.children.length),
    });
    (node.children || []).forEach((ch) => flattenElkNodes(ch, x, y, out));
  }

  function elkEdgePoints(edge) {
    const sections = edge.sections || [];
    const pts = [];
    sections.forEach((sec) => {
      if (sec.startPoint) pts.push(sec.startPoint);
      (sec.bendPoints || []).forEach((b) => pts.push(b));
      if (sec.endPoint) pts.push(sec.endPoint);
    });
    return pts;
  }

  /** Orthogonal path between two leaf boxes (ELK layout positions only). */
  function hierarchyConnectPath(srcBox, tgtBox) {
    if (!srcBox || !tgtBox) return null;
    const sp = { x: srcBox.x, y: srcBox.y };
    const tp = { x: tgtBox.x, y: tgtBox.y };
    const sm = { width: srcBox.width, height: srcBox.height };
    const tm = { width: tgtBox.width, height: tgtBox.height };
    const [side1, side2] = erdPickSides(sp, sm, tp, tm);
    const a1 = erdAnchorOnSide(sp, sm, side1);
    const a2 = erdAnchorOnSide(tp, tm, side2);
    return {
      d: orthogonalErdPath(a1.x, a1.y, a2.x, a2.y, null, side1, side2),
      midX: (a1.x + a2.x) / 2,
      midY: (a1.y + a2.y) / 2,
    };
  }

  function downloadBlob(filename, blob) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }

  function exportHierarchySvg(svgEl, basename) {
    if (!svgEl) return;
    const clone = svgEl.cloneNode(true);
    clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    const bg = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    bg.setAttribute("x", "0");
    bg.setAttribute("y", "0");
    bg.setAttribute("width", "100%");
    bg.setAttribute("height", "100%");
    bg.setAttribute("fill", "#ffffff");
    clone.insertBefore(bg, clone.firstChild);
    const xml = new XMLSerializer().serializeToString(clone);
    downloadBlob(
      `${basename || "moex-hierarchy"}.svg`,
      new Blob([xml], { type: "image/svg+xml;charset=utf-8" })
    );
  }

  function exportHierarchyPng(svgEl, basename) {
    if (!svgEl) return;
    const clone = svgEl.cloneNode(true);
    clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    const vb = (clone.getAttribute("viewBox") || "0 0 800 600").split(/\s+/).map(Number);
    const w = vb[2] || 800;
    const h = vb[3] || 600;
    const bg = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    bg.setAttribute("x", String(vb[0] || 0));
    bg.setAttribute("y", String(vb[1] || 0));
    bg.setAttribute("width", String(w));
    bg.setAttribute("height", String(h));
    bg.setAttribute("fill", "#ffffff");
    clone.insertBefore(bg, clone.firstChild);
    const xml = new XMLSerializer().serializeToString(clone);
    const img = new Image();
    const url = URL.createObjectURL(
      new Blob([xml], { type: "image/svg+xml;charset=utf-8" })
    );
    img.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = Math.max(1, Math.round(w * 2));
      canvas.height = Math.max(1, Math.round(h * 2));
      const ctx = canvas.getContext("2d");
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      URL.revokeObjectURL(url);
      canvas.toBlob((blob) => {
        if (blob) downloadBlob(`${basename || "moex-hierarchy"}@2x.png`, blob);
      }, "image/png");
    };
    img.onerror = () => URL.revokeObjectURL(url);
    img.src = url;
  }

  function renderHierarchyVisualization(mod, section, opts) {
    const selected =
      opts && opts.selected instanceof Set ? opts.selected : new Set();
    const hops = opts && opts.hops ? opts.hops : { OWL: 1, CDM: 1, LDM: 1 };
    const onToggleSeed =
      opts && typeof opts.onToggleSeed === "function" ? opts.onToggleSeed : null;
    const onNeighborhoodChange =
      opts && typeof opts.onNeighborhoodChange === "function"
        ? opts.onNeighborhoodChange
        : null;

    const root = document.createElement("div");
    root.className = "hierarchy-viz";

    const toolbar = document.createElement("div");
    toolbar.className = "hierarchy-viz-toolbar section-toolbar";
    const hopWrap = document.createElement("div");
    hopWrap.className = "hierarchy-hop-controls chips";
    ["OWL", "CDM", "LDM"].forEach((band) => {
      const label = document.createElement("label");
      label.className = "hierarchy-hop-label";
      label.textContent = `${band} hop `;
      const input = document.createElement("input");
      input.type = "number";
      input.min = "0";
      input.max = "5";
      input.value = String(hops[band] ?? 1);
      input.dataset.band = band;
      input.addEventListener("change", () => {
        hops[band] = Math.max(0, Math.min(5, Number(input.value) || 0));
        paint();
        if (onNeighborhoodChange) onNeighborhoodChange();
      });
      label.appendChild(input);
      hopWrap.appendChild(label);
    });
    const btnSvg = document.createElement("button");
    btnSvg.type = "button";
    btnSvg.className = "erd-tool-btn";
    btnSvg.textContent = "Скачать SVG";
    const btnPng = document.createElement("button");
    btnPng.type = "button";
    btnPng.className = "erd-tool-btn";
    btnPng.textContent = "Скачать PNG";
    const status = document.createElement("span");
    status.className = "muted";
    toolbar.appendChild(hopWrap);
    toolbar.appendChild(btnSvg);
    toolbar.appendChild(btnPng);
    toolbar.appendChild(status);

    const canvas = document.createElement("div");
    canvas.className = "hierarchy-viz-canvas";
    root.appendChild(toolbar);
    root.appendChild(canvas);

    let svgEl = null;
    const view = { panX: 0, panY: 0, scale: 1 };

    btnSvg.addEventListener("click", () => exportHierarchySvg(svgEl, "moex-hierarchy"));
    btnPng.addEventListener("click", () => exportHierarchyPng(svgEl, "moex-hierarchy"));

    function paintEmpty(msg) {
      canvas.replaceChildren();
      svgEl = null;
      const p = document.createElement("p");
      p.className = "muted hierarchy-viz-empty";
      p.textContent = msg;
      canvas.appendChild(p);
    }

    async function paint() {
      if (!selected.size) {
        status.textContent = "";
        paintEmpty("Отметьте сущности на вкладке «Связи», чтобы построить схему.");
        return;
      }
      if (typeof ELK !== "function") {
        paintEmpty("Движок раскладки elkjs не загружен.");
        return;
      }
      const neigh = collectHierarchyNeighborhood(section, [...selected], hops);
      if (!neigh.nodes.length) {
        paintEmpty("Нет узлов в окрестности с текущими hop.");
        return;
      }
      status.textContent = `${neigh.nodes.length} узлов · ${neigh.edges.length} рёбер`;
      const elkGraph = buildElkHierarchyGraph(neigh.nodes, neigh.edges);
      let laid;
      try {
        laid = await new ELK().layout(elkGraph);
      } catch (err) {
        paintEmpty(`Ошибка раскладки ELK: ${err?.message || err}`);
        return;
      }
      const flat = [];
      flattenElkNodes(laid, 0, 0, flat);
      const byId = new Map(neigh.nodes.map((n) => [n.id, n]));
      const width = Math.max(400, (laid.width || 800) + 40);
      const height = Math.max(300, (laid.height || 600) + 40);

      const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.setAttribute("class", "hierarchy-scene");
      svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
      svg.setAttribute("width", "100%");
      svg.setAttribute("height", "100%");

      // Legend
      const legend = document.createElementNS("http://www.w3.org/2000/svg", "g");
      legend.setAttribute("class", "hierarchy-legend");
      [
        ["OWL", "#e8eef7"],
        ["CDM", "#eef6ee"],
        ["LDM", "#f7f0e8"],
      ].forEach(([name, fill], i) => {
        const x = 16 + i * 88;
        const r = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        r.setAttribute("x", String(x));
        r.setAttribute("y", "8");
        r.setAttribute("width", "16");
        r.setAttribute("height", "16");
        r.setAttribute("rx", "3");
        r.setAttribute("fill", fill);
        r.setAttribute("stroke", "#9aa8bc");
        const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
        t.setAttribute("x", String(x + 22));
        t.setAttribute("y", "20");
        t.setAttribute("class", "hierarchy-legend-label");
        t.textContent = name;
        legend.appendChild(r);
        legend.appendChild(t);
      });
      svg.appendChild(legend);

      const gWorld = document.createElementNS("http://www.w3.org/2000/svg", "g");
      gWorld.setAttribute("class", "hierarchy-world");

      // Compounds (bands / clusters)
      flat
        .filter((n) => n.isCompound)
        .forEach((n) => {
          const isBand = String(n.id).startsWith("band:");
          const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
          rect.setAttribute("x", String(n.x));
          rect.setAttribute("y", String(n.y));
          rect.setAttribute("width", String(n.width));
          rect.setAttribute("height", String(n.height));
          rect.setAttribute("rx", isBand ? "10" : "8");
          rect.setAttribute(
            "class",
            isBand
              ? `hierarchy-band hierarchy-band--${String(n.id).slice(5)}`
              : "hierarchy-cluster"
          );
          gWorld.appendChild(rect);
          const label = (n.labels && n.labels[0] && n.labels[0].text) || "";
          if (label) {
            const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
            t.setAttribute("x", String(n.x + 12));
            t.setAttribute("y", String(n.y + 18));
            t.setAttribute("class", "hierarchy-band-label");
            t.textContent = label;
            gWorld.appendChild(t);
          }
        });

      // Edges: snap to leaf boxes (ignore ELK compound-port polylines).
      const leafBoxes = new Map();
      flat
        .filter((n) => !n.isCompound)
        .forEach((n) => leafBoxes.set(n.id, n));
      (neigh.edges || []).forEach((edge) => {
        const srcBox = leafBoxes.get(String(edge.source));
        const tgtBox = leafBoxes.get(String(edge.target));
        if (!srcBox || !tgtBox) return;
        const conn = hierarchyConnectPath(srcBox, tgtBox);
        if (!conn) return;
        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        path.setAttribute("d", conn.d);
        path.setAttribute("class", "hierarchy-edge");
        path.setAttribute("fill", "none");
        gWorld.appendChild(path);
        const rel = edge.rel ? String(edge.rel) : "";
        if (rel) {
          const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
          t.setAttribute("x", String(conn.midX));
          t.setAttribute("y", String(conn.midY - 4));
          t.setAttribute("class", "hierarchy-edge-label");
          t.textContent = rel.length > 28 ? rel.slice(0, 27) + "…" : rel;
          gWorld.appendChild(t);
        }
      });

      // Leaf nodes
      flat
        .filter((n) => !n.isCompound)
        .forEach((n) => {
          const meta = byId.get(n.id) || {};
          const layer = String(meta.layer || "CDM").toUpperCase();
          const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
          g.setAttribute("class", "hierarchy-node");
          g.dataset.nodeId = n.id;
          if (selected.has(n.id)) g.classList.add("is-seed");
          const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
          rect.setAttribute("x", String(n.x));
          rect.setAttribute("y", String(n.y));
          rect.setAttribute("width", String(n.width));
          rect.setAttribute("height", String(n.height));
          rect.setAttribute("rx", "6");
          rect.setAttribute(
            "class",
            `hierarchy-node-rect hierarchy-node-rect--${
              layer === "OWL" || layer === "LDM" ? layer : "CDM"
            }`
          );
          const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
          t.setAttribute("x", String(n.x + n.width / 2));
          t.setAttribute("y", String(n.y + n.height / 2 + 4));
          t.setAttribute("text-anchor", "middle");
          t.setAttribute("class", "hierarchy-node-label");
          const label = meta.title || meta.name || n.id;
          t.textContent =
            label.length > 32 ? label.slice(0, 31) + "…" : label;
          g.appendChild(rect);
          g.appendChild(t);
          g.style.cursor = "pointer";
          g.addEventListener("click", (ev) => {
            ev.stopPropagation();
            if (onToggleSeed) onToggleSeed(n.id);
            else {
              if (selected.has(n.id)) selected.delete(n.id);
              else selected.add(n.id);
              paint();
            }
          });
          gWorld.appendChild(g);
        });

      svg.appendChild(gWorld);
      canvas.replaceChildren();
      canvas.appendChild(svg);
      svgEl = svg;

      // Simple pan/zoom
      let dragging = false;
      let lastX = 0;
      let lastY = 0;
      function applyTransform() {
        gWorld.setAttribute(
          "transform",
          `translate(${view.panX},${view.panY}) scale(${view.scale})`
        );
      }
      applyTransform();
      svg.addEventListener("wheel", (e) => {
        e.preventDefault();
        const factor = e.deltaY < 0 ? 1.08 : 0.92;
        view.scale = Math.min(2.5, Math.max(0.35, view.scale * factor));
        applyTransform();
      }, { passive: false });
      svg.addEventListener("pointerdown", (e) => {
        if (e.button !== 0) return;
        dragging = true;
        lastX = e.clientX;
        lastY = e.clientY;
        svg.classList.add("is-panning");
        svg.setPointerCapture(e.pointerId);
      });
      svg.addEventListener("pointermove", (e) => {
        if (!dragging) return;
        view.panX += e.clientX - lastX;
        view.panY += e.clientY - lastY;
        lastX = e.clientX;
        lastY = e.clientY;
        applyTransform();
      });
      svg.addEventListener("pointerup", () => {
        dragging = false;
        svg.classList.remove("is-panning");
      });
    }

    // Expose repaint for shared selection updates when tab already mounted.
    root._hierarchyRepaint = paint;
    paint();
    return root;
  }

  function renderHierarchyMermaidPane(mod, section, opts) {
    const selected =
      opts && opts.selected instanceof Set ? opts.selected : new Set();
    const hops = opts && opts.hops ? opts.hops : { OWL: 1, CDM: 1, LDM: 1 };

    const root = document.createElement("div");
    root.className = "hierarchy-mermaid-pane erd-source";

    const actions = document.createElement("div");
    actions.className = "erd-source-actions";
    const hint = document.createElement("span");
    hint.className = "muted";
    hint.style.marginRight = "auto";
    hint.textContent = "Вставьте код на mermaid.live";
    const copyBtn = document.createElement("button");
    copyBtn.type = "button";
    copyBtn.className = "copy-btn";
    copyBtn.textContent = "Копировать";
    actions.appendChild(hint);
    actions.appendChild(copyBtn);
    root.appendChild(actions);

    const pre = document.createElement("pre");
    pre.className = "erd-source-pre";
    const code = document.createElement("code");
    pre.appendChild(code);
    root.appendChild(pre);

    let currentText = "";

    function refresh() {
      if (!selected.size) {
        currentText = hierarchyNeighborhoodToMermaid([], []);
      } else {
        const neigh = collectHierarchyNeighborhood(
          section,
          [...selected],
          hops
        );
        currentText = hierarchyNeighborhoodToMermaid(
          neigh.nodes,
          neigh.edges
        );
      }
      code.textContent = currentText;
      copyBtn.disabled = !currentText.trim();
    }

    copyBtn.addEventListener("click", () => {
      if (!currentText) return;
      navigator.clipboard?.writeText(currentText).then(
        () => {
          copyBtn.textContent = "Скопировано";
          setTimeout(() => {
            copyBtn.textContent = "Копировать";
          }, 1200);
        },
        () => {}
      );
    });

    root._hierarchyMermaidRefresh = refresh;
    refresh();
    return root;
  }

  function renderGlossary(mod, section) {
    const root = document.createElement("div");
    root.className = "glossary-section-tabs";
    const n = (section.items || []).length;
    const scope = (section.attributes || {}).glossary_scope || "";

    if (scope === "hierarchy") {
      const sharedSelected = new Set();
      const hops = { OWL: 1, CDM: 1, LDM: 1 };
      let vizRoot = null;
      let mermaidRoot = null;
      function refreshHierarchyViews() {
        if (vizRoot && vizRoot._hierarchyRepaint) {
          vizRoot._hierarchyRepaint();
        }
        if (mermaidRoot && mermaidRoot._hierarchyMermaidRefresh) {
          mermaidRoot._hierarchyMermaidRefresh();
        }
      }
      mountTabs(
        root,
        [
          {
            id: "glossary-relations",
            label: "Связи",
            count: n,
            render(panel) {
              panel.appendChild(
                renderGlossaryRelations(mod, section, {
                  selected: sharedSelected,
                  onSelectionChange: refreshHierarchyViews,
                })
              );
            },
          },
          {
            id: "hierarchy-visualization",
            label: "Визуализация",
            render(panel) {
              vizRoot = renderHierarchyVisualization(mod, section, {
                selected: sharedSelected,
                hops,
                onNeighborhoodChange() {
                  if (mermaidRoot && mermaidRoot._hierarchyMermaidRefresh) {
                    mermaidRoot._hierarchyMermaidRefresh();
                  }
                },
                onToggleSeed(id) {
                  if (sharedSelected.has(id)) sharedSelected.delete(id);
                  else sharedSelected.add(id);
                  refreshHierarchyViews();
                },
              });
              panel.appendChild(vizRoot);
            },
          },
          {
            id: "hierarchy-mermaid",
            label: "Mermaid",
            render(panel) {
              mermaidRoot = renderHierarchyMermaidPane(mod, section, {
                selected: sharedSelected,
                hops,
              });
              panel.appendChild(mermaidRoot);
            },
          },
        ],
        { initial: "glossary-relations" }
      );
      return root;
    }

    mountTabs(
      root,
      [
        {
          id: "overview",
          label: "Overview",
          count: n,
          render(panel) {
            panel.appendChild(renderGlossaryOverview(mod, section));
          },
        },
        {
          id: "list",
          label: "Список",
          count: n,
          render(panel) {
            panel.appendChild(renderGlossaryListTable(mod, section));
          },
        },
        {
          id: "hierarchy",
          label: "Иерархия",
          render(panel) {
            panel.appendChild(renderGlossaryHierarchyTable(mod, section));
          },
        },
        {
          id: "glossary-relations",
          label: "Связи",
          render(panel) {
            panel.appendChild(renderGlossaryRelations(mod, section));
          },
        },
      ],
      { initial: "overview" }
    );
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
      setTreeToggle(toggle, { open, leaf: !hasKids });
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
          setTreeToggle(toggle, { open: !kids.hidden, leaf: false });
        });
      }
      label.addEventListener("click", () => {
        if (hasKids) {
          const currentlyOpen = !kids.hidden;
          if (item.id === selectedItemId && currentlyOpen) {
            kids.hidden = true;
            setTreeToggle(toggle, { open: false, leaf: false });
          } else if (!currentlyOpen) {
            kids.hidden = false;
            setTreeToggle(toggle, { open: true, leaf: false });
          }
        }
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

  const searchDialog = document.getElementById("search-dialog");
  const searchTrigger = document.getElementById("search-trigger");
  const statusRegion = document.getElementById("status-region");
  const sidebarEl = document.getElementById("sidebar");
  const sidebarBackdrop = document.getElementById("sidebar-backdrop");
  const overflowMenu = document.getElementById("overflow-menu");
  let searchHitButtons = [];
  let searchActiveIndex = -1;

  function announce(msg) {
    if (statusRegion) statusRegion.textContent = msg;
  }

  let searchFocusTrapHandler = null;

  function openSearchDialog() {
    if (!searchDialog) return;
    searchDialog.hidden = false;
    searchInput?.focus();
    searchInput?.select?.();
    runSearch(searchInput?.value || "");
    if (searchFocusTrapHandler) {
      searchDialog.removeEventListener("keydown", searchFocusTrapHandler);
    }
    searchFocusTrapHandler = (e) => {
      if (e.key !== "Tab") return;
      const panel = searchDialog.querySelector(".search-dialog-panel");
      const focusables = panel
        ? Array.from(
            panel.querySelectorAll(
              'input, button:not([disabled]), [href], [tabindex]:not([tabindex="-1"])'
            )
          ).filter((el) => !el.hidden && el.offsetParent !== null)
        : [];
      if (!focusables.length) return;
      const first = focusables[0];
      const last = focusables[focusables.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };
    searchDialog.addEventListener("keydown", searchFocusTrapHandler);
  }

  function closeSearchDialog() {
    if (!searchDialog) return;
    searchDialog.hidden = true;
    searchResults.classList.add("hidden");
    searchActiveIndex = -1;
    if (searchFocusTrapHandler) {
      searchDialog.removeEventListener("keydown", searchFocusTrapHandler);
      searchFocusTrapHandler = null;
    }
    searchTrigger?.focus();
  }

  function setSidebarOpen(open) {
    sidebarEl?.classList.toggle("is-open", open);
    if (sidebarBackdrop) {
      sidebarBackdrop.hidden = !open;
      sidebarBackdrop.classList.toggle("is-open", open);
    }
  }

  function runSearch(q) {
    const query = q.trim().toLowerCase();
    searchHitButtons = [];
    searchActiveIndex = -1;
    if (!query) {
      const starter = searchIndex.slice(0, 8);
      searchResults.innerHTML = "";
      const hint = document.createElement("div");
      hint.className = "muted";
      hint.style.padding = "10px 12px";
      hint.textContent =
        "Type to search classes, attributes, terms and files. Suggestions:";
      searchResults.appendChild(hint);
      starter.forEach((h) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "search-hit";
        btn.setAttribute("role", "option");
        btn.innerHTML = `${escapeHtml(h.title || h.item_id || h.node_id || "")}<div class="muted">${escapeHtml(
          h.kind === "catalog" ? h.node_id || "" : h.module_id || ""
        )}</div>`;
        btn.addEventListener("click", () => {
          closeSearchDialog();
          if (h.kind === "catalog" && h.node_id) {
            const node = catalogNode(h.node_id);
            if (node) navigateToNode(node);
            return;
          }
          if (h.module_id) {
            navigateToModule(h.module_id, {
              section: h.section_id,
              item: h.item_id,
            });
          }
        });
        searchResults.appendChild(btn);
        searchHitButtons.push(btn);
      });
      searchResults.classList.remove("hidden");
      announce("Search suggestions");
      return;
    }
    const hits = searchIndex
      .filter(
        (h) =>
          (h.title || "").toLowerCase().includes(query) ||
          (h.description || "").toLowerCase().includes(query) ||
          (h.item_id || "").toLowerCase().includes(query) ||
          (h.node_id || "").toLowerCase().includes(query)
      )
      .slice(0, 10);

    if (!hits.length) {
      searchResults.innerHTML = `<div class="search-hit muted">No results</div>`;
      searchResults.classList.remove("hidden");
      announce("No results");
      return;
    }

    const groups = { module: [], section: [], item: [], catalog: [] };
    hits.forEach((h) => groups[h.kind]?.push(h));
    searchResults.innerHTML = "";
    const labels = {
      catalog: "Publications",
      module: "Modules",
      section: "Sections",
      item: "Classes & terms",
    };
    ["catalog", "module", "section", "item"].forEach((kind) => {
      if (!groups[kind].length) return;
      const title = document.createElement("div");
      title.className = "muted";
      title.style.padding = "6px 12px";
      title.textContent = labels[kind] || kind;
      searchResults.appendChild(title);
      groups[kind].forEach((h) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "search-hit";
        btn.setAttribute("role", "option");
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
          closeSearchDialog();
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
        searchHitButtons.push(btn);
      });
    });
    searchResults.classList.remove("hidden");
    announce(`${hits.length} results`);
  }

  function moveSearchSelection(delta) {
    if (!searchHitButtons.length) return;
    searchActiveIndex = (searchActiveIndex + delta + searchHitButtons.length) % searchHitButtons.length;
    searchHitButtons.forEach((b, i) => {
      b.setAttribute("aria-selected", i === searchActiveIndex ? "true" : "false");
      if (i === searchActiveIndex) b.scrollIntoView({ block: "nearest" });
    });
  }

  searchInput?.addEventListener("input", () => runSearch(searchInput.value));
  searchInput?.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      moveSearchSelection(1);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      moveSearchSelection(-1);
    } else if (e.key === "Enter" && searchActiveIndex >= 0) {
      e.preventDefault();
      searchHitButtons[searchActiveIndex]?.click();
    } else if (e.key === "Escape") {
      e.preventDefault();
      closeSearchDialog();
    }
  });

  searchTrigger?.addEventListener("click", () => openSearchDialog());
  searchDialog?.addEventListener("click", (e) => {
    if (e.target === searchDialog) closeSearchDialog();
  });

  document.addEventListener("keydown", (e) => {
    const meta = e.metaKey || e.ctrlKey;
    if (meta && e.key.toLowerCase() === "k") {
      e.preventDefault();
      openSearchDialog();
      return;
    }
    if (e.key === "/" && !e.metaKey && !e.ctrlKey && !e.altKey) {
      const tag = (e.target && e.target.tagName) || "";
      if (tag === "INPUT" || tag === "TEXTAREA" || e.target?.isContentEditable) return;
      e.preventDefault();
      openSearchDialog();
      return;
    }
    if (e.key === "Escape") {
      if (settingsDialog && !settingsDialog.hidden) {
        closeSettingsDialog();
        return;
      }
      if (searchDialog && !searchDialog.hidden) closeSearchDialog();
      else setSidebarOpen(false);
      if (overflowMenu) overflowMenu.hidden = true;
    }
  });

  document.getElementById("btn-menu")?.addEventListener("click", () => {
    setSidebarOpen(!sidebarEl?.classList.contains("is-open"));
  });
  sidebarBackdrop?.addEventListener("click", () => setSidebarOpen(false));

  function applyDisplayPrefs({ rerender = true } = {}) {
    applyAppearancePrefs();
    if (!rerender) return;
    const route = parseHash();
    renderModuleNav({
      item: selectedItemId || route.item || null,
      section: route.section || null,
    });
    if (currentModuleId) {
      showModule(currentModuleId, {
        section: route.section || null,
        item: selectedItemId || route.item || null,
      });
    }
  }

  function choiceLabel(value) {
    return String(value || "")
      .replace(/-/g, " ")
      .replace(/\b\w/g, (c) => c.toUpperCase());
  }

  function renderSettingsFields() {
    const body = document.getElementById("settings-dialog-body");
    if (!body) return;
    body.innerHTML = "";
    const availableRoots = collectAllSectionRoots();
    const byGroup = new Map();
    displaySettings.forEach((s) => {
      const g = s.group || "Other";
      if (!byGroup.has(g)) byGroup.set(g, []);
      byGroup.get(g).push(s);
    });
    byGroup.forEach((settings, groupName) => {
      const section = document.createElement("section");
      section.className = "settings-group";
      const h = document.createElement("h3");
      h.className = "settings-group-title";
      h.textContent = groupName;
      section.appendChild(h);
      settings.forEach((meta) => {
        const field = document.createElement("div");
        field.className = "settings-field";
        const label = document.createElement("label");
        label.className = "settings-field-label";
        label.textContent = meta.label || meta.key;
        field.appendChild(label);
        if (meta.description) {
          const desc = document.createElement("div");
          desc.className = "settings-field-desc";
          desc.textContent = meta.description;
          field.appendChild(desc);
        }
        const key = meta.key;
        if (meta.type === "bool") {
          const row = document.createElement("label");
          row.style.display = "inline-flex";
          row.style.alignItems = "center";
          row.style.gap = "8px";
          const input = document.createElement("input");
          input.type = "checkbox";
          input.checked = !!getPref(key);
          input.addEventListener("change", () => {
            setPref(key, input.checked);
            applyDisplayPrefs();
          });
          row.appendChild(input);
          row.appendChild(document.createTextNode(input.checked ? "On" : "Off"));
          input.addEventListener("change", () => {
            row.lastChild.textContent = input.checked ? "On" : "Off";
          });
          field.appendChild(row);
        } else if (meta.type === "choice") {
          const select = document.createElement("select");
          (meta.options || []).forEach((opt) => {
            const o = document.createElement("option");
            o.value = opt;
            o.textContent = choiceLabel(opt);
            select.appendChild(o);
          });
          select.value = getPref(key);
          select.addEventListener("change", () => {
            setPref(key, select.value);
            applyDisplayPrefs();
          });
          field.appendChild(select);
        } else if (meta.type === "multi-from-data") {
          const box = document.createElement("div");
          box.className = "settings-multi";
          const selected = new Set(getPref(key) || []);
          if (!availableRoots.length) {
            const empty = document.createElement("div");
            empty.className = "settings-field-desc";
            empty.textContent = "No section roots in loaded publications.";
            box.appendChild(empty);
          }
          availableRoots.forEach((root) => {
            const row = document.createElement("label");
            const cb = document.createElement("input");
            cb.type = "checkbox";
            cb.checked = selected.has(root);
            cb.addEventListener("change", () => {
              const next = new Set(getPref(key) || []);
              if (cb.checked) next.add(root);
              else next.delete(root);
              setPref(key, [...next].sort());
              applyDisplayPrefs();
            });
            row.appendChild(cb);
            row.appendChild(document.createTextNode(root));
            box.appendChild(row);
          });
          field.appendChild(box);
        }
        section.appendChild(field);
      });
      body.appendChild(section);
    });
  }

  const settingsDialog = document.getElementById("settings-dialog");

  function openSettingsDialog() {
    if (!settingsDialog) return;
    renderSettingsFields();
    settingsDialog.hidden = false;
    document.getElementById("settings-close")?.focus();
  }

  function closeSettingsDialog() {
    if (!settingsDialog) return;
    settingsDialog.hidden = true;
  }

  document.getElementById("btn-theme")?.addEventListener("click", () => {
    const order = ["light", "dark", "system"];
    const cur = getPref("appearance.theme") || "light";
    const idx = order.indexOf(cur);
    const next = order[(idx + 1) % order.length];
    setPref("appearance.theme", next);
    applyDisplayPrefs({ rerender: false });
    announce(`Theme: ${next}`);
  });
  document.getElementById("btn-settings")?.addEventListener("click", () => {
    if (overflowMenu) overflowMenu.hidden = true;
    openSettingsDialog();
  });
  document.getElementById("settings-close")?.addEventListener("click", closeSettingsDialog);
  document.getElementById("settings-dialog-x")?.addEventListener("click", closeSettingsDialog);
  settingsDialog?.addEventListener("click", (e) => {
    if (e.target === settingsDialog) closeSettingsDialog();
  });
  document.getElementById("settings-reset")?.addEventListener("click", () => {
    resetPrefs();
    applyDisplayPrefs();
    renderSettingsFields();
    announce("Settings reset");
  });
  document.getElementById("settings-export")?.addEventListener("click", () => {
    const blob = new Blob([exportPrefsJson()], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "moex-viewer-prefs.json";
    a.click();
    URL.revokeObjectURL(url);
    announce("Settings exported");
  });
  document.getElementById("settings-import")?.addEventListener("click", () => {
    document.getElementById("settings-import-file")?.click();
  });
  document.getElementById("settings-import-file")?.addEventListener("change", (e) => {
    const file = e.target?.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        importPrefsJson(String(reader.result || ""));
        applyDisplayPrefs();
        renderSettingsFields();
        announce("Settings imported");
      } catch {
        announce("Import failed");
      }
    };
    reader.readAsText(file);
    e.target.value = "";
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
  document.getElementById("btn-collapse")?.addEventListener("click", () => {
    openGroups.clear();
    renderModuleNav({ item: selectedItemId });
    content.querySelectorAll(".section").forEach((s) => s.classList.add("collapsed"));
    if (overflowMenu) overflowMenu.hidden = true;
  });
  document.getElementById("btn-copy-link")?.addEventListener("click", () => {
    navigator.clipboard?.writeText(location.href).then(
      () => announce("Link copied"),
      () => announce("Copy failed")
    );
    if (overflowMenu) overflowMenu.hidden = true;
  });
  document.getElementById("btn-overflow")?.addEventListener("click", (e) => {
    e.stopPropagation();
    if (!overflowMenu) return;
    const open = overflowMenu.hidden;
    overflowMenu.hidden = !open;
    document.getElementById("btn-overflow")?.setAttribute("aria-expanded", open ? "true" : "false");
  });
  document.addEventListener("click", (e) => {
    if (overflowMenu && !overflowMenu.hidden && !overflowMenu.contains(e.target) && e.target !== document.getElementById("btn-overflow")) {
      overflowMenu.hidden = true;
    }
  });

  const treeFilter = document.getElementById("tree-filter");
  treeFilter?.addEventListener("input", () => {
    const q = treeFilter.value.trim().toLowerCase();
    moduleNav.querySelectorAll(".nav-item-btn, .nav-group-btn, .module-btn, .nav-section-btn").forEach((btn) => {
      const text = (btn.textContent || "").toLowerCase();
      const row = btn.closest(".nav-tree-row") || btn;
      if (!q || text.includes(q)) {
        row.style.display = "";
        btn.style.display = "";
      } else {
        if (btn.classList.contains("nav-item-btn")) row.style.display = "none";
        else btn.style.display = "none";
      }
    });
  });

  const resizeHandle = document.getElementById("sidebar-resize");
  resizeHandle?.addEventListener("pointerdown", (e) => {
    e.preventDefault();
    const startX = e.clientX;
    const startW = sidebarEl.getBoundingClientRect().width;
    function onMove(ev) {
      const rootStyles = getComputedStyle(document.documentElement);
      const minW = parseFloat(rootStyles.getPropertyValue("--sidebar-min")) || 300;
      const maxW = parseFloat(rootStyles.getPropertyValue("--sidebar-max")) || 520;
      const next = Math.min(maxW, Math.max(minW, startW + (ev.clientX - startX)));
      document.documentElement.style.setProperty("--sidebar-w", `${next}px`);
    }
    function onUp() {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
    }
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp);
  });

  // Prefs already loaded + appearance applied at startup (prefs store).

  const shortcutKbd = document.getElementById("search-shortcut-kbd");
  if (shortcutKbd) shortcutKbd.textContent = `${shortcutModKey()}+K`;

  function applyRoute() {
    const { node, module, section, item } = parseHash();
    // Hash/deep-link restore: expand focus folder once (not on every re-render).
    if (item) openGroups.add(item);
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
      const mod = firstSpec.module_id
        ? modules.find((m) => m.module_id === firstSpec.module_id)
        : null;
      const expl = explorerSection(mod);
      const hasImpls =
        expl &&
        (expl.items || []).some((i) => i.id === "group:implementations");
      if (hasImpls) {
        navigateToNode(firstSpec, {
          section: expl.id,
          item: "group:implementations",
        });
      } else {
        navigateToNode(firstSpec);
      }
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

  /** Serve-mode edit layer: replace in-memory modules and re-render current route. */
  window.__moexReplacePublicationData = function replacePublicationData(next) {
    if (next && Array.isArray(next.modules)) {
      modules = next.modules;
    }
    if (next && Array.isArray(next.search_index)) {
      searchIndex = next.search_index;
    }
    const dataEl = document.getElementById("publication-data");
    if (dataEl && next && next.modules) {
      dataEl.textContent = JSON.stringify(next.modules);
    }
    const searchEl = document.getElementById("search-index");
    if (searchEl && next && next.search_index) {
      searchEl.textContent = JSON.stringify(next.search_index);
    }
    applyRoute();
  };

  window.__moexGetModules = function getModules() {
    return modules;
  };
})();
