"""Tests for ImplementationCatalog port and id → slug helper."""

from __future__ import annotations

from pathlib import Path

from moex_modeling import (
    ImplementationAsset,
    ImplementationCatalog,
    PublicationTarget,
)
from moex_modeling.assets.domain import slug_and_version_from_id


def test_implementation_catalog_protocol_is_runtime_checkable() -> None:
    asset = ImplementationAsset(
        id="moex:implementation:mdm:0.1.0",
        slug="mdm",
        title="MDM",
        version="0.1.0",
        implementation_kind="linkml",
        implementation_profile="dams-data-model",
        dams_model_level="solution",
        envelope_path=Path("implementation.yaml"),
        body_path=Path("body.yaml"),
        specification_envelope_path=None,
        publication_manifest_path=None,
    )

    class _Stub:
        def list(self) -> tuple[ImplementationAsset, ...]:
            return (asset,)

        def resolve(self, token: str) -> ImplementationAsset:
            return asset

        def load_body(self, token: str) -> str:
            return "id: x\n"

        def resolve_schema(self, token: str) -> Path:
            return Path("schema.yaml")

        def publication_target(self, token: str) -> PublicationTarget:
            return PublicationTarget(repo_path="body.yaml", manifest_path=None)

    assert isinstance(_Stub(), ImplementationCatalog)


def test_slug_and_version_from_id() -> None:
    assert slug_and_version_from_id("moex:implementation:trading:1.0.0") == (
        "trading",
        "1.0.0",
    )
    assert slug_and_version_from_id(
        "moex:implementation:client-accounts-csv-draft:0.1"
    ) == ("client-accounts-csv-draft", "0.1")
    assert slug_and_version_from_id(
        "moex:implementation:moex-hierarchy:0.1"
    ) == ("moex-hierarchy", "0.1")
