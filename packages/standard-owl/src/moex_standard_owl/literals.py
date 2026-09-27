"""Helpers for selecting and joining RDF literals by language preference."""

from __future__ import annotations

from collections.abc import Iterable

from rdflib import Literal
from rdflib.term import Node

from moex_standard_owl.constants import DEFINITION_JOIN, LABEL_JOIN


def _lang(literal: Literal) -> str | None:
    lang = literal.language
    if lang is None:
        return None
    return lang.lower()


def preferred_literal_values(
    nodes: Iterable[Node],
    *,
    join: str = LABEL_JOIN,
) -> tuple[str | None, str | None]:
    """
    Pick preferred literal text(s) from RDF nodes.

    Preference order within available literals:
    1. English (@en / @en-*)
    2. Language-neutral (no language tag)
    3. Any other language (only if neither 1 nor 2 exist)

    Multiple values at the chosen preference level are joined uniquely
    with ``join``, preserving first-seen order.
    """
    literals = [n for n in nodes if isinstance(n, Literal)]
    if not literals:
        return None, None

    en: list[Literal] = []
    neutral: list[Literal] = []
    other: list[Literal] = []
    for lit in literals:
        lang = _lang(lit)
        if lang is None:
            neutral.append(lit)
        elif lang == "en" or lang.startswith("en-"):
            en.append(lit)
        else:
            other.append(lit)

    chosen: list[Literal]
    lang_tag: str | None
    if en:
        chosen = en
        lang_tag = "en"
    elif neutral:
        chosen = neutral
        lang_tag = None
    else:
        chosen = other
        # Report the languages that were used (unique, sorted for stability)
        langs = sorted({_lang(x) or "" for x in chosen})
        lang_tag = "|".join(langs) if langs else None

    values: list[str] = []
    seen: set[str] = set()
    for lit in chosen:
        text = str(lit).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        values.append(text)

    if not values:
        return None, lang_tag
    return join.join(values), lang_tag


def join_unique(values: Iterable[str | None], sep: str) -> str | None:
    """Join unique non-empty strings preserving first-seen order."""
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value is None:
            continue
        text = value.strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    if not result:
        return None
    return sep.join(result)


def join_definitions(values: Iterable[str]) -> str | None:
    return join_unique(values, DEFINITION_JOIN)


def join_labels(values: Iterable[str]) -> str | None:
    return join_unique(values, LABEL_JOIN)
