"""schema-diff — classify DAMS LinkML schema changes between two revisions/files."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from moex_dams.application.schema_diff import (
    diff_schemas,
    write_schema_diff_report,
)
from moex_model_cli.bootstrap import SlicePaths

_SCHEMA_REL = "model-assets/specifications/moex-dams/0.1/schemas"
_DEFAULT_CHANGELOG = "docs/migration/CHANGELOG-technical-asset.md"


def run_schema_diff(
    paths: SlicePaths,
    *,
    from_ref: str | None = None,
    to_ref: str | None = None,
    left: Path | None = None,
    right: Path | None = None,
    changelog: Path | None = None,
    has_compatibility_baseline_ref: bool = False,
    fail_on_breaking: bool = False,
    as_json: bool = False,
    out_json: Path | None = None,
    out_text: Path | None = None,
) -> tuple[int, str]:
    try:
        if left is not None and right is not None:
            left_path = left if left.is_absolute() else paths.root / left
            right_path = right if right.is_absolute() else paths.root / right
            base_label = str(left)
            target_label = str(right)
            result = diff_schemas(
                left_path,
                right_path,
                base_label=base_label,
                target_label=target_label,
                changelog_path=_resolve_changelog(paths.root, changelog),
                has_compatibility_baseline_ref=has_compatibility_baseline_ref,
            )
        elif from_ref is not None and to_ref is not None:
            with tempfile.TemporaryDirectory(prefix="moex-schema-diff-") as tmp:
                tmp_path = Path(tmp)
                left_root = tmp_path / "left"
                right_root = tmp_path / "right"
                _materialize_schema_tree(paths.root, from_ref, left_root)
                if to_ref in {"WORKTREE", "workdir", ":"}:
                    _copy_worktree_schemas(paths.root, right_root)
                else:
                    _materialize_schema_tree(paths.root, to_ref, right_root)
                left_path = left_root / "moex-dams.yaml"
                right_path = right_root / "moex-dams.yaml"
                result = diff_schemas(
                    left_path,
                    right_path,
                    base_label=from_ref,
                    target_label=to_ref,
                    changelog_path=_resolve_changelog(paths.root, changelog),
                    has_compatibility_baseline_ref=has_compatibility_baseline_ref,
                )
        else:
            return 2, "schema-diff requires --from/--to or --left/--right\n"
    except Exception as exc:
        return 2, f"schema-diff failed: {exc}\n"

    if out_json is not None or out_text is not None:
        write_schema_diff_report(
            result,
            json_path=out_json,
            text_path=out_text,
        )

    if as_json:
        import json

        text = json.dumps(result.to_json_dict(), indent=2, ensure_ascii=False) + "\n"
    else:
        text = result.text_summary()

    if fail_on_breaking and result.uncovered_breaking:
        return 1, text
    if fail_on_breaking and result.has_breaking and not result.has_compatibility_baseline_ref:
        # Covered by changelog → uncovered empty; still OK.
        if result.uncovered_breaking:
            return 1, text
    return 0, text


def _resolve_changelog(root: Path, changelog: Path | None) -> Path | None:
    if changelog is not None:
        return changelog if changelog.is_absolute() else root / changelog
    default = root / _DEFAULT_CHANGELOG
    return default if default.is_file() else None


def _materialize_schema_tree(repo: Path, revision: str, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    listing = subprocess.run(
        ["git", "-C", str(repo), "ls-tree", "-r", "--name-only", revision, _SCHEMA_REL],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    files = [ln.strip() for ln in listing.stdout.splitlines() if ln.strip()]
    if not files:
        raise FileNotFoundError(f"no schema files at {revision}:{_SCHEMA_REL}")
    for rel in files:
        blob = subprocess.run(
            ["git", "-C", str(repo), "show", f"{revision}:{rel}"],
            check=True,
            capture_output=True,
        )
        name = Path(rel).name
        (dest / name).write_bytes(blob.stdout)


def _copy_worktree_schemas(repo: Path, dest: Path) -> None:
    import shutil

    src = repo / _SCHEMA_REL
    if not src.is_dir():
        raise FileNotFoundError(src)
    shutil.copytree(src, dest, dirs_exist_ok=True)
