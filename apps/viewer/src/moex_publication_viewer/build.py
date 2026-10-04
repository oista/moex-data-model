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
from moex_publication_viewer.normalizers.linkml_normalizer import clear_schema_view_cache
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

# Stay at Реализации root (not nested under folders).
_DAMS_IMPL_ROOT_IDS = frozenset(
    {
        "moex-dsp",
        "moex-enterprise-conceptual-model",
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
) -> PublicationItem:
    return PublicationItem(
        id=folder_id,
        title=title,
        description=description,
        attributes={
            "kind": "group",
            "group_style": "section_folder",
            "member_ids": [c.id for c in children],
            "impl_count": len(children),
        },
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
            if not pub_section.items and not pub_section.content:
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


def impl_section_nav_children(
    catalog_impl_id: str,
    impl_module: PublicationModule | None,
) -> list[PublicationItem]:
    """Build-time section_ref children for an implementation_ref (ADR seamless nav).

    Emit one leaf per top-level publication section (including ``explorer``,
    e.g. moex.dsp «Classes»). Do **not** expand explorer class trees here —
    Spec nav under Реализации → Impl stays section-level.
    """
    if impl_module is None:
        return []
    children: list[PublicationItem] = []
    for sec in impl_module.sections:
        children.append(
            PublicationItem(
                id=f"implnav:{catalog_impl_id}:{sec.id}",
                title=sec.title,
                description=sec.description
                or f"Open publication section «{sec.title}».",
                attributes={
                    "kind": "section_ref",
                    "section_id": sec.id,
                    "target_module_id": impl_module.module_id,
                    "target_section_id": sec.id,
                    "description": sec.description
                    or f"Open publication section «{sec.title}».",
                },
            )
        )
    return children


def module_section_ids(mod: PublicationModule | None) -> set[str]:
    """Ids of all top-level PublicationSection on a module."""
    if mod is None:
        return set()
    return {s.id for s in mod.sections}


def impl_nav_section_ids(ref: PublicationItem) -> set[str]:
    """section_id values of section_ref children under an implementation_ref."""
    ids: set[str] = set()
    for child in ref.children or []:
        attrs = child.attributes or {}
        if attrs.get("kind") != "section_ref":
            continue
        sid = attrs.get("section_id")
        if isinstance(sid, str) and sid:
            ids.add(sid)
    return ids


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
    for child in ref.children or []:
        assert (child.attributes or {}).get("kind") == "section_ref"
        assert child.children == [], (
            f"{child.id}: explorer/class tree must not nest under Impl section_ref"
        )


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
        attrs["nav_section_count"] = len(kids)
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
    enrich_dams_explorer_implementations(modules, catalog)
    enrich_fibo_explorer_implementations(modules, catalog)
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
    )
    index_path = dist_dir / "index.html"
    index_path.write_text(html, encoding="utf-8")

    # Dev convenience copies (not required at runtime — HTML is autonomous).
    (dist_dir / "viewer.css").write_text(css_text, encoding="utf-8")
    (dist_dir / "viewer.js").write_text(js_text, encoding="utf-8")

    return index_path
