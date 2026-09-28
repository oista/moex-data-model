"""publish command — publish gate + publication export_slice_projection."""

from __future__ import annotations

import json
from pathlib import Path

from moex_publication.application.build_publication import (
    build_publication_module,
    export_slice_projection,
)
from moex_model_cli.bootstrap import DEFAULT_SLICE_JSON, SlicePaths
from moex_model_cli.gates.publish_gate import refuse_generated_draft, verify_publish_gate


def run_publish(
    paths: SlicePaths,
    *,
    out: Path | None = None,
    implementation_id: str | None = None,
    skip_gate: bool = False,
) -> tuple[int, str]:
    lines: list[str] = []
    out_path = out if out is not None else paths.root / DEFAULT_SLICE_JSON
    if not out_path.is_absolute():
        out_path = (paths.root / out_path).resolve()

    draft_errors = refuse_generated_draft(root=paths.root, candidate=out_path)
    if draft_errors:
        return 1, "publish refused (generated-draft)\n" + "\n".join(draft_errors) + "\n"

    if not skip_gate:
        errors = verify_publish_gate(
            root=paths.root,
            refresh_bundle=False,
            publish_target=out_path,
        )
        if errors:
            return 1, "publish-gate FAILED\n" + "\n".join(errors) + "\n"
        lines.append("publish-gate OK")
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
        bundle_manifest = (
            paths.root / "generated" / "manifests" / "moex-dams-bundle.json"
        )
        if bundle_manifest.is_file():
            digest = json.loads(bundle_manifest.read_text(encoding="utf-8")).get(
                "content_digest"
            )
            if digest:
                lines.append(f"bundle_digest={digest}")
    return (0 if result.report.is_conformant else 1, "\n".join(lines) + "\n")
