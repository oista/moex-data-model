"""Facade: ModelPackage ↔ DBML round-trip."""

from __future__ import annotations

from typing import Any

from moex_dams.projection.dbml import project_model_package_to_dbml

from moex_drawdb.domain import ModelPatch, Profile, ProjectedDiagram
from moex_drawdb.parse import parse_dbml
from moex_drawdb.patch import apply_model_patch, compute_model_patch


class DrawDbProjectionService:
    """ADR-005/006 projection service for drawDB sessions."""

    def to_dbml(self, package: dict[str, Any], *, profile: Profile) -> str:
        return project_model_package_to_dbml(package, profile=profile)

    def parse(self, dbml: str) -> ProjectedDiagram:
        return parse_dbml(dbml)

    def compute_patch(
        self,
        base_package: dict[str, Any],
        diagram: ProjectedDiagram,
        *,
        profile: Profile,
    ) -> ModelPatch:
        return compute_model_patch(base_package, diagram, profile=profile)

    def apply_patch(
        self, base_package: dict[str, Any], patch: ModelPatch
    ) -> dict[str, Any]:
        return apply_model_patch(base_package, patch)

    def from_dbml(
        self,
        base_package: dict[str, Any],
        dbml: str,
        *,
        profile: Profile,
    ) -> tuple[dict[str, Any], ModelPatch]:
        diagram = self.parse(dbml)
        patch = self.compute_patch(base_package, diagram, profile=profile)
        merged = self.apply_patch(base_package, patch)
        return merged, patch
