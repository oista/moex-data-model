"""Cross-manifest validation and diagnostics."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

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
    for w in warnings:
        logger.warning("%s", w)
    return warnings


def _spec_asset_dir(root: Path, specification_ref: str) -> Path | None:
    """Resolve moex-dams@0.1 → model-assets/specifications/moex-dams/0.1."""
    ref = specification_ref.strip()
    if "@" in ref:
        name, version = ref.split("@", 1)
    else:
        name, version = ref, "0.1"
    name = name.strip()
    version = version.strip()
    candidates = [
        root / "model-assets" / "specifications" / name / version,
        root / "specifications" / name / version,
    ]
    for c in candidates:
        if c.is_dir():
            return c
    alt = name.replace("_", "-")
    for c in (
        root / "model-assets" / "specifications" / alt / version,
        root / "specifications" / alt / version,
    ):
        if c.is_dir():
            return c
    return None


def _load_publication_requirements(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else None


def _collect_required_ids(
    doc: dict[str, Any],
    profile_id: str,
) -> list[str]:
    """Collect required requirement ids for profile + parent chain."""
    profiles = {
        p.get("id"): p
        for p in (doc.get("profiles") or [])
        if isinstance(p, dict) and p.get("id")
    }
    collected: list[str] = []
    seen_profiles: set[str] = set()
    current: str | None = profile_id
    while current and current not in seen_profiles:
        seen_profiles.add(current)
        prof = profiles.get(current)
        if prof is None:
            break
        for req in prof.get("requirements") or []:
            if not isinstance(req, dict):
                continue
            obligation = req.get("obligation") or "required"
            if obligation != "required":
                continue
            rid = req.get("id")
            if isinstance(rid, str):
                collected.append(rid)
        parent = prof.get("parent_profile_ref")
        current = parent if isinstance(parent, str) else None
    return collected


def check_publication_contract_coverage(
    modules: list[PublicationModule],
    root: Path,
) -> list[str]:
    """Soft ADR-019 checks: inherited required requirements must appear in satisfies."""
    warnings: list[str] = []
    req_cache: dict[Path, dict[str, Any] | None] = {}

    for module in modules:
        implements = module.implements or []
        if not implements:
            continue
        covered: set[str] = set()
        for section in module.sections:
            for sid in section.satisfies or []:
                if isinstance(sid, str):
                    covered.add(sid)

        loc = module.manifest_path or module.module_id
        for impl in implements:
            if not isinstance(impl, dict):
                continue
            spec_ref = impl.get("specification_ref")
            profile_ref = impl.get("profile_ref")
            if not isinstance(spec_ref, str) or not isinstance(profile_ref, str):
                continue
            asset_dir = _spec_asset_dir(root, spec_ref)
            if asset_dir is None:
                warnings.append(
                    f"{loc}: implements {spec_ref} but specification asset dir not found"
                )
                continue
            req_path = asset_dir / "publication-requirements.yaml"
            if req_path not in req_cache:
                req_cache[req_path] = _load_publication_requirements(req_path)
            doc = req_cache[req_path]
            if doc is None:
                warnings.append(
                    f"{loc}: implements profile '{profile_ref}' but missing "
                    f"{req_path.name} under {asset_dir}"
                )
                continue
            required_ids = _collect_required_ids(doc, profile_ref)
            missing = [r for r in required_ids if r not in covered]
            if missing:
                warnings.append(
                    f"{loc}: publication contract '{profile_ref}' missing satisfies "
                    f"coverage: {', '.join(missing)}"
                )

    for w in warnings:
        logger.warning("%s", w)
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
