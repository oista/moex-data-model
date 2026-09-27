"""Stubs for Stage-2 CLI surface not implemented yet (ADR-008/009)."""

from __future__ import annotations


def run_not_implemented(command: str) -> tuple[int, str]:
    return (
        2,
        f"moex-model {command}: not implemented yet "
        f"(see ADR-008/ADR-009 / IMPLEMENTATION_PLAN stage 2)\n",
    )
