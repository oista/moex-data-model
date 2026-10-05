"""diagram — one-way ModelPackage → DBML or Mermaid erDiagram (ADR-006)."""

from __future__ import annotations

from pathlib import Path

from moex_dams.projection.dbml import write_dbml_artifact
from moex_dams.projection.mermaid_er import (
    try_render_er_svg,
    write_er_diagram_artifact,
)
from moex_model_cli.bootstrap import SlicePaths

SUPPORTED_FORMATS = frozenset({"dbml", "mermaid"})
SUPPORTED_PROFILES = frozenset({"logical", "physical", "conceptual"})


def run_diagram(
    paths: SlicePaths,
    *,
    out: Path | None = None,
    profile: str = "logical",
    fmt: str = "dbml",
    render_svg: bool = True,
    reset_layout: bool = False,
) -> tuple[int, str]:
    if fmt not in SUPPORTED_FORMATS:
        return 2, f"unsupported --format {fmt!r} (dbml|mermaid)\n"
    if profile not in SUPPORTED_PROFILES:
        return 2, f"unsupported --profile {profile!r} (logical|physical|conceptual)\n"
    if not paths.implementation.is_file():
        return 1, f"missing implementation: {paths.implementation}\n"

    if fmt == "dbml":
        dest = (
            out
            if out is not None
            else paths.implementation.parent / "publications" / f"{profile}.dbml"
        )
        if not dest.is_absolute():
            dest = (paths.root / dest).resolve()
        try:
            manifest = write_dbml_artifact(
                implementation_path=paths.implementation,
                out_path=dest,
                profile=profile,  # type: ignore[arg-type]
            )
        except (OSError, ValueError, TypeError) as exc:
            return 1, f"diagram failed: {exc}\n"
        return (
            0,
            f"diagram profile={profile} format={fmt} "
            f"wrote {dest} digest={manifest.content_digest}\n",
        )

    # mermaid erDiagram → publications/{profile}.erd.md (+ optional .svg)
    dest = (
        out
        if out is not None
        else paths.implementation.parent / "publications" / f"{profile}.erd.md"
    )
    if not dest.is_absolute():
        dest = (paths.root / dest).resolve()
    try:
        manifest = write_er_diagram_artifact(
            implementation_path=paths.implementation,
            out_md=dest,
            profile=profile,  # type: ignore[arg-type]
            reset_layout=reset_layout,
        )
    except (OSError, ValueError, TypeError) as exc:
        return 1, f"diagram failed: {exc}\n"

    msg = (
        f"diagram profile={profile} format={fmt} "
        f"wrote {dest} digest={manifest.content_digest}"
    )
    if render_svg:
        svg = try_render_er_svg(dest)
        if svg is not None:
            msg += f" svg={svg}"
        else:
            msg += " svg=skipped (npx/@mermaid-js/mermaid-cli unavailable)"
    return 0, msg + "\n"
