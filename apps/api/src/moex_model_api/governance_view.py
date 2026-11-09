"""Refresh EffectiveGovernanceView for one published package body."""

from __future__ import annotations

import tempfile
from pathlib import Path

import yaml

from moex_dams.governance.materialize import (
    discover_package_paths,
    dump_governance_view,
    materialize_governance_view,
)
from moex_git.ports import FileChange


def _without_built_at(text: str) -> object:
    data = yaml.safe_load(text)
    if isinstance(data, dict):
        data.pop("built_at", None)
    return data


def governance_view_change(
    repo_root: Path | str,
    rel: str,
    content: str,
) -> FileChange | None:
    """View file for repo_root with ``rel`` replaced by ``content``.

    Returns None when that path is not a package body the view is built from,
    or when the regenerated view matches the file already in the tree.
    ``built_at`` is ignored in the comparison, the same way the check ignores it.
    """
    root = Path(repo_root)
    target = (root / rel).resolve()
    if not target.is_file():
        return None
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".yaml",
        encoding="utf-8",
        newline="\n",
        delete=False,
    ) as handle:
        handle.write(content)
        overlay = Path(handle.name)
    try:
        paths = discover_package_paths(root)
        replaced = False
        overlaid: list[Path] = []
        for path in paths:
            if path.resolve() == target:
                overlaid.append(overlay)
                replaced = True
            else:
                overlaid.append(path)
        if not replaced:
            return None
        out, view, _findings = materialize_governance_view(
            root,
            package_paths=overlaid,
            write=False,
        )
        text = dump_governance_view(view)
        if out.is_file() and _without_built_at(out.read_text(encoding="utf-8")) == _without_built_at(text):
            return None
        return FileChange(
            path=out.relative_to(root).as_posix(),
            content=text.encode("utf-8"),
        )
    finally:
        overlay.unlink(missing_ok=True)
