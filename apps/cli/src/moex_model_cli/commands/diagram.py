"""diagram — expose DBML golden sample path (ADR-006 projection)."""

from __future__ import annotations

import shutil
from pathlib import Path

from moex_model_cli.bootstrap import SlicePaths

DEFAULT_DBML = (
    Path("generated")
    / "artifacts"
    / "moex-dams"
    / "0.1"
    / "moex-dams-drawdb-colored.dbml"
)


def run_diagram(
    paths: SlicePaths,
    *,
    out: Path | None = None,
    profile: str = "physical",
) -> tuple[int, str]:
    src = paths.root / DEFAULT_DBML
    if not src.is_file():
        return 1, f"missing DBML golden sample: {src}\n"
    dest = out if out is not None else paths.root / "generated" / "artifacts" / "diagrams" / f"dams-{profile}.dbml"
    if not dest.is_absolute():
        dest = (paths.root / dest).resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    return 0, f"diagram profile={profile} wrote {dest}\n"
