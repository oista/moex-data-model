import json
import re
import urllib.request

html = urllib.request.urlopen("http://127.0.0.1:8877/", timeout=60).read().decode(
    "utf-8", "replace"
)
m = re.search(r'id="publication-data"[^>]*>(.*?)</script>', html, re.S)
assert m, "publication-data not found"
mods = json.loads(m.group(1))
for mod in mods:
    blob = json.dumps(mod, ensure_ascii=False)
    if not any(k in blob for k in ("/mdm/", "/crm/", "/esed/")):
        continue
    title = mod.get("title") or mod.get("name") or mod.get("id")
    for sec in mod.get("sections") or []:
        attrs = sec.get("attributes") or {}
        layout = attrs.get("erd_layout")
        if not layout:
            continue
        nodes = layout.get("nodes") or {}
        sample = {
            k.split("/")[-1]: {"x": v.get("x"), "y": v.get("y")}
            for k, v in nodes.items()
        }
        print("MODULE", title)
        print(" section", sec.get("id"), sec.get("title"))
        print(" nodes", json.dumps(sample, ensure_ascii=False))
        print("---")
