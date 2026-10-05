"""Shared helpers for Mermaid erDiagram and ER scene projections."""

from __future__ import annotations

from typing import Any

from moex_dams.projection.dbml import _ident

MANY = 999999


def unique_table_name(raw: str | None, *, fallback: str, used: set[str]) -> str:
    tname = _ident(raw, fallback=fallback)
    base = tname
    n = 2
    while tname in used:
        tname = f"{base}_{n}"
        n += 1
    used.add(tname)
    return tname


def is_many(max_card: Any) -> bool:
    if max_card is None:
        return True
    try:
        return int(max_card) > 1
    except (TypeError, ValueError):
        return True


def is_optional(min_card: Any) -> bool:
    if min_card is None:
        return True
    try:
        return int(min_card) == 0
    except (TypeError, ValueError):
        return True


def attr_keys_for_entity(entity: dict[str, Any]) -> set[str]:
    keys: set[str] = set()
    for ref in entity.get("key_attribute_refs") or []:
        keys.add(str(ref))
    return keys


def fk_roles_for_entity(
    entity_id: str, relationships: list[dict[str, Any]]
) -> set[str]:
    roles: set[str] = set()
    for rel in relationships:
        if str(rel.get("source_entity_ref") or "") != entity_id:
            continue
        role = rel.get("source_role")
        if role:
            roles.add(str(role))
    return roles


def relation_term_label(
    rel: dict[str, Any], terms_by_id: dict[str, dict[str, Any]]
) -> str:
    """Prefer RelationTerm forward/inverse label; fall back to relationship name."""
    term = terms_by_id.get(str(rel.get("relation_term_ref") or ""))
    direction = str(rel.get("term_direction") or "forward").lower()
    if term:
        if direction == "inverse":
            for key in ("inverse_label", "inverse_label_en", "title", "name"):
                val = term.get(key)
                if val:
                    return str(val)
        else:
            for key in ("forward_label", "forward_label_en", "title", "name"):
                val = term.get(key)
                if val:
                    return str(val)
    for key in ("title", "name"):
        val = rel.get(key)
        if val:
            return str(val)
    return "rel"


def cardinality_kind(
    *,
    min_card: Any,
    max_card: Any,
) -> str:
    """Return crow's-foot kind: onlyOne | zeroOrOne | oneOrMore | zeroOrMore."""
    many = is_many(max_card)
    opt = is_optional(min_card)
    if many:
        return "zeroOrMore" if opt else "oneOrMore"
    return "zeroOrOne" if opt else "onlyOne"
