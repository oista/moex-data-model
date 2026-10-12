"""moex-model check-manifest (ADR-047)."""

from __future__ import annotations

from pathlib import Path

from moex_repository_loader.check import run_checks


def run_check_manifest(repo_root: Path) -> tuple[int, str]:
    problems = run_checks(repo_root)
    if not problems:
        return 0, "check-manifest OK\n"
    lines = ["check-manifest FAILED:"]
    for p in problems:
        lines.append(f"  [{p.code}] {p.message}")
    return 1, "\n".join(lines) + "\n"
