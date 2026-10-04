"""Sidecar SpecificationImplementation envelope (YAML, no kernel package)."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from moex_standard_linkml.ingest.profile import IngestProfile

GENERATOR_ID = "moex-standard-linkml/ingest@0.1.0"


def content_digest_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def content_digest_file(path: Path) -> str:
    return content_digest_bytes(path.read_bytes())


def build_envelope(
    *,
    profile: IngestProfile,
    package_path: Path,
    source_path: Path,
    package_bytes: bytes | None = None,
    revision: str | None = None,
    created_by: str = "moex-linkml-ingest",
    source_label: str | None = None,
) -> dict[str, Any]:
    """Build a kernel-shaped SpecificationImplementation as plain YAML dict.

    ``source_label`` (optional) replaces filesystem URI in source/provenance
    when absolute paths must not be persisted (ADR-022).
    """
    body = package_bytes if package_bytes is not None else package_path.read_bytes()
    digest = content_digest_bytes(body)
    rev = revision or digest.removeprefix("sha256:")[:12]
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    source_uri = source_label or source_path.resolve().as_uri()

    return {
        "id": f"moex:implementation:{profile.solution_slug}:{profile.model_version}",
        "name": profile.package_name,
        "description": profile.package_description,
        "version": profile.model_version,
        "revision": rev,
        "content_digest": digest,
        "conforms_to": {
            "specification_id": profile.conforms_to.specification_id,
            "specification_version": profile.conforms_to.specification_version,
            "specification_revision": profile.conforms_to.specification_revision,
        },
        "implementation_kind": "linkml",
        "lifecycle_status": profile.defaults.lifecycle_status,
        "source": {
            "source_uri": source_uri,
            "media_type": _media_type(source_path),
            "source_root_type": "ModelPackage",
            "authoritative": True,
        },
        "provenance": {
            "generated_from": source_uri,
            "created_by": created_by,
            "generator_id": GENERATOR_ID,
            "created_at": now,
        },
        "body_ref": package_path.name,
    }


def _media_type(path: Path) -> str:
    if path.is_dir():
        return "text/csv"
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xlsm"}:
        return (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    if suffix == ".csv":
        return "text/csv"
    return "application/octet-stream"
