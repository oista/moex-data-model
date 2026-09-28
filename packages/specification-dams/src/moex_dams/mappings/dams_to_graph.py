"""Project ModelPackage instance data into DamsModelGraphView."""

from __future__ import annotations

from typing import Any

from moex_standard_linkml.domain.body import LinkMLImplementationBody

from moex_dams.domain.graph import (
    DamsModelGraphView,
    EdgeKind,
    GraphEdge,
    GraphNode,
    NodeKind,
)


def build_dams_graph(body: LinkMLImplementationBody) -> DamsModelGraphView:
    data = body.data
    package_id = str(data.get("element_id") or data.get("name") or body.source_path)
    nodes: list[GraphNode] = [
        GraphNode(
            id=package_id,
            kind=NodeKind.PACKAGE,
            name=data.get("name"),
            title=data.get("title"),
            description=data.get("description"),
        )
    ]
    edges: list[GraphEdge] = []

    def add_entity(collection: str, kind: NodeKind) -> None:
        for item in data.get(collection) or []:
            if not isinstance(item, dict):
                continue
            eid = item.get("element_id")
            if not eid:
                continue
            eid = str(eid)
            nodes.append(
                GraphNode(
                    id=eid,
                    kind=kind,
                    name=item.get("name"),
                    title=item.get("title"),
                    description=item.get("description"),
                )
            )
            edges.append(
                GraphEdge(source=package_id, target=eid, kind=EdgeKind.CONTAINS)
            )

            for cref in item.get("conceptual_entity_refs") or []:
                edges.append(
                    GraphEdge(
                        source=eid,
                        target=str(cref),
                        kind=EdgeKind.CONCEPTUAL_REF,
                    )
                )
            if item.get("context_ref"):
                edges.append(
                    GraphEdge(
                        source=eid,
                        target=str(item["context_ref"]),
                        kind=EdgeKind.CONTEXT_REF,
                    )
                )

            for attr in item.get("attributes") or []:
                if not isinstance(attr, dict):
                    continue
                aid = attr.get("element_id")
                if not aid:
                    continue
                aid = str(aid)
                nodes.append(
                    GraphNode(
                        id=aid,
                        kind=NodeKind.ATTRIBUTE,
                        name=attr.get("name"),
                        title=attr.get("title"),
                        description=attr.get("description"),
                    )
                )
                edges.append(
                    GraphEdge(source=eid, target=aid, kind=EdgeKind.CONTAINS)
                )
                if attr.get("owner_entity_ref"):
                    edges.append(
                        GraphEdge(
                            source=aid,
                            target=str(attr["owner_entity_ref"]),
                            kind=EdgeKind.OWNER_ENTITY,
                        )
                    )

            for field in item.get("physical_fields") or []:
                if not isinstance(field, dict):
                    continue
                fid = field.get("element_id")
                if not fid:
                    continue
                fid = str(fid)
                nodes.append(
                    GraphNode(
                        id=fid,
                        kind=NodeKind.FIELD,
                        name=field.get("name"),
                        title=field.get("title"),
                        description=field.get("description"),
                    )
                )
                edges.append(
                    GraphEdge(source=eid, target=fid, kind=EdgeKind.CONTAINS)
                )
                if field.get("physical_object_ref"):
                    edges.append(
                        GraphEdge(
                            source=fid,
                            target=str(field["physical_object_ref"]),
                            kind=EdgeKind.PHYSICAL_OBJECT_REF,
                        )
                    )

    add_entity("conceptual_entities", NodeKind.CONCEPTUAL_ENTITY)
    add_entity("domain_contexts", NodeKind.DOMAIN_CONTEXT)
    add_entity("logical_entities", NodeKind.LOGICAL_ENTITY)
    add_entity("physical_objects", NodeKind.PHYSICAL_OBJECT)

    for item in data.get("relationships") or []:
        if not isinstance(item, dict):
            continue
        rid = item.get("element_id")
        if not rid:
            continue
        rid = str(rid)
        nodes.append(
            GraphNode(
                id=rid,
                kind=NodeKind.RELATIONSHIP,
                name=item.get("name"),
                title=item.get("title"),
                description=item.get("description"),
            )
        )
        edges.append(GraphEdge(source=package_id, target=rid, kind=EdgeKind.CONTAINS))
        if item.get("source_entity_ref"):
            edges.append(
                GraphEdge(
                    source=rid,
                    target=str(item["source_entity_ref"]),
                    kind=EdgeKind.RELATES_TO,
                )
            )
        if item.get("target_entity_ref"):
            edges.append(
                GraphEdge(
                    source=rid,
                    target=str(item["target_entity_ref"]),
                    kind=EdgeKind.RELATES_TO,
                )
            )

    for item in data.get("mappings") or []:
        if not isinstance(item, dict):
            continue
        mid = item.get("element_id")
        if not mid:
            continue
        mid = str(mid)
        nodes.append(
            GraphNode(
                id=mid,
                kind=NodeKind.MAPPING,
                name=item.get("name"),
                title=item.get("title"),
                description=item.get("description"),
            )
        )
        edges.append(GraphEdge(source=package_id, target=mid, kind=EdgeKind.CONTAINS))
        for src in item.get("source_refs") or []:
            edges.append(
                GraphEdge(source=mid, target=str(src), kind=EdgeKind.MAPS_TO)
            )
        for tgt in item.get("target_refs") or []:
            edges.append(
                GraphEdge(source=mid, target=str(tgt), kind=EdgeKind.MAPS_TO)
            )

    return DamsModelGraphView(
        package_id=package_id,
        package_name=data.get("name"),
        nodes=tuple(nodes),
        edges=tuple(edges),
    )


def package_index(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Index element_id → item for reference checks."""
    index: dict[str, dict[str, Any]] = {}
    root_id = data.get("element_id")
    if root_id:
        index[str(root_id)] = data
    for collection in (
        "conceptual_entities",
        "logical_entities",
        "physical_objects",
        "domain_contexts",
        "mappings",
        "relationships",
    ):
        for item in data.get(collection) or []:
            if isinstance(item, dict) and item.get("element_id"):
                index[str(item["element_id"])] = item
            if not isinstance(item, dict):
                continue
            for nested_key in ("attributes", "physical_fields"):
                for nested in item.get(nested_key) or []:
                    if isinstance(nested, dict) and nested.get("element_id"):
                        index[str(nested["element_id"])] = nested
    return index
