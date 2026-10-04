import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
html = Path("apps/viewer/dist/index.html").read_text(encoding="utf-8")
match = re.search(
    r'<script id="publication-data" type="application/json">(.*?)</script>',
    html,
    re.S,
)
data = json.loads(match.group(1))
dams = next(m for m in data if m.get("module_id") == "moex:module:dams")
explorer = next(s for s in dams["sections"] if s.get("type") == "explorer")


def find(items, item_id):
    for it in items or []:
        if it.get("id") == item_id:
            return it
        hit = find(it.get("children") or [], item_id)
        if hit:
            return hit
    return None


impls = find(explorer.get("items") or [], "group:implementations")
assert impls, "group:implementations missing"
titles = [c.get("title") for c in impls.get("children") or []]
ids = [c.get("id") for c in impls.get("children") or []]
print("Реализации children:")
for i, t in zip(ids, titles):
    print(f"  - {i}: {t}")
for need in ("mdm-solution", "ucd-solution", "crm-solution", "esed-solution"):
    assert need in ids, f"missing {need}"
print("OK: four solutions under Реализации")
