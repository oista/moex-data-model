"""LinkML YAML normalizer via SchemaView (resolves imports)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from linkml_runtime.utils.schemaview import SchemaView

from moex_publication_viewer.models.manifest_models import ManifestSection
from moex_publication_viewer.models.publication_models import PublicationItem, PublicationSection
from moex_publication_viewer.normalizers.base import NormalizeError
from moex_publication_viewer.normalizers.helpers import section_meta

# Cache SchemaView per absolute path for one build process
_VIEW_CACHE: dict[str, SchemaView] = {}


def get_schema_view(source_path: Path) -> SchemaView:
    key = str(source_path.resolve())
    if key not in _VIEW_CACHE:
        _VIEW_CACHE[key] = SchemaView(str(source_path))
    return _VIEW_CACHE[key]


def clear_schema_view_cache() -> None:
    _VIEW_CACHE.clear()


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _normalize_classes(sv: SchemaView, as_tree: bool) -> list[PublicationItem]:
    items_by_name: dict[str, PublicationItem] = {}
    for name, cls in sv.all_classes().items():
        items_by_name[name] = PublicationItem(
            id=name,
            title=name,
            description=cls.description,
            attributes={
                "name": name,
                "description": cls.description,
                "is_a": cls.is_a,
                "abstract": bool(cls.abstract) if cls.abstract is not None else False,
                "mixins": list(cls.mixins or []),
                "class_uri": cls.class_uri,
            },
        )

    if not as_tree:
        return sorted(items_by_name.values(), key=lambda i: i.id)

    # Build parent → children via is_a
    roots: list[PublicationItem] = []
    children_map: dict[str, list[str]] = {n: [] for n in items_by_name}
    for name, item in items_by_name.items():
        parent = item.attributes.get("is_a")
        if parent and parent in items_by_name:
            children_map[parent].append(name)
        else:
            roots.append(item)

    def attach(node: PublicationItem) -> PublicationItem:
        kids = [
            attach(items_by_name[child_name])
            for child_name in sorted(children_map.get(node.id, []))
        ]
        return node.model_copy(update={"children": kids})

    return [attach(r) for r in sorted(roots, key=lambda i: i.id)]


def _normalize_slots(sv: SchemaView) -> list[PublicationItem]:
    items: list[PublicationItem] = []
    for name, slot in sv.all_slots().items():
        items.append(
            PublicationItem(
                id=name,
                title=name,
                description=slot.description,
                attributes={
                    "name": name,
                    "description": slot.description,
                    "range": slot.range,
                    "required": bool(slot.required) if slot.required is not None else False,
                    "multivalued": bool(slot.multivalued) if slot.multivalued is not None else False,
                    "slot_uri": slot.slot_uri,
                },
            )
        )
    return sorted(items, key=lambda i: i.id)


def _normalize_enums(sv: SchemaView) -> list[PublicationItem]:
    items: list[PublicationItem] = []
    for name, enum in sv.all_enums().items():
        children: list[PublicationItem] = []
        pvs = enum.permissible_values or {}
        for value_name, pv in pvs.items():
            desc = pv.description if pv is not None else None
            children.append(
                PublicationItem(
                    id=str(value_name),
                    title=str(value_name),
                    description=desc,
                    attributes={"name": str(value_name), "description": desc},
                )
            )
        items.append(
            PublicationItem(
                id=name,
                title=name,
                description=enum.description,
                attributes={"name": name, "description": enum.description},
                children=children,
            )
        )
    return sorted(items, key=lambda i: i.id)


def _normalize_types(sv: SchemaView) -> list[PublicationItem]:
    items: list[PublicationItem] = []
    for name, typ in sv.all_types().items():
        items.append(
            PublicationItem(
                id=name,
                title=name,
                description=getattr(typ, "description", None),
                attributes={
                    "name": name,
                    "description": getattr(typ, "description", None),
                    "base": getattr(typ, "base", None),
                    "uri": getattr(typ, "uri", None),
                },
            )
        )
    return sorted(items, key=lambda i: i.id)


class LinkmlNormalizer:
    def normalize(self, section: ManifestSection, source_path: Path) -> PublicationSection:
        select = section.source.select or "classes"
        try:
            sv = get_schema_view(source_path)
        except Exception as exc:
            raise NormalizeError(f"cannot load LinkML schema {source_path}: {exc}") from exc

        as_tree = section.type == "tree"
        try:
            if select == "classes":
                items = _normalize_classes(sv, as_tree=as_tree)
                default_columns = ["name", "description", "is_a", "abstract", "mixins"]
            elif select == "slots":
                items = _normalize_slots(sv)
                default_columns = ["name", "description", "range", "required", "multivalued"]
            elif select == "enums":
                items = _normalize_enums(sv)
                default_columns = ["name", "description"]
            elif select == "types":
                items = _normalize_types(sv)
                default_columns = ["name", "description", "base"]
            else:
                raise NormalizeError(
                    f"unsupported linkml-yaml select '{select}' "
                    "(expected classes|slots|enums|types)"
                )
        except NormalizeError:
            raise
        except Exception as exc:
            raise NormalizeError(f"failed to normalize LinkML select={select}: {exc}") from exc

        return PublicationSection(
            **{**section_meta(section), "columns": section.columns or default_columns},
            items=items,
        )
