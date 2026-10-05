from __future__ import annotations

import json
import re
from pathlib import Path

html = Path("apps/viewer/dist/index.html").read_text(encoding="utf-8")
m = re.search(
    r'<script id="publication-data" type="application/json">(.*?)</script>',
    html,
    re.S,
)
print("publication-data found", bool(m))
if not m:
    raise SystemExit(1)
raw = m.group(1)
print("json len", len(raw))
try:
    modules = json.loads(raw)
except json.JSONDecodeError as exc:
    print("JSON ERROR", exc)
    # show context around error
    pos = getattr(exc, "pos", None)
    if pos is not None:
        print(raw[max(0, pos - 80) : pos + 80])
    raise SystemExit(2)

crm = next(x for x in modules if "crm" in x["module_id"])
print("crm title", crm["title"])
for s in crm["sections"]:
    if s.get("type") == "mermaid-diagram":
        attrs = s.get("attributes") or {}
        scene = attrs.get("erd_scene")
        print(
            s["id"],
            "has_scene",
            bool(scene),
            "nodes",
            len((scene or {}).get("nodes") or []),
            "has_layout",
            bool(attrs.get("erd_layout")),
            "content_len",
            len(s.get("content") or ""),
        )

# Check if viewer.js inline is present and contains renderErdScene
inline = re.search(r'<script id="viewer-js">(.*?)</script>', html, re.S)
print("inline js", bool(inline), "len", len(inline.group(1)) if inline else 0)
if inline:
    print("renderErdScene in inline", "function renderErdScene" in inline.group(1))
