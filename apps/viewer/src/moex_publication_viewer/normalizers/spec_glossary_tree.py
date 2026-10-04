"""Overview Glossary tree: definition-site folders + class/enum leaves (ADR-024/027).

Folders group by where a term is defined (schema package / domain→module).
Hierarchy (is_a / subClassOf) stays on the card Taxonomy block and under Classes —
never as folder edges. See also is derived from the native graph, never authored.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from linkml_runtime.utils.schemaview import SchemaView

from moex_publication_viewer.models.publication_models import PublicationItem

GLOSSARY_LEAF_PREFIX = "glossary:"
OVERVIEW_GLOSSARY_ID = "group:overview-glossary"


def glossary_leaf_id(canonical_id: str) -> str:
    cid = str(canonical_id).strip()
    if cid.startswith(GLOSSARY_LEAF_PREFIX):
        return cid
    return f"{GLOSSARY_LEAF_PREFIX}{cid}"


def canonical_term_id(node_id: str) -> str:
    raw = str(node_id or "").strip()
    if raw.startswith(GLOSSARY_LEAF_PREFIX):
        return raw[len(GLOSSARY_LEAF_PREFIX) :]
    return raw


def _section_ref(section_id: str, title: str) -> PublicationItem:
    return PublicationItem(
        id=f"section:{section_id}",
        title=title,
        description=f"Open publication section «{title}».",
        attributes={
            "kind": "section_ref",
            "section_id": section_id,
            "description": f"Open publication section «{title}».",
        },
    )


def _schema_key_for(sv: SchemaView, element_name: str) -> str:
    try:
        key = sv.in_schema(element_name)
        if key:
            return str(key)
    except Exception:
        pass
    return "unknown"


def _is_linkml_builtin_key(schema_key: str) -> bool:
    return schema_key.startswith("linkml")


def _origin_for_schema(
    sv: SchemaView,
    element_name: str,
    schema_key: str,
    spec_dir: Path | None,
) -> str:
    """own if element is declared in a YAML under spec_dir; else imported."""
    if _is_linkml_builtin_key(schema_key):
        return "imported"
    if spec_dir is None:
        return "own"
    try:
        # SchemaView.source_file / schema map — prefer concrete file when available
        from_schema = None
        cls = sv.get_class(element_name)
        if cls is not None:
            from_schema = getattr(cls, "from_schema", None)
        if from_schema is None:
            enum = sv.get_enum(element_name)
            if enum is not None:
                from_schema = getattr(enum, "from_schema", None)
        # Resolve schema key → relative path heuristic
        key = schema_key.replace("_", "-")
        candidates = [
            spec_dir / "schemas" / f"{key}.yaml",
            spec_dir / "schemas" / f"{schema_key}.yaml",
            spec_dir / f"{key}.yaml",
        ]
        for cand in candidates:
            if cand.is_file():
                return "own"
        # If from_schema URI/path points inside spec_dir
        if from_schema:
            fs = str(from_schema).replace("\\", "/")
            spec_s = str(spec_dir.resolve()).replace("\\", "/")
            if spec_s in fs or fs.endswith(f"/{key}.yaml") or f"/schemas/{key}" in fs:
                return "own"
            if "linkml" in fs.lower():
                return "imported"
        # Declared in a non-builtin schema package of this SchemaView → treat as own
        if schema_key and not _is_linkml_builtin_key(schema_key):
            return "own"
    except Exception:
        pass
    return "imported"


def _is_a_chain(sv: SchemaView, class_name: str, known: set[str]) -> list[str]:
    chain: list[str] = []
    seen: set[str] = set()
    current = class_name
    while True:
        try:
            cls = sv.get_class(current)
        except Exception:
            break
        if cls is None:
            break
        parent = getattr(cls, "is_a", None)
        if not parent or parent in seen:
            break
        parent_s = str(parent)
        if parent_s not in known:
            break
        chain.append(parent_s)
        seen.add(parent_s)
        current = parent_s
    return chain


def _rel_entry(target_id: str, rel: str) -> dict[str, str]:
    return {"id": str(target_id), "rel": rel}


def build_linkml_glossary_leaves(
    sv: SchemaView,
    *,
    spec_dir: Path | None = None,
    include_enums: bool = True,
) -> list[PublicationItem]:
    """Flat class (+ optional enum) leaves with ADR-027 taxonomy / see_also / origin."""
    class_names = {
        name
        for name in sv.all_classes()
        if not _is_linkml_builtin_key(_schema_key_for(sv, name))
    }
    enum_names: set[str] = set()
    if include_enums:
        enum_names = {
            name
            for name in sv.all_enums()
            if not _is_linkml_builtin_key(_schema_key_for(sv, name))
        }
    coverage = class_names | enum_names

    # subclasses via is_a
    children_map: dict[str, list[str]] = {n: [] for n in class_names}
    for name in class_names:
        try:
            cls = sv.get_class(name)
        except Exception:
            continue
        parent = getattr(cls, "is_a", None) if cls is not None else None
        if parent and str(parent) in children_map:
            children_map[str(parent)].append(name)

    # see_also from slot ranges (symmetric), excluding taxonomy edges
    see_also_map: dict[str, set[tuple[str, str]]] = {n: set() for n in coverage}

    def add_see(a: str, b: str, rel: str) -> None:
        if a == b or a not in coverage or b not in coverage:
            return
        # Never put parent/child (is_a) into see_also
        if b in children_map.get(a, []) or a in children_map.get(b, []):
            return
        try:
            cls_a = sv.get_class(a) if a in class_names else None
        except Exception:
            cls_a = None
        if cls_a is not None:
            if str(getattr(cls_a, "is_a", None) or "") == b:
                return
            if b in [str(m) for m in (cls_a.mixins or [])]:
                return
        try:
            cls_b = sv.get_class(b) if b in class_names else None
        except Exception:
            cls_b = None
        if cls_b is not None:
            if str(getattr(cls_b, "is_a", None) or "") == a:
                return
            if a in [str(m) for m in (cls_b.mixins or [])]:
                return
        see_also_map.setdefault(a, set()).add((b, rel))
        see_also_map.setdefault(b, set()).add((a, rel))

    for name in class_names:
        try:
            slots = sv.class_induced_slots(name)
        except Exception:
            slots = []
        for slot in slots or []:
            rng = getattr(slot, "range", None)
            if not rng:
                continue
            rng_s = str(rng)
            if rng_s in coverage:
                add_see(name, rng_s, f"range:{slot.name}")

    leaves: list[PublicationItem] = []
    for name in sorted(class_names):
        try:
            cls = sv.get_class(name)
        except Exception:
            cls = None
        schema_key = _schema_key_for(sv, name)
        mixins = [str(m) for m in (getattr(cls, "mixins", None) or []) if str(m) in coverage]
        is_a = str(getattr(cls, "is_a", None) or "") or None
        if is_a and is_a not in coverage:
            is_a = None
        parents = []
        if is_a:
            parents.append(_rel_entry(is_a, "is_a"))
        for m in mixins:
            parents.append(_rel_entry(m, "mixin"))
        chain = _is_a_chain(sv, name, class_names)
        children = [
            _rel_entry(c, "subclass") for c in sorted(children_map.get(name, []))
        ]
        see_also = [
            _rel_entry(tid, rel)
            for tid, rel in sorted(see_also_map.get(name, set()), key=lambda x: x[0])
        ]
        origin = _origin_for_schema(sv, name, schema_key, spec_dir)
        attrs: dict[str, Any] = {
            "kind": "class",
            "name": name,
            "schema_key": schema_key,
            "from_schema": getattr(cls, "from_schema", None) if cls else None,
            "is_a": is_a,
            "mixins": mixins,
            "defined_in": schema_key,
            "is_a_chain": chain,
            "definition_depth": len(chain),
            "origin": origin,
            "taxonomy_parents": parents,
            "taxonomy_children": children,
            "see_also": see_also,
            "glossary_view": True,
        }
        leaves.append(
            PublicationItem(
                id=glossary_leaf_id(name),
                title=name,
                description=getattr(cls, "description", None) if cls else None,
                attributes=attrs,
            )
        )

    for name in sorted(enum_names):
        try:
            enum = sv.get_enum(name)
        except Exception:
            enum = None
        schema_key = _schema_key_for(sv, name)
        see_also = [
            _rel_entry(tid, rel)
            for tid, rel in sorted(see_also_map.get(name, set()), key=lambda x: x[0])
        ]
        origin = _origin_for_schema(sv, name, schema_key, spec_dir)
        attrs = {
            "kind": "enum",
            "name": name,
            "schema_key": schema_key,
            "from_schema": getattr(enum, "from_schema", None) if enum else None,
            "defined_in": schema_key,
            "is_a_chain": [],
            "definition_depth": 0,
            "origin": origin,
            "taxonomy_parents": [],
            "taxonomy_children": [],
            "see_also": see_also,
            "glossary_view": True,
        }
        leaves.append(
            PublicationItem(
                id=glossary_leaf_id(name),
                title=name,
                description=getattr(enum, "description", None) if enum else None,
                attributes=attrs,
            )
        )
    return leaves


def group_linkml_leaves_by_schema(leaves: list[PublicationItem]) -> list[PublicationItem]:
    """One section_folder per schema_key; leaves sorted by title."""
    by_key: dict[str, list[PublicationItem]] = {}
    for leaf in leaves:
        key = str((leaf.attributes or {}).get("schema_key") or "unknown")
        by_key.setdefault(key, []).append(leaf)
    folders: list[PublicationItem] = []
    for key in sorted(by_key.keys()):
        kids = sorted(by_key[key], key=lambda i: (i.title or i.id).lower())
        folders.append(
            PublicationItem(
                id=f"group:glossary-site:{key}",
                title=key.replace("_", "-"),
                description=f"Terms defined in schema package «{key}».",
                attributes={
                    "kind": "group",
                    "group_style": "section_folder",
                    "definition_site": key,
                    "schema_key": key,
                    "purpose": f"Definition site: {key}",
                    "member_ids": [c.id for c in kids],
                    "class_count": sum(
                        1 for c in kids if (c.attributes or {}).get("kind") == "class"
                    ),
                    "enum_count": sum(
                        1 for c in kids if (c.attributes or {}).get("kind") == "enum"
                    ),
                },
                children=kids,
            )
        )
    return folders


def build_linkml_glossary_tree(
    sv: SchemaView,
    *,
    spec_dir: Path | None = None,
    include_enums: bool = True,
) -> list[PublicationItem]:
    """Definition-site folders for LinkML specification Overview → Glossary."""
    leaves = build_linkml_glossary_leaves(
        sv, spec_dir=spec_dir, include_enums=include_enums
    )
    return group_linkml_leaves_by_schema(leaves)


def flat_glossary_items_from_leaves(leaves: list[PublicationItem]) -> list[PublicationItem]:
    """A–Z section rows: canonical ids (no glossary: prefix), same attrs."""
    rows: list[PublicationItem] = []
    for leaf in leaves:
        cid = canonical_term_id(leaf.id)
        attrs = dict(leaf.attributes or {})
        rows.append(
            PublicationItem(
                id=cid,
                title=leaf.title or cid,
                description=leaf.description,
                attributes=attrs,
                children=[],
            )
        )
    return sorted(rows, key=lambda i: (i.title or i.id).lower())


def build_ontology_glossary_tree(items: list[PublicationItem]) -> list[PublicationItem]:
    """FIBO-style folders: source_domain → optional module_path → class leaves.

    Does not nest by subClassOf (that stays under Classes). See also is empty
    until object properties exist (ADR-027).
    """
    # Index parents/children within the set
    by_id = {i.id: i for i in items}
    children_map: dict[str, list[str]] = {i.id: [] for i in items}
    for item in items:
        parent = str((item.attributes or {}).get("parent_local_name") or "").strip()
        if parent and parent in by_id and parent != item.id:
            children_map[parent].append(item.id)

    def depth_of(item_id: str) -> int:
        depth = 0
        seen: set[str] = set()
        current = item_id
        while current not in seen:
            seen.add(current)
            node = by_id.get(current)
            if node is None:
                break
            parent = str((node.attributes or {}).get("parent_local_name") or "").strip()
            if not parent or parent not in by_id:
                break
            depth += 1
            current = parent
        return depth

    def chain_of(item_id: str) -> list[str]:
        chain: list[str] = []
        seen: set[str] = set()
        current = item_id
        while current not in seen:
            seen.add(current)
            node = by_id.get(current)
            if node is None:
                break
            parent = str((node.attributes or {}).get("parent_local_name") or "").strip()
            if not parent or parent not in by_id:
                break
            chain.append(parent)
            current = parent
        return chain

    # domain → module_path → leaves
    nested: dict[str, dict[str, list[PublicationItem]]] = {}
    for item in items:
        attrs = dict(item.attributes or {})
        domain = str(attrs.get("source_domain") or "unknown").strip() or "unknown"
        module_path = str(attrs.get("module_path") or "").strip()
        parent = str(attrs.get("parent_local_name") or "").strip()
        parents = [_rel_entry(parent, "subClassOf")] if parent else []
        children = [
            _rel_entry(c, "subClassOf") for c in sorted(children_map.get(item.id, []))
        ]
        chain = chain_of(item.id)
        defined_bits = [domain]
        if module_path:
            defined_bits.append(module_path)
        enriched = {
            **attrs,
            "kind": attrs.get("kind") or "class",
            "origin": attrs.get("origin") or "own",
            "defined_in": " / ".join(defined_bits),
            "is_a_chain": chain,
            "definition_depth": depth_of(item.id),
            "taxonomy_parents": parents,
            "taxonomy_children": children,
            "see_also": list(attrs.get("see_also") or []),
            "glossary_view": True,
        }
        # Preview: no object properties → empty see_also (do not invent siblings)
        if "see_also" not in attrs:
            enriched["see_also"] = []
        leaf = PublicationItem(
            id=glossary_leaf_id(item.id),
            title=item.title or item.id,
            description=item.description,
            attributes=enriched,
            children=[],
        )
        nested.setdefault(domain, {}).setdefault(module_path, []).append(leaf)

    domain_folders: list[PublicationItem] = []
    for domain in sorted(nested.keys()):
        modules = nested[domain]
        module_keys = sorted(modules.keys(), key=lambda k: (k == "", k))
        # If only one empty module_path, put leaves directly under domain
        if module_keys == [""]:
            kids = sorted(modules[""], key=lambda i: (i.title or i.id).lower())
            domain_folders.append(
                PublicationItem(
                    id=f"group:glossary-site:{domain}",
                    title=domain,
                    description=f"Terms defined in domain {domain}.",
                    attributes={
                        "kind": "group",
                        "group_style": "section_folder",
                        "definition_site": domain,
                        "source_domain": domain,
                        "purpose": f"Definition site: domain {domain}",
                        "member_ids": [c.id for c in kids],
                        "class_count": len(kids),
                        "enum_count": 0,
                    },
                    children=kids,
                )
            )
            continue

        module_folders: list[PublicationItem] = []
        for mpath in module_keys:
            kids = sorted(modules[mpath], key=lambda i: (i.title or i.id).lower())
            label = mpath or "(root)"
            module_folders.append(
                PublicationItem(
                    id=f"group:glossary-site:{domain}:{mpath or '_root'}",
                    title=label,
                    description=f"Module {label} in domain {domain}.",
                    attributes={
                        "kind": "group",
                        "group_style": "section_folder",
                        "definition_site": f"{domain}/{mpath}" if mpath else domain,
                        "source_domain": domain,
                        "module_path": mpath,
                        "purpose": f"Definition site: {label}",
                        "member_ids": [c.id for c in kids],
                        "class_count": len(kids),
                        "enum_count": 0,
                    },
                    children=kids,
                )
            )
        domain_folders.append(
            PublicationItem(
                id=f"group:glossary-site:{domain}",
                title=domain,
                description=f"Terms defined in domain {domain}.",
                attributes={
                    "kind": "group",
                    "group_style": "section_folder",
                    "definition_site": domain,
                    "source_domain": domain,
                    "purpose": f"Definition site: domain {domain}",
                    "member_ids": [c.id for c in module_folders],
                    "class_count": sum(
                        int((c.attributes or {}).get("class_count") or 0)
                        for c in module_folders
                    ),
                    "enum_count": 0,
                },
                children=module_folders,
            )
        )
    return domain_folders


def make_overview_glossary_folder(
    site_folders: list[PublicationItem] | None = None,
    *,
    az_section_id: str = "glossary",
    az_title: str = "A–Z",
) -> PublicationItem:
    """Overview → Glossary folder: A–Z section_ref + definition-site folders."""
    folders = list(site_folders or [])
    az = _section_ref(az_section_id, az_title)
    children = [az, *folders]
    return PublicationItem(
        id=OVERVIEW_GLOSSARY_ID,
        title="Glossary",
        description="Terms by definition site; A–Z is the flat alphabetical view.",
        attributes={
            "kind": "group",
            "group_style": "section_folder",
            "default_collapsed": True,
            "purpose": "Glossary view: definition-site folders + flat A–Z (ADR-024/027).",
            "structure_why": (
                "Folders = where the term is defined; hierarchy and See also "
                "live on the term card, not as folder edges."
            ),
            "member_ids": [c.id for c in children],
            "class_count": sum(
                int((c.attributes or {}).get("class_count") or 0) for c in folders
            ),
            "enum_count": sum(
                int((c.attributes or {}).get("enum_count") or 0) for c in folders
            ),
        },
        children=children,
    )


def collect_glossary_leaf_canonical_ids(nodes: list[PublicationItem]) -> set[str]:
    ids: set[str] = set()
    for node in nodes:
        kind = (node.attributes or {}).get("kind")
        if kind in ("class", "enum") and (node.attributes or {}).get("glossary_view"):
            ids.add(canonical_term_id(node.id))
        ids |= collect_glossary_leaf_canonical_ids(list(node.children or []))
    return ids
