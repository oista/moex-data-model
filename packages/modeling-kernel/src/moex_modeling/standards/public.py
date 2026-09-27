"""Public ports for standard providers."""

from __future__ import annotations

from typing import Generic, Protocol, TypeVar, runtime_checkable

from moex_modeling.conformance.domain import Diagnostic
from moex_modeling.shared.enums import StandardFamily
from moex_modeling.shared.types import ImplementationRef, SpecificationRef
from moex_modeling.standards.domain import ModelingStandard

TSpecBody = TypeVar("TSpecBody")
TImplBody = TypeVar("TImplBody")
TElement = TypeVar("TElement")


class LoadedImplementation(Generic[TImplBody]):
    """Implementation envelope coordinates plus typed body."""

    __slots__ = ("ref", "body", "source_uri")

    def __init__(
        self,
        *,
        ref: ImplementationRef,
        body: TImplBody,
        source_uri: str | None = None,
    ) -> None:
        self.ref = ref
        self.body = body
        self.source_uri = source_uri


@runtime_checkable
class StandardProvider(Protocol, Generic[TSpecBody, TImplBody, TElement]):
    """
    Load and validate standard-specific bodies.

    ``TSpecBody`` (schema / normative body) and ``TImplBody`` (instance body)
    MUST be distinct type parameters — never a single shared TypeVar.
    """

    family: StandardFamily

    def load_specification_body(
        self,
        specification: SpecificationRef,
        *,
        path: str,
    ) -> TSpecBody: ...

    def load_implementation_body(
        self,
        implementation: ImplementationRef,
        *,
        path: str,
    ) -> TImplBody: ...

    def enumerate_elements(self, body: TImplBody) -> tuple[TElement, ...]: ...

    def validate_standard(self, body: TImplBody) -> tuple[Diagnostic, ...]: ...


__all__ = [
    "LoadedImplementation",
    "ModelingStandard",
    "StandardProvider",
    "TElement",
    "TImplBody",
    "TSpecBody",
]
