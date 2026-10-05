"""Compile manifests into PublicationModule list and render HTML."""

from __future__ import annotations

import json
from pathlib import Path

from moex_publication_viewer.catalog_loader import catalog_path, load_architecture_catalog
from moex_publication_viewer.discovery import discover_manifest_paths
from moex_publication_viewer.manifest_loader import load_manifest, resolve_source_path
from moex_publication_viewer.models.catalog_models import ArchitectureCatalog
from moex_publication_viewer.models.publication_models import (
    PublicationItem,
    PublicationModule,
)
from moex_publication_viewer.normalizers import get_normalizer
from moex_publication_viewer.normalizers.base import NormalizeError
from moex_publication_viewer.normalizers.edit_targets import relativize_module_edit_targets
from moex_publication_viewer.normalizers.helpers import items_to_domain_explorer
from moex_publication_viewer.normalizers.linkml_normalizer import clear_schema_view_cache
from moex_publication_viewer.normalizers.implementation_glossary import (
    IMPLEMENTATIONS_GLOSSARY_ID,
    IMPLEMENTATIONS_GLOSSARY_NAV_ID,
    build_implementation_glossary_section,
)
from moex_publication_viewer.normalizers.hierarchy_projection import (
    HIERARCHY_CATALOG_ID,
    enrich_dams_hierarchy_module,
)
from moex_publication_viewer.normalizers.spec_glossary_tree import (
    OVERVIEW_GLOSSARY_ID,
    build_ontology_glossary_tree,
    flat_glossary_items_from_leaves,
    make_overview_glossary_folder,
)
from moex_publication_viewer.renderers.html_renderer import render_viewer
from moex_publication_viewer.validators import (
    ValidationError,
    check_catalog_publication_contract_gate,
    check_publication_profiles,
    validate_architecture_catalog,
    validate_manifests,
)
from moex_publication_viewer.publication_contract import run_publication_contracts
from moex_publication_viewer.publication_profiles import get_renderer_mode

PACKAGE_DIR = Path(__file__).resolve().parent
VIEWER_ROOT = PACKAGE_DIR.parent.parent  # apps/viewer/
DAMS_MODULE_ID = "moex:module:dams"
DAMS_CATALOG_SPEC_ID = "moex-dams"
FIBO_PROFILE_MODULE_ID = "moex:module:fibo-profile"
FIBO_PROFILE_CATALOG_SPEC_ID = "moex-fibo-profile"
ONTOLOGY_CATALOG_MODULE_ID = "moex:module:ontology-catalog"
DSP_MODULE_ID = "moex:module:dsp"

# Stay at Реализации root (not nested under folders).
_DAMS_IMPL_ROOT_IDS = frozenset(
    {
        "moex-dsp",
        "moex-enterprise-conceptual-model",
        HIERARCHY_CATALOG_ID,
    }
)
# Nested under «ИТ-решения»; everything else (except root) → «Проекты».
_DAMS_IMPL_IT_SOLUTION_IDS = frozenset(
    {
        "mdm-solution",
        "ucd-solution",
        "crm-solution",
        "esed-solution",
    }
)


def _impl_folder(
    *,
    folder_id: str,
    title: str,
    description: str,
    children: list[PublicationItem],
    extra_attrs: dict | None = None,
) -> PublicationItem:
    attrs: dict = {
        "kind": "group",
        "group_style": "section_folder",
        "member_ids": [c.id for c in children],
        "impl_count": len(children),
    }
    if extra_attrs:
        attrs.update(extra_attrs)
    return PublicationItem(
        id=folder_id,
        title=title,
        description=description,
        attributes=attrs,
        children=children,
    )


def group_dams_implementation_children(
    children: list[PublicationItem],
) -> list[PublicationItem]:
    """
    Nest DAMS Impl refs: ИТ-решения → Проекты → root (dsp, conceptual).

    Catalog order inside each bucket is preserved.
    """
    it_items: list[PublicationItem] = []
    project_items: list[PublicationItem] = []
    root_items: list[PublicationItem] = []
    for child in children:
        if child.id in _DAMS_IMPL_ROOT_IDS:
            root_items.append(child)
        elif child.id in _DAMS_IMPL_IT_SOLUTION_IDS:
            it_items.append(child)
        else:
            project_items.append(child)

    grouped: list[PublicationItem] = []
    if it_items:
        grouped.append(
            _impl_folder(
                folder_id="group:implementations-it-solutions",
                title="ИТ-решения",
                description="Реализации моделей данных ИТ-решений.",
                children=it_items,
            )
        )
    if project_items:
        grouped.append(
            _impl_folder(
                folder_id="group:implementations-projects",
                title="Проекты",
                description="Проектные и демо-реализации DAMS.",
                children=project_items,
            )
        )
    grouped.extend(root_items)
    return grouped


