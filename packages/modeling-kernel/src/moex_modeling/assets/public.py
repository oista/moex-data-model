"""Asset resolution ports — composition over StandardProvider."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from moex_modeling.shared.types import ImplementationRef, SpecificationRef


@runtime_checkable
class SchemaRepository(Protocol):
    """
    Resolve specification assets and load bodies via a StandardProvider.

    Does not replace StandardProvider — composes path resolution + load.
    """

    def resolve_specification_path(self, specification: SpecificationRef) -> Path: ...

    def load_specification(self, specification: SpecificationRef) -> Any: ...

    def load_implementation(
        self,
        implementation: ImplementationRef,
        *,
        path: Path | str,
    ) -> Any: ...


__all__ = ["SchemaRepository"]
