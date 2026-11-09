"""semantic-diff — classified DAMS ModelPackage changes between two revisions/files."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from moex_dams.application.diff import diff_implementations
from moex_git import LocalGitProvider
from moex_model_cli.bootstrap import (
    SlicePaths,
    resolve_body_from_implementation_envelope,
)
from moex_repository_loader.loader import RepositoryLoader


def _report_json(report) -> str:
    """Dump the report and include has_breaking.

    ``has_breaking`` is a property, so ``model_dump_json`` omits it.
    ``breaking-gate --from-report`` reads this field.
    """
    payload = json.loads(report.model_dump_json())
    payload["has_breaking"] = bool(report.has_breaking)
    return json.dumps(payload, indent=2) + "\n"


def _manifest_docs(root: Path, *, ref: str | None = None) -> dict[str, str]:
    """Map implementation id -> envelope path relative to implementations root."""
    if ref is None:
        loader = RepositoryLoader(root, verify_hashes=False)
        return {doc.id: doc.path for doc in loader.load_manifest().documents}
    git = LocalGitProvider(root)
    text = git.get_file(
        ref, "model-assets/implementations/manifest.yaml"
    ).decode("utf-8", errors="replace")
    import yaml

    raw = yaml.safe_load(text) or {}
    out: dict[str, str] = {}
    for item in raw.get("documents") or []:
        if isinstance(item, dict) and item.get("id") and item.get("path"):
            out[str(item["id"])] = str(item["path"]).replace("\\", "/")
    return out


def _body_rel_for_envelope(root: Path, envelope_rel: str) -> str:
    envelope = root / "model-assets" / "implementations" / envelope_rel
    body = resolve_body_from_implementation_envelope(envelope)
    return body.relative_to(root).as_posix()


def _body_rels(root: Path) -> list[str]:
    return [
        _body_rel_for_envelope(root, path)
        for path in _manifest_docs(root).values()
    ]


def run_semantic_diff(
    paths: SlicePaths,
    *,
    from_ref: str | None = None,
    to_ref: str | None = None,
    path: str | None = None,
    left: Path | None = None,
    right: Path | None = None,
    as_json: bool = False,
    fail_on: str | None = None,
    all_from_manifest: bool = False,
) -> tuple[int, str]:
    if all_from_manifest:
        return _run_all(
            paths,
            from_ref=from_ref,
            to_ref=to_ref,
            as_json=as_json,
            fail_on=fail_on,
        )
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

    counts = report.counts_by_category()
    if as_json:
        text = _report_json(report)
    else:
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
                f"{change.category.value.upper()} {change.change_code} {subject}: "
                f"{change.message}\n"
            )
        text = "".join(lines)

    # Default behaviour preserved: exit 1 on breaking unless --fail-on narrows it.
    if fail_on is None:
        return (1 if report.has_breaking else 0, text)
    if fail_on == "breaking":
        return (1 if report.has_breaking else 0, text)
    if fail_on == "never":
        return 0, text
    return 2, f"unsupported --fail-on {fail_on!r} (breaking|never)\n"


def _run_all(
    paths: SlicePaths,
    *,
    from_ref: str | None,
    to_ref: str | None,
    as_json: bool,
    fail_on: str | None,
) -> tuple[int, str]:
    if from_ref is None or to_ref is None:
        return 2, "semantic-diff --all requires --from and --to\n"
    changes: list[dict] = []
    skipped: list[str] = []
    base_docs = _manifest_docs(paths.root, ref=from_ref)
    if to_ref in {"HEAD", "WORKTREE", "workdir", ":"}:
        head_docs = _manifest_docs(paths.root)
    else:
        # Prefer worktree manifest when to_ref is the current tip.
        try:
            head_docs = _manifest_docs(paths.root, ref=to_ref)
        except Exception:
            head_docs = _manifest_docs(paths.root)

    removed = sorted(set(base_docs) - set(head_docs))
    added = sorted(set(head_docs) - set(base_docs))
    for impl_id in removed:
        changes.append(
            {
                "change_code": "IMPLEMENTATION-REMOVED",
                "category": "breaking",
                "subject_ref": impl_id,
                "message": f"implementation {impl_id} removed from manifest",
                "path": f"model-assets/implementations/{base_docs[impl_id]}",
            }
        )
    for impl_id in added:
        changes.append(
            {
                "change_code": "IMPLEMENTATION-ADDED",
                "category": "backward_compatible",
                "subject_ref": impl_id,
                "message": f"implementation {impl_id} added to manifest",
                "path": f"model-assets/implementations/{head_docs[impl_id]}",
            }
        )

    shared = sorted(set(base_docs) & set(head_docs))
    for impl_id in shared:
        try:
            rel = _body_rel_for_envelope(paths.root, head_docs[impl_id])
        except Exception as exc:
            skipped.append(f"{impl_id}: {exc}")
            continue
        try:
            left_text, right_text = _load_pair(paths.root, rel, from_ref, to_ref)
        except Exception as exc:
            skipped.append(f"{rel}: {exc}")
            continue
        if left_text == right_text:
            continue
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
        for change in report.changes:
            item = json.loads(change.model_dump_json())
            item["path"] = rel
            changes.append(item)
    has_breaking = any(c.get("category") == "breaking" for c in changes)
    if as_json:
        text = json.dumps(
            {
                "base_label": from_ref,
                "target_label": to_ref,
                "has_breaking": has_breaking,
                "changes": changes,
                "skipped": skipped,
            },
            indent=2,
        ) + "\n"
    else:
        lines = [
            f"semantic-diff base={from_ref} target={to_ref} "
            f"shared={len(shared)} added={len(added)} removed={len(removed)} "
            f"changes={len(changes)} "
            f"breaking={sum(1 for c in changes if c.get('category') == 'breaking')}\n"
        ]
        for change in changes:
            lines.append(
                f"{str(change.get('category') or '').upper()} "
                f"{change.get('change_code')} {change.get('path')}: "
                f"{change.get('message')}\n"
            )
        for note in skipped:
            lines.append(f"SKIP {note}\n")
        text = "".join(lines)
    if fail_on == "never":
        return 0, text
    if fail_on not in (None, "breaking"):
        return 2, f"unsupported --fail-on {fail_on!r} (breaking|never)\n"
    return (1 if has_breaking else 0, text)


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
