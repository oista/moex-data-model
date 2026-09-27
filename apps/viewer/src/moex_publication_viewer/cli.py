"""CLI entrypoint."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from moex_publication_viewer.build import build
from moex_publication_viewer.validators import ValidationError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="moex-publication-viewer")
    sub = parser.add_subparsers(dest="command", required=True)

    build_p = sub.add_parser("build", help="Build static viewer HTML")
    build_p.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to scan for publish.yaml",
    )
    build_p.add_argument(
        "--dist",
        type=Path,
        default=None,
        help="Output directory (default: viewer/dist)",
    )

    check_p = sub.add_parser("check", help="Validate manifests and build")
    check_p.add_argument("--root", type=Path, default=Path.cwd())
    check_p.add_argument("--dist", type=Path, default=None)

    args = parser.parse_args(argv)
    try:
        index = build(args.root, args.dist)
    except ValidationError as exc:
        print("Build failed:", file=sys.stderr)
        for err in exc.errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {index}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
