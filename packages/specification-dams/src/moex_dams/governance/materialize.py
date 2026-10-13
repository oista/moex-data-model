"""Materialize EffectiveGovernanceView under generated/governance/ (ADR-049)."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from moex_dams.rules.assignment_resolver import diagnose_governance, resolve_governed
from moex_dams.rules.cascade import GOVERNED_SLOTS

DEFAULT_AS_OF = "2026-10-12"

_ASSIGNMENT_KEYS = (
    "classification_assignments",
    "policy_bindings",
    "ownership_assignments",
)


def as_of_config_path(repo_root: Path | str) -> Path:
    return (
        Path(repo_root)
        / "model-assets"
        / "specifications"
        / "moex-governance-view"
        / "0.1"
        / "as_of.txt"
    )


def load_as_of(repo_root: Path | str) -> str:
    path = as_of_config_path(repo_root)
    if path.is_file():
        text = path.read_text(encoding="utf-8").strip()
        if text:
            return text.splitlines()[0].strip()
    return DEFAULT_AS_OF


def governance_view_path(repo_root: Path | str, as_of: str) -> Path:
    safe = as_of.replace("/", "_").replace("\\", "_")
    return Path(repo_root) / "generated" / "governance" / f"effective-governance-view-{safe}.yaml"


def _manifest_package_body_paths(repo_root: Path) -> list[Path]:
    """Resolve ModelPackage body paths via ADR-047 repository manifest (optional)."""
    try:
        from moex_repository_loader.loader import RepositoryLoader
    except ImportError:
        return []
    impl = repo_root / "model-assets" / "implementations"
    if not (impl / "manifest.yaml").is_file():
        return []
    loader = RepositoryLoader(repo_root, verify_hashes=False)
    paths: list[Path] = []
    for ref in loader.load_manifest().documents:
        if ref.kind != "package":
            continue
        env_path = impl / Path(ref.path)
        if not env_path.is_file():
            continue
        try:
            descriptor = yaml.safe_load(env_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(descriptor, dict):
            continue
        body_name = descriptor.get("body_ref") or descriptor.get("implementation_body")
        if not body_name:
            continue
        body_path = (env_path.parent / str(body_name)).resolve()
        if body_path.is_file():
            paths.append(body_path)
    return paths


def discover_package_paths(repo_root: Path) -> list[Path]:
    """Governance fixtures, curated examples, and manifest package bodies (ADR-047)."""
    paths: list[Path] = []
    example = (
        repo_root
        / "model-assets"
        / "specifications"
        / "moex-dams"
        / "0.1"
        / "requirements"
        / "examples"
        / "it-solution-model.example.yaml"
    )
    if example.is_file():
        paths.append(example)
    gov_example = (
        repo_root
        / "model-assets"
        / "specifications"
        / "moex-dams"
        / "0.1"
        / "examples"
        / "governance-assignments.example.yaml"
    )
    if gov_example.is_file():
        paths.append(gov_example)
    impl = repo_root / "model-assets" / "implementations"
    if impl.is_dir():
        for p in sorted(impl.rglob("*.governance.yaml")):
            paths.append(p)
    paths.extend(_manifest_package_body_paths(repo_root))
    seen: set[Path] = set()
    out: list[Path] = []
    for p in paths:
        key = p.resolve()
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be a mapping")
    return data


def _extract_package_and_assignments(
    data: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, list[Any]]]:
    """Support ModelPackage root or repository-shaped wrapper."""
    assignments: dict[str, list[Any]] = {
        key: list(data.get(key) or []) for key in _ASSIGNMENT_KEYS
    }
    if "model_packages" in data and isinstance(data.get("model_packages"), list):
        packages = [p for p in data["model_packages"] if isinstance(p, dict)]
        if not packages:
            raise ValueError("repository has no model_packages")
        # One view entry per package; caller flattens by iterating packages.
        return packages[0], assignments
    return data, assignments


def _serialize_value(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _input_digest(packages: list[dict[str, Any]], as_of: str) -> str:
    payload = {"as_of": as_of, "packages": packages}
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build_governance_view(
    packages: list[tuple[dict[str, Any], dict[str, list[Any]]]],
    *,
    as_of: str,
    built_at: str | None = None,
) -> tuple[dict[str, Any], list[Any]]:
    """Build EffectiveGovernanceView dict and aggregate diagnostics."""
    when = built_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    elements: list[dict[str, Any]] = []
    findings: list[Any] = []
    package_refs: list[str] = []
    digest_packages: list[dict[str, Any]] = []

    for body, assignments in packages:
        pkg_id = str(body.get("element_id") or body.get("name") or "")
        if pkg_id:
            package_refs.append(pkg_id)
        digest_packages.append({"body": body, "assignments": assignments})
        resolved = resolve_governed(body, as_of=as_of, assignments=assignments)
        findings.extend(diagnose_governance(body, as_of=as_of, assignments=assignments))
        for eid, slots in sorted(resolved.items()):
            slot_rows: list[dict[str, Any]] = []
            for slot_name in sorted(GOVERNED_SLOTS):
                prov = slots.get(slot_name)
                if prov is None:
                    continue
                row: dict[str, Any] = {
                    "slot_name": slot_name,
                    "value": _serialize_value(prov.value),
                    "layer": prov.layer,
                }
                if prov.source_element_id:
                    row["source_element_id"] = prov.source_element_id
                if prov.assignment_id:
                    row["assignment_id"] = prov.assignment_id
                slot_rows.append(row)
            elements.append(
                {
                    "element_ref": eid,
                    "package_ref": pkg_id,
                    "slots": slot_rows,
                }
            )

    view = {
        "as_of": as_of,
        "built_at": when,
        "input_digest": _input_digest(digest_packages, as_of),
        "package_refs": package_refs,
        "elements": elements,
    }
    return view, findings


def dump_governance_view(view: dict[str, Any]) -> str:
    header = (
        "# Generated EffectiveGovernanceView (ADR-049). Do not edit by hand.\n"
        "# Regenerate: python -m moex_dams.governance.cli materialize --root .\n"
    )
    body = yaml.safe_dump(view, sort_keys=False, allow_unicode=True)
    if not body.endswith("\n"):
        body += "\n"
    return header + body


def _load_packages(
    paths: list[Path],
) -> list[tuple[dict[str, Any], dict[str, list[Any]]]]:
    out: list[tuple[dict[str, Any], dict[str, list[Any]]]] = []
    for path in paths:
        data = _load_yaml(path)
        if "model_packages" in data and isinstance(data.get("model_packages"), list):
            assignments = {key: list(data.get(key) or []) for key in _ASSIGNMENT_KEYS}
            for pkg in data["model_packages"]:
                if isinstance(pkg, dict):
                    out.append((pkg, assignments))
        else:
            out.append(_extract_package_and_assignments(data))
    return out


def materialize_governance_view(
    repo_root: Path | str,
    *,
    as_of: str | None = None,
    package_paths: list[Path] | None = None,
    write: bool = True,
) -> tuple[Path, dict[str, Any], list[Any]]:
    """Load packages, build view, optionally write generated/governance/."""
    root = Path(repo_root)
    when = as_of or load_as_of(root)
    paths = package_paths if package_paths is not None else discover_package_paths(root)
    packages = _load_packages(paths)
    view, findings = build_governance_view(packages, as_of=when)
    out = governance_view_path(root, when)
    if write:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(dump_governance_view(view), encoding="utf-8")
    return out, view, findings


def check_governance_view(
    repo_root: Path | str,
    *,
    as_of: str | None = None,
    package_paths: list[Path] | None = None,
) -> list[str]:
    """Regenerate and diff against committed EffectiveGovernanceView.

    Also fails when diagnostics include severity=error.
    """
    root = Path(repo_root)
    errors: list[str] = []
    out, view, findings = materialize_governance_view(
        root,
        as_of=as_of,
        package_paths=package_paths,
        write=False,
    )
    for f in findings:
        if getattr(f, "severity", None) == "error":
            errors.append(f"{f.code}: {f.message}")
    expected_text = dump_governance_view(view)
    if not out.is_file():
        errors.append(f"missing generated EffectiveGovernanceView: {out}")
        return errors
    committed = yaml.safe_load(out.read_text(encoding="utf-8"))
    regenerated = yaml.safe_load(expected_text)
    if isinstance(committed, dict):
        committed.pop("built_at", None)
    if isinstance(regenerated, dict):
        regenerated.pop("built_at", None)
    if committed != regenerated:
        errors.append(
            f"EffectiveGovernanceView drift (hand-edit or stale): {out}. "
            "Run: python -m moex_dams.governance.cli materialize --root ."
        )
    return errors
