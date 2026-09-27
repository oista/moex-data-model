"""Small helpers that avoid importing standard-owl from application layer wrongly."""

from __future__ import annotations


def curie_guess(iri: str) -> str | None:
    """Best-effort CURIE-like short form for display (not a full prefix map)."""
    if "#" in iri:
        return iri.rsplit("#", 1)[-1] or None
    return iri.rstrip("/").rsplit("/", 1)[-1] or None
