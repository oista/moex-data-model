"""Vertical slice on trading-solution-model.yaml."""

from __future__ import annotations

from pathlib import Path

from moex_modeling import ConformanceResult, RelationKind

from moex_dams import assess_implementation, build_dams_graph
from moex_dams.domain.graph import NodeKind
from moex_standard_linkml.provider import LinkMLStandardProvider
from moex_modeling import ImplementationRef


def test_assess_trading_solution(dams_schema: Path, trading_solution: Path) -> None:
    result = assess_implementation(
        schema_path=dams_schema,
        implementation_path=trading_solution,
        implementation_id="moex:implementation:trading:1.0.0",
    )

    assert result.report.overall_result in {
        ConformanceResult.CONFORMANT,
        ConformanceResult.CONFORMANT_WITH_WARNINGS,
    }
    assert result.report.is_conformant
    assert result.graph.package_id == "dams:model/trading/1.0.0"
    assert result.graph.nodes_by_kind(NodeKind.CONCEPTUAL_ENTITY)
    assert result.graph.nodes_by_kind(NodeKind.LOGICAL_ENTITY)
    assert result.graph.nodes_by_kind(NodeKind.MAPPING)

    kinds = {r.relation_kind for r in result.universe.relations}
    assert RelationKind.CONFORMS_TO in kinds
    assert RelationKind.EXPRESSED_IN in kinds
    assert RelationKind.IMPLEMENTS in kinds

    assert result.specification_body.root_class == "MOEXModelRepository"
    assert type(result.specification_body) is not type(result.implementation_body)


def test_build_graph_from_provider(
    dams_schema: Path,
    trading_solution: Path,
) -> None:
    provider = LinkMLStandardProvider(default_schema_path=dams_schema)
    body = provider.load_implementation_body(
        ImplementationRef(
            implementation_id="moex:implementation:trading:1.0.0",
            implementation_revision="1",
        ),
        path=str(trading_solution),
    )
    graph = build_dams_graph(body)
    assert "dams:logical/trading/Client" in graph.node_ids()
    assert "dams:logical/trading/Client/clientId" in graph.node_ids()
