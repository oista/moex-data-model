import json
import re
import urllib.request

html = urllib.request.urlopen("http://127.0.0.1:8877/", timeout=60).read().decode(
    "utf-8", "replace"
)
m = re.search(r'id="publication-data"[^>]*>(.*?)</script>', html, re.S)
mods = json.loads(m.group(1))
for mod in mods:
    blob = json.dumps(mod, ensure_ascii=False)
    if not any(k in blob for k in ("/mdm/", "/crm/", "/esed/")):
        continue
    keys = sorted(mod.keys())
    print("keys", keys[:20])
    print(
        "id=",
        mod.get("id"),
        "module_id=",
        mod.get("module_id"),
        "slug=",
        mod.get("slug"),
        "title=",
        mod.get("title"),
        "name=",
        mod.get("name"),
    )
    # print first section ids
    secs = [
        (s.get("id"), s.get("title"))
        for s in (mod.get("sections") or [])
        if "erd" in str(s.get("id", "")).lower()
        or "erd" in str(s.get("title", "")).lower()
    ]
    print("erd sections", secs)
    print("---")
