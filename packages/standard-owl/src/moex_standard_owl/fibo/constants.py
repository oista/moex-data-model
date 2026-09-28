"""FIBO-specific constants."""

from __future__ import annotations

DEFAULT_RELEASE = "master_2026Q2"

DEFAULT_DOMAINS: tuple[str, ...] = (
    "FND",
    "BE",
    "FBC",
    "SEC",
    "DER",
    "LOAN",
    "IND",
    "MD",
    "BP",
    "CAE",
    "ACTUS",
)

# Domains allowed via --domains (includes EXMP for explicit opt-in)
ALL_DOMAINS: tuple[str, ...] = DEFAULT_DOMAINS + ("EXMP",)

EXAMPLES_DOMAIN = "EXMP"

SKIP_DIR_NAMES: frozenset[str] = frozenset(
    {
        ".github",
        "etc",
        ".git",
        "__pycache__",
        ".venv",
        "venv",
    }
)

UPSTREAM_URL = "https://github.com/edmcouncil/fibo"
