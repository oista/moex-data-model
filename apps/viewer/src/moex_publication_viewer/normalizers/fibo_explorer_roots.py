"""Wrap FIBO profile explorer roots: Overview / metamodel groups / Implementations."""

from __future__ import annotations

from moex_publication_viewer.models.publication_models import PublicationItem


def _section_ref(section_id: str, title: str) -> PublicationItem:
    return PublicationItem(
        id=f"section:{section_id}",
        title=title,
        description=None,
        attributes={
            "kind": "section_ref",
            "section_id": section_id,
        },
    )


def wrap_fibo_explorer_roots(
    metamodel_groups: list[PublicationItem],
) -> list[PublicationItem]:
    """Prefix Overview and append Implementations around metamodel explorer groups."""
    overview_root = PublicationItem(
        id="group:fibo-overview",
        title="Overview",
        description="FIBO ontology profile README.",
        attributes={
            "kind": "group",
            "section_root": "overview",
            "section_id": "overview",
            "purpose": "Entry into the FIBO organizational metamodel (not domain classes).",
            "member_ids": ["section:overview"],
        },
        children=[_section_ref("overview", "Overview")],
    )
    impls_root = PublicationItem(
        id="group:implementations",
        title="Реализации",
        description="FIBO release content registered against this profile.",
        attributes={
            "kind": "group",
            "section_root": "implementations",
            "purpose": "Transition to release / preview content (conforms_to FIBO profile).",
            "structure_why": "List from architecture-catalog; glossary explorer lives in Impl module.",
            "member_ids": [],
        },
        children=[],
    )
    return [overview_root, *metamodel_groups, impls_root]


def is_fibo_profile_section(tags: list[str] | None) -> bool:
    return "fibo-profile" in (tags or [])
