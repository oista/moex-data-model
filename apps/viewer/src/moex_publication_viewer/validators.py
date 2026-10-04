"""Cross-manifest validation and diagnostics."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from moex_publication_viewer.manifest_loader import resolve_source_path
from moex_publication_viewer.models.catalog_models import ArchitectureCatalog
from moex_publication_viewer.models.manifest_models import PublicationManifest
from moex_publication_viewer.models.publication_models import PublicationModule
from moex_publication_viewer.publication_profiles import (
    SECTION_ROOT_TO_KIND,
    profile_spec,
)

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """One or more build-blocking diagnostics."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("\n".join(errors))


def validate_manifests(
    pairs: list[tuple[Path, PublicationManifest]],
) -> None:
    """Fail on duplicate module_id / section.id and missing sources."""
    errors: list[str] = []
    seen_modules: dict[str, Path] = {}

    for path, manifest in pairs:
        if manifest.module_id in seen_modules:
            errors.append(
                f"{path}: duplicate module_id '{manifest.module_id}' "
                f"(also in {seen_modules[manifest.module_id]})"
            )
        else:
            seen_modules[manifest.module_id] = path

        section_ids: set[str] = set()
        for section in manifest.sections:
            if section.id in section_ids:
                errors.append(
                    f"{path}: duplicate section.id '{section.id}' in module '{manifest.module_id}'"
                )
            section_ids.add(section.id)

            source_path = resolve_source_path(path, section.source.path)
            if not source_path.is_file():
                errors.append(
                    f"{path}: missing source file for section '{section.id}': "
                    f"{section.source.path} (resolved: {source_path})"
                )

        if not manifest.sections:
            errors.append(f"{path}: module '{manifest.module_id}' has no sections")

    if errors:
        raise ValidationError(errors)


def _collect_module_kinds(module: PublicationModule) -> set[str]:
    kinds: set[str] = set()
    for section in module.sections:
        if section.kind:
            kinds.add(section.kind)
        if section.type == "explorer":
            for item in section.items:
                root = (item.attributes or {}).get("section_root")
                if isinstance(root, str) and root in SECTION_ROOT_TO_KIND:
                    kinds.add(SECTION_ROOT_TO_KIND[root])
    return kinds


def check_publication_profiles(modules: list[PublicationModule]) -> list[str]:
    """Soft ProfileSpec checks (ADR-016). Returns warnings; does not raise."""
    warnings: list[str] = []
    for module in modules:
        spec = profile_spec(module.profile)
        if spec is None:
            continue
        present = _collect_module_kinds(module)
        loc = module.manifest_path or module.module_id
        missing_req = sorted(spec.required - present)
        if missing_req:
            warnings.append(
                f"{loc}: profile '{module.profile}' missing required kinds: "
                f"{', '.join(missing_req)}"
            )
        forbidden_hit = sorted(spec.forbidden & present)
        if forbidden_hit:
            warnings.append(
                f"{loc}: profile '{module.profile}' has forbidden kinds: "
                f"{', '.join(forbidden_hit)}"
            )
        missing_rec = sorted(spec.recommended - present)
        if missing_rec:
            warnings.append(
                f"{loc}: profile '{module.profile}' missing recommended kinds: "
                f"{', '.join(missing_rec)}"
            )
    warnings.extend(check_instance_of_classes(modules))
    for w in warnings:
        logger.warning("%s", w)
    return warnings


def _dams_explorer_class_ids(modules: list[PublicationModule]) -> set[str]:
    """Class / enum ids from the DAMS reference explorer (if present)."""
    dams = next((m for m in modules if m.module_id == "moex:module:dams"), None)
    if dams is None:
        return set()
    expl = next((s for s in dams.sections if s.type == "explorer"), None)
    if expl is None:
        return set()
    ids: set[str] = set()

    def walk(nodes: list) -> None:
        for node in nodes or []:
            kind = (node.attributes or {}).get("kind")
            if kind in ("class", "enum"):
                ids.add(node.id)
            if node.children:
                walk(node.children)

    walk(expl.items)
    return ids


def check_instance_of_classes(modules: list[PublicationModule]) -> list[str]:
    """Warn when section.instance_of names a class missing from DAMS explorer."""
    known = _dams_explorer_class_ids(modules)
    if not known:
        return []
    warnings: list[str] = []
    for module in modules:
        loc = module.manifest_path or module.module_id
        for section in module.sections:
            cls = getattr(section, "instance_of", None)
            if not cls:
                continue
            if cls not in known:
                warnings.append(
                    f"{loc}: section '{section.id}' instance_of '{cls}' "
                    f"not found in DAMS explorer classes"
                )
    return warnings


def _spec_asset_dir(root: Path, specification_ref: str) -> Path | None:
    from moex_publication_viewer.publication_contract import spec_asset_dir

    return spec_asset_dir(root, specification_ref)


def _load_publication_requirements(path: Path) -> dict[str, Any] | None:
    from moex_publication_viewer.publication_contract import load_publication_requirements

    return load_publication_requirements(path)


def _collect_required_ids(
    doc: dict[str, Any],
    profile_id: str,
) -> list[str]:
    from moex_publication_viewer.publication_contract import collect_required_ids

    return collect_required_ids(doc, profile_id)


