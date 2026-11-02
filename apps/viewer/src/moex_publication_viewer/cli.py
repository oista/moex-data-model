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
        help="Output directory (default: apps/viewer/dist)",
    )

    check_p = sub.add_parser("check", help="Validate manifests and build")
    check_p.add_argument("--root", type=Path, default=Path.cwd())
    check_p.add_argument("--dist", type=Path, default=None)

    build_user_p = sub.add_parser(
        "build-user-docs",
        help="Build docs/user/index.html (ADR-057)",
    )
    build_user_p.add_argument("--root", type=Path, default=Path.cwd())

    check_user_p = sub.add_parser(
        "check-user-docs",
        help="Validate docs/user sources and freshness (ADR-057)",
    )
    check_user_p.add_argument("--root", type=Path, default=Path.cwd())

    serve_p = sub.add_parser(
        "serve",
        help="Serve viewer on 127.0.0.1 with inline edit API",
    )
    serve_p.add_argument("--root", type=Path, default=Path.cwd())
    serve_p.add_argument("--dist", type=Path, default=None)
    serve_p.add_argument("--port", type=int, default=8765)
    serve_p.add_argument(
        "--open",
        action="store_true",
        help="Open the browser after start",
    )

    args = parser.parse_args(argv)

    if args.command == "serve":
        from moex_publication_viewer.serve import serve

        try:
            serve(
                args.root,
                dist_dir=args.dist,
                port=args.port,
                open_browser=args.open,
            )
        except ValidationError as exc:
            print("Serve failed:", file=sys.stderr)
            for err in exc.errors:
                print(f"  - {err}", file=sys.stderr)
            return 1
        except Exception as exc:
            print(f"Serve failed: {exc}", file=sys.stderr)
            return 1
        return 0

    if args.command == "build-user-docs":
        from moex_publication_viewer.user_docs import UserDocsError, build_user_docs

        try:
            index = build_user_docs(args.root)
        except UserDocsError as exc:
            print("build-user-docs failed:", file=sys.stderr)
            for err in exc.errors:
                print(f"  - {err}", file=sys.stderr)
            return 1
        except Exception as exc:
            print(f"build-user-docs failed: {exc}", file=sys.stderr)
            return 1
        print(f"Wrote {index}")
        return 0

    if args.command == "check-user-docs":
        from moex_publication_viewer.user_docs import check_user_docs

        errors, warnings = check_user_docs(args.root)
        for warning in warnings:
            print(f"warning: {warning}", file=sys.stderr)
        if errors:
            print("check-user-docs failed:", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            return 1
        print("check-user-docs OK")
        return 0

    # build and check share the same build path
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
