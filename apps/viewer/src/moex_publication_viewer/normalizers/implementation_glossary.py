"""Cross-implementation glossary for DAMS Реализации (ADR-025 view).

Aggregates ConceptualEntity (CDM), LogicalEntity (LDM), and RelationTerm rows
from every DAMS specification_implementation. Viewer-local lightweight
definition resolution — no dependency on ``moex_dams`` at runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from moex_publication_viewer.models.catalog_models import CatalogNode
from moex_publication_viewer.models.publication_models import (
    PublicationItem,
    PublicationModule,
    PublicationSection,
)

IMPLEMENTATIONS_GLOSSARY_ID = "implementations-glossary"
IMPLEMENTATIONS_GLOSSARY_NAV_ID = "implnav:glossary"

_INSTANCE_LEVELS: dict[str, tuple[str, str]] = {
    "ConceptualEntity": ("CDM", "entity"),
    "LogicalEntity": ("LDM", "entity"),
    "RelationTerm": ("CDM", "relation-term"),
}


class DefinitionMode(str, Enum):
    OWN = "own"
    OWN_ADAPTED = "own_adapted"
    INHERITED = "inherited"
    SCOPED = "scoped"
    UNRESOLVED = "unresolved"


@dataclass
class _IndexedElement:
    element_id: str
    level: str
    data: dict[str, Any]
    glossary_row_id: str | None = None


@dataclass
class DefinitionIndex:
    elements: dict[str, _IndexedElement] = field(default_factory=dict)
    # Prefer first-seen; later packages may shadow for lookup of shared CDM ids.
    first_row_for_element: dict[str, str] = field(default_factory=dict)

    def add(
        self,
        element_id: str,
        level: str,
        data: dict[str, Any],
        *,
        glossary_row_id: str | None = None,
    ) -> None:
        if not element_id:
            return
        if element_id not in self.elements:
            self.elements[element_id] = _IndexedElement(
                element_id, level, data, glossary_row_id
            )
        elif glossary_row_id and not self.elements[element_id].glossary_row_id:
            self.elements[element_id].glossary_row_id = glossary_row_id
        if glossary_row_id and element_id not in self.first_row_for_element:
            self.first_row_for_element[element_id] = glossary_row_id

    def get(self, element_id: str) -> _IndexedElement | None:
        return self.elements.get(element_id)


@dataclass(frozen=True)
class DefinitionProvenance:
    text: str | None
    mode: DefinitionMode
    source_element_id: str | None
    level: str | None
    diagnostic: str | None = None


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _attrs_as_element(item: PublicationItem) -> dict[str, Any]:
    """Rebuild a definition-bearing element dict from a publication item."""
    attrs = dict(item.attributes or {})
    eid = str(item.id)
    out: dict[str, Any] = {
        "element_id": eid,
        "name": attrs.get("name") or item.title or eid,
        "title": item.title or attrs.get("title") or attrs.get("name") or eid,
        "description": item.description or attrs.get("description"),
    }
    for key in (
        "definition_source_ref",
        "definition_rationale",
        "scoped_definitions",
        "conceptual_entity_refs",
        "conceptual_alignment_status",
        "external_class_refs",
        "parent_concept_ref",
        "entity_tier",
        "genesis_kind",
        "lifecycle_status",
        "aliases",
        "forward_label",
        "inverse_label",
        "symmetric",
        "dependency_kind",
    ):
        if key in attrs:
            out[key] = attrs[key]
    return out


def resolve_definition(
    element: dict[str, Any],
    index: DefinitionIndex,
    *,
    level: str | None = None,
    _stack: tuple[str, ...] = (),
) -> DefinitionProvenance:
    """Lightweight ADR-025 resolution (scoped → own → source_ref → single concept)."""
    eid = str(element.get("element_id") or element.get("name") or "")
    level = level or "ModelElement"
    if eid and eid in _stack:
        return DefinitionProvenance(
            text=None,
            mode=DefinitionMode.UNRESOLVED,
            source_element_id=eid or None,
            level=level,
            diagnostic=f"Cycle in definition resolution at {eid!r}.",
        )
    stack = _stack + ((eid,) if eid else ())

    alignment = str(element.get("conceptual_alignment_status") or "")
    own_required = alignment in {"pending", "local-only", "not-applicable"}

    description = element.get("description")
    source_ref = element.get("definition_source_ref")
    has_description = _nonempty(description)
    has_source = _nonempty(source_ref)

    if has_description:
        text = str(description).strip()
        mode = DefinitionMode.OWN_ADAPTED if has_source else DefinitionMode.OWN
        return DefinitionProvenance(
            text=text,
            mode=mode,
            source_element_id=eid or None,
            level=level,
        )

    if own_required:
        return DefinitionProvenance(
            text=None,
            mode=DefinitionMode.UNRESOLVED,
            source_element_id=eid or None,
            level=level,
            diagnostic=(
                f"Alignment status {alignment!r} requires an own description "
                "(inheritance not allowed)."
            ),
        )

    if has_source:
        return _resolve_ref(str(source_ref), index, stack=stack)

    if level == "LogicalEntity":
        refs = element.get("conceptual_entity_refs") or []
        if isinstance(refs, list):
            refs = [str(r) for r in refs if r]
        else:
            refs = []
        if len(refs) > 1:
            return DefinitionProvenance(
                text=None,
                mode=DefinitionMode.UNRESOLVED,
                source_element_id=eid or None,
                level=level,
                diagnostic=(
                    "Multiple conceptual_entity_refs without own description "
                    "or definition_source_ref (ambiguous)."
                ),
            )
        if len(refs) == 1:
            return _resolve_ref(refs[0], index, stack=stack)

    return DefinitionProvenance(
        text=None,
        mode=DefinitionMode.UNRESOLVED,
        source_element_id=eid or None,
        level=level,
        diagnostic="No description, definition_source_ref, or inheritable concept.",
    )


def _resolve_ref(
    ref: str,
    index: DefinitionIndex,
    *,
    stack: tuple[str, ...],
) -> DefinitionProvenance:
    if ref in stack:
        return DefinitionProvenance(
            text=None,
            mode=DefinitionMode.UNRESOLVED,
            source_element_id=ref,
            level=None,
            diagnostic=f"Cycle in definition_source_ref involving {ref!r}.",
        )
    indexed = index.get(ref)
    if indexed is None:
        return DefinitionProvenance(
            text=None,
            mode=DefinitionMode.UNRESOLVED,
            source_element_id=ref,
            level=None,
            diagnostic=f"Definition source {ref!r} not found.",
        )
    nested = resolve_definition(
        indexed.data,
        index,
        level=indexed.level,
        _stack=stack,
    )
    if nested.mode is DefinitionMode.UNRESOLVED:
        return nested
    return DefinitionProvenance(
        text=nested.text,
        mode=DefinitionMode.INHERITED,
        source_element_id=nested.source_element_id or indexed.element_id,
        level=nested.level,
        diagnostic=nested.diagnostic,
    )


def _reference_definition_without_own(
    element: dict[str, Any],
    index: DefinitionIndex,
    *,
    level: str,
) -> str | None:
    """What would be inherited if own description were absent."""
    shadow = {k: v for k, v in element.items() if k != "description"}
    inherited = resolve_definition(shadow, index, level=level)
    if inherited.mode is DefinitionMode.INHERITED and _nonempty(inherited.text):
        return inherited.text
    return None


def glossary_row_id(impl_catalog_id: str, element_id: str) -> str:
    return f"{impl_catalog_id}:{element_id}"


def _module_by_id(
    modules: list[PublicationModule], module_id: str | None
) -> PublicationModule | None:
    if not module_id:
        return None
    return next((m for m in modules if m.module_id == module_id), None)


@dataclass
class _TermSource:
    impl_catalog_id: str
    impl_title: str
    impl_module_id: str
    section_id: str
    instance_of: str
    model_level: str
    kind: str
    item: PublicationItem
    element: dict[str, Any]


def _collect_term_sources(
    modules: list[PublicationModule],
    impl_nodes: list[CatalogNode],
) -> list[_TermSource]:
    sources: list[_TermSource] = []
    for node in impl_nodes:
        mod = _module_by_id(modules, node.module_id)
        if mod is None:
            continue
        for sec in mod.sections:
            if sec.type == "explorer":
                continue
            level_kind = _INSTANCE_LEVELS.get(sec.instance_of or "")
            if level_kind is None:
                continue
            model_level, kind = level_kind
            for item in sec.items or []:
                eid = str(item.id or "").strip()
                if not eid:
                    continue
                sources.append(
                    _TermSource(
                        impl_catalog_id=node.id,
                        impl_title=node.title or mod.title,
                        impl_module_id=mod.module_id,
                        section_id=sec.id,
                        instance_of=sec.instance_of or "",
                        model_level=model_level,
                        kind=kind,
                        item=item,
                        element=_attrs_as_element(item),
                    )
                )
    return sources


def _build_index(sources: list[_TermSource]) -> DefinitionIndex:
    idx = DefinitionIndex()
    # Prefer ConceptualEntity / RelationTerm over LogicalEntity for shared ids.
    ordered = sorted(
        sources,
        key=lambda s: (
            0
            if s.instance_of in ("ConceptualEntity", "RelationTerm")
            else 1,
            s.impl_catalog_id,
            s.item.id,
        ),
    )
    for src in ordered:
        row_id = glossary_row_id(src.impl_catalog_id, src.item.id)
        level = src.instance_of or "ModelElement"
        idx.add(
            src.item.id,
            level,
            src.element,
            glossary_row_id=row_id,
        )
    return idx


def _rel_entry(target_id: str, rel: str) -> dict[str, str]:
    return {"id": target_id, "rel": rel}


def build_implementation_glossary_items(
    modules: list[PublicationModule],
    impl_nodes: list[CatalogNode],
) -> list[PublicationItem]:
    """Build flat A–Z glossary rows for all DAMS implementation terms."""
    sources = _collect_term_sources(modules, impl_nodes)
    if not sources:
        return []
    index = _build_index(sources)

    # element_id → all glossary row ids (for see_also same_concept)
    by_element: dict[str, list[str]] = {}
    # (impl_id, element_id) → row id
    row_ids: dict[tuple[str, str], str] = {}
    for src in sources:
        rid = glossary_row_id(src.impl_catalog_id, src.item.id)
        row_ids[(src.impl_catalog_id, src.item.id)] = rid
        by_element.setdefault(src.item.id, []).append(rid)

    # Precompute LDM→CDM parent links for taxonomy
    parents_map: dict[str, list[dict[str, str]]] = {}
    children_map: dict[str, list[dict[str, str]]] = {}

    for src in sources:
        rid = row_ids[(src.impl_catalog_id, src.item.id)]
        if src.instance_of != "LogicalEntity":
            continue
        refs = src.element.get("conceptual_entity_refs") or []
        if not isinstance(refs, list):
            continue
        for ref in refs:
            ref_s = str(ref).strip()
            if not ref_s:
                continue
            # Prefer CDM row in same solution, else first known CDM row.
            same = row_ids.get((src.impl_catalog_id, ref_s))
            parent_row = same or index.first_row_for_element.get(ref_s)
            if not parent_row:
                continue
            parents_map.setdefault(rid, []).append(
                _rel_entry(parent_row, "conceptual_entity_ref")
            )
            children_map.setdefault(parent_row, []).append(
                _rel_entry(rid, "realized_by")
            )

    # parent_concept_ref taxonomy among ConceptualEntity
    for src in sources:
        if src.instance_of != "ConceptualEntity":
            continue
        rid = row_ids[(src.impl_catalog_id, src.item.id)]
        pref = str(src.element.get("parent_concept_ref") or "").strip()
        if not pref:
            continue
        same = row_ids.get((src.impl_catalog_id, pref))
        parent_row = same or index.first_row_for_element.get(pref)
        if not parent_row:
            continue
        parents_map.setdefault(rid, []).append(
            _rel_entry(parent_row, "parent_concept_ref")
        )
        children_map.setdefault(parent_row, []).append(
            _rel_entry(rid, "child_concept")
        )

    items: list[PublicationItem] = []
    for src in sources:
        rid = row_ids[(src.impl_catalog_id, src.item.id)]
        level_name = src.instance_of or "ModelElement"
        prov = resolve_definition(src.element, index, level=level_name)
        ref_text = _reference_definition_without_own(
            src.element, index, level=level_name
        )
        own_text = (
            str(src.element.get("description")).strip()
            if _nonempty(src.element.get("description"))
            else ""
        )
        redundant = bool(
            own_text
            and ref_text
            and own_text == ref_text.strip()
            and prov.mode in (DefinitionMode.OWN, DefinitionMode.OWN_ADAPTED)
        )

        see_also: list[dict[str, str]] = []
        for other_rid in by_element.get(src.item.id, []):
            if other_rid != rid:
                see_also.append(_rel_entry(other_rid, "same_concept"))

        attrs: dict[str, Any] = {
            "kind": src.kind,
            "name": src.element.get("name") or src.item.id,
            "label": src.item.title or src.element.get("name") or src.item.id,
            "definition": prov.text or "",
            "definition_mode": prov.mode.value,
            "definition_source": prov.source_element_id,
            "definition_diagnostic": prov.diagnostic,
            "definition_rationale": src.element.get("definition_rationale"),
            "reference_definition": ref_text,
            "redundant_override": redundant,
            "model_level": src.model_level,
            "solution": src.impl_title,
            "solution_id": src.impl_catalog_id,
            "impl_module_id": src.impl_module_id,
            "impl_section_id": src.section_id,
            "source_item_id": src.item.id,
            "instance_of": src.instance_of,
            "scoped_definitions": src.element.get("scoped_definitions") or [],
            "conceptual_entity_refs": src.element.get("conceptual_entity_refs")
            or [],
            "external_class_refs": src.element.get("external_class_refs") or [],
            "aliases": src.element.get("aliases") or [],
            "entity_tier": src.element.get("entity_tier"),
            "genesis_kind": src.element.get("genesis_kind"),
            "lifecycle_status": src.element.get("lifecycle_status"),
            "taxonomy_parents": parents_map.get(rid, []),
            "taxonomy_children": children_map.get(rid, []),
            "see_also": see_also,
            "defined_in": f"{src.impl_title} · {src.model_level}",
        }
        if src.kind == "relation-term":
            attrs["forward_label"] = src.element.get("forward_label")
            attrs["inverse_label"] = src.element.get("inverse_label")
            attrs["symmetric"] = src.element.get("symmetric")
        parent_ref = src.element.get("parent_concept_ref")
        if parent_ref:
            attrs["parent_concept_ref"] = str(parent_ref)

        items.append(
            PublicationItem(
                id=rid,
                title=src.item.title or str(src.element.get("name") or src.item.id),
                description=prov.text or src.item.description,
                attributes=attrs,
            )
        )

    items.sort(key=lambda i: (i.title or i.id).lower())
    return items


def build_implementation_glossary_section(
    modules: list[PublicationModule],
    impl_nodes: list[CatalogNode],
) -> PublicationSection | None:
    """Build the aggregated implementations glossary section, or None if empty."""
    items = build_implementation_glossary_items(modules, impl_nodes)
    if not items:
        return None
    return PublicationSection(
        id=IMPLEMENTATIONS_GLOSSARY_ID,
        title="Глоссарий",
        description=(
            "Термины из реализаций моделей данных (CDM / LDM): сущности и "
            "термины отношений с указанием решения и режима определения."
        ),
        type="glossary",
        kind="glossary",
        filterable=["model_level", "solution", "kind", "definition_mode"],
        items=items,
        attributes={
            "term_cards": True,
            "glossary_scope": "implementations",
        },
    )
