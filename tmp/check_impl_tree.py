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
top_ids = [c.get("id") for c in impls.get("children") or []]
print("Реализации children:")
for i, t in zip(
    top_ids, [c.get("title") for c in impls.get("children") or []]
):
    print(f"  - {i}: {t}")
assert top_ids[:2] == [
    "group:implementations-it-solutions",
    "group:implementations-projects",
]
assert "moex-dsp" in top_ids
assert "moex-enterprise-conceptual-model" in top_ids
it_folder = find(impls.get("children") or [], "group:implementations-it-solutions")
it_ids = {c.get("id") for c in it_folder.get("children") or []}
for need in ("mdm-solution", "ucd-solution", "crm-solution", "esed-solution"):
    assert need in it_ids, f"missing {need} under ИТ-решения"
print("OK: folders + four solutions under ИТ-решения")
