"""Ontology profile report and schema URI semantic diff (ADR-030 / Stage 8)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from moex_modeling import (
    ChangeCategory,
    CurieUriResolver,
    DiagnosticDetail,
    SemanticChange,
    SemanticDiffReport,
)

from moex_dams.rules.identifiers import (
    load_merged_schema_prefix_map,
    load_schema_view,
)
from moex_dams.rules.ontology_uris import check_ontology_uris, _expand_element_iri


def schema_files_digest(schema_path: Path | str) -> str:
    """Stable sha256 over root schema + imported YAML paths (sorted)."""
    path = Path(schema_path).resolve()
    sv = load_schema_view(path, merge_imports=False)
    files: list[Path] = [path]
    schema_dir = path.parent
    for name in sv.imports_closure():
        if name.startswith("linkml:"):
            continue
        candidate = schema_dir / f"{name}.yaml"
        if candidate.is_file():
            files.append(candidate.resolve())
    unique = sorted({p.resolve() for p in files}, key=lambda p: p.as_posix().lower())
    h = hashlib.sha256()
    for file_path in unique:
        rel = file_path.name
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(file_path.read_bytes())
        h.update(b"\0")
    return "sha256:" + h.hexdigest()


def _element_iri_table(schema_path: Path | str) -> dict[str, str]:
    """Map stable element keys → expanded IRI."""
    sv = load_schema_view(schema_path, merge_imports=True)
    prefixes, default_prefix = load_merged_schema_prefix_map(schema_path)
    resolver = CurieUriResolver.from_schema_prefixes(
        prefixes, default_prefix=default_prefix
    )
    table: dict[str, str] = {}
    for class_name, cls in sv.all_classes().items():
        iri = _expand_element_iri(sv, resolver, cls)
        if iri:
            table[f"class:{class_name}"] = iri
    for slot_name, slot in sv.all_slots().items():
        iri = _expand_element_iri(sv, resolver, slot)
        if iri:
            table[f"slot:{slot_name}"] = iri
    for enum_name, enum in sv.all_enums().items():
        iri = _expand_element_iri(sv, resolver, enum)
        if iri:
            table[f"enum:{enum_name}"] = iri
        base = iri or resolver.expand(enum_name) or ""
        for pv_name in enum.permissible_values or {}:
            if base:
                table[f"enum_value:{enum_name}#{pv_name}"] = f"{base}#{pv_name}"
    return table


def diff_schema_element_uris(
    old_schema: Path | str,
    new_schema: Path | str,
    *,
    base_label: str | None = None,
    target_label: str | None = None,
) -> SemanticDiffReport:
    """Compare element IRIs; removed/changed → MOEX-ONT-010 BREAKING."""
    old_table = _element_iri_table(old_schema)
    new_table = _element_iri_table(new_schema)
    changes: list[SemanticChange] = []

    for key, old_iri in sorted(old_table.items()):
        if key not in new_table:
            changes.append(
                SemanticChange(
                    change_code="MOEX-ONT-010",
                    category=ChangeCategory.BREAKING,
                    subject_ref=key,
                    message=f"Removed element IRI {old_iri}",
                    path=key,
                    before=(
                        DiagnosticDetail(detail_key="iri", detail_value=old_iri),
                    ),
                )
            )
        elif new_table[key] != old_iri:
            changes.append(
                SemanticChange(
                    change_code="MOEX-ONT-010",
                    category=ChangeCategory.BREAKING,
                    subject_ref=key,
                    message=f"IRI changed from {old_iri} to {new_table[key]}",
                    path=key,
                    before=(
                        DiagnosticDetail(detail_key="iri", detail_value=old_iri),
                    ),
                    after=(
                        DiagnosticDetail(
                            detail_key="iri", detail_value=new_table[key]
                        ),
                    ),
                )
            )

    for key, new_iri in sorted(new_table.items()):
        if key not in old_table:
            changes.append(
                SemanticChange(
                    change_code="MOEX-ONT-010",
                    category=ChangeCategory.NON_BREAKING,
                    subject_ref=key,
                    message=f"Added element IRI {new_iri}",
                    path=key,
                    after=(
                        DiagnosticDetail(detail_key="iri", detail_value=new_iri),
                    ),
                )
            )

    old_path = Path(old_schema)
    new_path = Path(new_schema)
    return SemanticDiffReport(
        id="moex:diff:schema-uris",
        base_label=base_label or str(old_path),
        target_label=target_label or str(new_path),
        changes=tuple(changes),
    )


def build_ontology_profile(schema_path: Path | str) -> dict[str, Any]:
    """Build deterministic ontology-profile JSON dict."""
    path = Path(schema_path)
    sv = load_schema_view(path, merge_imports=True)
    prefixes, default_prefix = load_merged_schema_prefix_map(path)
    resolver = CurieUriResolver.from_schema_prefixes(
        prefixes, default_prefix=default_prefix
    )
    issues = [
        {
            "code": d.diagnostic_code,
            "severity": d.severity.value,
            "message": d.diagnostic_message,
            "subject": d.subject_ref,
        }
        for d in check_ontology_uris(path)
    ]

    classes: list[dict[str, Any]] = []
    for class_name, cls in sorted(sv.all_classes().items()):
        parents: list[str] = []
        if cls.is_a:
            parents.append(str(cls.is_a))
        parents.extend(str(m) for m in (cls.mixins or ()))
        classes.append(
            {
                "name": class_name,
                "iri": _expand_element_iri(sv, resolver, cls),
                "is_mixin": bool(cls.mixin),
                "parents": sorted(parents),
            }
        )

    slots: list[dict[str, Any]] = []
    for slot_name, slot in sorted(sv.all_slots().items()):
        slots.append(
            {
                "name": slot_name,
                "iri": _expand_element_iri(sv, resolver, slot),
            }
        )

    enums: list[dict[str, Any]] = []
    for enum_name, enum in sorted(sv.all_enums().items()):
        iri = _expand_element_iri(sv, resolver, enum)
        values = sorted((enum.permissible_values or {}).keys())
        enums.append(
            {
                "name": enum_name,
                "iri": iri,
                "values": [
                    {
                        "name": v,
                        "iri": f"{iri}#{v}" if iri else None,
                    }
                    for v in values
                ],
            }
        )

    return {
        "schema_id": sv.schema.id,
        "schema_name": sv.schema.name,
        "schema_version": sv.schema.version,
        "schema_digest": schema_files_digest(path),
        "default_prefix": default_prefix,
        "prefixes": dict(sorted(prefixes.items())),
        "classes": classes,
        "slots": slots,
        "enums": enums,
        "issues": issues,
    }


def ontology_profile_markdown(profile: dict[str, Any]) -> str:
    lines = [
        f"# Ontology profile: {profile.get('schema_name')}",
        "",
        f"- schema_id: `{profile.get('schema_id')}`",
        f"- schema_version: `{profile.get('schema_version')}`",
        f"- schema_digest: `{profile.get('schema_digest')}`",
        f"- default_prefix: `{profile.get('default_prefix')}`",
        f"- classes: {len(profile.get('classes') or [])}",
        f"- slots: {len(profile.get('slots') or [])}",
        f"- enums: {len(profile.get('enums') or [])}",
        f"- issues: {len(profile.get('issues') or [])}",
        "",
        "## Prefixes",
        "",
    ]
    for key, uri in (profile.get("prefixes") or {}).items():
        lines.append(f"- `{key}`: `{uri}`")
    if profile.get("issues"):
        lines.extend(["", "## Issues", ""])
        for issue in profile["issues"]:
            lines.append(
                f"- `{issue['code']}` {issue.get('subject') or '-'}: "
                f"{issue['message']}"
            )
    lines.append("")
    return "\n".join(lines)


def write_ontology_profile(
    schema_path: Path | str,
    *,
    json_path: Path,
    md_path: Path | None = None,
) -> str:
    """Write ontology-profile.json (+ optional .md); return content digest."""
    profile = build_ontology_profile(schema_path)
    text = json.dumps(profile, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(text, encoding="utf-8", newline="\n")
    if md_path is not None:
        md_path.write_text(
            ontology_profile_markdown(profile), encoding="utf-8", newline="\n"
        )
    digest = "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()
    return digest


__all__ = [
    "build_ontology_profile",
    "diff_schema_element_uris",
    "ontology_profile_markdown",
    "schema_files_digest",
    "write_ontology_profile",
]
