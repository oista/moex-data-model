"""publications-fresh — regenerate vertical_slice.json and compare to committed."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from moex_model_cli.bootstrap import (
    SlicePaths,
    resolve_body_from_implementation_envelope,
)
from moex_publication.application.build_publication import export_slice_projection
from moex_publication.slice_canonical import slices_equal
from moex_repository_loader.loader import RepositoryLoader


def check_publications_fresh(repo_root: Path) -> tuple[int, str]:
    root = repo_root.resolve()
    loader = RepositoryLoader(root, verify_hashes=False)
    schema = SlicePaths.resolve(root=root).schema
    problems: list[str] = []
    checked = 0

    for ref in loader.load_manifest().documents:
        envelope = loader.implementations_root / ref.path
        pub_dir = envelope.parent / "publications"
        committed = pub_dir / "vertical_slice.json"
        if not committed.is_file():
            continue
        body = resolve_body_from_implementation_envelope(envelope)
        checked += 1
        with tempfile.TemporaryDirectory(prefix="moex-pub-fresh-") as tmp:
            out = Path(tmp) / "vertical_slice.json"
            export_slice_projection(
                schema_path=schema,
                implementation_path=body,
                out_path=out,
                implementation_id=ref.id,
            )
            committed_data = json.loads(committed.read_text(encoding="utf-8"))
            fresh_data = json.loads(out.read_text(encoding="utf-8"))
            if not slices_equal(committed_data, fresh_data):
                rel = committed.relative_to(root).as_posix()
                problems.append(
                    f"{rel} is stale; regenerate with "
                    f"moex-model publish --root . --implementation-id {ref.id} "
                    f"--out {rel}"
                )

    if not checked:
        return 0, "publications-fresh OK (no vertical_slice.json found)\n"
    if problems:
        lines = [f"publications-fresh FAILED checked={checked}:"]
        lines.extend(f"  {p}" for p in problems)
        return 1, "\n".join(lines) + "\n"
    return 0, f"publications-fresh OK checked={checked}\n"


def run_publications_fresh(repo_root: Path) -> tuple[int, str]:
    return check_publications_fresh(repo_root)
