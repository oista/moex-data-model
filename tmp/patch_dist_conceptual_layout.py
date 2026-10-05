"""Inject conceptual.layout.json into dist/index.html publication-data."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "apps/viewer/dist/index.html"
LAYOUT = (
    ROOT
    / "model-assets/implementations/enterprise/moex-enterprise-conceptual-model"
    / "0.1/publications/conceptual.layout.json"
)
from moex_publication_viewer.edits import value_hash

html = HTML.read_text(encoding="utf-8")
start = html.index('<script id="publication-data" type="application/json">')
start = html.index(">", start) + 1
end = html.index("</script>", start)
payload = json.loads(html[start:end])
layout = json.loads(LAYOUT.read_text(encoding="utf-8"))
path = (
    "model-assets/implementations/enterprise/moex-enterprise-conceptual-model/"
    "0.1/publications/conceptual.layout.json"
)

hit = 0
for mod in payload:
    if mod.get("module_id") != "moex:module:enterprise-conceptual":
        continue
    for sec in mod.get("sections") or []:
        if sec.get("id") != "conceptual-erd":
            continue
        attrs = sec.setdefault("attributes", {})
        attrs["erd_layout"] = layout
        attrs["erd_layout_path"] = path
        attrs["erd_layout_hash"] = value_hash(layout)
        hit += 1

if hit != 1:
    raise SystemExit(f"expected 1 section patch, got {hit}")

new_html = html[:start] + json.dumps(payload, ensure_ascii=False) + html[end:]
HTML.write_text(new_html, encoding="utf-8")
print("patched", HTML, "nodes", len(layout["nodes"]))
print("LegalEntity", layout["nodes"]["dams:concept/LegalEntity"])
print("Trade", layout["nodes"]["dams:concept/Trade"])
