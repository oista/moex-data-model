#!/usr/bin/env python3
"""CLI wrapper for ADR-057 user-docs freshness check."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VIEWER_SRC = REPO_ROOT / "apps" / "viewer" / "src"
if str(VIEWER_SRC) not in sys.path:
    sys.path.insert(0, str(VIEWER_SRC))

from moex_publication_viewer.user_docs import main_check  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main_check())
