"""Cross-implementation OWL/CDM/LDM hierarchy projection for moex.hierarchy.

Builds glossary-shaped entity rows, a compact hierarchy_graph for the viewer,
and a generated ModelPackage YAML without attributes or physical objects.
"""

from __future__ import annotations

from typing import Any

import yaml

from moex_publication_viewer.models.catalog_models import CatalogNode
from moex_publication_viewer.models.publication_models import (
    PublicationItem,
    PublicationModule,
    PublicationSection,
)
from moex_publication_viewer.normalizers.implementation_glossary import (
    _attrs_as_element,
    _build_index,
    _build_relationship_see_also,
    _collect_relationship_elements,
    _collect_term_sources,
    _module_by_id,
    _nonempty,
    _rel_entry,
    _resolve_glossary_row,
    glossary_row_id,
    resolve_definition,
    _reference_definition_without_own,
    DefinitionMode,
)

HIERARCHY_MODULE_ID = "moex:module:hierarchy"
HIERARCHY_CATALOG_ID = "moex-hierarchy"
HIERARCHY_SECTION_ID = "entity-hierarchy"
HIERARCHY_ARTIFACT_BODY_ID = "artifact-model-body"

_ENTITY_INSTANCES = frozenset({"ConceptualEntity", "LogicalEntity"})
_SKIP_IMPL_IDS = frozenset({HIERARCHY_CATALOG_ID, "moex-dsp"})


def _dams_impl_nodes(catalog_nodes: list[CatalogNode]) -> list[CatalogNode]:
    nodes = [
        n
        for n in catalog_nodes
        if n.role == "specification_implementation"
        and n.conforms_to == "moex-dams"
        and n.id not in _SKIP_IMPL_IDS
    ]
    nodes.sort(key=lambda n: (n.order, n.title))
    return nodes


def _owl_title_from_iri(iri: str) -> str:
    iri = iri.strip()
    if "#" in iri:
        return iri.rsplit("#", 1)[-1] or iri
    return iri.rstrip("/").rsplit("/", 1)[-1] or iri


def _external_target(ref: Any) -> str | None:
    if isinstance(ref, str) and ref.strip():
        return ref.strip()
    if isinstance(ref, dict):
        for key in ("target_ref", "external_class_ref", "iri", "id"):
            val = ref.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
    return None


def _collect_mappings(
    modules: list[PublicationModule],
    impl_nodes: list[CatalogNode],
) -> list[tuple[str, dict[str, Any]]]:
    out: list[tuple[str, dict[str, Any]]] = []
    for node in impl_nodes:
        mod = _module_by_id(modules, node.module_id)
        if mod is None:
            continue
        for sec in mod.sections:
            if sec.id not in {"alignments", "mappings"} and (
                (sec.attributes or {}).get("select") != "mappings"
            ):
                # Prefer sections that look like mapping tables.
                cols = {c.lower() for c in (sec.columns or [])}
                if "mapping_type" not in cols and sec.id != "alignments":
                    # Still accept entity-table titled mappings
                    title = (sec.title or "").lower()
                    if "mapping" not in title and "alignment" not in title:
                        continue
            for item in sec.items or []:
                attrs = _attrs_as_element(item)
                attrs.setdefault("element_id", item.id)
                out.append((node.id, attrs))
    return out


