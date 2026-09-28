"""ReferenceSpecification catalog + promote helpers for Stage 7 import."""

from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

DEFAULT_TARGET_PROFILE_ID = "moex:specification:moex-dams:0.1"
GENERATED_DRAFT_BANNER_STATUS = "generated-draft"
WORKSPACE_DRAFT_BANNER_STATUS = "workspace-draft"

_BANNER_LINE = re.compile(r"^#\s*([a-z_]+)\s*:\s*(.+?)\s*$", re.IGNORECASE)


class ImportProfileInfo(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    name: str
    version: str
    path: str


def specifications_root(repo_root: Path) -> Path:
    return repo_root / "model-assets" / "specifications"


def list_import_profiles(repo_root: Path) -> list[ImportProfileInfo]:
    """Scan model-assets/specifications/**/specification.yaml envelopes."""
    root = specifications_root(repo_root)
    if not root.is_dir():
        return []
    found: list[ImportProfileInfo] = []
    for spec_path in sorted(root.glob("**/specification.yaml")):
        try:
            data = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError):
            continue
        if not isinstance(data, dict):
            continue
        sid = data.get("id")
        if not isinstance(sid, str) or not sid.strip():
            continue
        name = data.get("name")
        version = data.get("version") or data.get("revision") or ""
        found.append(
            ImportProfileInfo(
                id=sid.strip(),
                name=str(name).strip() if name else sid.strip(),
                version=str(version),
                path=spec_path.relative_to(repo_root).as_posix(),
            )
        )
    return found


def resolve_profile(
    repo_root: Path, profile_id: str
) -> ImportProfileInfo | None:
    for p in list_import_profiles(repo_root):
        if p.id == profile_id:
            return p
    return None


def parse_banner_meta(content: str) -> dict[str, str]:
    """Parse leading `# key: value` comment lines until first non-banner line."""
    meta: dict[str, str] = {}
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            if meta:
                break
            continue
        if not stripped.startswith("#"):
            break
        m = _BANNER_LINE.match(stripped)
        if m:
            meta[m.group(1).lower()] = m.group(2).strip()
        elif meta:
            # continuation comment after keys — keep scanning only key lines
            continue
    return meta


def strip_import_banner(content: str) -> str:
    """Remove leading `# …` banner block; return schema body."""
    lines = content.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped == "" and i == 0:
            i += 1
            continue
        if stripped.startswith("#"):
            i += 1
            continue
        break
    # drop one blank line after banner if present
    if i < len(lines) and lines[i].strip() == "":
        i += 1
    return "".join(lines[i:])


def build_import_banner(
    *,
    status: str,
    target_profile_id: str,
    import_job_id: str,
    note: str | None = None,
) -> str:
    lines = [
        f"# status: {status}",
        f"# target_profile: {target_profile_id}",
        f"# import_job: {import_job_id}",
    ]
    if note:
        lines.append(f"# {note}")
    return "\n".join(lines) + "\n"


def rewrite_promote_banner(
    content: str,
    *,
    target_profile_id: str,
    import_job_id: str,
) -> str:
    body = strip_import_banner(content)
    banner = build_import_banner(
        status=WORKSPACE_DRAFT_BANNER_STATUS,
        target_profile_id=target_profile_id,
        import_job_id=import_job_id,
        note="Stage 7 promote — publication candidate (not auto-published)",
    )
    return banner + body


def validate_linkml_schema_text(schema_text: str) -> list[str]:
    """Return human-readable errors if text is not a loadable LinkML schema."""
    errors: list[str] = []
    text = schema_text.strip()
    if not text:
        return ["schema body is empty"]
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        return [f"invalid YAML: {exc}"]
    if not isinstance(data, dict):
        return ["schema must be a YAML mapping"]
    if not data.get("name") and not data.get("id"):
        errors.append("schema requires name or id")
    tmp: Path | None = None
    try:
        from linkml_runtime import SchemaView

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".yaml",
            encoding="utf-8",
            delete=False,
            newline="\n",
        ) as fh:
            fh.write(text if text.endswith("\n") else text + "\n")
            tmp = Path(fh.name)
        SchemaView(str(tmp))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"LinkML SchemaView load failed: {exc}")
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)
    return errors


def load_job_manifest(job_dir: Path) -> dict[str, Any]:
    job_json = job_dir / "job.json"
    if not job_json.is_file():
        raise FileNotFoundError(f"import job.json missing: {job_json}")
    data = yaml.safe_load(job_json.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("job.json is not a mapping")
    return data


def load_job_diagnostics(job_dir: Path) -> list[dict[str, Any]]:
    path = job_dir / "diagnostics.json"
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [d for d in data if isinstance(d, dict)]
    return []


__all__ = [
    "DEFAULT_TARGET_PROFILE_ID",
    "GENERATED_DRAFT_BANNER_STATUS",
    "ImportProfileInfo",
    "WORKSPACE_DRAFT_BANNER_STATUS",
    "build_import_banner",
    "list_import_profiles",
    "load_job_diagnostics",
    "load_job_manifest",
    "parse_banner_meta",
    "resolve_profile",
    "rewrite_promote_banner",
    "specifications_root",
    "strip_import_banner",
    "validate_linkml_schema_text",
]
