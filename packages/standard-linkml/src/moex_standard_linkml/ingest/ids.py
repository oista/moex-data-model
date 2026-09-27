"""Deterministic CURIE builders for ingested DAMS elements."""

from __future__ import annotations

import re


_SAFE = re.compile(r"[^A-Za-z0-9_.\-]+")


def slugify(value: str) -> str:
    text = value.strip()
    if not text:
        raise ValueError("Cannot slugify empty value")
    # Preserve CamelCase entity names; only scrub unsafe chars
    cleaned = _SAFE.sub("_", text)
    cleaned = cleaned.strip("_")
    if not cleaned:
        raise ValueError(f"Cannot slugify value: {value!r}")
    return cleaned


def concept_id(prefix: str, entity_name: str) -> str:
    return f"{prefix}:concept/{slugify(entity_name)}"


def context_id(prefix: str, slug: str) -> str:
    return f"{prefix}:context/{slugify(slug)}"


def logical_entity_id(prefix: str, slug: str, entity_name: str) -> str:
    return f"{prefix}:logical/{slugify(slug)}/{slugify(entity_name)}"


def logical_attr_id(
    prefix: str, slug: str, entity_name: str, attr_name: str
) -> str:
    return (
        f"{prefix}:logical/{slugify(slug)}/"
        f"{slugify(entity_name)}/{slugify(attr_name)}"
    )


def relationship_id(prefix: str, slug: str, rel_name: str) -> str:
    return f"{prefix}:rel/{slugify(slug)}/{slugify(rel_name)}"


def package_id(prefix: str, slug: str, version: str) -> str:
    return f"{prefix}:model/{slugify(slug)}/{version}"


def physical_object_id(prefix: str, slug: str, object_name: str) -> str:
    return f"{prefix}:physical/{slugify(slug)}/{slugify(object_name)}"


def physical_field_id(
    prefix: str, slug: str, object_name: str, field_name: str
) -> str:
    return (
        f"{prefix}:physical/{slugify(slug)}/"
        f"{slugify(object_name)}/{slugify(field_name)}"
    )


def mapping_id(prefix: str, slug: str, mapping_name: str) -> str:
    return f"{prefix}:mapping/{slugify(slug)}/{slugify(mapping_name)}"