def build_hierarchy_graph_and_items(
    modules: list[PublicationModule],
    impl_nodes: list[CatalogNode],
) -> tuple[list[PublicationItem], dict[str, Any]]:
    """Return (glossary items, hierarchy_graph) for entity hierarchy section."""
    sources = [
        s
        for s in _collect_term_sources(modules, impl_nodes)
        if s.instance_of in _ENTITY_INSTANCES
    ]
    if not sources:
        return [], {"nodes": [], "edges": []}

    index = _build_index(sources)
    by_element: dict[str, list[str]] = {}
    row_ids: dict[tuple[str, str], str] = {}
    for src in sources:
        rid = glossary_row_id(src.impl_catalog_id, src.item.id)
        row_ids[(src.impl_catalog_id, src.item.id)] = rid
        by_element.setdefault(src.item.id, []).append(rid)

    parents_map: dict[str, list[dict[str, str]]] = {}
    children_map: dict[str, list[dict[str, str]]] = {}
    edges: list[dict[str, str]] = []
    edge_keys: set[tuple[str, str, str]] = set()

    def add_edge(source: str, target: str, rel: str, *, bidirectional_see: bool = False) -> None:
        key = (source, target, rel)
        if not source or not target or source == target or key in edge_keys:
            return
        edge_keys.add(key)
        edges.append({"source": source, "target": target, "rel": rel})
        if bidirectional_see:
            return

    # LDM → nominal CDM
    for src in sources:
        rid = row_ids[(src.impl_catalog_id, src.item.id)]
        if src.instance_of != "LogicalEntity":
            continue
        refs = src.element.get("conceptual_entity_refs") or []
        if not isinstance(refs, list):
            continue
        for ref in refs:
            ref_s = str(ref).strip()
            if not ref_s:
                continue
            parent_row = row_ids.get((src.impl_catalog_id, ref_s)) or index.first_row_for_element.get(
                ref_s
            )
            if not parent_row:
                continue
            parents_map.setdefault(rid, []).append(
                _rel_entry(parent_row, "conceptual_entity_ref")
            )
            children_map.setdefault(parent_row, []).append(_rel_entry(rid, "realized_by"))
            add_edge(rid, parent_row, "conceptual_entity_ref")

    # CDM taxonomy
    for src in sources:
        if src.instance_of != "ConceptualEntity":
            continue
        rid = row_ids[(src.impl_catalog_id, src.item.id)]
        pref = str(src.element.get("parent_concept_ref") or "").strip()
        if not pref:
            continue
        parent_row = row_ids.get((src.impl_catalog_id, pref)) or index.first_row_for_element.get(
            pref
        )
        if not parent_row:
            continue
        parents_map.setdefault(rid, []).append(_rel_entry(parent_row, "parent_concept_ref"))
        children_map.setdefault(parent_row, []).append(_rel_entry(rid, "child_concept"))
        add_edge(rid, parent_row, "parent_concept_ref")

    # Relationships (same-layer associations)
    rel_see_also = _build_relationship_see_also(
        modules, impl_nodes, sources, row_ids, index
    )
    for impl_id, rel in _collect_relationship_elements(modules, impl_nodes):
        src_ref = str(rel.get("source_entity_ref") or "").strip()
        tgt_ref = str(rel.get("target_entity_ref") or "").strip()
        if not src_ref or not tgt_ref:
            continue
        src_row = _resolve_glossary_row(impl_id, src_ref, row_ids, index)
        tgt_row = _resolve_glossary_row(impl_id, tgt_ref, row_ids, index)
        if not src_row or not tgt_row:
            continue
        term_ref = str(rel.get("relation_term_ref") or "").strip()
        label = f"relationship:{rel.get('name') or term_ref or 'related'}"
        add_edge(src_row, tgt_row, label)

    # Mapping realizes / aligns_with
    for impl_id, mapping in _collect_mappings(modules, impl_nodes):
        mtype = str(mapping.get("mapping_type") or "").strip().lower()
        sources_refs = mapping.get("source_refs") or []
        target_refs = mapping.get("target_refs") or []
        if not isinstance(sources_refs, list):
            sources_refs = [sources_refs] if sources_refs else []
        if not isinstance(target_refs, list):
            target_refs = [target_refs] if target_refs else []
        for sref in sources_refs:
            for tref in target_refs:
                s_row = _resolve_glossary_row(impl_id, str(sref), row_ids, index)
                t_row = _resolve_glossary_row(impl_id, str(tref), row_ids, index)
                if mtype == "realizes" and s_row and t_row:
                    add_edge(s_row, t_row, "realizes")
                elif mtype == "aligns_with" and s_row:
                    # target may be OWL IRI
                    iri = str(tref).strip()
                    if iri.startswith("http"):
                        add_edge(s_row, iri, "aligns_with")
                    elif t_row:
                        add_edge(s_row, t_row, "aligns_with")

    # OWL stubs from external_class_refs
    owl_nodes: dict[str, dict[str, Any]] = {}
    for src in sources:
        rid = row_ids[(src.impl_catalog_id, src.item.id)]
        refs = src.element.get("external_class_refs") or []
        if not isinstance(refs, list):
            continue
        for ref in refs:
            iri = _external_target(ref)
            if not iri or not iri.startswith("http"):
                continue
            match_kind = "external"
            if isinstance(ref, dict):
                match_kind = str(ref.get("match_kind") or match_kind)
            owl_nodes.setdefault(
                iri,
                {
                    "id": iri,
                    "layer": "OWL",
                    "title": _owl_title_from_iri(iri),
                    "solution": "ontology",
                    "solution_id": "ontology",
                    "kind": "owl-class",
                },
            )
            add_edge(rid, iri, f"external_class_ref:{match_kind}")

    # same_concept cross-solution
    for eid, rids in by_element.items():
        if len(rids) < 2:
            continue
        for i, a in enumerate(rids):
            for b in rids[i + 1 :]:
                add_edge(a, b, "same_concept")
                add_edge(b, a, "same_concept")

    items: list[PublicationItem] = []
    graph_nodes: list[dict[str, Any]] = []

    for src in sources:
        rid = row_ids[(src.impl_catalog_id, src.item.id)]
        level_name = src.instance_of or "ModelElement"
        prov = resolve_definition(src.element, index, level=level_name)
        ref_text = _reference_definition_without_own(
            src.element, index, level=level_name
        )
        own_text = (
            str(src.element.get("description")).strip()
            if _nonempty(src.element.get("description"))
            else ""
        )
        redundant = bool(
            own_text
            and ref_text
            and own_text == ref_text.strip()
            and prov.mode in (DefinitionMode.OWN, DefinitionMode.OWN_ADAPTED)
        )
        see_also: list[dict[str, str]] = []
        for other_rid in by_element.get(src.item.id, []):
            if other_rid != rid:
                see_also.append(_rel_entry(other_rid, "same_concept"))
        see_also.extend(rel_see_also.get(rid, []))

        layer = src.model_level  # CDM | LDM
        attrs: dict[str, Any] = {
            "kind": src.kind,
            "name": src.element.get("name") or src.item.id,
            "label": src.item.title or src.element.get("name") or src.item.id,
            "definition": prov.text or "",
            "definition_mode": prov.mode.value,
            "definition_source": prov.source_element_id,
            "definition_diagnostic": prov.diagnostic,
            "reference_definition": ref_text,
            "redundant_override": redundant,
            "model_level": layer,
            "layer": layer,
            "solution": src.impl_title,
            "solution_id": src.impl_catalog_id,
            "impl_module_id": src.impl_module_id,
            "impl_section_id": src.section_id,
            "source_item_id": src.item.id,
            "instance_of": src.instance_of,
            "conceptual_entity_refs": src.element.get("conceptual_entity_refs") or [],
            "external_class_refs": src.element.get("external_class_refs") or [],
            "aliases": src.element.get("aliases") or [],
            "taxonomy_parents": parents_map.get(rid, []),
            "taxonomy_children": children_map.get(rid, []),
            "see_also": see_also,
            "defined_in": f"{src.impl_title} · {layer}",
        }
        parent_ref = src.element.get("parent_concept_ref")
        if parent_ref:
            attrs["parent_concept_ref"] = str(parent_ref)

        title = src.item.title or str(src.element.get("name") or src.item.id)
        items.append(
            PublicationItem(
                id=rid,
                title=title,
                description=prov.text or src.item.description,
                attributes=attrs,
            )
        )
        graph_nodes.append(
            {
                "id": rid,
                "layer": layer,
                "title": title,
                "name": attrs["name"],
                "solution": src.impl_title,
                "solution_id": src.impl_catalog_id,
                "kind": src.kind,
                "element_id": src.item.id,
                "description": (prov.text or "")[:240],
            }
        )

    for iri, node in sorted(owl_nodes.items(), key=lambda kv: kv[0]):
        items.append(
            PublicationItem(
                id=iri,
                title=node["title"],
                description=f"OWL class {iri}",
                attributes={
                    "kind": "owl-class",
                    "name": node["title"],
                    "label": node["title"],
                    "definition": iri,
                    "model_level": "OWL",
                    "layer": "OWL",
                    "solution": "ontology",
                    "solution_id": "ontology",
                    "source_item_id": iri,
                    "instance_of": "OwlClass",
                    "see_also": [],
                    "taxonomy_parents": [],
                    "taxonomy_children": [],
                    "external_class_refs": [],
                    "defined_in": "OWL · ontology",
                },
            )
        )
        graph_nodes.append(node)

    items.sort(key=lambda i: (i.title or i.id).lower())
    graph = {"nodes": graph_nodes, "edges": edges}
    return items, graph


