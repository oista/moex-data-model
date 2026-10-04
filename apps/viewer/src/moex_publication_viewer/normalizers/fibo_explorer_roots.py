"""Wrap FIBO profile explorer roots: Overview / Classes / Modules / Identity / Glossary / Implementations."""

from __future__ import annotations

from moex_publication_viewer.models.publication_models import PublicationItem

_MODULES_GROUP_IDS = frozenset({"group:fibo-domains"})
_IDENTITY_GROUP_IDS = frozenset({"group:fibo-patterns", "group:fibo-annotations"})


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
    metamodel_groups: list[PublicationItem],
) -> list[PublicationItem]:
    """Build ontology-profile roots (ADR-024): Overview, Classes, Modules, Identity, Glossary, Impls."""
    modules_kids = [
        g for g in metamodel_groups if g.id in _MODULES_GROUP_IDS
    ]
    identity_kids = [
        g for g in metamodel_groups if g.id in _IDENTITY_GROUP_IDS
    ]
    # Any unexpected groups stay under Modules so they are not dropped.
    known = _MODULES_GROUP_IDS | _IDENTITY_GROUP_IDS
    modules_kids.extend(g for g in metamodel_groups if g.id not in known)

    overview_root = PublicationItem(
        id="group:overview",
        title="Overview",
        description="FIBO ontology profile README.",
        attributes={
            "kind": "group",
            "section_root": "overview",
            "purpose": "Entry into the FIBO organizational profile (ADR-024 ontology).",
            "member_ids": ["section:overview"],
        },
        children=[_section_ref("overview", "Overview")],
    )
    classes_root = PublicationItem(
        id="group:classes",
        title="Классы",
        description="OWL class hierarchy by domain (subClassOf); filled at build from glossary source.",
        attributes={
            "kind": "group",
            "section_root": "classes",
            "purpose": "Primary class nav for ontology profile (ADR-024).",
            "structure_why": "Same entities as Glossary; tree via parent_local_name / source_domain.",
            "member_ids": [],
            "class_count": 0,
        },
        children=[],
    )
    modules_root = PublicationItem(
        id="group:schema-files",
        title="Модули",
        description="Domains, modules, and ontology documents (owl:imports axis).",
        attributes={
            "kind": "group",
            "section_root": "schema-files",
            "purpose": "Organizational modules of the FIBO profile (ADR-024 schema-files).",
            "structure_why": "Domains → modules → ontology documents (ONTOLOGY_GUIDE).",
            "member_ids": [g.id for g in modules_kids],
            "file_count": len(modules_kids),
        },
        children=modules_kids,
    )
    identity_root = PublicationItem(
        id="group:identity",
        title="Identity",
        description="IRI, prefix, and annotation conventions for the profile.",
        attributes={
            "kind": "group",
            "section_root": "identity",
            "purpose": "Identity axis: IRI/prefix patterns and annotation requirements.",
            "member_ids": [g.id for g in identity_kids],
        },
        children=identity_kids,
    )
    glossary_root = PublicationItem(
        id="group:glossary",
        title="Glossary",
        description="Flat alphabetical view of the same OWL classes (ADR-024).",
        attributes={
            "kind": "group",
            "section_root": "glossary",
            "purpose": "Glossary is a view of classes, not a separate dataset.",
            "member_ids": ["section:glossary"],
        },
        children=[_section_ref("glossary", "Glossary")],
    )
    impls_root = PublicationItem(
        id="group:implementations",
        title="Реализации",
        description="FIBO release / application content registered against this profile.",
        attributes={
            "kind": "group",
            "section_root": "implementations",
            "purpose": "Transition to release / preview content (conforms_to FIBO profile).",
            "structure_why": "List from architecture-catalog; bodies live in Impl modules.",
            "member_ids": [],
        },
        children=[],
    )
    return [
        overview_root,
        classes_root,
        modules_root,
        identity_root,
        glossary_root,
        impls_root,
    ]


def is_fibo_profile_section(tags: list[str] | None) -> bool:
    return "fibo-profile" in (tags or [])
