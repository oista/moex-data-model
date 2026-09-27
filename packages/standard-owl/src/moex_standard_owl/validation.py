"""CLI / config validation helpers."""

from __future__ import annotations

from pathlib import Path

from moex_standard_owl.constants import (
    ALL_ENTITY_TYPES,
    DEFAULT_ENTITY_TYPES,
    DEFAULT_OUTPUT_FORMATS,
    OUTPUT_FORMATS,
)


class ValidationError(ValueError):
    """Invalid CLI arguments or source layout."""


def parse_csv_list(raw: str | None, *, default: tuple[str, ...]) -> list[str]:
    """Parse a comma-separated list; empty/None yields ``default``."""
    if raw is None or not raw.strip():
        return list(default)
    items = [part.strip() for part in raw.split(",") if part.strip()]
    if not items:
        return list(default)
    return items


def validate_entity_types(types: list[str]) -> list[str]:
    unknown = [t for t in types if t not in ALL_ENTITY_TYPES]
    if unknown:
        raise ValidationError(
            f"Unknown entity type(s): {', '.join(unknown)}. "
            f"Allowed: {', '.join(ALL_ENTITY_TYPES)}"
        )
    # Preserve order, drop duplicates
    seen: set[str] = set()
    result: list[str] = []
    for t in types:
        if t not in seen:
            seen.add(t)
            result.append(t)
    return result


def validate_formats(formats: list[str]) -> list[str]:
    unknown = [f for f in formats if f not in OUTPUT_FORMATS]
    if unknown:
        raise ValidationError(
            f"Unknown format(s): {', '.join(unknown)}. "
            f"Allowed: {', '.join(OUTPUT_FORMATS)}"
        )
    seen: set[str] = set()
    result: list[str] = []
    for f in formats:
        if f not in seen:
            seen.add(f)
            result.append(f)
    return result


def validate_source_path(source: Path) -> Path:
    path = source.expanduser().resolve()
    if not path.exists():
        raise ValidationError(f"Source path does not exist: {path}")
    if not path.is_dir():
        raise ValidationError(f"Source path is not a directory: {path}")
    return path


def validate_output_path(output: Path) -> Path:
    path = output.expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    if not path.is_dir():
        raise ValidationError(f"Output path is not a directory: {path}")
    return path


def validate_domains(domains: list[str], *, allowed: tuple[str, ...]) -> list[str]:
    allowed_set = set(allowed)
    unknown = [d for d in domains if d not in allowed_set]
    if unknown:
        raise ValidationError(
            f"Unknown domain(s): {', '.join(unknown)}. "
            f"Allowed: {', '.join(allowed)}"
        )
    seen: set[str] = set()
    result: list[str] = []
    for d in domains:
        if d not in seen:
            seen.add(d)
            result.append(d)
    return result


def default_types() -> list[str]:
    return list(DEFAULT_ENTITY_TYPES)


def default_formats() -> list[str]:
    return list(DEFAULT_OUTPUT_FORMATS)