def build_hierarchy_yaml(
    modules: list[PublicationModule],
    impl_nodes: list[CatalogNode],
    items: list[PublicationItem],
) -> str:
    """Serialize aggregated entities/relationships without attributes/PDM."""
    conceptual: list[dict[str, Any]] = []
    logical: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    mappings: list[dict[str, Any]] = []
    seen_rel: set[str] = set()

    for item in items:
        attrs = item.attributes or {}
        layer = attrs.get("layer") or attrs.get("model_level")
        eid = str(attrs.get("source_item_id") or item.id)
        if layer == "OWL":
            continue
        row: dict[str, Any] = {
            "element_id": eid,
            "name": attrs.get("name") or eid,
            "title": item.title,
            "description": item.description,
        }
        if attrs.get("parent_concept_ref"):
            row["parent_concept_ref"] = attrs["parent_concept_ref"]
        if attrs.get("conceptual_entity_refs"):
            row["conceptual_entity_refs"] = attrs["conceptual_entity_refs"]
        if attrs.get("external_class_refs"):
            # Keep only IRI refs, strip nested noise for readability
            cleaned = []
            for ref in attrs["external_class_refs"]:
                if isinstance(ref, dict):
                    cleaned.append(
                        {
                            k: ref[k]
                            for k in (
                                "external_class_ref_id",
                                "target_ref",
                                "match_kind",
                                "source_kind",
                            )
                            if k in ref
                        }
                    )
                elif isinstance(ref, str):
                    cleaned.append(ref)
            if cleaned:
                row["external_class_refs"] = cleaned
        # Explicitly omit attributes / physical
        if layer == "CDM":
            conceptual.append(row)
        elif layer == "LDM":
            logical.append(row)

    for impl_id, rel in _collect_relationship_elements(modules, impl_nodes):
        rid = str(rel.get("element_id") or "").strip()
        if not rid or rid in seen_rel:
            continue
        seen_rel.add(rid)
        relationships.append(
            {
                "element_id": rid,
                "name": rel.get("name"),
                "title": rel.get("title"),
                "description": rel.get("description"),
                "source_entity_ref": rel.get("source_entity_ref"),
                "target_entity_ref": rel.get("target_entity_ref"),
                "relation_term_ref": rel.get("relation_term_ref"),
                "term_direction": rel.get("term_direction"),
                "_source_implementation": impl_id,
            }
        )

    for impl_id, mapping in _collect_mappings(modules, impl_nodes):
        mtype = str(mapping.get("mapping_type") or "").strip().lower()
        if mtype not in {"realizes", "aligns_with"}:
            continue
        mid = str(mapping.get("element_id") or "").strip()
        if not mid:
            continue
        mappings.append(
            {
                "element_id": mid,
                "name": mapping.get("name"),
                "description": mapping.get("description"),
                "mapping_type": mapping.get("mapping_type"),
                "source_refs": mapping.get("source_refs"),
                "target_refs": mapping.get("target_refs"),
                "_source_implementation": impl_id,
            }
        )

    package = {
        "element_id": "dams:model/hierarchy/0.1.0",
        "api_version": "dams.moex/v0.1",
        "model_version": "0.1.0",
        "implementation_scope": "enterprise",
        "name": "moex.hierarchy",
        "title": "moex.hierarchy",
        "description": (
            "Derived hierarchy projection across DAMS implementations "
            "(entities and relationships only; no attributes / physical)."
        ),
        "conceptual_entities": conceptual,
        "logical_entities": logical,
        "relationships": relationships,
        "mappings": mappings,
    }
    return yaml.safe_dump(
        package,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=100,
    )


