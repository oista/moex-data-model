"""Shared helpers for turning records into PublicationItem."""

from __future__ import annotations

from typing import Any

from moex_publication_viewer.models.publication_models import PublicationItem, PublicationSection


def select_path(data: Any, select: str | None) -> Any:
    if not select:
        return data
    current = data
    for part in select.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            raise KeyError(f"select path '{select}' not found (failed at '{part}')")
    return current


def dict_to_item(
    record: dict[str, Any],
    *,
    key_column: str | None = None,
    index: int = 0,
) -> PublicationItem:
    key = key_column or "id"
    item_id = str(record.get(key) or record.get("name") or record.get("title") or f"row-{index}")
    title = record.get("title") or record.get("label") or record.get("name")
    description = record.get("description") or record.get("definition")
    attrs = {k: v for k, v in record.items() if k not in {"id", "title", "description", "children", "tags"}}
    tags = record.get("tags") or []
    if not isinstance(tags, list):
        tags = [str(tags)]
    children_raw = record.get("children") or []
    children = [
        dict_to_item(c, key_column=key_column, index=i)
        for i, c in enumerate(children_raw)
        if isinstance(c, dict)
    ]
    return PublicationItem(
        id=item_id,
        title=str(title) if title is not None else None,
        description=str(description) if description is not None else None,
        attributes=attrs,
        children=children,
        tags=[str(t) for t in tags],
        source_ref=str(record["source_ref"]) if record.get("source_ref") else None,
    )


def records_to_items(
    data: Any,
    *,
    key_column: str | None = None,
) -> list[PublicationItem]:
    if isinstance(data, list):
        items: list[PublicationItem] = []
        for i, row in enumerate(data):
            if isinstance(row, dict):
                items.append(dict_to_item(row, key_column=key_column, index=i))
            else:
                items.append(PublicationItem(id=f"row-{i}", title=str(row)))
        return items
    if isinstance(data, dict):
        # key-value object → one item per key, or treat as single record
        if all(isinstance(v, (str, int, float, bool, type(None))) for v in data.values()):
            return [
                PublicationItem(id=str(k), title=str(k), description=None, attributes={"value": v})
                for k, v in data.items()
            ]
        return [dict_to_item(data, key_column=key_column)]
    return [PublicationItem(id="value", title=str(data))]


def section_meta(section) -> dict[str, Any]:
    """Common PublicationSection fields from a ManifestSection."""
    sort = getattr(section, "sort", None)
    return {
        "id": section.id,
        "title": section.title,
        "description": section.description,
        "type": section.type,
        "columns": section.columns,
        "filterable": section.filterable,
        "groupby": section.groupby,
        "sort_by": sort.by if sort else None,
        "sort_order": sort.order if sort else "asc",
        "tags": section.tags,
        "default_collapsed": section.default_collapsed,
    }
