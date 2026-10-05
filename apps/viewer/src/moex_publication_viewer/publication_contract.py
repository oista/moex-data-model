"""ADR-019 phase 2: publication contract assessment (semantic content + reports)."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from moex_publication_viewer.manifest_loader import load_manifest, resolve_source_path
from moex_publication_viewer.models.manifest_models import (
    ManifestSection,
    PublicationManifest,
)
from moex_publication_viewer.models.publication_models import PublicationModule
from moex_publication_viewer.normalizers.helpers import select_path

logger = logging.getLogger(__name__)

# Semantic type → how to count entities in YAML/JSON sources (DAMS-oriented).
_SELECT_SUFFIXES: dict[str, tuple[str, ...]] = {
    "LogicalEntity": ("logical_entities", "logical-entities"),
    "LogicalAttribute": ("logical_attributes", "logical-attributes", "attributes"),
    "Relationship": ("relationships", "relations"),
    "DataCarrier": ("data_carriers",),
    "AccessPoint": ("access_points",),
    "DataContainer": ("data_containers",),
    "ExecutionAsset": ("execution_assets",),
    "PhysicalField": ("physical_fields", "physical-fields", "fields"),
    "EntityPhysicalMapping": ("mappings", "physical_mappings", "nodes"),
    "AttributePhysicalMapping": ("mappings", "physical_mappings", "nodes"),
}

_KIND_MARKERS: dict[str, frozenset[str]] = {
    "LogicalEntity": frozenset({"logical_entity", "LogicalEntity"}),
    "LogicalAttribute": frozenset({"attribute", "LogicalAttribute", "logical_attribute"}),
    "Relationship": frozenset({"relationship", "Relationship", "relation"}),
    "DataCarrier": frozenset({"data_carrier", "DataCarrier"}),
    "AccessPoint": frozenset({"access_point", "AccessPoint"}),
    "DataContainer": frozenset({"data_container", "DataContainer"}),
    "ExecutionAsset": frozenset({"execution_asset", "ExecutionAsset"}),
    "PhysicalField": frozenset({"field", "PhysicalField", "physical_field"}),
    "EntityPhysicalMapping": frozenset(
        {
            "mapping",
            "EntityPhysicalMapping",
            "maps_to",
            "entity_mapping",
            "entity_physical",
        }
    ),
    "AttributePhysicalMapping": frozenset(
        {
            "mapping",
            "AttributePhysicalMapping",
            "maps_to",
            "attribute_mapping",
            "field_mapping",
        }
    ),
}


@dataclass
class RequirementResultView:
    requirement_ref: str
    covered: bool
    covering_section_ids: list[str] = field(default_factory=list)
    result_status: str = "fail"  # pass | fail | skipped | warning
    result_message: str = ""
    obligation: str = "required"


@dataclass
class PublicationConformanceReportView:
    id: str
    implementation_ref: str
    reference_specification_ref: str
    profile_ref: str
    overall_publication_status: str
    requirement_results: list[RequirementResultView] = field(default_factory=list)
    title: str | None = None
    description: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "implementation_ref": self.implementation_ref,
            "reference_specification_ref": self.reference_specification_ref,
            "profile_ref": self.profile_ref,
            "overall_publication_status": self.overall_publication_status,
            "requirement_results": [asdict(r) for r in self.requirement_results],
        }


def spec_asset_dir(root: Path, specification_ref: str) -> Path | None:
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


def load_publication_requirements(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else None


def collect_profile_requirements(
    doc: dict[str, Any],
    profile_id: str,
    *,
    obligations: frozenset[str] | None = None,
) -> list[dict[str, Any]]:
    """Collect requirement dicts for profile + parent chain (dedupe by id, child wins)."""
    profiles = {
        p.get("id"): p
        for p in (doc.get("profiles") or [])
        if isinstance(p, dict) and p.get("id")
    }
    collected: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    seen_profiles: set[str] = set()
    current: str | None = profile_id
    chain: list[str] = []
    while current and current not in seen_profiles:
        seen_profiles.add(current)
        chain.append(current)
        prof = profiles.get(current)
        if prof is None:
            break
        parent = prof.get("parent_profile_ref")
        current = parent if isinstance(parent, str) else None

    # Walk parents first, then child overrides
    for pid in reversed(chain):
        prof = profiles.get(pid)
        if prof is None:
            continue
        for req in prof.get("requirements") or []:
            if not isinstance(req, dict):
                continue
            obligation = req.get("obligation") or "required"
            if obligations is not None and obligation not in obligations:
                continue
            rid = req.get("id")
            if not isinstance(rid, str):
                continue
            if rid not in collected:
                order.append(rid)
            collected[rid] = req
    return [collected[i] for i in order]


def _load_source_data(path: Path, fmt: str) -> Any:
    text = path.read_text(encoding="utf-8")
    if fmt in ("yaml", "linkml-yaml"):
        return yaml.safe_load(text)
    if fmt == "json":
        return json.loads(text)
    return None


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return [value]
    return []


def _min_occurs(req: dict[str, Any], default: int = 1) -> int:
    if "min_occurs" not in req or req.get("min_occurs") is None:
        return default
    return int(req["min_occurs"])


def count_semantic_entities(
    data: Any,
    semantic_types: list[str],
    *,
    select: str | None = None,
) -> int:
    """Count entities matching any of the expected semantic types."""
    if data is None or not semantic_types:
        return 0
    selected = data
    if select:
        try:
            selected = select_path(data, select)
        except KeyError:
            selected = data

    counts = [_count_one_type(data, selected, select, stype) for stype in semantic_types]
    return max(counts) if counts else 0


def _count_one_type(
    root: Any,
    selected: Any,
    select: str | None,
    stype: str,
) -> int:
    markers = _KIND_MARKERS.get(stype, frozenset())
    suffixes = _SELECT_SUFFIXES.get(stype, ())

    # Nested attributes under logical entities
    if stype == "LogicalAttribute":
        entities = _as_list(selected)
        if select and select.split(".")[-1] in ("logical_entities", "logical-entities"):
            return sum(
                len(_as_list(e.get("attributes")))
                for e in entities
                if isinstance(e, dict)
            )
        if isinstance(root, dict):
            ents = _as_list(root.get("logical_entities") or root.get("logical-entities"))
            nested = sum(
                len(_as_list(e.get("attributes"))) for e in ents if isinstance(e, dict)
            )
            if nested:
                return nested
        return len(
            [
                x
                for x in _as_list(selected)
                if isinstance(x, dict)
                and str(x.get("kind") or x.get("type") or "") in markers
            ]
        )

    if stype == "PhysicalField":
        objs = _as_list(selected)
        leaf = select.split(".")[-1] if select else ""
        if leaf in (
            "data_carriers",
            "physical-objects",
        ):
            return sum(
                len(_as_list(o.get("physical_fields") or o.get("fields")))
                for o in objs
                if isinstance(o, dict)
            )
        if isinstance(root, dict):
            pobjs = _as_list(
                root.get("data_carriers") or root.get("physical-objects")
            )
            nested = sum(
                len(_as_list(o.get("physical_fields") or o.get("fields")))
                for o in pobjs
                if isinstance(o, dict)
            )
            if nested:
                return nested

    items = _as_list(selected)
    if select:
        leaf = select.split(".")[-1]
        if leaf in suffixes or any(leaf == s for s in suffixes):
            if markers:
                marked = [
                    x
                    for x in items
                    if isinstance(x, dict)
                    and str(x.get("kind") or x.get("type") or "") in markers
                ]
                # mappings/nodes lists often mix kinds — prefer marked when present
                if marked:
                    return len(marked)
                if leaf in ("mappings", "physical_mappings"):
                    return len(items)
                if leaf == "nodes":
                    return len(
                        [
                            x
                            for x in items
                            if isinstance(x, dict)
                            and str(x.get("kind") or "") in markers
                        ]
                    )
                return len(items)
            return len(items)

    # Fall back: scan root for known keys
    if isinstance(root, dict):
        for suf in suffixes:
            if suf in root and isinstance(root[suf], list):
                vals = root[suf]
                if markers and suf == "nodes":
                    return len(
                        [
                            x
                            for x in vals
                            if isinstance(x, dict)
                            and str(x.get("kind") or "") in markers
                        ]
                    )
                if markers and suf in ("mappings", "physical_mappings"):
                    marked = [
                        x
                        for x in vals
                        if isinstance(x, dict)
                        and str(x.get("kind") or x.get("mapping_type") or "") in markers
                    ]
                    return len(marked) if marked else len(vals)
                return len(vals)

    if markers:
        return len(
            [
                x
                for x in items
                if isinstance(x, dict)
                and str(x.get("kind") or x.get("type") or "") in markers
            ]
        )
    return 0


def _physical_in_scope(module: PublicationModule, manifest: PublicationManifest) -> bool:
    covered = {
        sid
        for sec in module.sections
        for sid in (sec.satisfies or [])
        if isinstance(sid, str)
    }
    if "dams:physical-objects" in covered:
        return True
    for sec in manifest.sections:
        select = (sec.source.select or "").replace("-", "_")
        if "physical_object" in select:
            return True
    return False


def applies_when_active(
    applies_when: str | None,
    module: PublicationModule,
    manifest: PublicationManifest,
) -> bool:
    """Return False when requirement should be skipped (not applicable)."""
    if not applies_when:
        return True
    text = applies_when.lower()
    if "physical" in text:
        return _physical_in_scope(module, manifest)
    return True


def _section_covers(
    section: ManifestSection,
    req: dict[str, Any],
) -> bool:
    rid = req.get("id")
    if not isinstance(rid, str) or rid not in (section.satisfies or []):
        return False
    accepted_kinds = req.get("accepted_section_kinds") or []
    if accepted_kinds and section.kind and section.kind not in accepted_kinds:
        return False
    accepted_renderers = req.get("accepted_renderers") or []
    if accepted_renderers and section.type not in accepted_renderers:
        # Allow soft match: entity-table vs entity_table
        norm = {str(r).replace("_", "-") for r in accepted_renderers}
        if section.type.replace("_", "-") not in norm:
            return False
    return True


def _covering_sections(
    manifest: PublicationManifest,
    req: dict[str, Any],
) -> list[ManifestSection]:
    return [s for s in manifest.sections if _section_covers(s, req)]


def _assess_required_section(
    req: dict[str, Any],
    covering: list[ManifestSection],
) -> RequirementResultView:
    rid = str(req["id"])
    ids = [s.id for s in covering]
    min_occurs = _min_occurs(req, 1)
    if len(covering) >= min_occurs:
        return RequirementResultView(
            requirement_ref=rid,
            covered=True,
            covering_section_ids=ids,
            result_status="pass",
            result_message=f"covered by {len(covering)} section(s)",
            obligation=str(req.get("obligation") or "required"),
        )
    return RequirementResultView(
        requirement_ref=rid,
        covered=False,
        covering_section_ids=ids,
        result_status="fail",
        result_message=f"need >= {min_occurs} covering section(s), found {len(covering)}",
        obligation=str(req.get("obligation") or "required"),
    )


def _assess_semantic_content(
    req: dict[str, Any],
    covering: list[ManifestSection],
    manifest_path: Path,
) -> RequirementResultView:
    rid = str(req["id"])
    obligation = str(req.get("obligation") or "required")
    ids = [s.id for s in covering]
    if not covering:
        return RequirementResultView(
            requirement_ref=rid,
            covered=False,
            covering_section_ids=[],
            result_status="fail",
            result_message="no section with satisfies + accepted kind/renderer",
            obligation=obligation,
        )
    types = [str(t) for t in (req.get("expected_semantic_types") or [])]
    min_occurs = _min_occurs(req, 1)
    total = 0
    details: list[str] = []
    for sec in covering:
        src_path = resolve_source_path(manifest_path, sec.source.path)
        if not src_path.is_file():
            details.append(f"{sec.id}: missing source")
            continue
        try:
            data = _load_source_data(src_path, sec.source.format)
        except Exception as exc:  # noqa: BLE001
            details.append(f"{sec.id}: load error {exc}")
            continue
        n = count_semantic_entities(data, types, select=sec.source.select)
        total += n
        details.append(f"{sec.id}: {n}")
    if total >= min_occurs:
        return RequirementResultView(
            requirement_ref=rid,
            covered=True,
            covering_section_ids=ids,
            result_status="pass",
            result_message=f"semantic count={total} (>= {min_occurs}); {'; '.join(details)}",
            obligation=obligation,
        )
    return RequirementResultView(
        requirement_ref=rid,
        covered=False,
        covering_section_ids=ids,
        result_status="fail",
        result_message=(
            f"semantic count={total} < min_occurs={min_occurs} "
            f"for types {types}; {'; '.join(details)}"
        ),
        obligation=obligation,
    )


def _assess_binding(
    req: dict[str, Any],
    module: PublicationModule,
    spec_ref: str,
) -> RequirementResultView:
    rid = str(req["id"])
    obligation = str(req.get("obligation") or "required")
    matches = [
        i
        for i in (module.implements or [])
        if isinstance(i, dict) and i.get("specification_ref") == spec_ref
    ]
    if matches:
        return RequirementResultView(
            requirement_ref=rid,
            covered=True,
            covering_section_ids=[],
            result_status="pass",
            result_message=f"implements {spec_ref}",
            obligation=obligation,
        )
    return RequirementResultView(
        requirement_ref=rid,
        covered=False,
        covering_section_ids=[],
        result_status="fail",
        result_message=f"missing implements for {spec_ref}",
        obligation=obligation,
    )


def _assess_evidence(
    req: dict[str, Any],
    covering: list[ManifestSection],
    manifest_path: Path,
) -> RequirementResultView:
    rid = str(req["id"])
    obligation = str(req.get("obligation") or "required")
    ids = [s.id for s in covering]
    required_fields = [str(f) for f in (req.get("required_fields") or [])]
    if not required_fields:
        return RequirementResultView(
            requirement_ref=rid,
            covered=True,
            covering_section_ids=ids,
            result_status="skipped",
            result_message="no required_fields declared on requirement",
            obligation=obligation,
        )
    if not covering:
        return RequirementResultView(
            requirement_ref=rid,
            covered=False,
            covering_section_ids=[],
            result_status="fail",
            result_message="no covering section for evidence",
            obligation=obligation,
        )
    for sec in covering:
        src_path = resolve_source_path(manifest_path, sec.source.path)
        if not src_path.is_file():
            continue
        try:
            data = _load_source_data(src_path, sec.source.format)
        except Exception:  # noqa: BLE001
            continue
        if sec.source.select:
            try:
                data = select_path(data, sec.source.select)
            except KeyError:
                pass
        if isinstance(data, dict):
            missing = [f for f in required_fields if f not in data or data[f] in (None, "")]
            if not missing:
                return RequirementResultView(
                    requirement_ref=rid,
                    covered=True,
                    covering_section_ids=ids,
                    result_status="pass",
                    result_message=f"evidence fields present in {sec.id}",
                    obligation=obligation,
                )
            return RequirementResultView(
                requirement_ref=rid,
                covered=False,
                covering_section_ids=ids,
                result_status="fail",
                result_message=f"missing evidence fields in {sec.id}: {', '.join(missing)}",
                obligation=obligation,
            )
    return RequirementResultView(
        requirement_ref=rid,
        covered=False,
        covering_section_ids=ids,
        result_status="fail",
        result_message="evidence source not a dict with required_fields",
        obligation=obligation,
    )


def assess_requirement(
    req: dict[str, Any],
    *,
    module: PublicationModule,
    manifest: PublicationManifest,
    manifest_path: Path,
    spec_ref: str,
) -> RequirementResultView:
    obligation = str(req.get("obligation") or "required")
    rid = str(req.get("id") or "?")
    applies = req.get("applies_when")
    if isinstance(applies, str) and not applies_when_active(applies, module, manifest):
        return RequirementResultView(
            requirement_ref=rid,
            covered=True,
            covering_section_ids=[],
            result_status="skipped",
            result_message=f"applies_when not met: {applies}",
            obligation=obligation,
        )

    kind = str(req.get("kind") or "required-section")
    covering = _covering_sections(manifest, req)

    if kind == "required-binding":
        return _assess_binding(req, module, spec_ref)
    if kind == "required-semantic-content":
        return _assess_semantic_content(req, covering, manifest_path)
    if kind == "required-evidence":
        return _assess_evidence(req, covering, manifest_path)
    # required-section (default)
    return _assess_required_section(req, covering)


def _overall_status(
    results: list[RequirementResultView],
    *,
    draft: bool,
) -> str:
    if draft:
        return "draft-conformant"
    required_fails = [
        r for r in results if r.obligation == "required" and r.result_status == "fail"
    ]
    if required_fails:
        return "fail"
    recommended_gaps = [
        r
        for r in results
        if r.obligation == "recommended" and r.result_status in ("fail", "warning")
    ]
    if recommended_gaps:
        return "partially-conformant"
    return "conformant"


def assess_module_implements(
    module: PublicationModule,
    root: Path,
) -> list[PublicationConformanceReportView]:
    """Assess all implements entries; return one report per profile_ref."""
    if not module.implements or not module.manifest_path:
        return []
    manifest_path = Path(module.manifest_path)
    manifest = load_manifest(manifest_path)
    if manifest is None:
        return []

    reports: list[PublicationConformanceReportView] = []
    for impl in module.implements:
        if not isinstance(impl, dict):
            continue
        spec_ref = impl.get("specification_ref")
        profile_ref = impl.get("profile_ref")
        if not isinstance(spec_ref, str) or not isinstance(profile_ref, str):
            continue
        asset_dir = spec_asset_dir(root, spec_ref)
        if asset_dir is None:
            reports.append(
                PublicationConformanceReportView(
                    id=f"pubconf:{module.module_id}:{profile_ref}",
                    implementation_ref=module.module_id,
                    reference_specification_ref=spec_ref,
                    profile_ref=profile_ref,
                    overall_publication_status="fail",
                    requirement_results=[
                        RequirementResultView(
                            requirement_ref="*",
                            covered=False,
                            result_status="fail",
                            result_message=f"specification asset dir not found for {spec_ref}",
                            obligation="required",
                        )
                    ],
                    title=module.title,
                )
            )
            continue
        req_path = asset_dir / "publication-requirements.yaml"
        doc = load_publication_requirements(req_path)
        if doc is None:
            reports.append(
                PublicationConformanceReportView(
                    id=f"pubconf:{module.module_id}:{profile_ref}",
                    implementation_ref=module.module_id,
                    reference_specification_ref=spec_ref,
                    profile_ref=profile_ref,
                    overall_publication_status="fail",
                    requirement_results=[
                        RequirementResultView(
                            requirement_ref="*",
                            covered=False,
                            result_status="fail",
                            result_message=f"missing {req_path.name}",
                            obligation="required",
                        )
                    ],
                    title=module.title,
                )
            )
            continue

        reqs = collect_profile_requirements(doc, profile_ref)
        results = [
            assess_requirement(
                req,
                module=module,
                manifest=manifest,
                manifest_path=manifest_path,
                spec_ref=spec_ref,
            )
            for req in reqs
        ]
        draft = (
            str(impl.get("conformance_target") or "").lower() in ("draft", "draft-conformant")
            or str(getattr(manifest, "conformance_status", None) or "").lower()
            == "draft-conformant"
            or str(getattr(module, "conformance_status", None) or "").lower()
            == "draft-conformant"
        )
        status = _overall_status(results, draft=draft)
        reports.append(
            PublicationConformanceReportView(
                id=f"pubconf:{module.module_id}:{profile_ref}",
                implementation_ref=module.module_id,
                reference_specification_ref=spec_ref,
                profile_ref=profile_ref,
                overall_publication_status=status,
                requirement_results=results,
                title=module.title,
                description=(
                    f"Publication contract assessment for {profile_ref} "
                    f"against {spec_ref}"
                ),
            )
        )
    return reports


def write_conformance_reports(
    reports: list[PublicationConformanceReportView],
    modules: list[PublicationModule],
    dist_dir: Path | None,
) -> list[Path]:
    """Write per-module publication_conformance.json and optional dist index."""
    written: list[Path] = []
    by_module: dict[str, list[PublicationConformanceReportView]] = {}
    for rep in reports:
        by_module.setdefault(rep.implementation_ref, []).append(rep)

    module_by_id = {m.module_id: m for m in modules}
    for module_id, reps in by_module.items():
        mod = module_by_id.get(module_id)
        if mod is None or not mod.manifest_path:
            continue
        pub_dir = Path(mod.manifest_path).parent / "publications"
        pub_dir.mkdir(parents=True, exist_ok=True)
        # One file: if multiple profiles, nest under profiles list
        payload: dict[str, Any]
        if len(reps) == 1:
            payload = reps[0].to_dict()
        else:
            payload = {
                "implementation_ref": module_id,
                "reports": [r.to_dict() for r in reps],
                "overall_publication_status": reps[0].overall_publication_status,
            }
        out = pub_dir / "publication_conformance.json"
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(out)

    if dist_dir is not None:
        dist_dir.mkdir(parents=True, exist_ok=True)
        index = {
            "reports": [r.to_dict() for r in reports],
        }
        idx_path = dist_dir / "publication_conformance_index.json"
        idx_path.write_text(
            json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        written.append(idx_path)
    return written


def run_publication_contracts(
    modules: list[PublicationModule],
    root: Path,
    *,
    hard_fail: bool = True,
    dist_dir: Path | None = None,
) -> tuple[list[PublicationConformanceReportView], list[str]]:
    """
    Assess publication contracts for all modules with ``implements``.

    Required failures raise ValidationError when hard_fail is True.
    Recommended gaps are returned as warnings.
    """
    from moex_publication_viewer.validators import ValidationError

    reports: list[PublicationConformanceReportView] = []
    warnings: list[str] = []
    errors: list[str] = []

    for module in modules:
        if not module.implements:
            continue
        module_reports = assess_module_implements(module, root)
        reports.extend(module_reports)
        loc = module.manifest_path or module.module_id
        for rep in module_reports:
            for result in rep.requirement_results:
                msg = (
                    f"{loc}: [{rep.profile_ref}] {result.requirement_ref}: "
                    f"{result.result_status} — {result.result_message}"
                )
                if result.obligation == "required" and result.result_status == "fail":
                    errors.append(msg)
                elif result.obligation == "recommended" and result.result_status == "fail":
                    warnings.append(msg)
                    result.result_status = "warning"
                elif result.result_status == "skipped":
                    logger.info("%s", msg)

            if rep.overall_publication_status == "fail" and not any(
                r.obligation == "required" and r.result_status == "fail"
                for r in rep.requirement_results
            ):
                # structural fail (missing requirements file etc.)
                errors.append(
                    f"{loc}: publication contract '{rep.profile_ref}' overall fail"
                )

    write_conformance_reports(reports, modules, dist_dir)

    for w in warnings:
        logger.warning("%s", w)

    if hard_fail and errors:
        raise ValidationError(errors)
    for e in errors:
        logger.warning("%s", e)
        warnings.append(e)
    return reports, warnings


# Back-compat helpers used by older tests / validators
def collect_required_ids(doc: dict[str, Any], profile_id: str) -> list[str]:
    return [
        str(r["id"])
        for r in collect_profile_requirements(
            doc, profile_id, obligations=frozenset({"required"})
        )
        if r.get("id")
    ]
