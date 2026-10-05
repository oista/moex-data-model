import json, urllib.request
html = urllib.request.urlopen("http://127.0.0.1:8877/", timeout=60).read().decode("utf-8", errors="replace")
assert "collectGlossaryAlignmentNeighbours" in html
assert "relationship:memberOf" in html or "relationship:" in html
start = html.find('id="publication-data"')
start = html.find(">", start) + 1
end = html.find("</script>", start)
mods = json.loads(html[start:end])
dams = next(m for m in mods if m.get("module_id") == "moex:module:dams")
gloss = next(s for s in dams["sections"] if s.get("id") == "implementations-glossary")
legal = next(i for i in gloss["items"] if i["id"].endswith(":dams:concept/LegalEntity") and i["id"].startswith("moex-enterprise"))
see = legal.get("attributes", {}).get("see_also") or []
rels = [(e.get("id"), e.get("rel")) for e in see if str(e.get("rel","")).startswith("relationship:")]
ext = legal.get("attributes", {}).get("external_class_refs") or []
print("legal", legal["id"])
print("relationship edges", rels[:8], "count", len(rels))
print("external_class_refs", len(ext), ext[:1])
assert any(r[1] == "relationship:memberOf" for r in rels)
assert any("CorporateGroup" in (r[0] or "") for r in rels)
assert ext
print("OK")
