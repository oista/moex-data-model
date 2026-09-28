"""publish command — publish gate + publication export_slice_projection."""

from __future__ import annotations

import sys
from pathlib import Path

from moex_publication.application.build_publication import (
    build_publication_module,
    export_slice_projection,
)
from moex_model_cli.bootstrap import DEFAULT_SLICE_JSON, SlicePaths


def _run_publish_gate(root: Path) -> tuple[int, str]:
    gate = root / "scripts" / "publish_gate.py"
    if not gate.is_file():
        return 1, f"publish-gate script missing: {gate}\n"
    # Import in-process so API and CLI share the same checker.
    sys.path.insert(0, str(root / "scripts"))
    from publish_gate import verify_publish_gate  # noqa: WPS433

    errors = verify_publish_gate(refresh_bundle=False)
    if errors:
        return 1, "publish-gate FAILED\n" + "\n".join(errors) + "\n"
    return 0, "publish-gate OK\n"


def run_publish(
    paths: SlicePaths,
    *,
    out: Path | None = None,
    implementation_id: str | None = None,
    skip_gate: bool = False,
) -> tuple[int, str]:
    lines: list[str] = []
    if not skip_gate:
        code, gate_text = _run_publish_gate(paths.root)
        lines.append(gate_text.rstrip())
        if code != 0:
            return code, "\n".join(lines) + "\n"

    out_path = out if out is not None else paths.root / DEFAULT_SLICE_JSON
    if not out_path.is_absolute():
        out_path = (paths.root / out_path).resolve()
    result = export_slice_projection(
        schema_path=paths.schema,
        implementation_path=paths.implementation,
        out_path=out_path,
        implementation_id=implementation_id,
    )
    module = build_publication_module(result)
    lines.append(
        f"wrote {out_path} module={module.module_id} "
        f"overall={result.report.overall_result.value}"
    )
    if result.report.is_conformant:
        # Surface bundle digest for publication summary consumers.
        bundle_manifest = (
            paths.root / "generated" / "manifests" / "moex-dams-bundle.json"
        )
        if bundle_manifest.is_file():
            import json

            digest = json.loads(bundle_manifest.read_text(encoding="utf-8")).get(
                "content_digest"
            )
            if digest:
                lines.append(f"bundle_digest={digest}")
    return (0 if result.report.is_conformant else 1, "\n".join(lines) + "\n")