def build_hierarchy_section(
    modules: list[PublicationModule],
    impl_nodes: list[CatalogNode],
) -> PublicationSection | None:
    items, graph = build_hierarchy_graph_and_items(modules, impl_nodes)
    if not items:
        return None
    return PublicationSection(
        id=HIERARCHY_SECTION_ID,
        title="Entity hierarchy",
        description=(
            "Отбор сущностей и послойная визуализация связей OWL / CDM / LDM "
            "(без атрибутов и физического уровня)."
        ),
        type="glossary",
        kind="glossary",
        filterable=["model_level", "solution", "kind"],
        items=items,
        attributes={
            "term_cards": True,
            "glossary_scope": "hierarchy",
            "hierarchy_graph": graph,
        },
    )


def enrich_dams_hierarchy_module(
    modules: list[PublicationModule],
    catalog_nodes: list[CatalogNode] | None,
) -> None:
    """Replace entity-hierarchy section and artifact YAML on moex.hierarchy."""
    if not catalog_nodes:
        return
    hierarchy = next((m for m in modules if m.module_id == HIERARCHY_MODULE_ID), None)
    if hierarchy is None:
        return
    impl_nodes = _dams_impl_nodes(catalog_nodes)
    items, graph = build_hierarchy_graph_and_items(modules, impl_nodes)
    if not items:
        raise RuntimeError(
            f"{HIERARCHY_MODULE_ID}: enrich produced no hierarchy entities; "
            "refusing to leave entity-hierarchy without glossary_scope=hierarchy"
        )
    section = PublicationSection(
        id=HIERARCHY_SECTION_ID,
        title="Entity hierarchy",
        description=(
            "Отбор сущностей и послойная визуализация связей OWL / CDM / LDM "
            "(без атрибутов и физического уровня)."
        ),
        type="glossary",
        kind="glossary",
        filterable=["model_level", "solution", "kind"],
        items=items,
        attributes={
            "term_cards": True,
            "glossary_scope": "hierarchy",
            "hierarchy_graph": graph,
        },
    )
    yaml_text = build_hierarchy_yaml(modules, impl_nodes, items)

    existing = next((s for s in hierarchy.sections if s.id == HIERARCHY_SECTION_ID), None)
    if existing is not None:
        idx = hierarchy.sections.index(existing)
        hierarchy.sections[idx] = section
    else:
        hierarchy.sections.append(section)

    body = next(
        (s for s in hierarchy.sections if s.id == HIERARCHY_ARTIFACT_BODY_ID),
        None,
    )
    if body and body.items:
        item = body.items[0]
        attrs = dict(item.attributes or {})
        attrs["text"] = yaml_text
        attrs["description"] = (
            "Сгенерированный YAML обобщённой модели (сущности и связи, без атрибутов/PDM)."
        )
        body.items[0] = PublicationItem(
            id=item.id,
            title=body.title or item.title or "Полная модель moex",
            description=attrs["description"],
            attributes=attrs,
        )

    # Persist generated body next to the package for inspectability.
    if hierarchy.manifest_path:
        from pathlib import Path

        manifest = Path(hierarchy.manifest_path)
        out = manifest.parent / "moex-hierarchy-model.yaml"
        try:
            out.write_text(yaml_text, encoding="utf-8")
        except OSError:
            pass

    # Fail-closed: hierarchy UI tabs depend on this attribute.
    secured = next(
        (s for s in hierarchy.sections if s.id == HIERARCHY_SECTION_ID), None
    )
    if secured is None or (secured.attributes or {}).get("glossary_scope") != "hierarchy":
        raise RuntimeError(
            f"{HIERARCHY_MODULE_ID}: entity-hierarchy missing "
            "glossary_scope=hierarchy after enrich"
        )


