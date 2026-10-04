from pathlib import Path
import re

t = Path(
    "model-assets/implementations/solutions/ucd/publications/logical.erd.svg"
).read_text(encoding="utf-8")
ids = re.findall(r'id="([^"]+)"', t)
print("\n".join(ids[:60]))
print("--- classes sample ---")
for m in re.finditer(r'class="([^"]+)"', t):
    c = m.group(1)
    if "entity" in c.lower() or "rel" in c.lower() or "node" in c.lower():
        print(c)
        break
# show a chunk around first entity-like id
for i in ids:
    if "AGREEMENT" in i or "entity" in i.lower():
        idx = t.find(f'id="{i}"')
        print(i, "->", t[max(0, idx - 80) : idx + 200].replace("\n", " ")[:280])
        break
