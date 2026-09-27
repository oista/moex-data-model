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

# Display order and titles for DAMS schema packages (explorer groups)
_SCHEMA_GROUP_META: dict[str, tuple[int, str]] = {
    "moex_core": (10, "Core"),
    "moex-core": (10, "Core"),
    "moex_registries": (20, "Registries"),
    "moex-registries": (20, "Registries"),
    "moex_governance": (30, "Governance"),
    "moex-governance": (30, "Governance"),
    "moex_integration": (40, "Integration"),
    "moex-integration": (40, "Integration"),
    "moex_contract_binding": (50, "Contract binding"),
    "moex-contract-binding": (50, "Contract binding"),
    "moex_analytics": (60, "Analytics"),
    "moex-analytics": (60, "Analytics"),
    "moex_types": (70, "Types"),
    "moex-types": (70, "Types"),
    "moex_dams": (5, "Root"),
    "moex-dams": (5, "Root"),
}


def get_schema_view(source_path: Path) -> SchemaView:
    key = str(source_path.resolve())
    if key not in _VIEW_CACHE:
        _VIEW_CACHE[key] = SchemaView(str(source_path))
    return _VIEW_CACHE[key]


def clear_schema_view_cache() -> None:
    _VIEW_CACHE.clear()


def _group_title(schema_key: str) -> str:
    if schema_key in _SCHEMA_GROUP_META:
        return _SCHEMA_GROUP_META[schema_key][1]
    # moex_foo / moex-foo → Foo
    raw = schema_key.replace("moex_", "").replace("moex-", "").replace("_", " ").replace("-", " ")
    return raw.title() if raw else schema_key


def _group_order(schema_key: str) -> int:
    if schema_key in _SCHEMA_GROUP_META:
        return _SCHEMA_GROUP_META[schema_key][0]
    return 500


def _schema_key_for(sv: SchemaView, element_name: str) -> str:
    try:
        key = sv.in_schema(element_name)
        if key:
            return str(key)
    except Exception:
        pass
    return "unknown"


_SLOT_USAGE_FIELDS = (
    "required",
    "range",
    "multivalued",
    "inlined",
    "inlined_as_list",
    "identifier",
    "minimum_cardinality",
    "maximum_cardinality",
    "description",
)


def _declared_slot_names(cls: Any) -> list[str]:
    names: list[str] = []
    for slot_name in cls.slots or []:
        names.append(str(slot_name))
    return names


def _attributes_inline_names(cls: Any) -> list[str]:
    attrs = getattr(cls, "attributes", None) or {}
    return [str(name) for name in attrs.keys()]


def _declared_slot_set(cls: Any) -> set[str]:
    return set(_declared_slot_names(cls)) | set(_attributes_inline_names(cls))


def _compact_slot_usage(cls: Any) -> dict[str, dict[str, Any]]:
    usage = getattr(cls, "slot_usage", None) or {}
    out: dict[str, dict[str, Any]] = {}
    for slot_name, override in usage.items():
        if override is None:
            continue
        compact: dict[str, Any] = {}
        for field in _SLOT_USAGE_FIELDS:
            value = getattr(override, field, None)
            if value is not None and value != [] and value != {}:
                compact[field] = value
        if compact:
            out[str(slot_name)] = compact
    return out


def _class_identity_attrs(sv: SchemaView, name: str, cls: Any) -> dict[str, Any]:
    return {
        "name": name,
        "description": cls.description,
        "is_a": cls.is_a,
        "abstract": bool(cls.abstract) if cls.abstract is not None else False,
        "mixin": bool(cls.mixin) if getattr(cls, "mixin", None) is not None else False,
        "mixins": list(cls.mixins or []),
        "tree_root": bool(getattr(cls, "tree_root", False)),
        "class_uri": cls.class_uri,
        "from_schema": cls.from_schema,
        "schema_key": _schema_key_for(sv, name),
        "declared_slots": _declared_slot_names(cls),
        "attributes_inline": _attributes_inline_names(cls),
        "slot_usage": _compact_slot_usage(cls),
    }