def compile_modules(
    root: Path,
    *,
    enforce_publication_contract: bool = False,
    dist_dir: Path | None = None,
) -> list[PublicationModule]:
    clear_schema_view_cache()
    paths = discover_manifest_paths(root)
    pairs = []
    for path in paths:
        manifest = load_manifest(path)
        if manifest is None:
            continue
        pairs.append((path, manifest))

    validate_manifests(pairs)

    modules: list[PublicationModule] = []
    errors: list[str] = []

    for path, manifest in pairs:
        sections = []
        for section in manifest.sections:
            source_path = resolve_source_path(path, section.source.path)
            try:
                if section.kind == "documentation":
                    from moex_publication_viewer.package_docs import PackageDocsNormalizer

                    normalizer = PackageDocsNormalizer()
                elif section.type == "mermaid-diagram":
                    from moex_publication_viewer.normalizers.mermaid_diagram_normalizer import (
                        MermaidDiagramNormalizer,
                    )

                    normalizer = MermaidDiagramNormalizer()
                elif section.type == "source-file":
                    from moex_publication_viewer.normalizers.source_file_normalizer import (
                        SourceFileNormalizer,
                    )

                    normalizer = SourceFileNormalizer()
                else:
                    normalizer = get_normalizer(section.source.format)
            except KeyError:
                errors.append(
                    f"{path}: unsupported source.format '{section.source.format}' "
                    f"in section '{section.id}'"
                )
                continue
            try:
                pub_section = normalizer.normalize(section, source_path)
            except NormalizeError as exc:
                errors.append(f"{path}: section '{section.id}': {exc}")
                continue
            has_mermaid = bool(
                (pub_section.attributes or {}).get("mermaid_source")
            )
            if not pub_section.items and not pub_section.content and not has_mermaid:
                errors.append(
                    f"{path}: section '{section.id}' is empty after normalize "
                    f"(source: {source_path})"
                )
                continue
            if pub_section.kind:
                pub_section.renderer_mode = get_renderer_mode(
                    pub_section.kind, manifest.profile
                )
            sections.append(pub_section)

        modules.append(
            PublicationModule(
                module_id=manifest.module_id,
                title=manifest.title,
                description=manifest.description,
                icon=manifest.icon,
                version=manifest.version,
                order=manifest.order,
                profile=manifest.profile,
                implements=[
                    ref.model_dump(exclude_none=True) for ref in manifest.implements
                ],
                conformance_status=getattr(manifest, "conformance_status", None),
                implementation_profile=getattr(
                    manifest, "implementation_profile", None
                ),
                dams_model_level=getattr(manifest, "dams_model_level", None),
                sections=sections,
                manifest_path=str(path),
            )
        )

    if errors:
        raise ValidationError(errors)

    modules.sort(key=lambda m: (m.order, m.title))
    relativize_module_edit_targets(modules, root.resolve())
    check_publication_profiles(modules)
    if enforce_publication_contract:
        run_publication_contracts(
            modules, root, hard_fail=True, dist_dir=dist_dir
        )
    return modules


def compile_catalog(root: Path, modules: list[PublicationModule]) -> ArchitectureCatalog | None:
    catalog = load_architecture_catalog(root)
    if catalog is None:
        return None
    validate_architecture_catalog(
        catalog,
        {m.module_id for m in modules},
        catalog_path=catalog_path(root),
    )
    return catalog


def _module_by_id(
    modules: list[PublicationModule], module_id: str | None
) -> PublicationModule | None:
    if not module_id:
        return None
    return next((m for m in modules if m.module_id == module_id), None)


# Publication section ids → DAMS model-level plaque / glossary glyph.
_SECTION_ID_NAV_GLYPH: dict[str, str] = {
    "conceptual": "cdm",
    "conceptual-erd": "cdm",
    "logical": "ldm",
    "logical-erd": "ldm",
    "physical": "pdm",
    "physical-erd": "pdm",
    "glossary": "glossary",
    "relation-terms": "glossary",
    "vocabularies": "glossary",
    "implementations-glossary": "glossary",
    "entity-hierarchy": "glossary",
    "artifact-model-body": "source_file",
    "artifact-envelope": "source_file",
    "artifact-relation-terms": "source_file",
    "artifact-vocabularies": "source_file",
}

# Full solution-model publish.yaml set → nest under Overview / model folders.
# ``conceptual`` (Conceptual entities links) is optional and nests under
# Логическая модель — solutions align to enterprise via conceptual_entity_refs
# (ADR-021 / ADR-029); there is no solution CDM folder.
_SOLUTION_NAV_REQUIRED_SECTION_IDS = frozenset(
    {
        "package",
        "logical",
        "physical",
        "slice-summary",
        "slice-nodes",
        "slice-relations",
        "model-assessment",
    }
)
_SOLUTION_NAV_OVERVIEW_IDS = ("package", "slice-summary", "slice-relations", "slice-nodes")
_SOLUTION_NAV_LOGICAL_IDS = ("logical", "conceptual", "logical-erd")
_SOLUTION_NAV_PHYSICAL_IDS = ("physical", "physical-erd")
_SOLUTION_NAV_REQUIREMENTS_IDS = ("model-assessment",)
_SOLUTION_NAV_DOCUMENTATION_IDS = ("documentation",)
_SOLUTION_NAV_ARTIFACT_IDS = ("artifact-model-body", "artifact-envelope")

# Enterprise conceptual (moex.concept-data-model) → Overview + CDM + Model glossary.
_ENTERPRISE_CONCEPTUAL_NAV_REQUIRED_SECTION_IDS = frozenset(
    {
        "overview",
        "conformance",
        "alignments",
        "glossary",
        "relation-terms",
        "vocabularies",
        "conceptual",
    }
)
_ENTERPRISE_CONCEPTUAL_NAV_OVERVIEW_IDS = ("overview", "conformance", "alignments")
_ENTERPRISE_CONCEPTUAL_NAV_CONCEPTUAL_IDS = (
    "conceptual",
    "conceptual-erd",
    "relationships",
)
_ENTERPRISE_CONCEPTUAL_NAV_GLOSSARY_IDS = (
    "glossary",
    "relation-terms",
    "vocabularies",
)
_ENTERPRISE_CONCEPTUAL_NAV_ARTIFACT_IDS = (
    "artifact-model-body",
    "artifact-relation-terms",
    "artifact-vocabularies",
    "artifact-envelope",
)

