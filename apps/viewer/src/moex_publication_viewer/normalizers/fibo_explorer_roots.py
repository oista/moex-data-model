"""Wrap FIBO profile explorer roots: Overview / Classes / Modules / Identity / Implementations."""

from __future__ import annotations

from moex_publication_viewer.models.publication_models import PublicationItem
from moex_publication_viewer.normalizers.spec_glossary_tree import (
    make_overview_glossary_folder,
)

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
    *,
    glossary_folders: list[PublicationItem] | None = None,
) -> list[PublicationItem]:
    """Build ontology-profile roots (ADR-024): Overview(+Glossary), Classes, Modules, Identity, Impls."""
    modules_kids = [
        g for g in metamodel_groups if g.id in _MODULES_GROUP_IDS
    ]
    identity_kids = [
        g for g in metamodel_groups if g.id in _IDENTITY_GROUP_IDS
    ]
    # Any unexpected groups stay under Modules so they are not dropped.
    known = _MODULES_GROUP_IDS | _IDENTITY_GROUP_IDS
    modules_kids.extend(g for g in metamodel_groups if g.id not in known)

    glossary_folder = make_overview_glossary_folder(glossary_folders)
    overview_children = [
        _section_ref("overview", "Overview"),
        glossary_folder,
    ]
    overview_root = PublicationItem(
        id="group:overview",
        title="Overview",
        description="FIBO ontology profile README.",
        attributes={
            "kind": "group",
            "section_root": "overview",
            "purpose": "Entry into the FIBO organizational profile (ADR-024 ontology).",
            "member_ids": [c.id for c in overview_children],
        },
        children=overview_children,
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
        impls_root,
    ]


def is_fibo_profile_section(tags: list[str] | None) -> bool:
    return "fibo-profile" in (tags or [])
