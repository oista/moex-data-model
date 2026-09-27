"""Architecture fitness tests for modeling-kernel public APIs."""

from __future__ import annotations

from typing import get_type_hints

from moex_modeling.standards.public import StandardProvider


def test_standard_provider_has_distinct_body_types() -> None:
    """StandardProvider must not collapse specification body and
    implementation body into a single TypeVar — that was Critical #2
    in docs/architecture review 2026-09-27."""
    params = getattr(StandardProvider, "__parameters__", ())
    assert len(params) >= 2, "StandardProvider needs TSpecBody and TImplBody"
    assert params[0] is not params[1], (
        "spec and implementation body type parameters must differ"
    )

    hints = get_type_hints(StandardProvider.load_specification_body)
    impl_hints = get_type_hints(StandardProvider.load_implementation_body)
    assert hints["return"] is not impl_hints["return"], (
        "spec and implementation body types must differ per standard"
    )