def _hierarchy_entity_nav_leaf(
    item: PublicationItem, *, glyph: str
) -> PublicationItem:
    """Sidebar leaf/node that opens Entity hierarchy focused on this row."""
    attrs = item.attributes or {}
    desc = item.description or (
        f"Open «{item.title or item.id}» in Entity hierarchy."
    )
    return PublicationItem(
        id=item.id,
        title=item.title,
        description=desc,
        attributes={
            "kind": "hierarchy_entity",
            "section_id": HIERARCHY_SECTION_ID,
            "target_module_id": HIERARCHY_MODULE_ID,
            "target_section_id": HIERARCHY_SECTION_ID,
            "nav_glyph": glyph,
            "model_level": attrs.get("model_level") or attrs.get("layer"),
            "solution": attrs.get("solution"),
            "solution_id": attrs.get("solution_id"),
            "source_item_id": attrs.get("source_item_id"),
            "instance_of": attrs.get("instance_of"),
            "description": desc,
        },
        children=[],
    )


def _sort_nav_tree(nodes: list[PublicationItem]) -> list[PublicationItem]:
    ordered = sorted(nodes, key=lambda n: (n.title or n.id).lower())
    for node in ordered:
        if node.children:
            node.children = _sort_nav_tree(list(node.children))
    return ordered


