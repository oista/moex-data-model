import json
import re
from collections import defaultdict

path = r"c:\Users\bons1\IdeaProjects\moex-data-model\tmp\cmodel_content04_inventory.json"
d = json.load(open(path, encoding="utf-8"))

drawio = r"f:\!PASSPORT\!H_DATASC\!Data Architecture\MOEX_DataModel\MOEX Data Model Standart\enterpise_cdm_src\CModel_content04.drawio"
raw = open(drawio, encoding="utf-8").read()
print("=== RAW SCAN ===")
for label, pat in [
    ("swimlane", r"swimlane"),
    ("uml", r"shape=uml"),
    ("note", r"shape=note"),
    ("legend", r"legend"),
    ("text boxes (html=1, not table)", r'vertex="1"[^>]*html=1'),
]:
    print(f"{label}: {len(re.findall(pat, raw, re.I))}")
fills = sorted(set(re.findall(r"fillColor=([^;\"]+)", raw)))
print("all fillColor values:", fills)

print("\n=== ENTITIES BY DOMAIN COLOR ===")
for color, names in d["fill_color_domains"].items():
    domain = "TRADING/MARKET (#60a917 green)" if color == "#60a917" else "ENTERPRISE/ERP (#0050ef blue)"
    print(f"\n{color} — {domain} ({len(names)} entities)")
    for n in names:
        print(f"  - {n}")

print("\n=== EDGES (draw.io connectors) ===")
for e in d["edges"]:
    src = e.get("source_entity") or e.get("source_label") or e["source_id"]
    tgt = e.get("target_entity") or e.get("target_label") or e["target_id"]
    lab = e.get("label") or ""
    card = e.get("cardinality_hint") or ""
    extra = f" label={lab!r}" if lab else ""
    if card:
        extra += f" cardinality={card!r}"
    print(f"  {src} -> {tgt}{extra}")

print("\n=== INFERRED FK (from attribute markers) ===")
by_from = defaultdict(list)
for r in d["inferred_fk_relationships"]:
    by_from[r["from_entity"]].append(r)
for fr in sorted(by_from):
    for r in by_from[fr]:
        print(f"  {fr}.{r['via_attribute']} -> {r.get('to_entity_guess') or '?'}")

print("\n=== FULL ENTITY ATTRIBUTE INVENTORY ===")
for e in sorted(d["entities"], key=lambda x: (x["fillColor"], x["name"])):
    attrs = e["attributes"]
    parts = []
    for a in attrs:
        k = a.get("key") or ""
        tag = f"[{k}] " if k else ""
        parts.append(f"{tag}{a['name']}")
    print(f"\n{e['name']} ({e['fillColor']})")
    for p in parts:
        print(f"    {p}")
