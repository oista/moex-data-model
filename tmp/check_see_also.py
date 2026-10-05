import re, json, urllib.request
html = urllib.request.urlopen("http://127.0.0.1:8877/", timeout=30).read().decode("utf-8", errors="replace")
print("html_len", len(html))
patterns = [
    r"const modules\s*=\s*(\[.*?\]);\s*\n",
    r"window\.__MODULES__\s*=\s*(\[.*?\]);",
    r'id="modules-data"[^>]*>(\[.*?\])</script>',
]
m = None
for pat in patterns:
    m = re.search(pat, html, re.S)
    if m:
        print("matched", pat[:40])
        break
if not m:
    # find nearby markers
    for needle in ["modules =", "__MODULES__", "module_id", "see_also"]:
        print(needle, html.find(needle))
    raise SystemExit(0)
mods = json.loads(m.group(1))
dams = next((x for x in mods if "dams" in x.get("module_id", "")), None)
print("dams", dams and dams.get("module_id"))
gloss = next((s for s in (dams or {}).get("sections") or [] if s.get("id") == "glossary"), None)
items = (gloss or {}).get("items") or []
print("items", len(items))
nonempty = 0
samples = []
for it in items:
    sa = (it.get("attributes") or {}).get("see_also") or []
    if sa:
        nonempty += 1
        if len(samples) < 5:
            samples.append((it.get("id"), it.get("title"), sa[:4], len(sa)))
print("nonempty", nonempty)
for s in samples:
    print(s)
tax = sum(1 for it in items if (it.get("attributes") or {}).get("taxonomy_parents"))
print("with taxonomy_parents", tax)
