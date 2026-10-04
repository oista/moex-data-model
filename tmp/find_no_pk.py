import json

d = json.load(open(r"c:\Users\bons1\IdeaProjects\moex-data-model\tmp\cmodel_content04_inventory.json", encoding="utf-8"))
lines = []
for e in d["entities"]:
    if not any(a.get("key") == "PK" for a in e["attributes"]):
        lines.append(e["name"] + ": " + repr([a["name"] for a in e["attributes"]]))
open(r"c:\Users\bons1\IdeaProjects\moex-data-model\tmp\no_pk.txt", "w", encoding="utf-8").write("\n".join(lines))
