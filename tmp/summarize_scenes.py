import json
from pathlib import Path

paths = [
    "model-assets/implementations/solutions/mdm/publications/logical.scene.json",
    "model-assets/implementations/solutions/mdm/publications/physical.scene.json",
    "model-assets/implementations/solutions/esed/publications/logical.scene.json",
    "model-assets/implementations/solutions/esed/publications/physical.scene.json",
    "model-assets/implementations/solutions/crm/publications/logical.scene.json",
    "model-assets/implementations/solutions/crm/publications/physical.scene.json",
]
for p in paths:
    s = json.loads(Path(p).read_text(encoding="utf-8"))
    print("===", p, "===")
    for n in s["nodes"]:
        print(
            f"  {n['name']:32} cols={len(n.get('columns') or []):2d} id={n['element_id']}"
        )
    for e in s["edges"]:
        eid = str(e.get("id") or "")
        print(f"  EDGE {e['source']} -> {e['target']} | {eid}")
