"""semantic-diff — classified DAMS ModelPackage changes between two revisions/files."""

from __future__ import annotations

import tempfile
from pathlib import Path

from moex_dams.application.diff import diff_implementations
from moex_git import LocalGitProvider
from moex_model_cli.bootstrap import SlicePaths


def run_semantic_diff(
    paths: SlicePaths,
    *,
    from_ref: str | None = None,
    to_ref: str | None = None,
    path: str | None = None,
    left: Path | None = None,
    right: Path | None = None,
    as_json: bool = False,
) -> tuple[int, str]:
    try:
        if left is not None and right is not None:
            left_path = left if left.is_absolute() else paths.root / left
            right_path = right if right.is_absolute() else paths.root / right
            base_label = str(left)
            target_label = str(right)
            report = diff_implementations(
                schema_path=paths.schema,
                left_path=left_path,
                right_path=right_path,
                base_label=base_label,
                target_label=target_label,
            )
        elif from_ref is not None and to_ref is not None:
            rel = path
            if rel is None:
                try:
                    rel = paths.implementation.relative_to(paths.root).as_posix()
                except ValueError:
                    rel = paths.implementation.as_posix()
            left_text, right_text = _load_pair(paths.root, rel, from_ref, to_ref)
            with tempfile.TemporaryDirectory(prefix="moex-semantic-diff-") as tmp:
                tmp_path = Path(tmp)
                left_file = tmp_path / "left.yaml"
                right_file = tmp_path / "right.yaml"
                left_file.write_text(left_text, encoding="utf-8")
                right_file.write_text(right_text, encoding="utf-8")
                report = diff_implementations(
                    schema_path=paths.schema,
                    left_path=left_file,
                    right_path=right_file,
                    base_label=from_ref,
                    target_label=to_ref,
                )
        else:
            return 2, "semantic-diff requires --from/--to or --left/--right\n"
    except Exception as exc:
        return 2, f"semantic-diff failed: {exc}\n"

    if as_json:
        return (
            1 if report.has_breaking else 0,
            report.model_dump_json(indent=2) + "\n",
        )

    counts = report.counts_by_category()
    lines = [
        f"semantic-diff base={report.base_label} target={report.target_label} "
        f"changes={len(report.changes)} "
        f"breaking={counts.get('breaking', 0)} "
        f"backward_compatible={counts.get('backward_compatible', 0)} "
        f"governance={counts.get('governance', 0)} "
        f"operational={counts.get('operational', 0)} "
        f"non_breaking={counts.get('non_breaking', 0)}\n"
    ]
    for change in report.changes:
        subject = change.subject_ref or "-"
        lines.append(
            f"{change.category.value.upper()} {change.change_code} {subject}: {change.message}\n"
        )
    return (1 if report.has_breaking else 0, "".join(lines))


def _load_pair(
    root: Path,
    rel: str,
    from_ref: str,
    to_ref: str,
) -> tuple[str, str]:
    git = LocalGitProvider(root)
    try:
        left = git.get_file(from_ref, rel).decode("utf-8", errors="replace")
        right = git.get_file(to_ref, rel).decode("utf-8", errors="replace")
        return left, right
    except Exception as exc:
        if to_ref in {"WORKTREE", "workdir", ":"}:
            right = Path(root / rel).read_text(encoding="utf-8")
            try:
                left = git.get_file(from_ref, rel).decode("utf-8", errors="replace")
            except Exception:
                raise RuntimeError(f"cannot read {from_ref}:{rel}") from exc
            return left, right
        raise
