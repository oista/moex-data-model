"""Definition cascade along the semantic axis (ADR-025).

YAML stores declared description / definition_source_ref / scoped_definitions.
This module resolves the effective definition with provenance across packages
and external exact sources (ontology class, corporate GlossaryTerm).

Orthogonal to the containment cascade of governed properties (ADR-023).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol


class DefinitionMode(str, Enum):
    OWN = "own"
    OWN_ADAPTED = "own_adapted"
    INHERITED = "inherited"
    SCOPED = "scoped"
    UNRESOLVED = "unresolved"


# Alignment statuses that forbid inheriting a definition (must declare own text).
_OWN_REQUIRED_ALIGNMENT = frozenset({"pending", "local-only", "not-applicable"})

# Relations that allow inheriting definition text from an ontology / external term.
EXACT_MATCH_RELATIONS = frozenset(
    {
        "skos:exactMatch",
        "owl:equivalentClass",
        "exact",
        "equivalent",
    }
)


@dataclass(frozen=True)
class DefinitionProvenance:
    text: str | None
    language: str | None
    source_element_id: str | None
    level: str | None
    mode: DefinitionMode
    scope: str | None = None
    source_hash: str | None = None
    diagnostic: str | None = None


@dataclass(frozen=True)
class ExternalDefinition:
    """Definition supplied by an ontology class or GlossaryTerm."""

    id: str
    text: str
    language: str | None = None
    level: str = "external"
    exact: bool = False


class ExternalDefinitionProvider(Protocol):
    def lookup(self, ref: str) -> ExternalDefinition | None:
        """Return definition for ``ref``, or None if unknown."""
        ...


@dataclass
class _IndexedElement:
    element_id: str
    level: str
    data: dict[str, Any]


@dataclass
class DefinitionIndex:
    """Cross-package index of definition-bearing model elements."""

    elements: dict[str, _IndexedElement] = field(default_factory=dict)
    providers: tuple[ExternalDefinitionProvider, ...] = ()
    # solution_ref -> set of ITSystem ids (for scope_ref validation)
    solution_systems: dict[str, frozenset[str]] = field(default_factory=dict)

    def get(self, element_id: str) -> _IndexedElement | None:
        return self.elements.get(element_id)

    def add_package(self, body_data: dict[str, Any]) -> None:
        """Index ConceptualEntity / LogicalEntity / LogicalAttribute from a package."""
        if not isinstance(body_data, dict):
            return
        for ent in body_data.get("conceptual_entities") or []:
            if isinstance(ent, dict) and ent.get("element_id"):
                eid = str(ent["element_id"])
                self.elements[eid] = _IndexedElement(eid, "ConceptualEntity", ent)
        for ent in body_data.get("logical_entities") or []:
            if not isinstance(ent, dict) or not ent.get("element_id"):
                continue
            eid = str(ent["element_id"])
            self.elements[eid] = _IndexedElement(eid, "LogicalEntity", ent)
            for attr in ent.get("attributes") or []:
                if isinstance(attr, dict) and attr.get("element_id"):
                    aid = str(attr["element_id"])
                    self.elements[aid] = _IndexedElement(aid, "LogicalAttribute", attr)

    def add_solution_systems(
        self, solution_ref: str, system_refs: list[str] | tuple[str, ...]
    ) -> None:
        self.solution_systems[solution_ref] = frozenset(str(s) for s in system_refs)


def build_definition_index(
    *packages: dict[str, Any],
    providers: tuple[ExternalDefinitionProvider, ...] = (),
    solution_systems: dict[str, list[str]] | None = None,
) -> DefinitionIndex:
    idx = DefinitionIndex(providers=providers)
    for pkg in packages:
        idx.add_package(pkg)
    if solution_systems:
        for sol, systems in solution_systems.items():
            idx.add_solution_systems(sol, systems)
    return idx


def _text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _lookup_external(
    index: DefinitionIndex, ref: str
) -> ExternalDefinition | None:
    for provider in index.providers:
        found = provider.lookup(ref)
        if found is not None:
            return found
    return None


def _resolve_ref(
    ref: str,
    index: DefinitionIndex,
    *,
    stack: tuple[str, ...],
    require_exact_external: bool,
) -> DefinitionProvenance:
    if ref in stack:
        return DefinitionProvenance(
            text=None,
            language=None,
            source_element_id=ref,
            level=None,
            mode=DefinitionMode.UNRESOLVED,
            diagnostic=f"Cycle in definition_source_ref involving {ref!r}.",
        )
    indexed = index.get(ref)
    if indexed is not None:
        nested = resolve_definition(
            indexed.data,
            index,
            level=indexed.level,
            _stack=stack,
        )
        if nested.mode is DefinitionMode.UNRESOLVED:
            return nested
        # From the caller's perspective this is always inherited, even when
        # the target element's own mode is OWN / OWN_ADAPTED.
        return DefinitionProvenance(
            text=nested.text,
            language=nested.language,
            source_element_id=nested.source_element_id or indexed.element_id,
            level=nested.level,
            mode=DefinitionMode.INHERITED,
            scope=nested.scope,
            source_hash=nested.source_hash,
            diagnostic=nested.diagnostic,
        )
    external = _lookup_external(index, ref)
    if external is None:
        return DefinitionProvenance(
            text=None,
            language=None,
            source_element_id=ref,
            level=None,
            mode=DefinitionMode.UNRESOLVED,
            diagnostic=f"Definition source {ref!r} not found.",
        )
    if require_exact_external and not external.exact:
        return DefinitionProvenance(
            text=None,
            language=None,
            source_element_id=external.id,
            level=external.level,
            mode=DefinitionMode.UNRESOLVED,
            diagnostic=(
                f"Definition source {ref!r} is not an exact match "
                "(closeMatch/broadMatch cannot inherit; declare own description)."
            ),
        )
    if not _nonempty(external.text):
        return DefinitionProvenance(
            text=None,
            language=external.language,
            source_element_id=external.id,
            level=external.level,
            mode=DefinitionMode.UNRESOLVED,
            diagnostic=f"Definition source {ref!r} has empty text.",
        )
    return DefinitionProvenance(
        text=external.text.strip(),
        language=external.language,
        source_element_id=external.id,
        level=external.level,
        mode=DefinitionMode.INHERITED,
        source_hash=_text_hash(external.text.strip()),
    )


def _pick_scoped(
    scoped_defs: list[Any], scope: str
) -> dict[str, Any] | None:
    matches: list[dict[str, Any]] = []
    for sd in scoped_defs:
        if not isinstance(sd, dict):
            continue
        if str(sd.get("scope_ref") or "") == scope:
            matches.append(sd)
    if not matches:
        return None
    # Most specific: prefer replaces > narrows > refines > alternative; then last wins.
    rank = {"replaces": 3, "narrows": 2, "refines": 1, "alternative": 0}
    matches.sort(
        key=lambda m: rank.get(str(m.get("relation_to_reference") or ""), 0)
    )
    return matches[-1]


def resolve_definition(
    element: dict[str, Any],
    index: DefinitionIndex,
    *,
    scope: str | None = None,
    level: str | None = None,
    language: str | None = "ru",
    _stack: tuple[str, ...] = (),
) -> DefinitionProvenance:
    """Resolve the effective definition for a model element.

    See ADR-025 resolution order: scoped → own → definition_source_ref →
    single conceptual_entity_refs → unresolved.
    """
    eid = str(element.get("element_id") or element.get("name") or "")
    level = level or "ModelElement"
    if eid and eid in _stack:
        return DefinitionProvenance(
            text=None,
            language=None,
            source_element_id=eid,
            level=level,
            mode=DefinitionMode.UNRESOLVED,
            diagnostic=f"Cycle in definition resolution at {eid!r}.",
        )
    stack = _stack + ((eid,) if eid else ())

    # 1. Scoped
    if scope is not None:
        scoped_list = element.get("scoped_definitions") or []
        if isinstance(scoped_list, list):
            picked = _pick_scoped(scoped_list, scope)
            if picked is not None and _nonempty(picked.get("text")):
                text = str(picked["text"]).strip()
                return DefinitionProvenance(
                    text=text,
                    language=language,
                    source_element_id=str(
                        picked.get("scoped_definition_id") or eid
                    ),
                    level=level,
                    mode=DefinitionMode.SCOPED,
                    scope=scope,
                    source_hash=_text_hash(text),
                )

    # Alignment may forbid inheritance
    alignment = str(element.get("conceptual_alignment_status") or "")
    own_required = alignment in _OWN_REQUIRED_ALIGNMENT

    description = element.get("description")
    source_ref = element.get("definition_source_ref")
    has_description = _nonempty(description)
    has_source = _nonempty(source_ref)

    # 2. Own (optionally adapted)
    if has_description:
        text = str(description).strip()
        mode = (
            DefinitionMode.OWN_ADAPTED if has_source else DefinitionMode.OWN
        )
        return DefinitionProvenance(
            text=text,
            language=language,
            source_element_id=eid or None,
            level=level,
            mode=mode,
            source_hash=_text_hash(text),
        )

    if own_required:
        return DefinitionProvenance(
            text=None,
            language=None,
            source_element_id=eid or None,
            level=level,
            mode=DefinitionMode.UNRESOLVED,
            diagnostic=(
                f"Alignment status {alignment!r} requires an own description "
                "(inheritance not allowed)."
            ),
        )

    # 3. Explicit definition_source_ref
    if has_source:
        # Ontology / external: require exact. Internal model elements: always ok.
        require_exact = index.get(str(source_ref)) is None
        return _resolve_ref(
            str(source_ref),
            index,
            stack=stack,
            require_exact_external=require_exact,
        )

    # 4. Implicit: single conceptual_entity_refs (LogicalEntity)
    if level == "LogicalEntity":
        refs = element.get("conceptual_entity_refs") or []
        if isinstance(refs, list):
            refs = [str(r) for r in refs if r]
        else:
            refs = []
        if len(refs) > 1:
            return DefinitionProvenance(
                text=None,
                language=None,
                source_element_id=eid or None,
                level=level,
                mode=DefinitionMode.UNRESOLVED,
                diagnostic=(
                    "Multiple conceptual_entity_refs without own description "
                    "or definition_source_ref (ambiguous)."
                ),
            )
        if len(refs) == 1:
            return _resolve_ref(
                refs[0],
                index,
                stack=stack,
                require_exact_external=False,
            )

    # 5. Unresolved
    return DefinitionProvenance(
        text=None,
        language=None,
        source_element_id=eid or None,
        level=level,
        mode=DefinitionMode.UNRESOLVED,
        diagnostic="No description, definition_source_ref, or inheritable concept.",
    )


def resolve_package_definitions(
    body_data: dict[str, Any],
    index: DefinitionIndex | None = None,
    *,
    scope: str | None = None,
) -> dict[str, DefinitionProvenance]:
    """Resolve definitions for all indexed elements of ``body_data``.

    If ``index`` is None, builds a single-package index from ``body_data``.
    """
    idx = index or build_definition_index(body_data)
    if index is None:
        # Ensure current package is present even if caller passed empty index.
        pass
    else:
        # Elements of this package should already be in index; re-add is idempotent.
        idx.add_package(body_data)

    out: dict[str, DefinitionProvenance] = {}
    for eid, indexed in list(idx.elements.items()):
        # Only resolve elements that belong to this package body when filtering
        # is desired; for multi-package index resolve all.
        out[eid] = resolve_definition(
            indexed.data,
            idx,
            scope=scope,
            level=indexed.level,
        )
    return out


def find_redundant_definition_overrides(
    body_data: dict[str, Any],
    index: DefinitionIndex | None = None,
) -> list[tuple[str, str]]:
    """Return (element_id, parent_id) where own description equals inherited text.

    Compares declared description to what would be inherited if description
    were absent (via definition_source_ref or single conceptual_entity_refs).
    """
    idx = index or build_definition_index(body_data)
    idx.add_package(body_data)
    findings: list[tuple[str, str]] = []

    for eid, indexed in idx.elements.items():
        el = indexed.data
        if not _nonempty(el.get("description")):
            continue
        # Build a shadow element without description to see inherited text.
        shadow = {k: v for k, v in el.items() if k != "description"}
        inherited = resolve_definition(
            shadow, idx, level=indexed.level
        )
        if inherited.mode != DefinitionMode.INHERITED:
            continue
        if not _nonempty(inherited.text):
            continue
        if str(el["description"]).strip() == inherited.text.strip():
            parent = inherited.source_element_id or "?"
            findings.append((eid, parent))
    return findings


@dataclass(frozen=True)
class MappingExternalProvider:
    """Provider backed by an in-memory map of ExternalDefinition."""

    definitions: dict[str, ExternalDefinition]

    def lookup(self, ref: str) -> ExternalDefinition | None:
        return self.definitions.get(ref)


def validate_scoped_definition_systems(
    element: dict[str, Any],
    *,
    solution_ref: str | None,
    index: DefinitionIndex,
) -> list[str]:
    """Return diagnostic messages for scoped_definitions with invalid scope_ref."""
    messages: list[str] = []
    scoped = element.get("scoped_definitions") or []
    if not isinstance(scoped, list):
        return messages
    allowed: frozenset[str] | None = None
    if solution_ref and solution_ref in index.solution_systems:
        allowed = index.solution_systems[solution_ref]
    for sd in scoped:
        if not isinstance(sd, dict):
            continue
        if str(sd.get("scope_kind") or "system") != "system":
            continue
        ref = str(sd.get("scope_ref") or "")
        if not ref:
            messages.append("scoped_definition missing scope_ref.")
            continue
        if allowed is not None and ref not in allowed:
            messages.append(
                f"scope_ref {ref!r} is not a member of solution "
                f"{solution_ref!r} systems."
            )
    return messages
