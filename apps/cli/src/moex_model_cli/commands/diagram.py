"""diagram — one-way ModelPackage → DBML (ADR-006)."""

from __future__ import annotations

from pathlib import Path

from moex_dams.projection.dbml import write_dbml_artifact
from moex_model_cli.bootstrap import SlicePaths

SUPPORTED_FORMATS = frozenset({"dbml"})
SUPPORTED_PROFILES = frozenset({"logical", "physical"})


def run_diagram(
    paths: SlicePaths,
    *,
    out: Path | None = None,
    profile: str = "logical",
    fmt: str = "dbml",
) -> tuple[int, str]:
    if fmt not in SUPPORTED_FORMATS:
        return 2, f"unsupported --format {fmt!r} (only dbml)\n"
    if profile not in SUPPORTED_PROFILES:
        return 2, f"unsupported --profile {profile!r} (logical|physical)\n"
    if not paths.implementation.is_file():
        return 1, f"missing implementation: {paths.implementation}\n"

    dest = (
        out
        if out is not None
        else paths.root
        / "generated"
        / "artifacts"
        / "diagrams"
        / f"{paths.implementation.stem}-{profile}.dbml"
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
