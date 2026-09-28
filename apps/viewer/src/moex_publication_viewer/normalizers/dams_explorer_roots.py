"""Build DAMS Spec explorer roots: classes wrap, source files, ref graph."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from moex_publication_viewer.models.publication_models import PublicationItem


def is_dams_specification_dir(schema_path: Path) -> bool:
    """True when schema lives under …/moex-dams/…/schemas/ next to specification.yaml."""
    schemas_dir = schema_path.resolve().parent
    if schemas_dir.name != "schemas":
        return False
    return (schemas_dir.parent / "specification.yaml").is_file()


def _file_item_id(rel_path: str) -> str:
    return f"file:{rel_path.replace(chr(92), '/')}"


def _read_yaml_meta(path: Path) -> tuple[str | None, str | None, dict[str, Any]]:
    """Return (version, description, raw_mapping) best-effort."""
    text = path.read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(text)
    except Exception:
        return None, None, {}
    if not isinstance(data, dict):
        return None, None, {}
    version = data.get("version")
    if version is not None:
        version = str(version)
    description = data.get("description")
    if description is not None:
        description = str(description)
    return version, description, data


def _local_schema_file_id(import_ref: str, schemas_dir: Path) -> str | None:
    """Map a LinkML import path to a file:schemas/… id when local."""
    raw = import_ref.strip()
    if not raw or raw.startswith("http://") or raw.startswith("https://"):
        return None
    if ":" in raw and not raw.endswith(".yaml") and "/" not in raw.split(":", 1)[0]:
        # CURIE-like (e.g. linkml:types) — external
        if not raw.endswith(".yaml"):
            return None
    name = Path(raw).name
    if not name.endswith((".yaml", ".yml")):
        name = f"{name}.yaml"
    candidate = schemas_dir / name
    if candidate.is_file():
        return _file_item_id(f"schemas/{name}")
    # relative import from schemas/
    rel = (schemas_dir / raw).resolve()
    try:
        rel.relative_to(schemas_dir.resolve())
    except ValueError:
        return None
    if rel.is_file():
        return _file_item_id(f"schemas/{rel.name}")
    return None


def build_spec_file_items(spec_dir: Path) -> list[PublicationItem]:
    """
    Build source_file items for specification.yaml + schemas/*.yaml.

    Paths and ids are relative to ``spec_dir`` (moex-dams/0.1/).
    """
    spec_dir = spec_dir.resolve()
    schemas_dir = spec_dir / "schemas"
    entries: list[tuple[str, Path]] = []
    envelope = spec_dir / "specification.yaml"
    if not envelope.is_file():
        raise FileNotFoundError(f"missing specification.yaml under {spec_dir}")
    entries.append(("specification.yaml", envelope))
    if schemas_dir.is_dir():
        for path in sorted(schemas_dir.glob("*.yaml")):
            entries.append((f"schemas/{path.name}", path))

    # First pass: meta + text + provisional refs_out
    raw_by_id: dict[str, dict[str, Any]] = {}
    items_data: list[dict[str, Any]] = []
    for rel, path in entries:
        fid = _file_item_id(rel)
        version, description, data = _read_yaml_meta(path)
        text = path.read_text(encoding="utf-8")
        raw_by_id[fid] = data
        refs_out: list[str] = []
        if rel == "specification.yaml":
            for key in ("schema_body", "normative_sources"):
                val = data.get(key)
                targets = val if isinstance(val, list) else ([val] if val else [])
                for t in targets:
                    if not isinstance(t, str):
                        continue
                    t_norm = t.replace("\\", "/")
                    if t_norm.endswith((".yaml", ".yml")):
                        target_id = _file_item_id(t_norm)
                        if any(r == t_norm for r, _ in entries):
                            refs_out.append(target_id)
        else:
            imports = data.get("imports") or []
            if isinstance(imports, str):
                imports = [imports]
            for imp in imports:
                if not isinstance(imp, str):
                    continue
                local = _local_schema_file_id(imp, schemas_dir)
                if local:
                    refs_out.append(local)
        items_data.append(
            {
                "id": fid,
                "rel": rel,
                "path": path,
                "version": version,
                "description": description,
                "text": text,
                "refs_out": list(dict.fromkeys(refs_out)),
            }
        )

    known = {d["id"] for d in items_data}
    refs_in: dict[str, list[str]] = {i: [] for i in known}
    for d in items_data:
        for target in d["refs_out"]:
            if target in refs_in:
                refs_in[target].append(d["id"])

    items: list[PublicationItem] = []
    for d in items_data:
        name = Path(d["rel"]).name
        items.append(
            PublicationItem(
                id=d["id"],
                title=name,
                description=d["description"],
                attributes={
                    "kind": "source_file",
                    "path": d["rel"],
                    "version": d["version"],
                    "description": d["description"],
                    "text": d["text"],
                    "refs_out": d["refs_out"],
                    "refs_in": refs_in[d["id"]],
                },
            )
        )
    return items


def wrap_dams_explorer_roots(
    package_groups: list[PublicationItem],
    spec_dir: Path,
) -> list[PublicationItem]:
    """Wrap package groups under Классы / Спецификация (Реализации injected at build)."""
    class_count = sum(
        1
        for g in package_groups
        for c in g.children
        if (c.attributes or {}).get("kind") == "class"
    )
    classes_root = PublicationItem(
        id="group:classes",
        title="Классы",
        description="Пакеты схемы и классы/перечисления DAMS.",
        attributes={
            "kind": "group",
            "section_root": "classes",
            "purpose": "Навигация по классам и enum спецификации по пакетам схемы.",
            "structure_why": "Пакеты соответствуют LinkML-модулям DAMS; классы — тело TSpecBody.",
            "class_count": class_count,
            "enum_count": sum(
                1
                for g in package_groups
                for c in g.children
                if (c.attributes or {}).get("kind") == "enum"
            ),
            "member_ids": [g.id for g in package_groups],
        },
        children=package_groups,
    )

    file_items = build_spec_file_items(spec_dir)
    files_root = PublicationItem(
        id="group:spec-files",
        title="Спецификация",
        description="Нормативные YAML-файлы эталона DAMS.",
        attributes={
            "kind": "group",
            "section_root": "spec-files",
            "purpose": "Просмотр envelope и схем, составляющих reference specification.",
            "structure_why": "specification.yaml — дескриптор; schemas/* — нормативное тело LinkML.",
            "class_count": 0,
            "enum_count": 0,
            "member_ids": [f.id for f in file_items],
            "file_count": len(file_items),
        },
        children=file_items,
    )

    # Placeholder; build.py fills children from architecture catalog.
    impls_root = PublicationItem(
        id="group:implementations",
        title="Реализации",
        description="Specification implementations, registered against DAMS.",
        attributes={
            "kind": "group",
            "section_root": "implementations",
            "purpose": "Переход к зарегистрированным реализациям (conforms_to DAMS).",
            "structure_why": "Список из architecture-catalog; тела живут в своих модулях.",
            "class_count": 0,
            "enum_count": 0,
            "member_ids": [],
        },
        children=[],
    )
    return [classes_root, files_root, impls_root]
