(() => {
  /** Inline edit layer — active only when /api/capabilities responds. */
  let editToken = null;
  let layoutEdit = false;
  let enhancing = false;

  window.__moexGetEditToken = () => editToken;
  window.__moexCanEditLayout = () => !!(editToken && layoutEdit);

  function findItem(moduleId, sectionId, itemId) {
    const mods = typeof window.__moexGetModules === "function"
      ? window.__moexGetModules()
      : null;
    if (!mods) return null;
    const mod = mods.find((m) => m.module_id === moduleId);
    if (!mod) return null;
    const sec = (mod.sections || []).find((s) => s.id === sectionId);
    if (!sec) return null;

    function walk(nodes) {
      for (const n of nodes || []) {
        if (n.id === itemId) return n;
        const hit = walk(n.children);
        if (hit) return hit;
      }
      return null;
    }
    return walk(sec.items);
  }

  function fieldValue(item, field) {
    if (field === "description") return item.description || "";
    if (field === "title") return item.title || "";
    if (field === "aliases") {
      const a = item.attributes?.aliases;
      if (Array.isArray(a)) return a.join("\n");
      if (typeof a === "string") return a;
      return "";
    }
    return "";
  }

  function makeHint(text) {
    const span = document.createElement("span");
    span.className = "edit-hint muted";
    span.textContent = text;
    return span;
  }

  function startEdit(card, field, target, currentValue) {
    const existing = card.querySelector(`.edit-panel[data-field="${field}"]`);
    if (existing) {
      existing.remove();
      return;
    }
    const panel = document.createElement("div");
    panel.className = "edit-panel";
    panel.setAttribute("data-field", field);

    const input =
      field === "aliases" || field === "description"
        ? document.createElement("textarea")
        : document.createElement("input");
    input.className = "edit-field";
    if (input.tagName === "TEXTAREA") {
      input.rows = field === "aliases" ? 4 : 5;
    } else {
      input.type = "text";
    }
    input.value = currentValue;

    const err = document.createElement("p");
    err.className = "edit-error";
    err.hidden = true;

    const actions = document.createElement("div");
    actions.className = "edit-actions";
    const save = document.createElement("button");
    save.type = "button";
    save.className = "edit-btn edit-btn-primary";
    save.textContent = "Сохранить";
    const cancel = document.createElement("button");
    cancel.type = "button";
    cancel.className = "edit-btn";
    cancel.textContent = "Отмена";
    actions.appendChild(save);
    actions.appendChild(cancel);

    panel.appendChild(input);
    panel.appendChild(err);
    panel.appendChild(actions);

    const anchor =
      card.querySelector(`[data-edit-anchor="${field}"]`) ||
      card.querySelector(".detail-desc") ||
      card.querySelector(".detail-head") ||
      card;
    anchor.insertAdjacentElement("afterend", panel);
    input.focus();

    cancel.addEventListener("click", () => panel.remove());
    save.addEventListener("click", async () => {
      save.disabled = true;
      err.hidden = true;
      let newValue = input.value;
      if (field === "aliases") {
        newValue = input.value
          .split(/\r?\n/)
          .map((s) => s.trim())
          .filter(Boolean);
      }
      try {
        const resp = await fetch("/api/edit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            token: editToken,
            edit_target: target,
            new_value: newValue,
          }),
        });
        const data = await resp.json().catch(() => ({}));
        if (!resp.ok || !data.ok) {
          err.textContent = data.error || `Ошибка ${resp.status}`;
          err.hidden = false;
          save.disabled = false;
          return;
        }
        if (typeof window.__moexReplacePublicationData === "function") {
          window.__moexReplacePublicationData({
            modules: data.modules,
            search_index: data.search_index,
          });
        } else {
          location.reload();
        }
      } catch (e) {
        err.textContent = String(e.message || e);
        err.hidden = false;
        save.disabled = false;
      }
    });
  }

  function enhanceCard(card) {
    if (!editToken || card.dataset.editEnhanced === "1") return;
    const moduleId = card.getAttribute("data-module-id");
    const sectionId = card.getAttribute("data-section-id");
    const itemId = card.getAttribute("data-item-id");
    if (!moduleId || !sectionId || !itemId) return;

    const item = findItem(moduleId, sectionId, itemId);
    if (!item) return;
    card.dataset.editEnhanced = "1";

    const targets = item.edit_targets || {};
    const fields = ["description", "title", "aliases"];

    // Definition / description block
    const defBlock =
      card.querySelector('[data-renderer="definition"]') ||
      card.querySelector(".detail-desc")?.parentElement;
    const descP = card.querySelector(".detail-desc");
    if (descP) {
      descP.setAttribute("data-edit-anchor", "description");
      const wrap = document.createElement("div");
      wrap.className = "edit-toolbar";
      if (targets.description) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "edit-btn";
        btn.textContent = "Править";
        btn.addEventListener("click", () =>
          startEdit(card, "description", targets.description, fieldValue(item, "description"))
        );
        wrap.appendChild(btn);
      } else {
        wrap.appendChild(
          makeHint("поле вычисляется / нет в источнике")
        );
      }
      if (defBlock && defBlock.querySelector("h2")) {
        defBlock.querySelector("h2").appendChild(wrap);
      } else {
        descP.insertAdjacentElement("beforebegin", wrap);
      }
    }

    // Title in Identity dl
    const titleDt = Array.from(card.querySelectorAll("dt")).find(
      (dt) => (dt.textContent || "").trim() === "title"
    );
    if (titleDt) {
      titleDt.setAttribute("data-edit-anchor", "title");
      const wrap = document.createElement("span");
      wrap.className = "edit-toolbar inline";
      if (targets.title) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "edit-btn";
        btn.textContent = "Править";
        btn.addEventListener("click", () =>
          startEdit(card, "title", targets.title, fieldValue(item, "title"))
        );
        wrap.appendChild(btn);
      }
      titleDt.appendChild(wrap);
    }

    // Aliases row if present or target exists
    if (targets.aliases) {
      const head = card.querySelector(".detail-head");
      const wrap = document.createElement("div");
      wrap.className = "edit-toolbar";
      wrap.setAttribute("data-edit-anchor", "aliases");
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "edit-btn";
      btn.textContent = "Править aliases";
      btn.addEventListener("click", () =>
        startEdit(card, "aliases", targets.aliases, fieldValue(item, "aliases"))
      );
      wrap.appendChild(btn);
      if (head) head.appendChild(wrap);
      else card.appendChild(wrap);
    }
  }

  function scan() {
    if (!editToken || enhancing) return;
    enhancing = true;
    try {
      document
        .querySelectorAll("[data-publication-item]:not([data-edit-enhanced='1'])")
        .forEach((card) => enhanceCard(card));
    } finally {
      enhancing = false;
    }
  }

  function announce(msg) {
    const el = document.getElementById("status-region");
    if (el) el.textContent = msg;
    try {
      console.info("[moex-edit]", msg);
    } catch (_) {
      /* ignore */
    }
  }

  async function init() {
    if (location.protocol === "file:") {
      announce("Edit mode: off (file://). Use moex-viewer serve.");
      return;
    }
    try {
      const resp = await fetch("/api/capabilities");
      const ctype = (resp.headers.get("content-type") || "").toLowerCase();
      if (!resp.ok || !ctype.includes("application/json")) {
        announce(
          "Edit mode: off — /api/capabilities not available (wrong server on this port?). " +
            "Run: python -m moex_publication_viewer.cli serve --root . --port 8877"
        );
        return;
      }
      const data = await resp.json();
      if (!data.edit || !data.token) {
        announce("Edit mode: off — capabilities missing token.");
        return;
      }
      editToken = data.token;
      layoutEdit = !!data.layout_edit;
      announce("Edit mode: on — open an entity/class card to see «Править».");
    } catch (e) {
      announce("Edit mode: off — " + (e && e.message ? e.message : String(e)));
      return;
    }
    const content = document.getElementById("content");
    if (!content) return;
    const obs = new MutationObserver(() => scan());
    obs.observe(content, { childList: true, subtree: true });
    scan();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
