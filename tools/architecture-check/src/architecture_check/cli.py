"""CLI entry for architecture pack checks."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from architecture_check.doc_consistency import check_docs
from architecture_check.kernel_policy import check_extension_policy


def _repo_root_from_here() -> Path:
    # tools/architecture-check/src/architecture_check/cli.py → repo root
    return Path(__file__).resolve().parents[4]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MOEX architecture pack checks")
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root (default: detect from package location)",
    )
    args = parser.parse_args(argv)
    root = (args.root or _repo_root_from_here()).resolve()

    kernel = root / "docs" / "architecture" / "modeling-kernel.yaml"
    docs_dir = root / "docs" / "architecture"
    dams = (
        root
        / "model-assets"
        / "specifications"
        / "moex-dams"
        / "0.1"
        / "schemas"
        / "moex-dams.yaml"
    )

    errors: list[str] = []
    if not kernel.is_file():
        errors.append(f"missing kernel schema: {kernel}")
    else:
        for name in check_extension_policy(kernel):
            errors.append(f"kernel_policy: {name}")

    if not docs_dir.is_dir():
        errors.append(f"missing docs dir: {docs_dir}")
    elif not dams.is_file():
        errors.append(f"missing DAMS schema: {dams}")
    else:
        for msg in check_docs(docs_dir, dams):
            errors.append(f"doc_consistency: {msg}")

    if errors:
        print("architecture-check FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print("architecture-check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
