import json, urllib.request
html = urllib.request.urlopen("http://127.0.0.1:8877/", timeout=30).read().decode("utf-8", errors="replace")
start = html.find('id="publication-data"')
start = html.find(">", start) + 1
end = html.find("</script>", start)
mods = json.loads(html[start:end])
dams = next(x for x in mods if "dams" in x.get("module_id", ""))
gloss = next(s for s in dams["sections"] if s.get("id") == "glossary")
items = gloss["items"]
empty = [i["title"] for i in items if not (i.get("attributes") or {}).get("see_also")]
print("empty see_also", empty)
# terms with lots of taxonomy children but check see_also
for title in ["ModelElement", "GlossaryTerm", "LogicalEntity", "ConceptualEntity"]:
    it = next((i for i in items if i["title"]==title), None)
    if not it: continue
    a = it.get("attributes") or {}
    print(title, "see_also", len(a.get("see_also") or []), "tax_children", len(a.get("taxonomy_children") or []), "tax_parents", len(a.get("taxonomy_parents") or []))
# fibo
fibo = next((x for x in mods if "fibo" in x.get("module_id","") and "application" not in x.get("module_id","")), None)
if fibo:
    g = next((s for s in fibo["sections"] if s.get("id")=="glossary" or s.get("kind")=="glossary"), None)
    its = (g or {}).get("items") or []
    nonempty = sum(1 for i in its if (i.get("attributes") or {}).get("see_also"))
    print("fibo module", fibo["module_id"], "items", len(its), "nonempty see_also", nonempty)
