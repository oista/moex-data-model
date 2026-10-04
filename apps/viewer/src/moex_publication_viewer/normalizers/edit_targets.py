"""Attach edit_targets to PublicationItems for YAML / LinkML sources."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from moex_publication_viewer.edits import make_edit_target
from moex_publication_viewer.models.publication_models import PublicationItem

_YAML_FIELDS = ("description", "title", "aliases")
_LINKML_FIELDS = ("description", "aliases")  # title == class name; not editable


def _file_abs(path: Path) -> str:
    return str(path.resolve())


def _aliases_value(record: dict[str, Any]) -> list[str]:
    raw = record.get("aliases")
    if isinstance(raw, list):
        return [str(x) for x in raw]
    if raw is None:
        return []
    return [str(raw)]


def _targets_for_record(
    *,
    file: str,
    yaml_path_prefix: str,
    record: dict[str, Any],
) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for field in _YAML_FIELDS:
        if field == "aliases":
            value: Any = _aliases_value(record)
        else:
            raw = record.get(field)
            value = "" if raw is None else str(raw)
        out[field] = make_edit_target(
            file=file,
            yaml_path=f"{yaml_path_prefix}.{field}",
            field=field,
            value=value,
        )
    return out


def attach_yaml_list_edit_targets(
    items: list[PublicationItem],
    *,
    source_path: Path,
    select: str | None,
    records: list[dict[str, Any]],
    key_column: str | None = None,
) -> list[PublicationItem]:
    """Stamp edit_targets onto items built from a YAML list select."""
    if not select or not isinstance(records, list):
        return items
    file = _file_abs(source_path)
    key = key_column or "element_id"
    by_key: dict[str, dict[str, Any]] = {}
    for rec in records:
        if not isinstance(rec, dict):
            continue
        kid = rec.get(key) or rec.get("element_id") or rec.get("id") or rec.get("name")
        if kid is not None:
            by_key[str(kid)] = rec

    def stamp(item: PublicationItem, parent_prefix: str | None = None) -> PublicationItem:
        rec = by_key.get(item.id)
        # Nested children (attributes) use nested path when parent_prefix set
        prefix = parent_prefix
        if rec is not None and prefix is None:
            # Prefer element_id key in path when present
            if rec.get("element_id") is not None:
                prefix = f"{select}[element_id={rec['element_id']}]"
            elif rec.get("id") is not None:
                prefix = f"{select}[id={rec['id']}]"
            else:
                prefix = f"{select}[{key}={item.id}]"

        edit_targets = None
        if rec is not None and prefix is not None:
            edit_targets = _targets_for_record(
                file=file, yaml_path_prefix=prefix, record=rec
            )

        new_children: list[PublicationItem] = []
        nested_list_key = None
        nested_records: list[dict[str, Any]] = []
        if rec is not None:
            for nk in ("attributes", "physical_fields"):
                raw = rec.get(nk)
                if isinstance(raw, list) and raw and isinstance(raw[0], dict):
                    nested_list_key = nk
                    nested_records = [x for x in raw if isinstance(x, dict)]
                    break

        nested_by_id = {
            str(r.get("element_id") or r.get("id") or r.get("name")): r
            for r in nested_records
            if r.get("element_id") or r.get("id") or r.get("name")
        }

        for child in item.children or []:
            if nested_list_key and child.id in nested_by_id and prefix:
                child_prefix = (
                    f"{prefix}.{nested_list_key}"
                    f"[element_id={nested_by_id[child.id].get('element_id', child.id)}]"
                )
                child_rec = nested_by_id[child.id]
                child_targets = _targets_for_record(
                    file=file, yaml_path_prefix=child_prefix, record=child_rec
                )
                new_children.append(
                    child.model_copy(
                        update={
                            "edit_targets": child_targets,
                            "children": [
                                stamp(gc) for gc in (child.children or [])
                            ],
                        }
                    )
                )
            else:
                new_children.append(stamp(child))

        return item.model_copy(
            update={"edit_targets": edit_targets, "children": new_children}
        )

    return [stamp(i) for i in items]


def relativize_edit_targets(item: PublicationItem, root: Path) -> PublicationItem:
    """Rewrite absolute ``file`` paths in edit_targets to root-relative posix."""
    root = root.resolve()

    def fix_map(targets: dict[str, dict[str, str]] | None) -> dict[str, dict[str, str]] | None:
        if not targets:
            return targets
        out: dict[str, dict[str, str]] = {}
        for field, et in targets.items():
            if not isinstance(et, dict) or "file" not in et:
                out[field] = et
                continue
            fp = Path(et["file"])
            try:
                rel = fp.resolve().relative_to(root).as_posix()
            except ValueError:
                rel = et["file"].replace("\\", "/")
            out[field] = {**et, "file": rel}
        return out

    kids = [relativize_edit_targets(c, root) for c in (item.children or [])]
    return item.model_copy(
        update={"edit_targets": fix_map(item.edit_targets), "children": kids}
    )


def relativize_module_edit_targets(modules: list[Any], root: Path) -> None:
    """In-place relativize edit_targets.file on all items."""
    for mod in modules:
        for sec in mod.sections:
            sec.items = [relativize_edit_targets(i, root) for i in (sec.items or [])]


def attach_linkml_edit_targets(
    items: list[PublicationItem],
    *,
    schema_dir: Path,
    source_file_for_key: Any,
) -> list[PublicationItem]:
    """Attach description/aliases edit_targets for LinkML class/enum/slot items.

    ``source_file_for_key(schema_key) -> filename`` relative to schema_dir.
    """

    def stamp(item: PublicationItem) -> PublicationItem:
        attrs = item.attributes or {}
        kind = attrs.get("kind")
        # Default bare SchemaView class items (no kind) to class
        if kind is None and attrs.get("schema_key"):
            kind = "slot" if "range" in attrs and "is_a" not in attrs else "class"
        kind = kind or "class"
        schema_key = attrs.get("schema_key")
        name = attrs.get("name") or item.id

        kids = [stamp(c) for c in (item.children or [])]

        # Skip groups, section folders, enum values, items without schema_key
        if kind in ("group", "enum_value", "section_ref", "implementation_ref"):
            return item.model_copy(update={"children": kids})
        if kind not in ("class", "enum", "slot") or not schema_key:
            return item.model_copy(update={"children": kids})

        filename = source_file_for_key(str(schema_key))
        file_path = (schema_dir / filename).resolve()
        if not file_path.is_file():
            alt = schema_dir / f"{str(schema_key).replace('_', '-')}.yaml"
            if alt.is_file():
                file_path = alt.resolve()
            else:
                return item.model_copy(update={"children": kids})

        file = _file_abs(file_path)
        collection = {"enum": "enums", "slot": "slots"}.get(kind, "classes")
        prefix = f"{collection}.{name}"
        targets: dict[str, dict[str, str]] = {}
        for field in _LINKML_FIELDS:
            if field == "description":
                value: Any = item.description or attrs.get("description") or ""
            else:
                raw = attrs.get("aliases")
                if isinstance(raw, list):
                    value = [str(x) for x in raw]
                elif raw is None:
                    value = []
                else:
                    value = [str(raw)]
            targets[field] = make_edit_target(
                file=file,
                yaml_path=f"{prefix}.{field}",
                field=field,
                value=value,
            )

        return item.model_copy(update={"edit_targets": targets, "children": kids})

    return [stamp(i) for i in items]