def _induced_slot_dicts(sv: SchemaView, class_name: str) -> list[dict[str, Any]]:
    slots: list[dict[str, Any]] = []
    try:
        cls = sv.get_class(class_name)
    except Exception:
        cls = None
    declared = _declared_slot_set(cls) if cls is not None else set()
    try:
        induced = sv.class_induced_slots(class_name)
    except Exception:
        return slots
    for slot in induced:
        slots.append(
            {
                "name": slot.name,
                "description": slot.description,
                "range": slot.range,
                "required": bool(slot.required) if slot.required is not None else False,
                "multivalued": bool(slot.multivalued) if slot.multivalued is not None else False,
                "identifier": bool(slot.identifier) if getattr(slot, "identifier", None) is not None else False,
                "inlined": bool(slot.inlined) if getattr(slot, "inlined", None) is not None else False,
                "inlined_as_list": (
                    bool(slot.inlined_as_list)
                    if getattr(slot, "inlined_as_list", None) is not None
                    else False
                ),
                "minimum_cardinality": getattr(slot, "minimum_cardinality", None),
                "maximum_cardinality": getattr(slot, "maximum_cardinality", None),
                "inherited": slot.name not in declared,
                "slot_uri": slot.slot_uri,
            }
        )
    return slots


def _normalize_classes(sv: SchemaView, as_tree: bool) -> list[PublicationItem]:
    items_by_name: dict[str, PublicationItem] = {}
    for name, cls in sv.all_classes().items():
        items_by_name[name] = PublicationItem(
            id=name,
            title=name,
            description=cls.description,
            attributes=_class_identity_attrs(sv, name, cls),
        )

    if not as_tree:
        return sorted(items_by_name.values(), key=lambda i: i.id)

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
                attributes={
                    "name": name,
                    "description": enum.description,
                    "kind": "enum",
                    "from_schema": enum.from_schema,
                    "schema_key": _schema_key_for(sv, name),
                },
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


def _normalize_explorer(sv: SchemaView) -> list[PublicationItem]:
    """Group classes (and enums) by LinkML schema package — specification body projection."""
    by_schema: dict[str, list[PublicationItem]] = {}

    for name, cls in sv.all_classes().items():
        schema_key = _schema_key_for(sv, name)
        attrs = _class_identity_attrs(sv, name, cls)
        attrs["kind"] = "class"
        attrs["slots"] = _induced_slot_dicts(sv, name)
        item = PublicationItem(
            id=name,
            title=name,
            description=cls.description,
            attributes=attrs,
        )
        by_schema.setdefault(schema_key, []).append(item)

    for name, enum in sv.all_enums().items():
        schema_key = _schema_key_for(sv, name)
        children: list[PublicationItem] = []
        pvs = enum.permissible_values or {}
        for value_name, pv in pvs.items():
            desc = pv.description if pv is not None else None
            children.append(
                PublicationItem(
                    id=f"{name}:{value_name}",
                    title=str(value_name),
                    description=desc,
                    attributes={"name": str(value_name), "description": desc, "kind": "enum_value"},
                )
            )
        item = PublicationItem(
            id=name,
            title=name,
            description=enum.description,
            attributes={
                "kind": "enum",
                "name": name,
                "description": enum.description,
                "from_schema": enum.from_schema,
                "schema_key": schema_key,
            },
            children=children,
        )
        by_schema.setdefault(schema_key, []).append(item)

    groups: list[PublicationItem] = []
    for schema_key in sorted(by_schema.keys(), key=lambda k: (_group_order(k), k)):
        # Skip linkml builtin types package if it appears
        if schema_key.startswith("linkml"):
            continue
        children = sorted(by_schema[schema_key], key=lambda i: i.id)
        groups.append(
            PublicationItem(
                id=f"group:{schema_key}",
                title=_group_title(schema_key),
                description=f"Schema package {schema_key}",
                attributes={
                    "kind": "group",
                    "schema_key": schema_key,
                    "name": schema_key,
                },
                children=children,
            )
        )
    return groups


class LinkmlNormalizer:
    def normalize(self, section: ManifestSection, source_path: Path) -> PublicationSection:
        select = section.source.select or "classes"
        try:
            sv = get_schema_view(source_path)
        except Exception as exc:
            raise NormalizeError(f"cannot load LinkML schema {source_path}: {exc}") from exc

        as_tree = section.type == "tree"
        try:
            if section.type == "explorer":
                items = _normalize_explorer(sv)
                default_columns = ["name", "description", "kind"]
            elif select == "classes":
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
