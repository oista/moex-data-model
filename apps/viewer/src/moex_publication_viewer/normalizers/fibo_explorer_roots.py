"""Wrap FIBO profile explorer roots: Overview / Taxonomy / Glossary / Implementations."""

from __future__ import annotations

from moex_publication_viewer.models.publication_models import PublicationItem


def _section_ref(section_id: str, title: str) -> PublicationItem:
    return PublicationItem(
        id=f"section:{section_id}",
        title=title,
        description=f"Open publication section «{title}».",
        attributes={
            "kind": "section_ref",
            "section_id": section_id,
            "description": f"Open publication section «{title}».",
        },
    )


def wrap_fibo_explorer_roots(
    taxonomy_groups: list[PublicationItem],
) -> list[PublicationItem]:
    """Build ontology-profile roots: Overview, Taxonomy, Glossary, Implementations."""
    overview_root = PublicationItem(
        id="group:overview",
        title="Overview",
        description="FIBO ontology profile README.",
        attributes={
            "kind": "group",
            "section_root": "overview",
            "section_id": "overview",
            "purpose": "Entry into the FIBO organizational profile (ADR-016 ontology).",
            "member_ids": ["section:overview"],
        },
        children=[_section_ref("overview", "Overview")],
    )
    taxonomy_root = PublicationItem(
        id="group:taxonomy",
        title="Taxonomy",
        description="Domains, modules, ontology documents, IRI patterns, annotations.",
        attributes={
            "kind": "group",
            "section_root": "taxonomy",
            "purpose": "Primary navigation axis for ontology profile (ADR-016).",
            "structure_why": "Domains → modules → ontology documents; patterns and annotations.",
            "member_ids": [g.id for g in taxonomy_groups],
        },
        children=taxonomy_groups,
    )
    glossary_root = PublicationItem(
        id="group:glossary",
        title="Glossary",
        description="Profile terms (domains, modules, IRI and annotation conventions).",
        attributes={
            "kind": "group",
            "section_root": "glossary",
            "section_id": "glossary",
            "purpose": "Natural-language terms for the FIBO profile.",
            "member_ids": ["section:glossary"],
        },
        children=[_section_ref("glossary", "Glossary")],
    )
    classes_root = PublicationItem(
        id="group:classes",
        title="All classes",
        description="Alphabetical ontology-list (IRI, definition) — recommended, not primary nav.",
        attributes={
            "kind": "group",
            "section_root": "classes",
            "purpose": "ontology-list renderer for profile ontology (ADR-016 recommended).",
            "member_ids": [],
        },
        children=[],
    )
    identity_root = PublicationItem(
        id="group:identity",
        title="Identity",
        description="IRI and namespace conventions for the profile.",
        attributes={
            "kind": "group",
            "section_root": "identity",
            "purpose": "Recommended identity axis (IRI patterns live under taxonomy too).",
            "member_ids": [],
        },
        children=[],
    )
    impls_root = PublicationItem(
        id="group:implementations",
        title="Реализации",
        description="FIBO release content registered against this profile.",
        attributes={
            "kind": "group",
            "section_root": "implementations",
            "purpose": "Transition to release / preview content (conforms_to FIBO profile).",
            "structure_why": "List from architecture-catalog; domain glossary lives in Impl module.",
            "member_ids": [],
        },
        children=[],
    )
    return [
        overview_root,
        taxonomy_root,
        glossary_root,
        classes_root,
        identity_root,
        impls_root,
    ]


def is_fibo_profile_section(tags: list[str] | None) -> bool:
    return "fibo-profile" in (tags or [])
