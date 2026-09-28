/**
 * MOEX drawDB postMessage bridge (ADR-005).
 * Injected into drawDB build and used by static-bridge/index.html.
 */
(function () {
  "use strict";

  var pendingDbml = "";
  var panel;

  function allowedOrigin(origin) {
    // Dev Workbench + same-host compose. Tighten in production deploy.
    if (!origin || origin === "null") return true;
    try {
      var u = new URL(origin);
      return (
        u.hostname === "localhost" ||
        u.hostname === "127.0.0.1" ||
        u.hostname === window.location.hostname
      );
    } catch (e) {
      return false;
    }
  }

  function ensurePanel() {
    if (panel) return panel;
    panel = document.createElement("div");
    panel.id = "moex-drawdb-bridge";
    panel.style.cssText =
      "position:fixed;z-index:99999;right:8px;bottom:8px;width:360px;" +
      "max-height:40vh;background:#1e1e1e;color:#eee;border:1px solid #555;" +
      "border-radius:6px;padding:8px;font:12px/1.4 system-ui,sans-serif;" +
      "display:flex;flex-direction:column;gap:6px;box-shadow:0 4px 16px #0008";
    panel.innerHTML =
      "<strong>MOEX DBML bridge</strong>" +
      "<textarea id='moex-dbml-text' style='width:100%;height:120px;font:11px monospace'></textarea>" +
      "<div style='display:flex;gap:6px'>" +
      "<button type='button' id='moex-copy'>Copy</button>" +
      "<button type='button' id='moex-send'>Export to Workbench</button>" +
      "</div>" +
      "<span id='moex-status' style='opacity:.8'>waiting…</span>";
    document.body.appendChild(panel);
    panel.querySelector("#moex-copy").onclick = function () {
      var ta = panel.querySelector("#moex-dbml-text");
      ta.select();
      document.execCommand("copy");
      setStatus("copied to clipboard — use File → Import DBML in drawDB if needed");
    };
    panel.querySelector("#moex-send").onclick = function () {
      var ta = panel.querySelector("#moex-dbml-text");
      exportToParent(ta.value);
    };
    return panel;
  }

  function setStatus(msg) {
    ensurePanel();
    panel.querySelector("#moex-status").textContent = msg;
  }

  function setDbml(text) {
    ensurePanel();
    pendingDbml = text || "";
    panel.querySelector("#moex-dbml-text").value = pendingDbml;
    setStatus("imported " + pendingDbml.length + " chars");
  }

  function exportToParent(dbml) {
    if (!window.parent || window.parent === window) {
      setStatus("no parent frame");
      return;
    }
    window.parent.postMessage(
      { type: "moex:export-dbml", dbml: dbml || "" },
      "*"
    );
    setStatus("exported to Workbench");
  }

  window.addEventListener("message", function (event) {
    if (!allowedOrigin(event.origin)) return;
    var data = event.data;
    if (!data || typeof data !== "object") return;
    if (data.type === "moex:import-dbml") {
      setDbml(data.dbml || "");
    } else if (data.type === "moex:request-export") {
      var ta = ensurePanel().querySelector("#moex-dbml-text");
      exportToParent(ta.value);
    }
  });

  function announceReady() {
    ensurePanel();
    if (window.parent && window.parent !== window) {
      window.parent.postMessage({ type: "moex:ready" }, "*");
    }
    setStatus("ready");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", announceReady);
  } else {
    announceReady();
  }

  window.__MOEX_DRAWDB_BRIDGE__ = {
    setDbml: setDbml,
    exportToParent: exportToParent,
  };
})();