# moex.hierarchy → Overview / Entity hierarchy / Артефакты
_HIERARCHY_NAV_REQUIRED_SECTION_IDS = frozenset(
    {
        "overview",
        "conformance",
        "entity-hierarchy",
        "artifact-model-body",
    }
)
_HIERARCHY_NAV_OVERVIEW_IDS = ("overview", "conformance")
_HIERARCHY_NAV_ENTITY_IDS = ("entity-hierarchy",)
_HIERARCHY_NAV_ARTIFACT_IDS = ("artifact-model-body", "artifact-envelope")


def group_hierarchy_impl_nav(
    catalog_impl_id: str,
    leaves: list[PublicationItem],
) -> list[PublicationItem]:
    """Nest moex.hierarchy section_refs under Overview / Entity hierarchy / Артефакты."""
    by_sid: dict[str, PublicationItem] = {}
    for leaf in leaves:
        sid = (leaf.attributes or {}).get("section_id")
        if isinstance(sid, str) and sid:
            by_sid[sid] = leaf
    if not _HIERARCHY_NAV_REQUIRED_SECTION_IDS.issubset(by_sid):
        return leaves

    claimed: set[str] = set()

    def take(ids: tuple[str, ...]) -> list[PublicationItem]:
        out: list[PublicationItem] = []
        for sid in ids:
            leaf = by_sid.get(sid)
            if leaf is not None:
                out.append(leaf)
                claimed.add(sid)
        return out

    overview_kids = take(_HIERARCHY_NAV_OVERVIEW_IDS)
    overview = PublicationItem(
        id=f"implnav:{catalog_impl_id}:group:overview",
        title="Overview",
        description="Overview and conformance for the hierarchy view.",
        attributes={
            "kind": "group",
            "nav_group": "overview",
            "member_ids": [c.id for c in overview_kids],
        },
        children=overview_kids,
    )
    # Single section — leaf section_ref, not a one-child folder (folder click
    # would open a group card without Связи/Визуализация tabs).
    entity_kids = take(_HIERARCHY_NAV_ENTITY_IDS)
    entity_leaf = entity_kids[0] if entity_kids else None
    if entity_leaf is not None:
        attrs = dict(entity_leaf.attributes or {})
        attrs["nav_glyph"] = "glossary"
        attrs["description"] = (
            entity_leaf.description
            or "Entity relations picker and layered OWL/CDM/LDM visualization."
        )
        entity_leaf.attributes = attrs
        entity_leaf.title = "Entity hierarchy"
    artifact_kids = take(_HIERARCHY_NAV_ARTIFACT_IDS)
    for leaf in artifact_kids:
        attrs = dict(leaf.attributes or {})
        attrs["nav_glyph"] = "source_file"
        leaf.attributes = attrs
    leftovers = [
        leaf
        for leaf in leaves
        if (leaf.attributes or {}).get("section_id") not in claimed
    ]
    grouped: list[PublicationItem] = [overview]
    if entity_leaf is not None:
        grouped.append(entity_leaf)
    if artifact_kids:
        grouped.append(
            _impl_folder(
                folder_id=f"implnav:{catalog_impl_id}:group:artifacts",
                title="Артефакты",
                description="Generated hierarchy YAML and implementation envelope.",
                children=artifact_kids,
                extra_attrs={
                    "nav_glyph": "source_file",
                    "nav_group": "artifacts",
                },
            )
        )
    grouped.extend(leftovers)
    return grouped


def group_enterprise_conceptual_impl_nav(
    catalog_impl_id: str,
    leaves: list[PublicationItem],
) -> list[PublicationItem]:
    """Nest enterprise-conceptual section_refs under Overview / CDM / glossary.

    Only modules that carry the full conceptual section-id set are grouped;
    solutions / dsp / FIBO stay unchanged (caller falls through to solution nav).
    """
    by_sid: dict[str, PublicationItem] = {}
    for leaf in leaves:
        sid = (leaf.attributes or {}).get("section_id")
        if isinstance(sid, str) and sid:
            by_sid[sid] = leaf
    if not _ENTERPRISE_CONCEPTUAL_NAV_REQUIRED_SECTION_IDS.issubset(by_sid):
        return leaves

    claimed: set[str] = set()

    def take(ids: tuple[str, ...]) -> list[PublicationItem]:
        out: list[PublicationItem] = []
        for sid in ids:
            leaf = by_sid.get(sid)
            if leaf is not None:
                out.append(leaf)
                claimed.add(sid)
        return out

    overview_kids = take(_ENTERPRISE_CONCEPTUAL_NAV_OVERVIEW_IDS)
    overview = PublicationItem(
        id=f"implnav:{catalog_impl_id}:group:overview",
        title="Overview",
        description="Overview, conformance, and external alignments.",
        attributes={
            "kind": "group",
            "nav_group": "overview",
            "member_ids": [c.id for c in overview_kids],
        },
        children=overview_kids,
    )
    conceptual_kids = take(_ENTERPRISE_CONCEPTUAL_NAV_CONCEPTUAL_IDS)
    glossary_kids = take(_ENTERPRISE_CONCEPTUAL_NAV_GLOSSARY_IDS)
    for leaf in glossary_kids:
        attrs = dict(leaf.attributes or {})
        attrs["nav_glyph"] = "glossary"
        leaf.attributes = attrs
    glossary = PublicationItem(
        id=f"implnav:{catalog_impl_id}:group:glossary",
        title="Model glossary",
        description="Model glossary, relation terms, and controlled vocabularies.",
        attributes={
            "kind": "group",
            "nav_group": "glossary",
            "nav_glyph": "glossary",
            "member_ids": [c.id for c in glossary_kids],
        },
        children=glossary_kids,
    )
    artifact_kids = take(_ENTERPRISE_CONCEPTUAL_NAV_ARTIFACT_IDS)
    for leaf in artifact_kids:
        attrs = dict(leaf.attributes or {})
        attrs["nav_glyph"] = "source_file"
        leaf.attributes = attrs
    leftovers = [
        leaf
        for leaf in leaves
        if (leaf.attributes or {}).get("section_id") not in claimed
    ]
    grouped: list[PublicationItem] = [overview]
    if conceptual_kids:
        grouped.append(
            _impl_folder(
                folder_id=f"implnav:{catalog_impl_id}:group:conceptual",
                title="Концептуальная модель",
                description="Conceptual entities, diagram, and relationships.",
                children=conceptual_kids,
                extra_attrs={
                    "nav_glyph": "cdm",
                    "requirement_section": "CDM",
                    "nav_group": "conceptual",
                },
            )
        )
    grouped.append(glossary)
    if artifact_kids:
        grouped.append(
            _impl_folder(
                folder_id=f"implnav:{catalog_impl_id}:group:artifacts",
                title="Артефакты",
                description="Authored implementation YAML (model body and envelope).",
                children=artifact_kids,
                extra_attrs={
                    "nav_glyph": "source_file",
                    "nav_group": "artifacts",
                },
            )
        )
    grouped.extend(leftovers)
    return grouped


