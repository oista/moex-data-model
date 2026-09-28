"""Apply chrome hygiene replacements in viewer.js."""
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "static" / "viewer.js"
t = p.read_text(encoding="utf-8")

repls = [
    (
        'toggle.textContent = hasKids ? (open ? "▼" : "▶") : "·";',
        "setTreeToggle(toggle, { open, leaf: !hasKids });",
    ),
    (
        'toggle.textContent = open ? "▼" : "▶";',
        "setTreeToggle(toggle, { open, leaf: false });",
    ),
    (
        'toggle.textContent = hasBody ? (open ? "▼" : "▶") : "·";',
        "setTreeToggle(toggle, { open, leaf: !hasBody });",
    ),
    (
        'toggle.textContent = kids.hidden ? "▶" : "▼";',
        "setTreeToggle(toggle, { open: !kids.hidden, leaf: false });",
    ),
    (
        'toggle.textContent = "▶";',
        "setTreeToggle(toggle, { open: false, leaf: false });",
    ),
    (
        'toggle.textContent = "▼";',
        "setTreeToggle(toggle, { open: true, leaf: false });",
    ),
    (
        '`<span class="module-icon">${escapeHtml(mod.icon || "📄")}</span>\n'
        '          <span>${escapeHtml(mod.title)}</span>',
        '`${displayIcon(mod.icon) ? `<span class="module-icon">${escapeHtml(displayIcon(mod.icon))}</span> ` : ""}'
        "<span>${escapeHtml(mod.title)}</span>",
    ),
]

for a, b in repls:
    if a not in t:
        print("MISSING:", repr(a[:60]))
    else:
        t = t.replace(a, b)
        print("OK", a[:24].encode("ascii", "replace").decode("ascii"))

# Headers: strip emoji icons cleanly
old_h = 'header.innerHTML = `<h1>${escapeHtml(mod.icon || "")} ${escapeHtml(mod.title)}</h1>'
new_h = (
    'header.innerHTML = `<h1>${escapeHtml(displayIcon(mod.icon) ? displayIcon(mod.icon) + " " : "")}'
    "${escapeHtml(mod.title)}</h1>"
)
count = t.count(old_h)
t = t.replace(old_h, new_h)
print("headers", count)

# depth: use CSS variable instead of marginLeft
old_depth = "if (depth) wrapNode.style.marginLeft = `${Math.min(depth, 6) * 8}px`;"
new_depth = "wrapNode.style.setProperty(\"--tree-level\", String(depth || 0));"
if old_depth in t:
    t = t.replace(old_depth, new_depth)
    print("depth OK")
else:
    print("depth MISSING")

p.write_text(t, encoding="utf-8")
print("triangles left", t.count("▼"), t.count("▶"))
print("emoji doc left", t.count("📄"))
