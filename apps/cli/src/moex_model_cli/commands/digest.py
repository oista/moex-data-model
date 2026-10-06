"""digest — verify / rewrite DataModelBinding.integrity_digest (ADR-042)."""

from __future__ import annotations

from pathlib import Path

from moex_dams.application.digest import verify_digests, write_digests
from moex_model_cli.bootstrap import SlicePaths


def run_digest(
    paths: SlicePaths,
    *,
    model: str | None = None,
    write: bool = False,
    allow_non_demo_write: bool = False,
) -> tuple[int, str]:
    root = paths.root
    lines: list[str] = []
    try:
        if write:
            written = write_digests(
                root,
                model=model,
                allow_non_demo=allow_non_demo_write,
            )
            if not written:
                lines.append("digest: no matching DataModelBinding instances\n")
                return 0, "".join(lines)
            for item in written:
                lines.append(
                    f"digest wrote {item.path.as_posix()} "
                    f"id={item.element_id or '-'} {item.digest}\n"
                )
            return 0, "".join(lines)

        matches, mismatches = verify_digests(root, model=model)
        for item in matches:
            lines.append(
                f"digest OK {item.path.as_posix()} "
                f"id={item.element_id or '-'} {item.digest}\n"
            )
        for item in mismatches:
            lines.append(f"digest FAIL {item.message}\n")
        if not matches and not mismatches:
            lines.append(
                "digest: no DataModelBinding instances with integrity_digest "
                "(see ADR-042 open question for solution models)\n"
            )
            return 0, "".join(lines)
        if mismatches:
            lines.append(f"digest FAILED ({len(mismatches)} mismatch(es))\n")
            return 1, "".join(lines)
        lines.append(f"digest OK ({len(matches)} binding(s))\n")
        return 0, "".join(lines)
    except Exception as exc:
        return 2, f"digest failed: {exc}\n"
