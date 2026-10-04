"""Normalize codes from Object/ObjectAttribute cells."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NormResult:
    raw: str | None
    value: str | None
    changed: bool
    had_nbsp: bool
    had_whitespace: bool


def normalize_code(raw: object | None) -> NormResult:
    """Trim, replace NBSP, collapse outer whitespace. Preserve inner spelling."""
    if raw is None:
        return NormResult(raw=None, value=None, changed=False, had_nbsp=False, had_whitespace=False)
    text = str(raw)
    had_nbsp = "\xa0" in text or "\u00a0" in text
    cleaned = text.replace("\xa0", " ").replace("\u00a0", " ")
    stripped = cleaned.strip()
    had_whitespace = stripped != text.replace("\xa0", " ").replace("\u00a0", " ") or (
        cleaned != stripped
    )
    # Also treat leading/trailing ordinary spaces on original as whitespace issue
    if text != text.strip() or had_nbsp:
        had_whitespace = True
    value = stripped or None
    changed = value != text if value is not None else text != ""
    if value is None and not text.strip().replace("\xa0", "").replace("\u00a0", ""):
        changed = bool(text)
    return NormResult(
        raw=text if text != "" else None,
        value=value,
        changed=bool(value is not None and value != text),
        had_nbsp=had_nbsp,
        had_whitespace=had_whitespace and value is not None,
    )


def match_key(value: str | None) -> str | None:
    """Casefold key for object/attribute matching."""
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    return text.casefold()
