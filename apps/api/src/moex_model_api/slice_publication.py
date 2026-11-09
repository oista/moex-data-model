"""Refresh publications/vertical_slice.json for one published package body."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from moex_git.ports import FileChange
from moex_model_cli.bootstrap import (
    DEFAULT_SCHEMA,
    SlicePaths,
    resolve_body_from_implementation_envelope,
)
from moex_publication.application.build_publication import export_slice_projection
from moex_publication.slice_canonical import slices_equal
from moex_repository_loader.loader import RepositoryLoader


def _slice_path_for_body(root: Path, body_rel: str) -> Path | None:
    """Return publications/vertical_slice.json next to the body, if it exists."""
    body = (root / body_rel).resolve()
    candidate = body.parent / "publications" / "vertical_slice.json"
    if candidate.is_file():
        return candidate
    # Body may live beside implementation.yaml; publications is sibling of envelope.
    envelope_parent = body.parent
    if (envelope_parent / "implementation.yaml").is_file():
        alt = envelope_parent / "publications" / "vertical_slice.json"
        if alt.is_file():
            return alt
    return None


def _implementation_id_for_body(root: Path, body_rel: str) -> str | None:
    loader = RepositoryLoader(root, verify_hashes=False)
    target = (root / body_rel).resolve()
    for ref in loader.load_manifest().documents:
        envelope = loader.implementations_root / ref.path
        try:
            body = resolve_body_from_implementation_envelope(envelope)
        except (OSError, ValueError, FileNotFoundError):
            continue
        if body.resolve() == target:
            return ref.id
    return None


def slice_publication_change(
    repo_root: Path | str,
    rel: str,
    content: str,
    *,
    implementation_id: str | None = None,
) -> FileChange | None:
    """Regenerate vertical_slice.json with ``rel`` replaced by ``content``.

    Returns None when the implementation has no committed vertical_slice.json,
    or when the regenerated slice matches the file already in the tree
    (time fields ignored via ``slices_equal``).
    """
    root = Path(repo_root).resolve()
    slice_path = _slice_path_for_body(root, rel)
    if slice_path is None:
        return None

    impl_id = implementation_id or _implementation_id_for_body(root, rel)
    schema = SlicePaths.resolve(root=root, schema=root / DEFAULT_SCHEMA).schema

    with tempfile.TemporaryDirectory(prefix="moex-slice-pub-") as tmp:
        tmp_path = Path(tmp)
        body_file = tmp_path / "body.yaml"
        body_file.write_text(content, encoding="utf-8", newline="\n")
        out = tmp_path / "vertical_slice.json"
        export_slice_projection(
            schema_path=schema,
            implementation_path=body_file,
            out_path=out,
            implementation_id=impl_id,
        )
        fresh_text = out.read_text(encoding="utf-8")
        fresh_data = json.loads(fresh_text)
        committed_data = json.loads(slice_path.read_text(encoding="utf-8"))
        if slices_equal(committed_data, fresh_data):
            return None
        # Prefer pretty JSON from export as committed content.
        return FileChange(
            path=slice_path.relative_to(root).as_posix(),
            content=fresh_text.encode("utf-8"),
        )
