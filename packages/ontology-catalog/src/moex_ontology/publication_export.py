"""Export viewer-compatible JSON projections from the catalog index."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from moex_ontology.adapters.sqlite_index import SqliteOntologyIndex
from moex_ontology.application.get_entity import get_entity
from moex_ontology.application.get_hierarchy import get_hierarchy
from moex_ontology.application.list_ontologies import list_ontologies
from moex_ontology.ports.ontology_provider import OntologyProviderPort
from moex_ontology.ports.semantic_binding_repository import SemanticBindingRepositoryPort
from moex_ontology.read_models.entity_card import OntologyTreeNode


def export_preview_json(
    out_dir: Path,
    *,
    index: SqliteOntologyIndex,
    provider: OntologyProviderPort | None = None,
    bindings: SemanticBindingRepositoryPort | None = None,
    hierarchy_root: str | None = None,
) -> dict[str, Path]:
    out_dir = out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}

    summaries = list_ontologies(index)
    catalog_rows = [
        {
            "id": s.id,
            "title": s.title,
            "description": f"{s.role} · {s.status}",
            "version": s.version,
            "ontology_iri": s.ontology_iri,
            "status": s.status,
            "role": s.role,
            "source_uri": s.source_uri,
            "imports": ", ".join(s.imports),
            "entity_count": s.entity_count,
            "class_count": s.class_count,
            "property_count": s.property_count,
        }
        for s in summaries
    ]
    written["catalog"] = _write(out_dir / "ontology_catalog.json", catalog_rows)

    entities = index.list_entities()
    search_rows = [
        {
            "id": e.iri,
            "title": e.label or e.iri.rsplit("/", 1)[-1],
            "description": e.definition,
            "kind": e.kind,
            "ontology_id": e.ontology_id,
            "aliases": " | ".join(e.alternative_labels),
            "deprecated": e.deprecated,
            "iri": e.iri,
        }
        for e in entities
    ]
    written["entities"] = _write(out_dir / "ontology_entities.json", search_rows)

    # Cards (flat list of attribute bags for entity-table)
    cards = []
    for e in entities:
        card = get_entity(index, e.iri, provider=provider, bindings=bindings)
        if card is None:
            continue
        cards.append(
            {
                "id": card.iri,
                "title": card.label or card.curie or card.iri,
                "description": card.definition,
                "kind": card.kind,
                "curie": card.curie,
                "aliases": " | ".join(card.aliases),
                "parents": " | ".join(card.parents),
                "children": " | ".join(card.children),
                "deprecated": card.deprecated,
                "replaced_by": card.replaced_by,
                "backlinks": len(card.related_model_elements)
                + len(card.related_glossary_terms)
                + len(card.external_mappings),
            }
        )
    written["cards"] = _write(out_dir / "ontology_entity_cards.json", cards)

    # Hierarchy: pick a root with children if possible
    root = hierarchy_root
    if root is None:
        for e in entities:
            if e.kind != "class":
                continue
            node = get_hierarchy(index, e.iri, provider=provider, max_depth=2)
            if node and node.children:
                root = e.iri
                break
        if root is None and entities:
            root = next((e.iri for e in entities if e.kind == "class"), entities[0].iri)

    tree_items: list[dict[str, Any]] = []
    if root:
        tree = get_hierarchy(index, root, provider=provider, max_depth=3)
        if tree:
            tree_items = [_tree_to_item(tree)]
    written["tree"] = _write(out_dir / "ontology_hierarchy.json", tree_items)

    explorer_items = _entities_to_explorer(
        entities,
        index=index,
        provider=provider,
        bindings=bindings,
    )
    written["explorer"] = _write(out_dir / "ontology_explorer.json", explorer_items)

    # Backlinks table
    backlink_rows: list[dict[str, Any]] = []
    if bindings is not None:
        for e in entities:
            for b in bindings.backlinks_for_ontology_entity(e.iri):
                backlink_rows.append(
                    {
                        "id": f"{b.subject_id}->{b.object_id}",
                        "title": b.subject_label or b.subject_id,
                        "description": b.justification,
                        "subject_id": b.subject_id,
                        "predicate": b.predicate,
                        "object_id": b.object_id,
                        "object_label": b.object_label,
                        "mapping_set_id": b.mapping_set_id,
                        "status": b.status,
                    }
                )
    written["backlinks"] = _write(out_dir / "ontology_backlinks.json", backlink_rows)

    return written


def _entities_to_explorer(
    entities: list[Any],
    *,
    index: SqliteOntologyIndex,
    provider: OntologyProviderPort | None = None,
    bindings: SemanticBindingRepositoryPort | None = None,
) -> list[dict[str, Any]]:
    """Group entities by ontology_id; nest classes by in-ontology parent IRI."""
    by_ontology: dict[str, list[dict[str, Any]]] = {}
    iris_by_ontology: dict[str, set[str]] = {}
    for e in entities:
        iris_by_ontology.setdefault(e.ontology_id, set()).add(e.iri)

    for e in entities:
        card = get_entity(index, e.iri, provider=provider, bindings=bindings)
        if card is None:
            continue
        onto_iris = iris_by_ontology.get(card.ontology_id, set())
        in_onto_parents = [p for p in card.parents if p in onto_iris and p != card.iri]
        parent_ref = in_onto_parents[0] if in_onto_parents else ""
        backlinks = (
            len(card.related_model_elements)
            + len(card.related_glossary_terms)
            + len(card.external_mappings)
        )
        row = {
            "id": card.iri,
            "title": card.label or card.curie or card.iri,
            "description": card.definition,
            "attributes": {
                "kind": card.kind,
                "iri": card.iri,
                "curie": card.curie,
                "ontology_id": card.ontology_id,
                "aliases": " | ".join(card.aliases),
                "parents": " | ".join(card.parents),
                "children": " | ".join(card.children),
                "domain": " | ".join(card.domain),
                "range": " | ".join(card.range),
                "deprecated": card.deprecated,
                "replaced_by": card.replaced_by,
                "backlinks": backlinks,
                "parent_ref": parent_ref,
            },
            "children": [],
        }
        by_ontology.setdefault(card.ontology_id, []).append(row)

    groups: list[dict[str, Any]] = []
    for ontology_id in sorted(by_ontology.keys()):
        rows = by_ontology[ontology_id]
        tree = _nest_by_parent_ref(rows)
        class_count = sum(1 for r in rows if (r.get("attributes") or {}).get("kind") == "class")
        groups.append(
            {
                "id": f"group:{ontology_id}",
                "title": ontology_id.rsplit(":", 1)[-1],
                "description": f"Ontology {ontology_id}",
                "attributes": {
                    "kind": "group",
                    "ontology_id": ontology_id,
                    "purpose": f"Indexed entities in {ontology_id}.",
                    "class_count": class_count,
                    "enum_count": 0,
                },
                "children": tree,
            }
        )
    return groups


def _nest_by_parent_ref(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {n["id"]: n for n in nodes}
    children_map: dict[str, list[str]] = {n["id"]: [] for n in nodes}
    roots: list[dict[str, Any]] = []
    for node in nodes:
        parent = str((node.get("attributes") or {}).get("parent_ref") or "").strip()
        if parent and parent in by_id and parent != node["id"]:
            children_map[parent].append(node["id"])
        else:
            roots.append(node)

    def attach(node: dict[str, Any]) -> dict[str, Any]:
        kids = [attach(by_id[cid]) for cid in sorted(children_map.get(node["id"], []))]
        out = dict(node)
        out["children"] = kids
        return out

    return [attach(r) for r in sorted(roots, key=lambda n: n["id"])]


def _tree_to_item(node: OntologyTreeNode) -> dict[str, Any]:
    return {
        "id": node.id,
        "title": node.title,
        "description": node.description,
        "attributes": dict(node.attributes),
        "children": [_tree_to_item(c) for c in node.children],
    }


def _write(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
