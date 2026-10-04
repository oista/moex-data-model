"""Build SpecificationImplementation envelope for solution-xlsx import."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from moex_standard_linkml.ingest.envelope import content_digest_bytes
from moex_standard_linkml.solution_xlsx.profile import SolutionXlsxProfile, SystemDefaults

GENERATOR_ID = "moex-standard-linkml/solution-xlsx@0.1.0"


def build_solution_envelope(
    *,
    profile: SolutionXlsxProfile,
    system: SystemDefaults,
    package_filename: str,
    package_bytes: bytes,
    source_filename: str,
    source_sha256: str,
    revision: str | None = None,
) -> dict[str, Any]:
    digest = content_digest_bytes(package_bytes)
    rev = revision or digest.removeprefix("sha256:")[:12]
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    source_label = f"{source_filename}#sha256:{source_sha256}"

    return {
        "id": f"moex:implementation:{system.slug}:{system.model_version}",
        "name": system.package_title,
        "description": system.package_description.strip(),
        "version": system.model_version,
        "revision": rev,
        "content_digest": digest,
        "conforms_to": {
            "specification_id": profile.conforms_to.specification_id,
            "specification_version": profile.conforms_to.specification_version,
            "specification_revision": profile.conforms_to.specification_revision,
        },
        "implementation_kind": "linkml",
        "implementation_profile": "dams-data-model",
        "dams_model_level": "solution",
        "lifecycle_status": profile.defaults.lifecycle_status,
        "source": {
            "source_uri": source_label,
            "media_type": (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
            "source_root_type": "ModelPackage",
            "authoritative": True,
        },
        "provenance": {
            "generated_from": source_label,
            "created_by": "moex-model import-solution",
            "generator_id": GENERATOR_ID,
            "created_at": now,
        },
        "body_ref": package_filename,
        "implementation_body": package_filename,
        "specification_envelope": profile.specification_envelope,
    }


def relative_spec_envelope(solution_dir: Path, repo_root: Path) -> str:
    """Compute relative path from solution dir to moex-dams specification.yaml."""
    target = (
        repo_root
        / "model-assets"
        / "specifications"
        / "moex-dams"
        / "0.1"
        / "specification.yaml"
    )
    try:
        return Path(
            __import__("os").path.relpath(target, start=solution_dir)
        ).as_posix()
    except ValueError:
        return "../../../specifications/moex-dams/0.1/specification.yaml"
