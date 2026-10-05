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
assert match, "publication-data script not found"
data = json.loads(match.group(1))
wanted = ("mdm", "ucd", "crm", "esed")
found = []
for mod in data:
    mid = str(mod.get("module_id") or "")
    if any(w in mid for w in wanted):
        found.append(mid)
        print(
            mid,
            "|",
            mod.get("title"),
            "|",
            mod.get("dams_model_level"),
            "|",
            mod.get("implementation_profile"),
        )
assert "moex:module:mdm-solution" in found
assert "moex:module:ucd-solution" in found
assert "moex:module:crm-solution" in found
assert "moex:module:esed-solution" in found
print("OK: four solution modules present")
