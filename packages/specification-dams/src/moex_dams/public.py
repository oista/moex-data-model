"""Public API for specification-dams."""

from moex_dams.application.assess import SliceResult, assess_implementation
from moex_dams.application.diff import diff_graphs, diff_implementations
from moex_dams.application.element_index import ElementIndexEntry, build_element_index
from moex_dams.application.repository import DamsAssetRepository
from moex_dams.application.rules_runner import (
    RuleSet,
    default_dams_rule_sets,
    run_rule_sets,
)
from moex_dams.contracts import ModelPackage
from moex_dams.domain.graph import (
    DamsModelGraphView,
    EdgeKind,
    GraphEdge,
    GraphNode,
    NodeKind,
)
from moex_dams.mappings.dams_to_graph import build_dams_graph
from moex_dams.projection.dbml import (
    DbmlManifest,
    project_model_package_to_dbml,
    write_dbml_artifact,
)
from moex_dams.rules.identifiers import (
    build_dams_curie_resolver,
    check_identifiers,
)
from moex_dams.rules.formal_checks import check_formal_requirements
from moex_dams.rules.references import check_references
from moex_dams.rules.structural import check_structural

__all__ = [
    "DamsAssetRepository",
    "DamsModelGraphView",
    "DbmlManifest",
    "EdgeKind",
    "ElementIndexEntry",
    "GraphEdge",
    "GraphNode",
    "ModelPackage",
    "NodeKind",
    "RuleSet",
    "SliceResult",
    "assess_implementation",
    "build_dams_curie_resolver",
    "build_dams_graph",
    "build_element_index",
    "check_identifiers",
    "check_formal_requirements",
    "check_references",
    "check_structural",
    "default_dams_rule_sets",
    "diff_graphs",
    "diff_implementations",
    "project_model_package_to_dbml",
    "run_rule_sets",
    "write_dbml_artifact",
]
