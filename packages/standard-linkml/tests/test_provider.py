"""LinkML StandardProvider: distinct spec/impl bodies."""

from __future__ import annotations

from pathlib import Path

from moex_modeling import ImplementationRef, SpecificationRef, StandardFamily

from moex_standard_linkml.domain.body import (
    LinkMLImplementationBody,
    LinkMLSpecificationBody,
)
from moex_standard_linkml.provider import LinkMLStandardProvider

REPO_ROOT = Path(__file__).resolve().parents[3]
DAMS_SCHEMA = (
    REPO_ROOT
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "schemas"
    / "moex-dams.yaml"
)
TRADING = (
    REPO_ROOT
    / "model-assets"
    / "implementations"
    / "solutions"
    / "trading-platform"
    / "trading-solution-model.yaml"
)


def test_load_specification_and_implementation_are_distinct_types() -> None:
    provider = LinkMLStandardProvider(default_schema_path=DAMS_SCHEMA)
    spec_ref = SpecificationRef(
        specification_id="moex:spec:dams",
        specification_version="0.1.0",
        specification_revision="0.1.0",
    )
    impl_ref = ImplementationRef(
        implementation_id="moex:implementation:trading:1.0.0",
        implementation_revision="1.0.0",
    )

    spec_body = provider.load_specification_body(spec_ref, path=str(DAMS_SCHEMA))
    impl_body = provider.load_implementation_body(impl_ref, path=str(TRADING))

    assert isinstance(spec_body, LinkMLSpecificationBody)
    assert isinstance(impl_body, LinkMLImplementationBody)
    assert type(spec_body) is not type(impl_body)
    assert provider.family is StandardFamily.LINKML
    assert "ModelPackage" in spec_body.class_names or "MOEXModelRepository" in (
        spec_body.root_class or ""
    )
    assert impl_body.element_id == "dams:model/trading/1.0.0"


def test_enumerate_and_validate_trading_solution() -> None:
    provider = LinkMLStandardProvider(default_schema_path=DAMS_SCHEMA)
    spec_ref = SpecificationRef(
        specification_id="moex:spec:dams",
        specification_version="0.1.0",
        specification_revision="0.1.0",
    )
    impl_ref = ImplementationRef(
        implementation_id="moex:implementation:trading:1.0.0",
        implementation_revision="1.0.0",
    )
    provider.load_specification_body(spec_ref, path=str(DAMS_SCHEMA))
    impl_body = provider.load_implementation_body(impl_ref, path=str(TRADING))

    elements = provider.enumerate_elements(impl_body)
    ids = {e.element_id for e in elements}
    # ADR-029: Client concept lives in enterprise SoT, not local conceptual_entities
    assert "dams:concept/Client" not in ids
    assert "dams:logical/trading/Client" in ids
    assert "dams:mapping/trading/client-realizes-client" in ids

    diagnostics = provider.validate_standard(impl_body)
    errors = [d for d in diagnostics if d.severity.value in {"error", "fatal"}]
    assert not errors, diagnostics