def group_solution_impl_nav(
    catalog_impl_id: str,
    leaves: list[PublicationItem],
) -> list[PublicationItem]:
    """Nest solution-model section_refs under Overview + model/requirements folders.

    Only modules that carry the full solution section-id set are grouped;
    dsp / FIBO / CSV drafts stay a flat section_ref list (enterprise conceptual
    is handled by ``group_enterprise_conceptual_impl_nav``).
    """
    by_sid: dict[str, PublicationItem] = {}
    for leaf in leaves:
        sid = (leaf.attributes or {}).get("section_id")
        if isinstance(sid, str) and sid:
            by_sid[sid] = leaf
    if not _SOLUTION_NAV_REQUIRED_SECTION_IDS.issubset(by_sid):
        return leaves

    claimed: set[str] = set()

    def take(ids: tuple[str, ...]) -> list[PublicationItem]:
        out: list[PublicationItem] = []
        for sid in ids:
            leaf = by_sid.get(sid)
            if leaf is not None:
                out.append(leaf)
                claimed.add(sid)
        return out

    overview_kids = take(_SOLUTION_NAV_OVERVIEW_IDS)
    overview = PublicationItem(
        id=f"implnav:{catalog_impl_id}:group:overview",
        title="Overview",
        description="Package and vertical-slice summary for this solution.",
        attributes={
            "kind": "group",
            "nav_group": "overview",
            "member_ids": [c.id for c in overview_kids],
        },
        children=overview_kids,
    )
    logical = _impl_folder(
        folder_id=f"implnav:{catalog_impl_id}:group:logical",
        title="Логическая модель",
        description="Logical entities, conceptual entity links, and ER diagram.",
        children=take(_SOLUTION_NAV_LOGICAL_IDS),
        extra_attrs={
            "nav_glyph": "ldm",
            "requirement_section": "LDM",
            "nav_group": "logical",
        },
    )
    physical = _impl_folder(
        folder_id=f"implnav:{catalog_impl_id}:group:physical",
        title="Физическая модель",
        description="Physical objects and ER diagram.",
        children=take(_SOLUTION_NAV_PHYSICAL_IDS),
        extra_attrs={
            "nav_glyph": "pdm",
            "requirement_section": "PDM",
            "nav_group": "physical",
        },
    )
    requirements = _impl_folder(
        folder_id=f"implnav:{catalog_impl_id}:group:requirements",
        title="Требования",
        description="Model assessment against DAMS requirements.",
        children=take(_SOLUTION_NAV_REQUIREMENTS_IDS),
        extra_attrs={"nav_group": "requirements"},
    )
    docs_kids = take(_SOLUTION_NAV_DOCUMENTATION_IDS)
    artifact_kids = take(_SOLUTION_NAV_ARTIFACT_IDS)
    for leaf in artifact_kids:
        attrs = dict(leaf.attributes or {})
        attrs["nav_glyph"] = "source_file"
        leaf.attributes = attrs
    leftovers = [leaf for leaf in leaves if (leaf.attributes or {}).get("section_id") not in claimed]
    grouped = [overview, logical, physical, requirements]
    if docs_kids:
        grouped.append(
            PublicationItem(
                id=f"implnav:{catalog_impl_id}:group:documentation",
                title="Documentation",
                description="Owner-authored package docs and model decisions.",
                attributes={
                    "kind": "group",
                    "nav_group": "documentation",
                    "member_ids": [c.id for c in docs_kids],
                },
                children=docs_kids,
            )
        )
    if artifact_kids:
        grouped.append(
            _impl_folder(
                folder_id=f"implnav:{catalog_impl_id}:group:artifacts",
                title="Артефакты",
                description="Authored implementation YAML (model body and envelope).",
                children=artifact_kids,
                extra_attrs={
                    "nav_glyph": "source_file",
                    "nav_group": "artifacts",
                },
            )
        )
    return [*grouped, *leftovers]


