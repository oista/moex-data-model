"""Seed term-file parser (IRI list for ROBOT extract)."""

from __future__ import annotations

from pathlib import Path


def parse_seed_iris(path: Path) -> tuple[str, ...]:
    """
    Parse a seed file: one IRI per line; blank lines and ``#`` comments ignored.
    """
    iris: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        iris.append(stripped)
    return tuple(iris)


def write_robot_term_file(iris: tuple[str, ...], dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(iris) + ("\n" if iris else ""), encoding="utf-8")
    return dest
