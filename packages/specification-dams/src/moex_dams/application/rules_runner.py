"""Conformance rule registration and execution by phase."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from moex_modeling import ConformancePhase, Diagnostic
from moex_standard_linkml.domain.body import LinkMLImplementationBody

from moex_dams.application.repository import DamsAssetRepository
from moex_dams.rules.catalog_topology import check_catalog_topology
from moex_dams.rules.dams_levels import check_dams_model_level
from moex_dams.rules.formal_checks import check_formal_requirements_for_repo
from moex_dams.rules.governance_assignments import check_governance_assignments
from moex_dams.rules.identifiers import build_dams_curie_resolver, check_identifiers
from moex_dams.rules.package_invariants import check_package_invariants
from moex_dams.rules.references import check_references
from moex_dams.rules.structural import check_structural

# Modules whose L2 validators are reached from assess / formal_checks / schema
# lint / check-manifest. Kept for docs; the normative gate is
# ``L2_PRODUCTION_CALLABLES`` (exact dotted path).
L2_PRODUCTION_MODULES: frozenset[str] = frozenset(
    {
        "moex_dams.rules.structural",
        "moex_dams.rules.package_invariants",
        "moex_dams.rules.governance_assignments",
        "moex_dams.rules.catalog_topology",
        "moex_dams.rules.technical_assets",
        "moex_dams.rules.data_structure",
        "moex_dams.rules.semantic_layer",
        "moex_dams.rules.conceptual_entity",
        "moex_dams.rules.relation_terms",
        # Schema lint (ontology-check / Stage 8), not package assess — INV-026.
        "moex_dams.rules.ontology_uris",
        # check-manifest (Stage 0), not package assess — INV-058.
        "moex_dams.rules.repository_invariants",
    }
)

# Exact ``dams_validator`` paths from constraint-matrix L2-implemented rows that
# are wired into a production channel. Meta-test requires every L2-implemented
# matrix ``dams_validator`` to appear here (module allowlist alone is not enough).
L2_PRODUCTION_CALLABLES: frozenset[str] = frozenset(
    {
        # assess → package-invariants
        "moex_dams.rules.package_invariants.check_solution_scope_refs",
        "moex_dams.rules.package_invariants.check_attribute_cardinality_bounds",
        "moex_dams.rules.package_invariants.check_parent_concept_cycles",
        "moex_dams.rules.package_invariants.check_selection_attribute_closure",
        "moex_dams.rules.package_invariants.check_binding_compatibility",
        "moex_dams.rules.package_invariants.check_package_element_id_uniqueness",
        "moex_dams.rules.package_invariants.check_mapping_cardinality_consistency",
        "moex_dams.rules.package_invariants.check_relationship_endpoint_kinds",
        "moex_dams.rules.package_invariants.check_alignment_dual_path_consistency",
        # assess → catalog-topology / governance-assignments / structural
        "moex_dams.rules.catalog_topology.check_catalog_topology",
        "moex_dams.rules.governance_assignments.check_governance_assignments",
        "moex_dams.rules.structural.check_structural_data",
        # assess → model-requirements (formal_checks)
        "moex_dams.rules.conceptual_entity.check_conceptual_entities",
        "moex_dams.rules.relation_terms.check_relation_terms",
        "moex_dams.rules.technical_assets.check_parent_ref_cycles",
        "moex_dams.rules.technical_assets.check_unique_asset_keys",
        "moex_dams.rules.technical_assets.check_asset_kind_allowlists",
        "moex_dams.rules.technical_assets.check_carrier_refs_are_data_carriers",
        "moex_dams.rules.technical_assets.check_direction_forbidden",
        "moex_dams.rules.technical_assets.check_mapping_endpoint_types",
        "moex_dams.rules.technical_assets.check_operation_interface_ref",
        "moex_dams.rules.technical_assets.check_in_memory_location",
        "moex_dams.rules.data_structure.check_source_pointer_requires_artifact",
        "moex_dams.rules.data_structure.check_schema_dialect_format_family",
        "moex_dams.rules.data_structure.check_node_kind_shape",
        "moex_dams.rules.data_structure.check_reference_node_target",
        "moex_dams.rules.data_structure.check_message_refs_kinds",
        "moex_dams.rules.data_structure.check_node_edge_cycles",
        "moex_dams.rules.data_structure.check_relational_slots",
        "moex_dams.rules.data_structure.check_local_key_unique",
        "moex_dams.rules.data_structure.check_root_local_key",
        "moex_dams.rules.data_structure.check_occurs_bounds",
        "moex_dams.rules.data_structure.check_message_payload",
        "moex_dams.rules.semantic_layer.check_identifying_requires_is_identifying",
        # schema lint / Stage 0 validate-schemas — INV-026
        "moex_dams.rules.ontology_uris.check_ontology_uris",
        # check-manifest — INV-058
        "moex_dams.rules.repository_invariants.check_repository_element_id_uniqueness",
    }
)


@dataclass(frozen=True)
class RuleSet:
    phase: ConformancePhase
    assessment_id: str
    description: str
    run: Callable[[LinkMLImplementationBody], tuple[Diagnostic, ...]]


def run_rule_sets(
    body: LinkMLImplementationBody,
    sets: Sequence[RuleSet],
) -> list[tuple[RuleSet, tuple[Diagnostic, ...]]]:
    return [(rule_set, rule_set.run(body)) for rule_set in sets]


def _repo_root_from_body(body: LinkMLImplementationBody) -> Path | None:
    src = Path(body.source_path) if getattr(body, "source_path", None) else None
    if src is None:
        return None
    for parent in [src.parent, *src.parents]:
        if (parent / "model-assets").is_dir() and (parent / "packages").is_dir():
            return parent
    return None


def default_dams_rule_sets(repo: DamsAssetRepository) -> tuple[RuleSet, ...]:
    """Register LinkML validate + DAMS structural/reference/identifier/L2 rules.

    L2 package invariants (ADR-045 / Wave C+), catalog topology (ADR-048), and
    governance assignments (ADR-049) run here so ``assess_implementation`` and
    the validate CLI apply the same checks as the constraint-matrix L2 runner.
    Complementary L2 modules (technical_assets, semantic_layer, conceptual,
    relation_terms) remain on the ``assessment:model-requirements`` path via
    ``formal_checks``.
    """

    def run_linkml(body: LinkMLImplementationBody) -> tuple[Diagnostic, ...]:
        return repo.validate_standard(body)

    resolver = None
    if repo.default_schema_path is not None:
        resolver = build_dams_curie_resolver(repo.default_schema_path)

    def run_identifiers(body: LinkMLImplementationBody) -> tuple[Diagnostic, ...]:
        if resolver is None:
            return ()
        return check_identifiers(body, resolver=resolver)

    def run_package_invariants(
        body: LinkMLImplementationBody,
    ) -> tuple[Diagnostic, ...]:
        data = body.data
        if not isinstance(data, dict):
            return ()
        return tuple(check_package_invariants(data))

    def run_catalog_topology(
        body: LinkMLImplementationBody,
    ) -> tuple[Diagnostic, ...]:
        data = body.data
        if not isinstance(data, dict):
            return ()
        root = _repo_root_from_body(body)
        return tuple(check_catalog_topology(data, repo_root=root))

    def run_governance_assignments(
        body: LinkMLImplementationBody,
    ) -> tuple[Diagnostic, ...]:
        data = body.data
        if not isinstance(data, dict):
            return ()
        as_of: str | None = None
        root = _repo_root_from_body(body)
        if root is not None:
            try:
                from moex_dams.governance.materialize import load_as_of

                as_of = load_as_of(root)
            except Exception:
                as_of = None
        return tuple(check_governance_assignments(data, as_of=as_of))

    return (
        RuleSet(
            phase=ConformancePhase.STANDARD_SYNTAX,
            assessment_id="assessment:standard-syntax",
            description="LinkML standard validation",
            run=run_linkml,
        ),
        RuleSet(
            phase=ConformancePhase.CORPORATE_SEMANTICS,
            assessment_id="assessment:structural",
            description="DAMS structural rules",
            run=check_structural,
        ),
        RuleSet(
            phase=ConformancePhase.CORPORATE_SEMANTICS,
            assessment_id="assessment:references",
            description="DAMS reference integrity rules",
            run=check_references,
        ),
        RuleSet(
            phase=ConformancePhase.CORPORATE_SEMANTICS,
            assessment_id="assessment:identifiers",
            description="CURIE/URI prefix rules",
            run=run_identifiers,
        ),
        RuleSet(
            phase=ConformancePhase.CORPORATE_SEMANTICS,
            assessment_id="assessment:dams-levels",
            description="DAMS enterprise-conceptual / solution package rules",
            run=check_dams_model_level,
        ),
        RuleSet(
            phase=ConformancePhase.CORPORATE_SEMANTICS,
            assessment_id="assessment:package-invariants",
            description="Wave C package L2 invariants (INV-042..053 subset)",
            run=run_package_invariants,
        ),
        RuleSet(
            phase=ConformancePhase.CORPORATE_SEMANTICS,
            assessment_id="assessment:catalog-topology",
            description="Catalog topology L2 invariants (INV-038..041, ADR-048)",
            run=run_catalog_topology,
        ),
        RuleSet(
            phase=ConformancePhase.CORPORATE_SEMANTICS,
            assessment_id="assessment:governance-assignments",
            description="Governance assignment L2 invariants (INV-054..056, ADR-049)",
            run=run_governance_assignments,
        ),
        RuleSet(
            phase=ConformancePhase.CORPORATE_SEMANTICS,
            assessment_id="assessment:model-requirements",
            description="IT-solution requirements catalog formal_checks (ADR-013)",
            run=check_formal_requirements_for_repo,
        ),
    )