def impl_section_nav_children(
    catalog_impl_id: str,
    impl_module: PublicationModule | None,
) -> list[PublicationItem]:
    """Build-time section_ref children for an implementation_ref (ADR seamless nav).

    Emit one leaf per top-level publication section (including ``explorer``,
    e.g. moex.dsp «Classes»). Do **not** expand explorer class trees here —
    Spec nav under Реализации → Impl stays section-level. Enterprise conceptual
    and solution modules with their full section sets are nested under folders.
    """
    if impl_module is None:
        return []
    leaves: list[PublicationItem] = []
    for sec in impl_module.sections:
        attrs: dict = {
            "kind": "section_ref",
            "section_id": sec.id,
            "target_module_id": impl_module.module_id,
            "target_section_id": sec.id,
            "description": sec.description
            or f"Open publication section «{sec.title}».",
        }
        glyph = _SECTION_ID_NAV_GLYPH.get(sec.id)
        if glyph:
            attrs["nav_glyph"] = glyph
        leaves.append(
            PublicationItem(
                id=f"implnav:{catalog_impl_id}:{sec.id}",
                title=sec.title,
                description=sec.description
                or f"Open publication section «{sec.title}».",
                attributes=attrs,
            )
        )
    grouped = group_hierarchy_impl_nav(catalog_impl_id, leaves)
    if grouped is not leaves:
        return grouped
    grouped = group_enterprise_conceptual_impl_nav(catalog_impl_id, leaves)
    if grouped is not leaves:
        return grouped
    return group_solution_impl_nav(catalog_impl_id, leaves)


def module_section_ids(mod: PublicationModule | None) -> set[str]:
    """Ids of all top-level PublicationSection on a module."""
    if mod is None:
        return set()
    return {s.id for s in mod.sections}


def _collect_section_ref_ids(items: list[PublicationItem] | None) -> set[str]:
    """Recursively collect section_id from section_ref leaves."""
    ids: set[str] = set()
    for item in items or []:
        attrs = item.attributes or {}
        if attrs.get("kind") == "section_ref":
            sid = attrs.get("section_id")
            if isinstance(sid, str) and sid:
                ids.add(sid)
        ids |= _collect_section_ref_ids(item.children)
    return ids


def impl_nav_section_ids(ref: PublicationItem) -> set[str]:
    """section_id values of section_ref descendants under an implementation_ref."""
    return _collect_section_ref_ids(ref.children)


def _assert_impl_nav_tree(items: list[PublicationItem] | None) -> None:
    """Direct children may be group or section_ref; section_ref leaves stay flat."""
    for child in items or []:
        kind = (child.attributes or {}).get("kind")
        assert kind in {"group", "section_ref"}, (
            f"{child.id}: unexpected kind {kind!r} under Impl nav"
        )
        if kind == "section_ref":
            assert child.children == [], (
                f"{child.id}: explorer/class tree must not nest under Impl section_ref"
            )
        else:
            _assert_impl_nav_tree(child.children)


def assert_impl_section_nav_coverage(
    ref: PublicationItem,
    modules: list[PublicationModule],
) -> None:
    """Assert implementation_ref nests exactly the module's PublicationSections."""
    mid = (ref.attributes or {}).get("module_id")
    mod = _module_by_id(modules, mid if isinstance(mid, str) else None)
    expected = module_section_ids(mod)
    actual = impl_nav_section_ids(ref)
    assert actual == expected, (
        f"implementation_ref {ref.id!r} (module={mid!r}): "
        f"nav section_ids {sorted(actual)} != module sections {sorted(expected)}"
    )
    _assert_impl_nav_tree(ref.children)


def attach_impl_section_nav_children(
    refs: list[PublicationItem],
    modules: list[PublicationModule],
) -> list[PublicationItem]:
    """Attach section_ref children onto each implementation_ref."""
    out: list[PublicationItem] = []
    for ref in refs:
        attrs = dict(ref.attributes or {})
        mid = attrs.get("module_id")
        kids = impl_section_nav_children(ref.id, _module_by_id(modules, mid))
        attrs["member_ids"] = [c.id for c in kids]
        attrs["nav_section_count"] = len(_collect_section_ref_ids(kids))
        out.append(
            PublicationItem(
                id=ref.id,
                title=ref.title,
                description=ref.description,
                attributes=attrs,
                children=kids,
                tags=list(ref.tags or []),
                source_ref=ref.source_ref,
            )
        )
    return out


def enrich_dams_explorer_implementations(
    modules: list[PublicationModule],
    catalog: ArchitectureCatalog | None,
) -> None:
    """Fill group:implementations under DAMS explorer from architecture catalog."""
    if catalog is None:
        return
    dams = next((m for m in modules if m.module_id == DAMS_MODULE_ID), None)
    if dams is None:
        return
    explorer = next((s for s in dams.sections if s.type == "explorer"), None)
    if explorer is None:
        return
    impl_nodes = [
        n
        for n in catalog.nodes
        if n.role == "specification_implementation" and n.conforms_to == DAMS_CATALOG_SPEC_ID
    ]
    impl_nodes.sort(key=lambda n: (n.order, n.title))
    children = [
        PublicationItem(
            id=n.id,
            title=n.title,
            description=n.description,
            attributes={
                "kind": "implementation_ref",
                "catalog_node_id": n.id,
                "module_id": n.module_id,
                "version": n.version,
                "conforms_to": n.conforms_to,
            },
        )
        for n in impl_nodes
    ]
    children = attach_impl_section_nav_children(children, modules)
    children = group_dams_implementation_children(children)
    impls_root = next(
        (i for i in explorer.items if i.id == "group:implementations"),
        None,
    )
    if impls_root is None:
        impls_root = PublicationItem(
            id="group:implementations",
            title="Реализации",
            description="Specification implementations, registered against DAMS.",
            attributes={
                "kind": "group",
                "section_root": "implementations",
                "purpose": "Переход к зарегистрированным реализациям (conforms_to DAMS).",
                "structure_why": (
                    "ИТ-решения и Проекты — папки; dsp и conceptual — в корне. "
                    "Список из architecture-catalog; тела живут в своих модулях."
                ),
                "class_count": 0,
                "enum_count": 0,
                "member_ids": [],
            },
            children=[],
        )
        explorer.items = list(explorer.items) + [impls_root]

    attrs = dict(impls_root.attributes or {})
    attrs["member_ids"] = [c.id for c in children]
    attrs["impl_count"] = len(impl_nodes)
    impls_root.attributes = attrs
    impls_root.children = children


