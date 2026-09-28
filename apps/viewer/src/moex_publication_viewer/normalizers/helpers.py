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
    skip = {"id", "title", "description", "children", "tags", "attributes", "source_ref"}
    attrs = {k: v for k, v in record.items() if k not in skip}
    nested = record.get("attributes")
    if isinstance(nested, dict):
        attrs = {**attrs, **nested}
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


def items_to_tree(
    items: list[PublicationItem],
    *,
    parent_attr: str = "parent_local_name",
) -> list[PublicationItem]:
    """Nest flat items using attributes[parent_attr]; unknown/empty parent → root."""
    by_id = {i.id: i for i in items}
    children_map: dict[str, list[str]] = {i.id: [] for i in items}
    roots: list[PublicationItem] = []
    for item in items:
        raw = (item.attributes or {}).get(parent_attr)
        parent = str(raw).strip() if raw not in (None, "") else ""
        if parent and parent in by_id and parent != item.id:
            children_map[parent].append(item.id)
        else:
            roots.append(item)

    def attach(node: PublicationItem) -> PublicationItem:
        kids = [attach(by_id[cid]) for cid in sorted(children_map.get(node.id, []))]
        return node.model_copy(update={"children": kids})

    return [attach(r) for r in sorted(roots, key=lambda i: i.id)]


def items_to_domain_explorer(
    items: list[PublicationItem],
    *,
    domain_attr: str = "source_domain",
    parent_attr: str = "parent_local_name",
) -> list[PublicationItem]:
    """Group flat items by domain_attr; nest by parent_attr within each domain."""
    by_domain: dict[str, list[PublicationItem]] = {}
    for item in items:
        raw = (item.attributes or {}).get(domain_attr)
        domain = str(raw).strip() if raw not in (None, "") else "unknown"
        enriched = item.model_copy(
            update={
                "attributes": {
                    **(item.attributes or {}),
                    "kind": (item.attributes or {}).get("kind") or "class",
                }
            }
        )
        by_domain.setdefault(domain, []).append(enriched)

    groups: list[PublicationItem] = []
    for domain in sorted(by_domain.keys()):
        domain_items = by_domain[domain]
        tree = items_to_tree(domain_items, parent_attr=parent_attr)
        groups.append(
            PublicationItem(
                id=f"group:{domain}",
                title=domain,
                description=f"Ontology domain {domain}",
                attributes={
                    "kind": "group",
                    "source_domain": domain,
                    "purpose": f"Classes in domain {domain} (preview).",
                    "class_count": len(domain_items),
                    "enum_count": 0,
                },
                children=tree,
            )
        )
    return groups


def section_meta(section) -> dict[str, Any]:
    """Common PublicationSection fields from a ManifestSection."""
    sort = getattr(section, "sort", None)
    return {
        "id": section.id,
        "title": section.title,
        "description": section.description,
        "type": section.type,
        "kind": getattr(section, "kind", None),
        "columns": section.columns,
        "filterable": section.filterable,
        "groupby": section.groupby,
        "sort_by": sort.by if sort else None,
        "sort_order": sort.order if sort else "asc",
        "tags": section.tags,
        "default_collapsed": section.default_collapsed,
    }
