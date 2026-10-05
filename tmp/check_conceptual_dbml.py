import json
import re
from pathlib import Path

html = Path("apps/viewer/dist/index.html").read_text(encoding="utf-8")
m = re.search(
    r'<script id="publication-data" type="application/json">(.*?)</script>',
    html,
    re.S,
)
data = json.loads(m.group(1))
mod = next(x for x in data if x.get("module_id") == "moex:module:enterprise-conceptual")
sec = next(s for s in mod["sections"] if s.get("id") == "conceptual-erd")
attrs = sec.get("attributes") or {}
src = attrs.get("dbml_source") or ""
print("dbml_missing", attrs.get("dbml_missing"))
print("dbml_len", len(src))
print("has Organization", "Table Organization" in src)
print("has conceptual projection", "conceptual projection" in src)