def _build_conceptual_entity_forest(
    cdm_items: list[PublicationItem],
) -> list[PublicationItem]:
    """Nest CDM rows by parent_concept_ref (same-solution parent preferred)."""
    nodes = {
        item.id: _hierarchy_entity_nav_leaf(item, glyph="cdm") for item in cdm_items
    }
    meta = {
        item.id: {
            "source": str((item.attributes or {}).get("source_item_id") or "").strip(),
            "parent": str(
                (item.attributes or {}).get("parent_concept_ref") or ""
            ).strip(),
            "solution_id": str(
                (item.attributes or {}).get("solution_id") or ""
            ).strip(),
        }
        for item in cdm_items
    }
    by_source: dict[str, list[str]] = {}
    for rid, m in meta.items():
        if m["source"]:
            by_source.setdefault(m["source"], []).append(rid)

    child_ids: set[str] = set()
    for rid, m in meta.items():
        pref = m["parent"]
        if not pref:
            continue
        candidates = by_source.get(pref) or []
        parent_row = next(
            (cid for cid in candidates if meta[cid]["solution_id"] == m["solution_id"]),
            None,
        )
        if parent_row is None and candidates:
            parent_row = candidates[0]
        if not parent_row or parent_row == rid or parent_row not in nodes:
            continue
        nodes[parent_row].children.append(nodes[rid])
        child_ids.add(rid)

    roots = [nodes[item.id] for item in cdm_items if item.id not in child_ids]
    return _sort_nav_tree(roots)


def _build_logical_entity_folders(
    ldm_items: list[PublicationItem],
) -> list[PublicationItem]:
    """Group LDM rows into solution folders (catalog encounter order)."""
    by_sol: dict[str, list[PublicationItem]] = {}
    order: list[str] = []
    titles: dict[str, str] = {}
    for item in ldm_items:
        attrs = item.attributes or {}
        sid = str(attrs.get("solution_id") or "unknown").strip() or "unknown"
        if sid not in by_sol:
            by_sol[sid] = []
            order.append(sid)
            titles[sid] = str(attrs.get("solution") or sid)
        by_sol[sid].append(_hierarchy_entity_nav_leaf(item, glyph="ldm"))

    folders: list[PublicationItem] = []
    for sid in order:
        kids = _sort_nav_tree(by_sol[sid])
        folders.append(
            PublicationItem(
                id=f"implnav:{HIERARCHY_CATALOG_ID}:group:logical:{sid}",
                title=titles[sid],
                description=f"Logical entities from {titles[sid]}.",
                attributes={
                    "kind": "group",
                    "group_style": "section_folder",
                    "nav_glyph": "ldm",
                    "nav_group": "logical-entities",
                    "member_ids": [c.id for c in kids],
                },
                children=kids,
            )
        )
    return folders


