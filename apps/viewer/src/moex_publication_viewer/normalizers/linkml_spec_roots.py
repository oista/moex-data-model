"""Wrap non-DAMS LinkML explorer package groups under ADR-016 roots (ADR-019 nav)."""

from __future__ import annotations

from moex_publication_viewer.models.publication_models import PublicationItem


def wrap_linkml_specification_roots(
    package_groups: list[PublicationItem],
) -> list[PublicationItem]:
    """Place schema packages under Classes; add empty Overview for orphan fold-in.

    Used when the explorer is a plain LinkML schema projection (e.g. moex.dsp),
    not the DAMS triple-root wrapper. Avoids package folders as top-level siblings
    of publication sections («Разделы» / «Dsp»).
    """
    if not package_groups:
        return package_groups
    if any((g.attributes or {}).get("section_root") for g in package_groups):
        return package_groups

    overview = PublicationItem(
        id="group:overview",
        title="Overview",
        description="Publication overview and linked sections.",
        attributes={
            "kind": "group",
            "section_root": "overview",
            "purpose": "Entry point for module overview and non-explorer sections.",
            "structure_why": "ADR-016/019: orphans fold into Overview, never «Разделы».",
            "member_ids": [],
            "class_count": 0,
            "enum_count": 0,
        },
        children=[],
    )
    class_count = sum(
        int((g.attributes or {}).get("class_count") or 0) for g in package_groups
    )
    enum_count = sum(
        int((g.attributes or {}).get("enum_count") or 0) for g in package_groups
    )
    classes = PublicationItem(
        id="group:classes",
        title="Classes",
        description="Schema packages and types of this LinkML specification body.",
        attributes={
            "kind": "group",
            "section_root": "classes",
            "purpose": "LinkML classes/enums grouped by schema package.",
            "structure_why": "Package folders nest under Classes, not as Spec siblings.",
            "member_ids": [g.id for g in package_groups],
            "class_count": class_count,
            "enum_count": enum_count,
        },
        children=list(package_groups),
    )
    return [overview, classes]
