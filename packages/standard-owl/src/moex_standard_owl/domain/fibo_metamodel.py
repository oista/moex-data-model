"""FIBO ontology profile metamodel (TSpecBody) — structure only, not domain classes."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict


class FiboElementKind(str, Enum):
    """Metamodel element kinds (conventions), not FIBO domain instances."""

    CLASS = "class"
    OBJECT_PROPERTY = "object_property"
    DATA_PROPERTY = "data_property"
    INDIVIDUAL = "individual"
    ONTOLOGY = "ontology"


class FiboDomain(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    code: str
    title: str
    iri_segment: str
    description: str | None = None


class FiboModule(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: str
    domain_code: str
    title: str
    path_segments: tuple[str, ...] = ()
    description: str | None = None


class FiboOntologyDocument(BaseModel):
    """Ontology header fields from FIBO ONTOLOGY_GUIDE."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: str
    module_id: str
    ontology_iri: str
    version_iri: str | None = None
    label: str
    abstract: str | None = None
    license: str | None = None
    copyright: str | None = None
    maturity: str | None = None
    abbreviation: str | None = None
    filename: str | None = None
    imports: tuple[str, ...] = ()


class FiboIriPattern(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: str
    name: str
    template: str
    description: str | None = None


class FiboPrefixPattern(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: str
    name: str
    template: str
    description: str | None = None


class FiboAnnotationRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: str
    annotation_property: str
    applies_to: Literal["ontology_header", "element"]
    required: bool = True
    description: str | None = None


class FiboSpecificationBody(BaseModel):
    """Root TSpecBody for the FIBO ontology profile (not release entity index)."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    descriptor_path: str
    specification_id: str
    name: str | None = None
    version: str | None = None
    revision: str | None = None
    domains: tuple[FiboDomain, ...] = ()
    modules: tuple[FiboModule, ...] = ()
    documents: tuple[FiboOntologyDocument, ...] = ()
    iri_patterns: tuple[FiboIriPattern, ...] = ()
    prefix_patterns: tuple[FiboPrefixPattern, ...] = ()
    annotation_requirements: tuple[FiboAnnotationRequirement, ...] = ()

    @property
    def path(self) -> Path:
        return Path(self.descriptor_path)


def _as_tuple_maps(raw: Any) -> list[dict[str, Any]]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ValueError("expected a YAML list")
    out: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("expected mapping entries in list")
        out.append(item)
    return out


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected mapping in {path}")
    return data


def load_fibo_specification_body(spec_dir: Path) -> FiboSpecificationBody:
    """Load profile envelope + metamodel YAML files under ``spec_dir``."""
    spec_dir = spec_dir.resolve()
    envelope_path = spec_dir / "specification.yaml"
    if not envelope_path.is_file():
        raise FileNotFoundError(f"missing specification.yaml under {spec_dir}")
    envelope = _load_yaml(envelope_path)

    meta = spec_dir / "metamodel"
    arch = _load_yaml(meta / "fibo-architecture.yaml")
    annotations = _load_yaml(meta / "annotation-profile.yaml")
    patterns = _load_yaml(meta / "iri-patterns.yaml")

    domains = tuple(FiboDomain.model_validate(d) for d in _as_tuple_maps(arch.get("domains")))
    modules = []
    for m in _as_tuple_maps(arch.get("modules")):
        segs = m.get("path_segments") or []
        if isinstance(segs, str):
            segs = [segs]
        modules.append(
            FiboModule.model_validate({**m, "path_segments": tuple(str(s) for s in segs)})
        )
    documents = []
    for d in _as_tuple_maps(arch.get("documents")):
        imports = d.get("imports") or []
        if isinstance(imports, str):
            imports = [imports]
        documents.append(
            FiboOntologyDocument.model_validate(
                {**d, "imports": tuple(str(x) for x in imports)}
            )
        )

    iri_patterns = tuple(
        FiboIriPattern.model_validate(p) for p in _as_tuple_maps(patterns.get("iri_patterns"))
    )
    prefix_patterns = tuple(
        FiboPrefixPattern.model_validate(p)
        for p in _as_tuple_maps(patterns.get("prefix_patterns"))
    )
    annotation_requirements = tuple(
        FiboAnnotationRequirement.model_validate(a)
        for a in _as_tuple_maps(annotations.get("requirements"))
    )

    return FiboSpecificationBody(
        descriptor_path=str(envelope_path),
        specification_id=str(envelope.get("id") or "moex-fibo-profile"),
        name=envelope.get("name"),
        version=envelope.get("version"),
        revision=envelope.get("revision"),
        domains=domains,
        modules=tuple(modules),
        documents=tuple(documents),
        iri_patterns=iri_patterns,
        prefix_patterns=prefix_patterns,
        annotation_requirements=annotation_requirements,
    )


def fibo_body_to_explorer_records(body: FiboSpecificationBody) -> list[dict[str, Any]]:
    """Nested PublicationItem-shaped dicts: Domains → Modules → Ontology documents."""
    modules_by_domain: dict[str, list[FiboModule]] = {}
    for mod in body.modules:
        modules_by_domain.setdefault(mod.domain_code, []).append(mod)

    docs_by_module: dict[str, list[FiboOntologyDocument]] = {}
    for doc in body.documents:
        docs_by_module.setdefault(doc.module_id, []).append(doc)

    domain_children: list[dict[str, Any]] = []
    for domain in body.domains:
        module_nodes: list[dict[str, Any]] = []
        for mod in modules_by_domain.get(domain.code, []):
            doc_nodes = [
                {
                    "id": f"onto:{doc.id}",
                    "title": doc.label,
                    "description": doc.abstract,
                    "attributes": {
                        "kind": "ontology_document",
                        "ontology_iri": doc.ontology_iri,
                        "version_iri": doc.version_iri,
                        "maturity": doc.maturity,
                        "abbreviation": doc.abbreviation,
                        "filename": doc.filename,
                        "imports": list(doc.imports),
                        "module_id": doc.module_id,
                    },
                }
                for doc in docs_by_module.get(mod.id, [])
            ]
            module_nodes.append(
                {
                    "id": f"module:{mod.id}",
                    "title": mod.title,
                    "description": mod.description,
                    "attributes": {
                        "kind": "fibo_module",
                        "domain_code": mod.domain_code,
                        "path_segments": list(mod.path_segments),
                    },
                    "children": doc_nodes,
                }
            )
        domain_children.append(
            {
                "id": f"domain:{domain.code}",
                "title": domain.code,
                "description": domain.title,
                "attributes": {
                    "kind": "fibo_domain",
                    "iri_segment": domain.iri_segment,
                    "purpose": domain.description or domain.title,
                },
                "children": module_nodes,
            }
        )

    metamodel_root = {
        "id": "group:fibo-domains",
        "title": "Domains and modules",
        "description": "FIBO domains, modules, and ontology document headers.",
        "attributes": {
            "kind": "group",
            "section_root": "taxonomy-domains",
            "purpose": "Organizational taxonomy of the FIBO ontology profile.",
            "structure_why": "Domains → modules → ontology documents (ONTOLOGY_GUIDE).",
            "member_ids": [c["id"] for c in domain_children],
        },
        "children": domain_children,
    }

    pattern_children = [
        {
            "id": f"iri:{p.id}",
            "title": p.name,
            "description": p.description,
            "attributes": {"kind": "iri_pattern", "template": p.template},
        }
        for p in body.iri_patterns
    ] + [
        {
            "id": f"prefix:{p.id}",
            "title": p.name,
            "description": p.description,
            "attributes": {"kind": "prefix_pattern", "template": p.template},
        }
        for p in body.prefix_patterns
    ]
    patterns_root = {
        "id": "group:fibo-patterns",
        "title": "IRI and prefixes",
        "description": "FIBO IRI and namespace prefix templates.",
        "attributes": {
            "kind": "group",
            "section_root": "patterns",
            "purpose": "Canonical IRI and prefix patterns from ONTOLOGY_GUIDE.",
            "member_ids": [c["id"] for c in pattern_children],
        },
        "children": pattern_children,
    }

    ann_children = [
        {
            "id": f"ann:{a.id}",
            "title": a.annotation_property,
            "description": a.description,
            "attributes": {
                "kind": "annotation_requirement",
                "applies_to": a.applies_to,
                "required": a.required,
            },
        }
        for a in body.annotation_requirements
    ]
    annotations_root = {
        "id": "group:fibo-annotations",
        "title": "Annotation profile",
        "description": "Required ontology header and element annotations.",
        "attributes": {
            "kind": "group",
            "section_root": "annotations",
            "purpose": "Minimum metadata for published FIBO ontologies and elements.",
            "member_ids": [c["id"] for c in ann_children],
        },
        "children": ann_children,
    }

    return [metamodel_root, patterns_root, annotations_root]
