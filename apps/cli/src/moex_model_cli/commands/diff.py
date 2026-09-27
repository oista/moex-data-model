"""diff — textual + line-count summary of two revisions/paths via GitProvider."""

from __future__ import annotations

import difflib
from pathlib import Path

from moex_git import LocalGitProvider
from moex_model_cli.bootstrap import SlicePaths


def run_diff(
    paths: SlicePaths,
    *,
    from_ref: str,
    to_ref: str,
    path: str | None = None,
) -> tuple[int, str]:
    rel = path
    if rel is None:
        try:
            rel = paths.implementation.relative_to(paths.root).as_posix()
        except ValueError:
            rel = paths.implementation.as_posix()

    git = LocalGitProvider(paths.root)
    try:
        left = git.get_file(from_ref, rel).decode("utf-8", errors="replace")
        right = git.get_file(to_ref, rel).decode("utf-8", errors="replace")
    except Exception as exc:
        # Fallback: worktree file vs empty when refs missing
        if to_ref in {"WORKTREE", "workdir", ":"}:
            right = Path(paths.root / rel).read_text(encoding="utf-8")
            try:
                left = git.get_file(from_ref, rel).decode("utf-8", errors="replace")
            except Exception:
                return 1, f"diff failed: {exc}\n"
        else:
            return 1, f"diff failed: {exc}\n"

    left_lines = left.splitlines(keepends=True)
    right_lines = right.splitlines(keepends=True)
    udiff = list(
        difflib.unified_diff(
            left_lines,
            right_lines,
            fromfile=f"{from_ref}:{rel}",
            tofile=f"{to_ref}:{rel}",
        )
    )
    added = sum(1 for ln in udiff if ln.startswith("+") and not ln.startswith("+++"))
    removed = sum(1 for ln in udiff if ln.startswith("-") and not ln.startswith("---"))
    summary = f"diff path={rel} +{added} -{removed} hunks={len(udiff)}\n"
    return 0, summary + "".join(udiff[:400])
