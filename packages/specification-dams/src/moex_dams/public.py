"""Public API for specification-dams."""

from moex_dams.application.assess import SliceResult, assess_implementation
from moex_dams.application.diff import diff_graphs, diff_implementations
from moex_dams.contracts import ModelPackage
from moex_dams.domain.graph import (
    DamsModelGraphView,
    EdgeKind,
    GraphEdge,
    GraphNode,
    NodeKind,
)
from moex_dams.mappings.dams_to_graph import build_dams_graph
from moex_dams.rules.references import check_references
from moex_dams.rules.structural import check_structural

__all__ = [
    "DamsModelGraphView",
    "EdgeKind",
    "GraphEdge",
    "GraphNode",
    "ModelPackage",
    "NodeKind",
    "SliceResult",
    "assess_implementation",
    "build_dams_graph",
    "check_references",
    "check_structural",
    "diff_graphs",
    "diff_implementations",
]
