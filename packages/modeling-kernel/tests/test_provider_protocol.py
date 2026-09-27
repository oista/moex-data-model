"""Protocol shape checks living next to the package."""

from __future__ import annotations

from typing import get_type_hints

from moex_modeling.standards.public import StandardProvider


def test_provider_type_params_are_distinct() -> None:
    t_spec, t_impl, *_ = StandardProvider.__parameters__
    assert t_spec is not t_impl
    assert get_type_hints(StandardProvider.load_specification_body)["return"] is t_spec
    assert get_type_hints(StandardProvider.load_implementation_body)["return"] is t_impl