def check_publication_contract_coverage(
    modules: list[PublicationModule],
    root: Path,
    *,
    hard_fail: bool = True,
) -> list[str]:
    """ADR-019 phase 2: assess contracts; required failures raise when hard_fail."""
    from moex_publication_viewer.publication_contract import run_publication_contracts

    _reports, warnings = run_publication_contracts(
        modules, root, hard_fail=hard_fail, dist_dir=None
    )
    return warnings


def validate_architecture_catalog(
    catalog: ArchitectureCatalog,
    module_ids: set[str],
    *,
    catalog_path: Path | None = None,
) -> None:
    """Validate catalog ids, conforms_to targets, and module_id references."""
    errors: list[str] = []
    loc = str(catalog_path) if catalog_path else "architecture-catalog"
    by_id: dict[str, object] = {}

    for node in catalog.nodes:
        if node.id in by_id:
            errors.append(f"{loc}: duplicate node id '{node.id}'")
        else:
            by_id[node.id] = node

        if node.module_id and node.module_id not in module_ids:
            errors.append(
                f"{loc}: node '{node.id}' references unknown module_id '{node.module_id}'"
            )

        if node.role == "reference_specification" and node.conforms_to:
            errors.append(
                f"{loc}: specification '{node.id}' must not set conforms_to"
            )

        if node.role == "specification_implementation" and node.expressed_in:
            errors.append(
                f"{loc}: implementation '{node.id}' must not set expressed_in "
                "(use label on the specification)"
            )

    for node in catalog.nodes:
        if not node.conforms_to:
            continue
        target = by_id.get(node.conforms_to)
        if target is None:
            errors.append(
                f"{loc}: node '{node.id}' conforms_to unknown id '{node.conforms_to}'"
            )
        elif getattr(target, "role", None) != "reference_specification":
            errors.append(
                f"{loc}: node '{node.id}' conforms_to '{node.conforms_to}' "
                "which is not a reference_specification"
            )

    if errors:
        raise ValidationError(errors)


def _spec_ref_name(specification_ref: str) -> str:
    return specification_ref.split("@", 1)[0].strip()


def check_catalog_publication_contract_gate(
    catalog: ArchitectureCatalog,
    modules: list[PublicationModule],
    root: Path,
) -> None:
    """Hard-fail when catalog Spec/Impl miss publication-requirements or implements.

    Spec gate: Spec with ≥1 non-exempt Impl (module_id set) must have
    publication-requirements.yaml.
    Impl gate: non-exempt catalog Impl whose publication module has
    profile=implementation must declare implements pointing at parent Spec.
    """
    from moex_publication_viewer.publication_contract import (
        load_publication_requirements,
        spec_asset_dir,
    )

    errors: list[str] = []
    by_id = {n.id: n for n in catalog.nodes}
    modules_by_id = {m.module_id: m for m in modules}
    specs_needing_reqs: set[str] = set()

    for node in catalog.nodes:
        if node.role != "specification_implementation":
            continue
        if node.contract_exempt or not node.module_id or not node.conforms_to:
            continue
        specs_needing_reqs.add(node.conforms_to)
        mod = modules_by_id.get(node.module_id)
        if mod is None:
            continue
        if mod.profile != "implementation":
            continue
        if not mod.implements:
            errors.append(
                f"catalog Impl '{node.id}' (module {node.module_id}, "
                f"profile=implementation) missing implements: "
                f"(parent Spec '{node.conforms_to}')"
            )
            continue
        matched = [
            i
            for i in mod.implements
            if isinstance(i, dict)
            and _spec_ref_name(str(i.get("specification_ref") or "")) == node.conforms_to
        ]
        if not matched:
            errors.append(
                f"catalog Impl '{node.id}': implements must reference "
                f"specification_ref for parent Spec '{node.conforms_to}'"
            )
            continue
        for entry in matched:
            pref = entry.get("profile_ref")
            if not isinstance(pref, str) or not pref.strip():
                errors.append(
                    f"catalog Impl '{node.id}': implements entry missing profile_ref"
                )

    for spec_id in sorted(specs_needing_reqs):
        spec_node = by_id.get(spec_id)
        version = "0.1"
        if spec_node and spec_node.version:
            parts = str(spec_node.version).split(".")
            version = f"{parts[0]}.{parts[1]}" if len(parts) >= 2 else parts[0]
        asset = spec_asset_dir(root, f"{spec_id}@{version}")
        if asset is None:
            asset = spec_asset_dir(root, f"{spec_id}@0.1")
        req_path = (asset / "publication-requirements.yaml") if asset else None
        if req_path is None or not req_path.is_file():
            errors.append(
                f"Spec '{spec_id}' has governed catalog Impls but missing "
                f"publication-requirements.yaml under specifications/{spec_id}/"
            )
            continue
        doc = load_publication_requirements(req_path)
        profiles = (doc or {}).get("profiles") if doc else None
        if not isinstance(profiles, list) or not profiles:
            errors.append(
                f"Spec '{spec_id}': publication-requirements.yaml has no profiles"
            )

    if errors:
        raise ValidationError(errors)
