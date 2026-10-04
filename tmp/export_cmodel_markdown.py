import json
from collections import defaultdict

inv = json.load(
    open(r"c:\Users\bons1\IdeaProjects\moex-data-model\tmp\cmodel_content04_inventory.json", encoding="utf-8")
)
out = []
out.append("# CModel_content04.drawio — structured inventory\n")
out.append(f"- **Source:** `{inv['source_file']}`")
out.append(f"- **Size:** {inv['file_size_bytes']:,} bytes")
out.append(f"- **Diagram pages:** {len(inv['diagrams'])}")
for diag in inv["diagrams"]:
    out.append(f"  - **{diag['name']}** (`{diag['id']}`)")
out.append(f"- **Entities (ER tables):** {inv['summary']['entity_count']}")
out.append(f"- **Connector edges:** {inv['summary']['edge_count']}")
out.append(f"- **FK-marked attributes:** {inv['summary']['inferred_fk_count']}")
out.append("- **Attribute data types:** not modeled in diagram (names + PK/FK markers only)")
out.append("- **Edge labels / cardinality:** none on connectors (74 unlabeled orthogonal edges)")
out.append("- **Notes / legend / free-text annotations:** none detected")
out.append("- **UML classes / swimlane subject areas:** 0 UML; swimlane styling used only inside table rows\n")

out.append("## Domain grouping (header fill color)\n")
out.append("| Color | Interpretation (draft) | Entity count |")
out.append("|-------|------------------------|--------------|")
for color, names in inv["fill_color_domains"].items():
    label = "Trading / market / TKS (green)" if color == "#60a917" else "Enterprise / CRM / HR / finance (blue)"
    out.append(f"| `{color}` | {label} | {len(names)} |")

out.append("\n## Entities by domain\n")
by_color = defaultdict(list)
for e in inv["entities"]:
    by_color[e["fillColor"]].append(e)
for color in sorted(by_color.keys()):
    label = "Trading / market (#60a917)" if color == "#60a917" else "Enterprise (#0050ef)"
    out.append(f"\n### {label}\n")
    for e in sorted(by_color[color], key=lambda x: x["name"]):
        out.append(f"#### {e['name']}\n")
        if not e["attributes"]:
            out.append("_No attributes parsed._\n")
            continue
        out.append("| Key | Attribute |")
        out.append("|-----|-----------|")
        for a in e["attributes"]:
            key = a.get("key") or ""
            name = a["name"].replace("\xa0", " ").strip()
            out.append(f"| {key} | {name} |")
        out.append("")

out.append("\n## Relationships (draw.io edges, entity-resolved)\n")
out.append("| From | To | Label | Cardinality |")
out.append("|------|----|-------|-------------|")
for e in sorted(inv["edges"], key=lambda x: (x.get("source_entity") or "", x.get("target_entity") or "")):
    fr = e.get("source_entity") or e.get("source_label") or e["source_id"]
    to = e.get("target_entity") or e.get("target_label") or e["target_id"]
    lab = e.get("label") or ""
    card = e.get("cardinality_hint") or ""
    out.append(f"| {fr} | {to} | {lab} | {card} |")

out.append("\n## FK hints (from `[FK]` column on attributes)\n")
out.append("Use explicit edges above where possible; name matching below is heuristic.\n")
out.append("| From entity | Attribute | Likely target entity |")
out.append("|-------------|-----------|----------------------|")
for r in inv["inferred_fk_relationships"]:
    out.append(f"| {r['from_entity']} | {r['via_attribute']} | {r.get('to_entity_guess') or '—'} |")

path = r"c:\Users\bons1\IdeaProjects\moex-data-model\tmp\cmodel_content04_inventory.md"
open(path, "w", encoding="utf-8").write("\n".join(out))
print("WROTE", path)
