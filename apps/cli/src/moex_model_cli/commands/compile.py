"""compile — regenerate DAMS Pydantic contracts (+ optional json-schema)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from moex_model_cli.bootstrap import SlicePaths


def run_compile(paths: SlicePaths, *, with_json_schema: bool = False) -> tuple[int, str]:
    script = paths.root / "scripts" / "generate_contracts.py"
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=paths.root,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        return proc.returncode, out

    lines = [out.rstrip(), "compile: contracts OK"]
    if with_json_schema:
        schema = paths.schema
        dest = (
            paths.root
            / "generated"
            / "artifacts"
            / "moex-dams"
            / "0.1"
            / "moex-dams.schema.json"
        )
        dest.parent.mkdir(parents=True, exist_ok=True)
        gen = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "from linkml.generators.jsonschemagen import JsonSchemaGenerator; "
                    f"open(r'{dest.as_posix()}','w',encoding='utf-8').write("
                    f"JsonSchemaGenerator(r'{schema.as_posix()}').serialize())"
                ),
            ],
            cwd=paths.root,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if gen.returncode != 0:
            return gen.returncode, out + (gen.stderr or "")
        lines.append(f"compile: json-schema → {dest.relative_to(paths.root)}")
    return 0, "\n".join(lines) + "\n"
