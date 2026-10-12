"""Pydantic models must not drift from LinkML slots (ADR-047)."""

from __future__ import annotations

from pathlib import Path

from linkml_runtime.utils.schemaview import SchemaView

from moex_repository_loader.models import (
    DocumentRef,
    RepositoryLockEntry,
    RepositoryLockHeader,
    RepositoryManifest,
)

REPO = Path(__file__).resolve().parents[3]
SCHEMA = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-repository-manifest"
    / "0.1"
    / "schemas"
    / "moex-repository-manifest.yaml"
)


def _slots(sv: SchemaView, class_name: str) -> set[str]:
    return set(sv.class_slots(class_name))


def test_pydantic_fields_match_linkml_slots() -> None:
    sv = SchemaView(str(SCHEMA))
    mapping = {
        "RepositoryManifest": RepositoryManifest,
        "DocumentRef": DocumentRef,
        "RepositoryLockHeader": RepositoryLockHeader,
        "RepositoryLockEntry": RepositoryLockEntry,
    }
    for cname, model in mapping.items():
        assert set(model.model_fields) == _slots(sv, cname), cname