def enrich_dams_implementation_glossary(
    modules: list[PublicationModule],
    catalog: ArchitectureCatalog | None,
) -> None:
    """Add aggregated implementations glossary under DAMS Реализации (first child)."""
    if catalog is None:
        return
    dams = next((m for m in modules if m.module_id == DAMS_MODULE_ID), None)
    if dams is None:
        return
    explorer = next((s for s in dams.sections if s.type == "explorer"), None)
    if explorer is None:
        return
    impls_root = next(
        (i for i in explorer.items if i.id == "group:implementations"),
        None,
    )
    if impls_root is None:
        return

    impl_nodes = [
        n
        for n in catalog.nodes
        if n.role == "specification_implementation"
        and n.conforms_to == DAMS_CATALOG_SPEC_ID
    ]
    impl_nodes.sort(key=lambda n: (n.order, n.title))
    section = build_implementation_glossary_section(modules, impl_nodes)
    if section is None:
        return

    # Replace or append the glossary section on the DAMS module.
    existing = next(
        (s for s in dams.sections if s.id == IMPLEMENTATIONS_GLOSSARY_ID),
        None,
    )
    if existing is not None:
        idx = dams.sections.index(existing)
        dams.sections[idx] = section
    else:
        dams.sections.append(section)

    glossary_ref = PublicationItem(
        id=IMPLEMENTATIONS_GLOSSARY_NAV_ID,
        title="Глоссарий",
        description=section.description
        or "Термины из всех реализаций моделей данных.",
        attributes={
            "kind": "section_ref",
            "section_id": IMPLEMENTATIONS_GLOSSARY_ID,
            "target_module_id": DAMS_MODULE_ID,
            "target_section_id": IMPLEMENTATIONS_GLOSSARY_ID,
            "nav_glyph": "glossary",
            "description": section.description
            or "Термины из всех реализаций моделей данных.",
        },
    )
    kids = list(impls_root.children or [])
    kids = [c for c in kids if c.id != IMPLEMENTATIONS_GLOSSARY_NAV_ID]
    kids.insert(0, glossary_ref)
    attrs = dict(impls_root.attributes or {})
    attrs["member_ids"] = [c.id for c in kids]
    impls_root.attributes = attrs
    impls_root.children = kids


def _collect_class_leaf_ids(nodes: list[PublicationItem]) -> set[str]:
    ids: set[str] = set()
    for node in nodes:
        kind = (node.attributes or {}).get("kind") or "class"
        if kind == "class":
            ids.add(node.id)
        ids |= _collect_class_leaf_ids(list(node.children or []))
    return ids


def _find_overview_glossary_folder(
    explorer_items: list[PublicationItem],
) -> PublicationItem | None:
    overview = next((i for i in explorer_items if i.id == "group:overview"), None)
    if overview is None:
        return None
    return next(
        (c for c in (overview.children or []) if c.id == OVERVIEW_GLOSSARY_ID),
        None,
    )


def _walk_glossary_leaves(nodes: list[PublicationItem]) -> list[PublicationItem]:
    leaves: list[PublicationItem] = []
    for node in nodes:
        kind = (node.attributes or {}).get("kind")
        if kind in ("class", "enum") and (node.attributes or {}).get("glossary_view"):
            leaves.append(node)
        leaves.extend(_walk_glossary_leaves(list(node.children or [])))
    return leaves


def enrich_fibo_explorer_classes(modules: list[PublicationModule]) -> None:
    """Fill group:classes and Overview/Glossary from the glossary section (ADR-024)."""
    profile = next((m for m in modules if m.module_id == FIBO_PROFILE_MODULE_ID), None)
    if profile is None:
        return
    explorer = next((s for s in profile.sections if s.type == "explorer"), None)
    glossary = next(
        (s for s in profile.sections if s.id == "glossary" or s.kind == "glossary"),
        None,
    )
    if explorer is None or glossary is None:
        return
    classes_root = next(
        (i for i in explorer.items if i.id == "group:classes"),
        None,
    )
    if classes_root is None:
        return

    # Flat glossary rows → domain groups with subClassOf nesting (Classes).
    class_items: list[PublicationItem] = []
    for item in glossary.items or []:
        attrs = dict(item.attributes or {})
        attrs.setdefault("kind", "class")
        attrs.setdefault("origin", "own")
        if item.description and "definition" not in attrs:
            attrs["definition"] = item.description
        class_items.append(
            item.model_copy(update={"attributes": attrs, "children": []})
        )
    domain_groups = items_to_domain_explorer(class_items)
    leaf_ids = _collect_class_leaf_ids(domain_groups)
    attrs = dict(classes_root.attributes or {})
    attrs["member_ids"] = [g.id for g in domain_groups]
    attrs["class_count"] = len(leaf_ids)
    classes_root.attributes = attrs
    classes_root.children = domain_groups

    # Overview → Glossary: definition-site folders (domain / module_path), not subClassOf.
    site_folders = build_ontology_glossary_tree(class_items)
    glossary_folder = make_overview_glossary_folder(site_folders)
    overview = next((i for i in explorer.items if i.id == "group:overview"), None)
    if overview is not None:
        kept = [
            c
            for c in (overview.children or [])
            if c.id != OVERVIEW_GLOSSARY_ID
        ]
        overview.children = [*kept, glossary_folder]
        oattrs = dict(overview.attributes or {})
        oattrs["member_ids"] = [c.id for c in overview.children]
        overview.attributes = oattrs

    # Enrich flat A–Z glossary rows with Taxonomy / See also / origin (ADR-027).
    leaf_by_canonical = {
        (leaf.attributes or {}).get("name")
        or leaf.id.removeprefix("glossary:"): leaf
        for leaf in _walk_glossary_leaves([glossary_folder])
    }
    enriched_rows: list[PublicationItem] = []
    for item in glossary.items or []:
        leaf = leaf_by_canonical.get(item.id)
        if leaf is None:
            attrs = dict(item.attributes or {})
            attrs.setdefault("kind", "class")
            attrs.setdefault("origin", "own")
            attrs.setdefault("see_also", [])
            attrs.setdefault("taxonomy_parents", [])
            attrs.setdefault("taxonomy_children", [])
            enriched_rows.append(item.model_copy(update={"attributes": attrs}))
            continue
        merged = dict(item.attributes or {})
        lattrs = leaf.attributes or {}
        for key in (
            "origin",
            "defined_in",
            "is_a_chain",
            "definition_depth",
            "taxonomy_parents",
            "taxonomy_children",
            "see_also",
            "glossary_view",
            "kind",
        ):
            if key in lattrs:
                merged[key] = lattrs[key]
        enriched_rows.append(item.model_copy(update={"attributes": merged}))
    glossary.items = enriched_rows


