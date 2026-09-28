"""One-shot: migrate baseline viewer.css into layered 40-components.css."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = (ROOT / "tests/fixtures/ui-baseline/viewer.css").read_text(encoding="utf-8")
src2 = re.sub(r":root\s*\{.*?\}\s*", "", src, count=1, flags=re.S)
src2 = re.sub(r'\[data-theme="dark"\]\s*\{.*?\}\s*', "", src2, count=1, flags=re.S)
src2 = re.sub(r"\*\s*\{.*?\}\s*", "", src2, count=1, flags=re.S)
src2 = re.sub(r"html,\s*body\s*\{.*?\}\s*", "", src2, count=1, flags=re.S)
src2 = re.sub(r"body\s*\{.*?\}\s*", "", src2, count=1, flags=re.S)
repls = [
    ("border-radius: 10px", "border-radius: var(--radius-lg)"),
    ("border-radius: 8px", "border-radius: var(--radius-md)"),
    ("border-radius: 6px", "border-radius: var(--radius-sm)"),
    ("box-shadow: var(--shadow);", "box-shadow: none;"),
    (
        ".module-btn.active { background: var(--accent-soft); border-color: var(--accent); }",
        ".module-btn.active { background: var(--selection-bg); border-color: transparent; box-shadow: inset 2px 0 0 var(--brand); }",
    ),
    (
        ".nav-group-btn.active, .nav-item-btn.active, .nav-section-btn.active { background: var(--accent-soft); font-weight: 600; }",
        ".nav-group-btn.active, .nav-item-btn.active, .nav-section-btn.active { background: var(--selection-bg); font-weight: 600; box-shadow: inset 2px 0 0 var(--brand); color: var(--text-primary); }",
    ),
    (".detail-card {", ".content-card,\n.detail-card {"),
    ("font-size: 22px", "font-size: var(--font-h2)"),
    ("max-width: 1400px", "max-width: var(--content-max)"),
    ("color: var(--accent)", "color: var(--link)"),
]
for a, b in repls:
    src2 = src2.replace(a, b)
src2 = re.sub(r"@media \(max-width: 900px\)\s*\{[\s\S]*\}\s*$", "", src2)
# Drop duplicate .app/.sidebar/.toolbar/.main/.content rules — layout layer owns shell
for sel in (
    r"\.app\s*\{.*?\}\s*",
    r"\.sidebar\s*\{.*?\}\s*",
    r"\.main\s*\{.*?\}\s*",
    r"\.toolbar\s*\{.*?\}\s*",
    r"\.content\s*\{.*?\}\s*",
):
    src2 = re.sub(sel, "", src2, count=1, flags=re.S)

out = ROOT / "static/css/40-components.css"
out.write_text("/* Components migrated from pre-Atlas viewer.css */\n" + src2, encoding="utf-8")
print(f"wrote {out} ({out.stat().st_size} bytes)")
