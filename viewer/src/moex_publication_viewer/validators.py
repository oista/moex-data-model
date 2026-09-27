"""Cross-manifest validation and diagnostics."""

from __future__ import annotations

from pathlib import Path

from moex_publication_viewer.manifest_loader import resolve_source_path
from moex_publication_viewer.models.manifest_models import PublicationManifest


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