def _linkml_glossary_leaves_from_manifest(
    mod: PublicationModule,
) -> list[PublicationItem]:
    """Rebuild glossary leaves from explorer LinkML source (DAMS top-level glossary)."""
    if not mod.manifest_path:
        return []
    try:
        from moex_publication_viewer.normalizers.linkml_normalizer import get_schema_view
        from moex_publication_viewer.normalizers.spec_glossary_tree import (
            build_linkml_glossary_leaves,
        )

        manifest = load_manifest(Path(mod.manifest_path))
        explorer_m = next(
            (s for s in manifest.sections if s.type == "explorer"),
            None,
        )
        if explorer_m is None or not explorer_m.source or not explorer_m.source.path:
            return []
        source_path = resolve_source_path(Path(mod.manifest_path), explorer_m.source.path)
        if source_path.suffix.lower() not in {".yaml", ".yml"}:
            return []
        sv = get_schema_view(source_path)
        spec_dir = source_path.resolve().parent.parent
        return build_linkml_glossary_leaves(sv, spec_dir=spec_dir)
    except Exception:
        return []


def enrich_linkml_glossary_sections(modules: list[PublicationModule]) -> None:
    """Replace hand JSON glossary rows with SchemaView projection (ADR-025 view)."""
    for mod in modules:
        if mod.profile != "linkml-specification":
            continue
        explorer = next((s for s in mod.sections if s.type == "explorer"), None)
        glossary = next(
            (s for s in mod.sections if s.id == "glossary" or s.kind == "glossary"),
            None,
        )
        if explorer is None or glossary is None:
            continue
        folder = _find_overview_glossary_folder(list(explorer.items or []))
        if folder is not None:
            leaves = _walk_glossary_leaves([folder])
        else:
            # DAMS: Glossary is a top-level section_ref, not Overview folder.
            leaves = _linkml_glossary_leaves_from_manifest(mod)
        if not leaves:
            continue
        glossary.items = flat_glossary_items_from_leaves(leaves)
        # Keep filterable useful for generated rows
        if not glossary.filterable:
            glossary.filterable = ["kind", "origin", "defined_in"]


def build_dsp_documentation_sidebar_siblings(
    modules: list[PublicationModule],
) -> list[dict]:
    """Sidebar sibling under Ontology Catalog: Documentation → moex.dsp sections.

    Same hierarchy level as Ontology Catalog (not nested in its explorer).
    """
    if not any(m.module_id == ONTOLOGY_CATALOG_MODULE_ID for m in modules):
        return []
    if not any(m.module_id == DSP_MODULE_ID for m in modules):
        return []

    def _dsp_section_ref(leaf_id: str, title: str, section_id: str) -> dict:
        attrs: dict = {
            "kind": "section_ref",
            "section_id": section_id,
            "target_module_id": DSP_MODULE_ID,
            "target_section_id": section_id,
            "description": f"Open moex.dsp section «{title}».",
        }
        glyph = _SECTION_ID_NAV_GLYPH.get(section_id)
        if glyph:
            attrs["nav_glyph"] = glyph
        return {
            "id": leaf_id,
            "title": title,
            "description": f"Open moex.dsp section «{title}».",
            "attributes": attrs,
            "children": [],
        }

    kids = [
        _dsp_section_ref(
            "ontcat:doc:moex.dsp.classes", "moex.dsp.classes", "explorer"
        ),
        _dsp_section_ref(
            "ontcat:doc:moex.dsp.glossary", "moex.dsp.glossary", "glossary"
        ),
    ]
    return [
        {
            "after_module_id": ONTOLOGY_CATALOG_MODULE_ID,
            "id": "sidebar:documentation",
            "title": "Documentation",
            "description": "Data Specification Player metamodel sections (moex.dsp).",
            "attributes": {
                "kind": "group",
                "nav_group": "documentation",
                "member_ids": [c["id"] for c in kids],
            },
            "children": kids,
        }
    ]


# Back-compat alias used by older tests/imports.
def enrich_ontology_catalog_documentation_nav(
    modules: list[PublicationModule],
) -> list[dict]:
    """Return sidebar siblings; does not mutate Ontology Catalog explorer."""
    return build_dsp_documentation_sidebar_siblings(modules)


