"""Bounded DamsModelGraphView over a ModelPackage instance."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict


class NodeKind(str, Enum):
    PACKAGE = "package"
    CONCEPTUAL_ENTITY = "conceptual_entity"
    LOGICAL_ENTITY = "logical_entity"
    PHYSICAL_OBJECT = "physical_object"
    DOMAIN_CONTEXT = "domain_context"
    MAPPING = "mapping"
    ATTRIBUTE = "attribute"
    FIELD = "field"


class EdgeKind(str, Enum):
    CONTAINS = "contains"
    CONCEPTUAL_REF = "conceptual_ref"
    CONTEXT_REF = "context_ref"
    MAPS_TO = "maps_to"
    OWNER_ENTITY = "owner_entity"
    PHYSICAL_OBJECT_REF = "physical_object_ref"


class GraphNode(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    id: str
    kind: NodeKind
    name: str | None = None
    title: str | None = None
    description: str | None = None


class GraphEdge(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    source: str
    target: str
    kind: EdgeKind


class DamsModelGraphView(BaseModel):
    """Bounded operational view of a DAMS ModelPackage."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    package_id: str
    package_name: str | None = None
    nodes: tuple[GraphNode, ...] = ()
    edges: tuple[GraphEdge, ...] = ()

    def node_ids(self) -> frozenset[str]:
        return frozenset(n.id for n in self.nodes)

    def nodes_by_kind(self, kind: NodeKind) -> tuple[GraphNode, ...]:
        return tuple(n for n in self.nodes if n.kind is kind)
