from __future__ import annotations

import json
import re
from pathlib import Path

html = Path("apps/viewer/dist/index.html").read_text(encoding="utf-8")
print("erd_scene count", html.count("erd_scene"))
print("modules_json marker", "modules_json" in html)

# Find embedded modules JSON assignment in base template patterns.
for pat in [
    r"const MODULES\s*=\s*(\[.*?\]);\s*</script>",
    r"window\.MODULES\s*=\s*(\[.*?\]);",
    r'id="modules-data"[^>]*>(.*?)</script>',
    r"<script type=\"application/json\" id=\"modules-data\">(.*?)</script>",
]:
    m = re.search(pat, html, re.S)
    print("pat", pat[:40], "->", bool(m), "len", len(m.group(1)) if m else 0)

# Grep template
base = Path("apps/viewer/templates/base.html.j2").read_text(encoding="utf-8")
for line in base.splitlines():
    if "modules" in line.lower() and ("script" in line.lower() or "json" in line.lower() or "MODULES" in line):
        print("TMPL:", line[:160])
