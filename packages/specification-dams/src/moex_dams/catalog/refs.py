"""Parse catalog CURIEs used by DataFlow.integration_ref (ADR-048)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CatalogRef:
    catalog: str
    kind: str
    external_id: str

    @property
    def curie(self) -> str:
        return f"{self.catalog}:{self.kind}/{self.external_id}"


def parse_catalog_ref(value: str | None) -> CatalogRef | None:
    """Parse ``{catalog}:{kind}/{external_id}``; return None if shape is wrong."""
    if not value or not isinstance(value, str):
        return None
    text = value.strip()
    if ":" not in text or "/" not in text:
        return None
    catalog, rest = text.split(":", 1)
    if not catalog or "/" not in rest:
        return None
    kind, external_id = rest.split("/", 1)
    if not kind or not external_id:
        return None
    if ":" in kind or "/" in kind:
        return None
    return CatalogRef(catalog=catalog, kind=kind, external_id=external_id)
