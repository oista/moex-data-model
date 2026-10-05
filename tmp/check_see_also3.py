import json, urllib.request
html = urllib.request.urlopen("http://127.0.0.1:8877/", timeout=30).read().decode("utf-8", errors="replace")
start = html.find('id="publication-data"')
start = html.find(">", start) + 1
end = html.find("</script>", start)
raw = html[start:end]
mods = json.loads(raw)
dams = next(x for x in mods if "dams" in x.get("module_id", ""))
gloss = next(s for s in dams["sections"] if s.get("id") == "glossary")
items = gloss["items"]
print("items", len(items))
print("sample ids", [i["id"] for i in items[:5]])
# ApprovalStatusEnum
ap = next(i for i in items if "Approval" in (i.get("title") or i.get("id") or ""))
print("Approval id", ap["id"])
print("Approval see_also", (ap.get("attributes") or {}).get("see_also"))
# resolve simulation
def canon(i):
    return i[len("glossary:"):] if str(i).startswith("glossary:") else str(i)
def resolve(raw):
    key = str(raw).strip(); cid = canon(key)
    return next((i for i in items if i["id"]==key or canon(i["id"])==cid or (i.get("attributes") or {}).get("name")==key), None)
sa = (ap.get("attributes") or {}).get("see_also") or []
print("resolvable", [(relTarget:=(e.get("id") if isinstance(e,dict) else e), bool(resolve(relTarget)), resolve(relTarget) and resolve(relTarget)["id"]) for e in sa[:8]])
# stats
nonempty=sum(1 for i in items if (i.get("attributes") or {}).get("see_also"))
total_links=sum(len((i.get("attributes") or {}).get("see_also") or []) for i in items)
unresolved=0
for i in items:
  for e in (i.get("attributes") or {}).get("see_also") or []:
    tid=e.get("id") if isinstance(e,dict) else e
    if not resolve(tid): unresolved+=1
print("nonempty items", nonempty, "total links", total_links, "unresolved", unresolved)
# simulate: pick 10 random with see_also, none selected among targets
from random import sample
pool=[i for i in items if (i.get("attributes") or {}).get("see_also")]
sel=sample(pool, min(5,len(pool)))
selected=set(i["id"] for i in sel)
selectedKeys=set(selected)|set(canon(x) for x in selected)
out=set()
for from_item in sel:
  for e in (from_item.get("attributes") or {}).get("see_also") or []:
    tid=e.get("id") if isinstance(e,dict) else e
    t=resolve(tid)
    if not t: continue
    if t["id"] in selectedKeys or canon(t["id"]) in selectedKeys: continue
    out.add(t["id"])
print("selected", [i["title"] for i in sel])
print("neighbours outside selection", len(out), list(out)[:10])
