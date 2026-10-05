"""One-way ModelPackage → Mermaid erDiagram projection (ADR-006)."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml

from moex_dams.projection.dbml import _ident, effective_attr_type
from moex_dams.projection.er_common import (
    MANY as _MANY,
    attr_keys_for_entity as _attr_keys_for_entity,
    fk_roles_for_entity as _fk_roles_for_entity,
    is_many as _is_many,
    is_optional as _is_optional,
    relation_term_label as _relation_term_label,
    unique_table_name as _unique_table_name,
)

MERMAID_CLI_PACKAGE = "@mermaid-js/mermaid-cli@11"
MERMAID_CONFIG_PATH = Path(__file__).with_name("mermaid_er_config.json")

Profile = Literal["logical", "physical", "conceptual"]

GENERATOR = "moex-dams-mermaid-er/0.1"

# Viewer section ids for conceptual clickmap deep-links / detail panels.
_CONCEPTUAL_ENTITY_SECTION = "conceptual"
_CONCEPTUAL_RELATIONSHIP_SECTION = "relationships"


@dataclass(frozen=True)
class ErDiagramManifest:
    content_digest: str
    profile: str
    source_path: str
    generator: str = GENERATOR

    def to_dict(self) -> dict[str, str]:
        return {
            "content_digest": self.content_digest,
            "profile": self.profile,
            "source_path": self.source_path,
            "generator": self.generator,
        }


def _escape_label(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _cardinality_edge(
    *,
    source_name: str,
    target_name: str,
    source_min: Any,
    source_max: Any,
    target_min: Any,
    target_max: Any,
    label: str,
) -> str:
    """Emit ``Target <left>--<right> Source : "label"`` (DBML ``>`` orientation)."""
    src_many = _is_many(source_max)
    tgt_many = _is_many(target_max)
    src_opt = _is_optional(source_min)
    tgt_opt = _is_optional(target_min)

    # Left marker = target end; right marker = source end.
    if tgt_many:
        left = "}o" if tgt_opt else "}|"
    else:
        left = "|o" if tgt_opt else "||"

    if src_many:
        right = "o{" if src_opt else "|{"
    else:
        right = "o|" if src_opt else "||"

    safe = _escape_label(label)
    return f'    {target_name} {left}--{right} {source_name} : "{safe}"'


def _attr_line(
    *,
    type_name: str,
    name: str,
    pk: bool,
    fk: bool,
    comment: str | None,
) -> str:
    bits = [type_name, name]
    # Mermaid erDiagram grammar: keys are comma-separated (PK,FK).
    keys: list[str] = []
    if pk:
        keys.append("PK")
    if fk:
        keys.append("FK")
    if keys:
        bits.append(",".join(keys))
    if comment:
        bits.append(f'"{_escape_label(comment)}"')
    return "        " + " ".join(bits)


def _entity_header(tname: str, title: Any) -> str:
    if title and str(title).strip() and str(title).strip() != tname:
        return f'    {tname}["{_escape_label(str(title).strip())}"] {{'
    return f"    {tname} {{"


def build_er_clickmap(
    data: dict[str, Any],
    *,
    profile: Profile,
) -> dict[str, Any]:
    """Map Mermaid entity/edge names to publication ``element_id`` targets."""
    entities: dict[str, dict[str, str]] = {}
    edges: list[dict[str, str]] = []
    table_names: set[str] = set()
    entity_table: dict[str, str] = {}

    if profile == "conceptual":
        entity_section = _CONCEPTUAL_ENTITY_SECTION
        rel_section = _CONCEPTUAL_RELATIONSHIP_SECTION
        for entity in data.get("conceptual_entities") or []:
            if not isinstance(entity, dict):
                continue
            tname = _unique_table_name(
                entity.get("name"), fallback="ConceptualEntity", used=table_names
            )
            eid = str(entity.get("element_id") or "")
            if eid:
                entity_table[eid] = tname
            entities[tname] = {
                "element_id": eid,
                "section_id": entity_section,
                "title": str(entity.get("title") or entity.get("name") or tname),
            }
        terms_by_id = {
            str(t.get("element_id")): t
            for t in (data.get("relation_terms") or [])
            if isinstance(t, dict) and t.get("element_id")
        }
        for rel in data.get("relationships") or []:
            if not isinstance(rel, dict):
                continue
            src_id = str(rel.get("source_entity_ref") or "")
            tgt_id = str(rel.get("target_entity_ref") or "")
            if src_id not in entity_table or tgt_id not in entity_table:
                continue
            edges.append(
                {
                    "source": entity_table[src_id],
                    "target": entity_table[tgt_id],
                    "label": _relation_term_label(rel, terms_by_id),
                    "element_id": str(rel.get("element_id") or ""),
                    "section_id": rel_section,
                }
            )
    return {"profile": profile, "entities": entities, "edges": edges}


def project_model_package_to_er_diagram(
    data: dict[str, Any],
    *,
    profile: Profile,
) -> str:
    """Project a ModelPackage mapping into Mermaid ``erDiagram`` text."""
    if profile not in ("logical", "physical", "conceptual"):
        raise ValueError(f"unsupported profile: {profile}")

    lines: list[str] = [
        "erDiagram",
        f"    %% Generated by {GENERATOR} profile={profile}",
        f"    %% source package_id={data.get('element_id') or data.get('name')}",
    ]

    entity_table: dict[str, str] = {}
    col_index: dict[str, tuple[str, str]] = {}
    table_names: set[str] = set()
    fk_field_ids: set[str] = set()

    relationships = [
        r for r in (data.get("relationships") or []) if isinstance(r, dict)
    ]
    mappings = [m for m in (data.get("mappings") or []) if isinstance(m, dict)]

    if profile == "physical":
        for mapping in mappings:
            if mapping.get("mapping_type") != "field_mapping":
                continue
            sources = [str(x) for x in (mapping.get("source_refs") or [])]
            targets = [str(x) for x in (mapping.get("target_refs") or [])]
            # Mark physical ends that participate in field_mapping between physical fields.
            for src in sources:
                for tgt in targets:
                    if src.startswith("dams:physical/") and tgt.startswith(
                        "dams:physical/"
                    ):
                        fk_field_ids.add(src)

    if profile == "conceptual":
        terms_by_id = {
            str(t.get("element_id")): t
            for t in (data.get("relation_terms") or [])
            if isinstance(t, dict) and t.get("element_id")
        }
        for entity in data.get("conceptual_entities") or []:
            if not isinstance(entity, dict):
                continue
            tname = _unique_table_name(
                entity.get("name"), fallback="ConceptualEntity", used=table_names
            )
            eid = entity.get("element_id")
            if eid:
                entity_table[str(eid)] = tname
            # Empty attribute block — conceptual layer has no PK/FK columns (ADR-029).
            # Mermaid requires a non-empty entity body; use a neutral marker field.
            lines.append(_entity_header(tname, entity.get("title")))
            lines.append('        string concept "concept"')
            lines.append("    }")
        for rel in relationships:
            src_id = str(rel.get("source_entity_ref") or "")
            tgt_id = str(rel.get("target_entity_ref") or "")
            if src_id not in entity_table or tgt_id not in entity_table:
                continue
            label = _relation_term_label(rel, terms_by_id)
            lines.append(
                _cardinality_edge(
                    source_name=entity_table[src_id],
                    target_name=entity_table[tgt_id],
                    source_min=rel.get("source_min_cardinality"),
                    source_max=rel.get("source_max_cardinality", _MANY),
                    target_min=rel.get("target_min_cardinality"),
                    target_max=rel.get("target_max_cardinality", 1),
                    label=label,
                )
            )
        return "\n".join(lines).rstrip() + "\n"

    if profile == "logical":
        for entity in data.get("logical_entities") or []:
            if not isinstance(entity, dict):
                continue
            tname = _unique_table_name(
                entity.get("name"), fallback="LogicalEntity", used=table_names
            )
            eid = entity.get("element_id")
            if eid:
                entity_table[str(eid)] = tname
            key_refs = _attr_keys_for_entity(entity)
            fk_roles = _fk_roles_for_entity(str(eid or ""), relationships)
            lines.append(_entity_header(tname, entity.get("title")))
            for attr in entity.get("attributes") or []:
                if not isinstance(attr, dict):
                    continue
                cname = _ident(attr.get("name"), fallback="attr")
                ctype = _ident(effective_attr_type(attr), fallback="string")
                aid = str(attr.get("element_id") or "")
                pk = (
                    effective_attr_type(attr) == "identifier"
                    or (aid and aid in key_refs)
                    or bool(attr.get("business_key_kind"))
                )
                # identifier alone is often PK; FK when role matches and not sole PK marker
                fk = str(attr.get("name") or "") in fk_roles
                if fk and effective_attr_type(attr) == "identifier" and not (
                    aid in key_refs or attr.get("business_key_kind")
                ):
                    # role-matched identifier acting as FK — keep FK, drop PK unless key
                    pk = False
                comment = attr.get("title")
                comment_s = str(comment) if comment else None
                lines.append(
                    _attr_line(
                        type_name=ctype,
                        name=cname,
                        pk=pk,
                        fk=fk,
                        comment=comment_s,
                    )
                )
                if aid:
                    col_index[aid] = (tname, cname)
            lines.append("    }")
    else:
        for obj in data.get("data_carriers") or []:
            if not isinstance(obj, dict):
                continue
            tname = _unique_table_name(
                obj.get("name"), fallback="DataCarrier", used=table_names
            )
            oid = obj.get("element_id")
            if oid:
                entity_table[str(oid)] = tname
            lines.append(_entity_header(tname, obj.get("title")))
            for field in obj.get("physical_fields") or []:
                if not isinstance(field, dict):
                    continue
                cname = _ident(
                    field.get("native_name") or field.get("name"),
                    fallback="field",
                )
                ctype = _ident(field.get("native_type"), fallback="string")
                fid = str(field.get("element_id") or "")
                pk = bool(field.get("business_key_kind")) or (
                    field.get("native_name") == "id" or field.get("name") == "id"
                )
                fk = bool(fid and fid in fk_field_ids)
                if fk:
                    pk = False
                comment = field.get("title")
                comment_s = str(comment) if comment else None
                lines.append(
                    _attr_line(
                        type_name=ctype,
                        name=cname,
                        pk=pk,
                        fk=fk,
                        comment=comment_s,
                    )
                )
                if fid:
                    col_index[fid] = (tname, cname)
            lines.append("    }")

    if profile == "logical":
        for rel in relationships:
            src_id = str(rel.get("source_entity_ref") or "")
            tgt_id = str(rel.get("target_entity_ref") or "")
            if src_id not in entity_table or tgt_id not in entity_table:
                continue
            rname = str(rel.get("name") or "rel")
            lines.append(
                _cardinality_edge(
                    source_name=entity_table[src_id],
                    target_name=entity_table[tgt_id],
                    source_min=rel.get("source_min_cardinality"),
                    source_max=rel.get("source_max_cardinality", _MANY),
                    target_min=rel.get("target_min_cardinality"),
                    target_max=rel.get("target_max_cardinality", 1),
                    label=rname,
                )
            )
    else:
        seen_edges: set[tuple[str, str, str]] = set()
        for mapping in mappings:
            mtype = mapping.get("mapping_type")
            sources = [str(x) for x in (mapping.get("source_refs") or [])]
            targets = [str(x) for x in (mapping.get("target_refs") or [])]
            mname = str(mapping.get("name") or "map")

            if mtype == "field_mapping":
                for src in sources:
                    for tgt in targets:
                        if src not in col_index or tgt not in col_index:
                            continue
                        st, _sc = col_index[src]
                        tt, _tc = col_index[tgt]
                        key = (st, tt, mname)
                        if key in seen_edges:
                            continue
                        seen_edges.add(key)
                        # FK field (source) many → target table one
                        lines.append(
                            _cardinality_edge(
                                source_name=st,
                                target_name=tt,
                                source_min=0,
                                source_max=_MANY,
                                target_min=0,
                                target_max=1,
                                label=mname,
                            )
                        )
            elif mtype in {"object_mapping", "entity_mapping"}:
                for src in sources:
                    for tgt in targets:
                        if src not in entity_table or tgt not in entity_table:
                            continue
                        st = entity_table[src]
                        tt = entity_table[tgt]
                        key = (st, tt, mname)
                        if key in seen_edges:
                            continue
                        seen_edges.add(key)
                        lines.append(
                            _cardinality_edge(
                                source_name=st,
                                target_name=tt,
                                source_min=0,
                                source_max=_MANY,
                                target_min=0,
                                target_max=1,
                                label=mname,
                            )
                        )

    return "\n".join(lines).rstrip() + "\n"


def write_er_diagram_artifact(
    *,
    implementation_path: Path,
    out_md: Path,
    profile: Profile,
    reset_layout: bool = False,
) -> ErDiagramManifest:
    """Load ModelPackage YAML, write Mermaid md + scene + layout sidecars."""
    from moex_dams.projection.er_layout import write_or_merge_layout
    from moex_dams.projection.er_scene import project_model_package_to_er_scene

    raw = yaml.safe_load(implementation_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"expected ModelPackage mapping in {implementation_path}")
    diagram = project_model_package_to_er_diagram(raw, profile=profile)
    body = (
        f"<!-- Generated by {GENERATOR} profile={profile} -->\n\n"
        f"```mermaid\n{diagram.rstrip()}\n```\n"
    )
    out_md.parent.mkdir(parents=True, exist_ok=True)
    data = body.encode("utf-8")
    out_md.write_bytes(data)
    digest = "sha256:" + hashlib.sha256(data).hexdigest()
    manifest = ErDiagramManifest(
        content_digest=digest,
        profile=profile,
        source_path=str(implementation_path),
    )
    manifest_path = out_md.with_name(out_md.name + ".manifest.json")
    manifest_path.write_text(
        json.dumps(manifest.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if profile == "conceptual":
        clickmap = build_er_clickmap(raw, profile=profile)
        # conceptual.erd.md → conceptual.erd.clickmap.json
        clickmap_path = out_md.parent / (out_md.stem + ".clickmap.json")
        clickmap_path.write_text(
            json.dumps(clickmap, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    # logical.erd.md → logical.scene.json / logical.layout.json
    stem = out_md.name
    if stem.endswith(".erd.md"):
        base = stem[: -len(".erd.md")]
    else:
        base = out_md.stem
    scene = project_model_package_to_er_scene(raw, profile=profile)
    scene_path = out_md.parent / f"{base}.scene.json"
    scene_path.write_text(
        json.dumps(scene, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    layout_path = out_md.parent / f"{base}.layout.json"
    write_or_merge_layout(
        scene=scene,
        layout_path=layout_path,
        profile=profile,
        reset=reset_layout,
    )
    return manifest


def _find_npx() -> str | None:
    """Resolve npx executable (prefer ``npx.cmd`` on Windows)."""
    for name in ("npx.cmd", "npx"):
        found = shutil.which(name)
        if found:
            return found
    return None


def _extract_mermaid_body(md_text: str) -> str:
    """Pull fenced `` ```mermaid `` body, or return text starting with ``erDiagram``."""
    marker = "```mermaid"
    start = md_text.find(marker)
    if start >= 0:
        rest = md_text[start + len(marker) :]
        end = rest.find("```")
        if end >= 0:
            return rest[:end].strip() + "\n"
    stripped = md_text.lstrip()
    if stripped.startswith("erDiagram"):
        return stripped if stripped.endswith("\n") else stripped + "\n"
    return md_text


