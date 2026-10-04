"""Generate enterprise conceptual.erd.md + clickmap + SVG."""
from pathlib import Path

from moex_dams.projection.mermaid_er import (
    try_render_er_svg,
    write_er_diagram_artifact,
)

ROOT = Path(__file__).resolve().parents[1]
IMPL = (
    ROOT
    / "model-assets"
    / "implementations"
    / "enterprise"
    / "moex-enterprise-conceptual-model"
    / "0.1"
    / "enterprise-conceptual-model.yaml"
)
OUT = IMPL.parent / "publications" / "conceptual.erd.md"

manifest = write_er_diagram_artifact(
    implementation_path=IMPL,
    out_md=OUT,
    profile="conceptual",
)
print(f"wrote {OUT} digest={manifest.content_digest}")
svg = try_render_er_svg(OUT)
print(f"svg={svg}")
