import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
js = json.loads((REPO / "generated/artifacts/moex-dams/0.1/moex-dams.schema.json").read_text(encoding="utf-8"))
d = js["$defs"]
for c in sys.argv[1:]:
    x = d[c]
    print("==", c, list(x.keys()))
    for k in ("if", "then", "else", "allOf", "anyOf", "oneOf", "not"):
        if k in x:
            print(k, json.dumps(x[k], ensure_ascii=False)[:2500])