def enrich_fibo_explorer_implementations(
    modules: list[PublicationModule],
    catalog: ArchitectureCatalog | None,
) -> None:
    """Fill group:implementations under FIBO profile explorer from architecture catalog."""
    if catalog is None:
        return
    profile = next((m for m in modules if m.module_id == FIBO_PROFILE_MODULE_ID), None)
    if profile is None:
        return
    explorer = next((s for s in profile.sections if s.type == "explorer"), None)
    if explorer is None:
        return
    impl_nodes = [
        n
        for n in catalog.nodes
        if n.role == "specification_implementation"
        and n.conforms_to == FIBO_PROFILE_CATALOG_SPEC_ID
    ]
    impl_nodes.sort(key=lambda n: (n.order, n.title))
    children = [
        PublicationItem(
            id=n.id,
            title=n.title,
            description=n.description,
            attributes={
                "kind": "implementation_ref",
                "catalog_node_id": n.id,
                "module_id": n.module_id,
                "version": n.version,
                "conforms_to": n.conforms_to,
            },
        )
        for n in impl_nodes
    ]
    children = attach_impl_section_nav_children(children, modules)
    impls_root = next(
        (i for i in explorer.items if i.id == "group:implementations"),
        None,
    )
    if impls_root is None:
        return

    attrs = dict(impls_root.attributes or {})
    attrs["member_ids"] = [c.id for c in children]
    attrs["impl_count"] = len(children)
    impls_root.attributes = attrs
    impls_root.children = children


def build_search_index(modules: list[PublicationModule]) -> list[dict]:
    index: list[dict] = []
    for mod in modules:
        index.append(
            {
                "kind": "module",
                "module_id": mod.module_id,
                "title": mod.title,
                "description": mod.description or "",
            }
        )
        for sec in mod.sections:
            index.append(
                {
                    "kind": "section",
                    "module_id": mod.module_id,
                    "section_id": sec.id,
                    "title": sec.title,
                    "description": sec.description or "",
                }
            )
            for item in sec.items:
                _index_item(index, mod.module_id, sec.id, item)
    return index


def _index_item(index: list[dict], module_id: str, section_id: str, item) -> None:
    # Hierarchy-only group nodes are not selectable cards — skip search hits
    attrs = item.attributes or {}
    if attrs.get("kind") != "group":
        index.append(
            {
                "kind": "item",
                "module_id": module_id,
                "section_id": section_id,
                "item_id": item.id,
                "title": item.title or item.id,
                "description": item.description or "",
            }
        )
    for child in item.children:
        _index_item(index, module_id, section_id, child)


def enrich_publication_modules(
    modules: list[PublicationModule],
    catalog: ArchitectureCatalog | None,
) -> None:
    """Shared enrich pipeline for build() and serve.refresh_from_disk().

    Keep a single call list so serve cannot drift and drop hierarchy/glossary UI.
    """
    enrich_dams_explorer_implementations(modules, catalog)
    enrich_dams_implementation_glossary(modules, catalog)
    if catalog is not None:
        enrich_dams_hierarchy_module(modules, catalog.nodes)
    enrich_fibo_explorer_classes(modules)
    enrich_fibo_explorer_implementations(modules, catalog)
    enrich_linkml_glossary_sections(modules)


def build(root: Path, dist_dir: Path | None = None) -> Path:
    """Build viewer into dist_dir (default apps/viewer/dist). Returns index.html path."""
    root = root.resolve()
    if dist_dir is None:
        dist_dir = VIEWER_ROOT / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)

    modules = compile_modules(
        root, enforce_publication_contract=True, dist_dir=dist_dir
    )
    catalog = compile_catalog(root, modules)
    if catalog is not None:
        check_catalog_publication_contract_gate(catalog, modules, root)
    enrich_publication_modules(modules, catalog)
    sidebar_siblings = build_dsp_documentation_sidebar_siblings(modules)
    search_index = build_search_index(modules)
    if catalog is not None:
        for node in catalog.nodes:
            search_index.append(
                {
                    "kind": "catalog",
                    "node_id": node.id,
                    "module_id": node.module_id or "",
                    "title": node.title,
                    "description": node.description or node.role,
                }
            )

    registry = {
        "modules": [
            {
                "module_id": m.module_id,
                "title": m.title,
                "profile": m.profile,
                "sections": [s.id for s in m.sections],
                "manifest_path": m.manifest_path,
            }
            for m in modules
        ],
        "catalog": (
            {
                "nodes": [
                    {
                        "id": n.id,
                        "role": n.role,
                        "title": n.title,
                        "version": n.version,
                        "expressed_in": n.expressed_in,
                        "conforms_to": n.conforms_to,
                        "module_id": n.module_id,
                        "order": n.order,
                        "description": n.description,
                        "contract_exempt": n.contract_exempt,
                    }
                    for n in catalog.nodes
                ]
            }
            if catalog is not None
            else None
        ),
    }
    (dist_dir / "manifest_registry.json").write_text(
        json.dumps(registry, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    from moex_publication_viewer.assets import assemble_css, assemble_js

    css_text = assemble_css()
    js_text = assemble_js()
    # Keep static/viewer.css in sync for tests/tooling that read the layered bundle.
    (VIEWER_ROOT / "static" / "viewer.css").write_text(css_text, encoding="utf-8")
    html = render_viewer(
        modules,
        search_index,
        VIEWER_ROOT,
        catalog=catalog,
        inline_css=css_text,
        inline_js=js_text,
        sidebar_siblings=sidebar_siblings,
    )
    index_path = dist_dir / "index.html"
    index_path.write_text(html, encoding="utf-8")

    # Dev convenience copies (not required at runtime — HTML is autonomous).
    (dist_dir / "viewer.css").write_text(css_text, encoding="utf-8")
    (dist_dir / "viewer.js").write_text(js_text, encoding="utf-8")

    return index_path