def build_hierarchy_entity_nav(
    items: list[PublicationItem],
) -> tuple[PublicationItem, PublicationItem]:
    """Build Conceptual Entities / Logical Entities sidebar groups from hierarchy rows."""
    cdm: list[PublicationItem] = []
    ldm: list[PublicationItem] = []
    for item in items:
        attrs = item.attributes or {}
        instance_of = attrs.get("instance_of")
        layer = attrs.get("layer") or attrs.get("model_level")
        if instance_of == "ConceptualEntity" or (
            layer == "CDM" and instance_of != "OwlClass"
        ):
            cdm.append(item)
        elif instance_of == "LogicalEntity" or layer == "LDM":
            ldm.append(item)

    cdm_kids = _build_conceptual_entity_forest(cdm)
    ldm_kids = _build_logical_entity_folders(ldm)

    conceptual = PublicationItem(
        id=f"implnav:{HIERARCHY_CATALOG_ID}:group:conceptual-entities",
        title="Conceptual Entities",
        description="All conceptual-model entities (CDM) across DAMS implementations.",
        attributes={
            "kind": "group",
            "nav_glyph": "cdm",
            "nav_group": "conceptual-entities",
            "member_ids": [c.id for c in cdm_kids],
        },
        children=cdm_kids,
    )
    logical = PublicationItem(
        id=f"implnav:{HIERARCHY_CATALOG_ID}:group:logical-entities",
        title="Logical Entities",
        description="Logical-model entities (LDM) grouped by IT solution.",
        attributes={
            "kind": "group",
            "nav_glyph": "ldm",
            "nav_group": "logical-entities",
            "member_ids": [c.id for c in ldm_kids],
        },
        children=ldm_kids,
    )
    return conceptual, logical


def attach_hierarchy_entity_nav(modules: list[PublicationModule]) -> None:
    """Insert Conceptual/Logical entity trees under moex.hierarchy in DAMS explorer."""
    hierarchy = next((m for m in modules if m.module_id == HIERARCHY_MODULE_ID), None)
    if hierarchy is None:
        return
    section = next((s for s in hierarchy.sections if s.id == HIERARCHY_SECTION_ID), None)
    if section is None or not section.items:
        return

    conceptual, logical = build_hierarchy_entity_nav(list(section.items))

    dams = next((m for m in modules if m.module_id == "moex:module:dams"), None)
    if dams is None:
        return
    explorer = next((s for s in dams.sections if s.type == "explorer"), None)
    if explorer is None:
        return
    impls = next(
        (i for i in (explorer.items or []) if i.id == "group:implementations"),
        None,
    )
    if impls is None:
        return

    def find_hierarchy_ref(
        nodes: list[PublicationItem] | None,
    ) -> PublicationItem | None:
        for node in nodes or []:
            if node.id == HIERARCHY_CATALOG_ID:
                return node
            found = find_hierarchy_ref(node.children)
            if found is not None:
                return found
        return None

    href = find_hierarchy_ref(impls.children)
    if href is None:
        return

    kids = list(href.children or [])
    # Drop prior attach (idempotent refresh / serve).
    kids = [
        c
        for c in kids
        if c.id
        not in {
            conceptual.id,
            logical.id,
        }
    ]
    insert_at = next(
        (
            i
            for i, c in enumerate(kids)
            if (c.attributes or {}).get("section_id") == HIERARCHY_SECTION_ID
        ),
        None,
    )
    if insert_at is None:
        # Fallback: before Артефакты, else append.
        insert_at = len(kids)
        for i, c in enumerate(kids):
            if (c.attributes or {}).get("nav_group") == "artifacts" or c.title == "Артефакты":
                insert_at = i
                break
        kids[insert_at:insert_at] = [conceptual, logical]
    else:
        kids[insert_at + 1 : insert_at + 1] = [conceptual, logical]

    href.children = kids
    attrs = dict(href.attributes or {})
    attrs["member_ids"] = [c.id for c in kids]
    href.attributes = attrs
