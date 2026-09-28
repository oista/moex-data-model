"""CURIE ↔ URI expand/compact against a prefix map."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CurieUriResolver:
    """
    Expand and compact identifiers using LinkML-style prefixes.

    Prefix values should end with `/` or `#` (normalized on construction).
    Unknown prefixes yield None from expand; compact returns None when no
    prefix URI is a prefix of the absolute URI.
    """

    prefixes: dict[str, str]
    default_prefix: str | None = None

    def __post_init__(self) -> None:
        normalized = {
            str(k): _normalize_prefix_uri(str(v))
            for k, v in self.prefixes.items()
            if k and v
        }
        object.__setattr__(self, "prefixes", normalized)

    @classmethod
    def from_schema_prefixes(
        cls,
        prefixes: dict[str, str] | None,
        *,
        default_prefix: str | None = None,
    ) -> CurieUriResolver:
        return cls(prefixes=dict(prefixes or {}), default_prefix=default_prefix)

    def expand(self, value: str) -> str | None:
        """CURIE or absolute URI → absolute URI; None if CURIE prefix unknown."""
        text = (value or "").strip()
        if not text:
            return None
        if _is_absolute_uri(text):
            return text
        prefix, sep, local = text.partition(":")
        if not sep or not prefix or not local:
            if self.default_prefix and self.default_prefix in self.prefixes:
                return self.prefixes[self.default_prefix] + text
            return None
        base = self.prefixes.get(prefix)
        if base is None:
            return None
        return base + local

    def compact(self, uri: str) -> str | None:
        """Absolute URI → CURIE using longest matching prefix; else None."""
        text = (uri or "").strip()
        if not text:
            return None
        if not _is_absolute_uri(text):
            # Already a CURIE-like token — return if expandable.
            if self.expand(text) is not None:
                return text
            return None
        best_prefix: str | None = None
        best_base = ""
        for prefix, base in self.prefixes.items():
            if text.startswith(base) and len(base) > len(best_base):
                best_prefix = prefix
                best_base = base
        if best_prefix is None:
            return None
        return f"{best_prefix}:{text[len(best_base) :]}"

    def is_expandable(self, value: str) -> bool:
        return self.expand(value) is not None

    def unknown_prefix(self, value: str) -> str | None:
        """
        Return the CURIE prefix if value looks like a CURIE with unknown prefix.

        Absolute URIs and bare local names (no colon) return None.
        """
        text = (value or "").strip()
        if not text or _is_absolute_uri(text):
            return None
        prefix, sep, local = text.partition(":")
        if not sep or not prefix or not local:
            return None
        if prefix in self.prefixes:
            return None
        return prefix


def _normalize_prefix_uri(uri: str) -> str:
    return uri.strip()


def _is_absolute_uri(value: str) -> bool:
    lower = value.lower()
    return lower.startswith("http://") or lower.startswith("https://")


__all__ = ["CurieUriResolver"]