def try_render_er_svg(md_path: Path, *, out_svg: Path | None = None) -> Path | None:
    """Render ``*.erd.md`` to sibling SVG via npx mermaid-cli. Returns path or None."""
    if not md_path.is_file():
        return None
    dest = out_svg or md_path.with_suffix(".svg")
    npx = _find_npx()
    if not npx:
        return None
    # mmdc renames multi-chart markdown outputs (*.erd-1.svg); feed a raw .mmd instead.
    body = _extract_mermaid_body(md_path.read_text(encoding="utf-8"))
    tmp_mmd = dest.with_suffix(".mmd")
    try:
        tmp_mmd.write_text(body, encoding="utf-8")
        cmd = [
            npx,
            "--yes",
            MERMAID_CLI_PACKAGE,
            "-i",
            str(tmp_mmd),
            "-o",
            str(dest),
            "-b",
            "transparent",
        ]
        if MERMAID_CONFIG_PATH.is_file():
            cmd.extend(["-c", str(MERMAID_CONFIG_PATH)])
        else:
            cmd.extend(["-t", "neutral"])
        proc = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=300,
            shell=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    finally:
        try:
            tmp_mmd.unlink(missing_ok=True)
        except OSError:
            pass
    if proc.returncode != 0 or not dest.is_file():
        return None
    return dest
