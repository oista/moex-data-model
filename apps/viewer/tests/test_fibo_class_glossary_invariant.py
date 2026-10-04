"""ADR-024: Classes tree and Glossary are two views of the same OWL class set."""

from __future__ import annotations

from pathlib import Path

from moex_publication_viewer.build import (
    compile_modules,
    enrich_fibo_explorer_classes,
)
from moex_publication_viewer.models.publication_models import PublicationItem
from moex_publication_viewer.publication_profiles import profile_spec
from moex_publication_viewer.validators import check_publication_profiles

REPO = Path(__file__).resolve().parents[3]
FIBO_PROFILE = "moex:module:fibo-profile"


def _class_ids(nodes: list[PublicationItem]) -> set[str]:
    ids: set[str] = set()
    for node in nodes:
        kind = (node.attributes or {}).get("kind") or "class"
        if kind == "class":
            ids.add(node.id)
        ids |= _class_ids(list(node.children or []))
    return ids


def test_fibo_classes_match_glossary_ids_and_have_iri() -> None:
    modules = compile_modules(REPO, enforce_publication_contract=False)
    enrich_fibo_explorer_classes(modules)
    profile = next(m for m in modules if m.module_id == FIBO_PROFILE)
    explorer = next(s for s in profile.sections if s.type == "explorer")
    glossary = next(s for s in profile.sections if s.id == "glossary")
    classes_root = next(i for i in explorer.items if i.id == "group:classes")

    class_ids = _class_ids(list(classes_root.children or []))
    glossary_ids = {i.id for i in glossary.items}
    assert class_ids
    assert class_ids == glossary_ids
    assert len(class_ids) == 50
    for item in glossary.items:
        assert (item.attributes or {}).get("iri"), item.id


def test_ontology_modules_have_no_missing_required_kinds() -> None:
    modules = compile_modules(REPO, enforce_publication_contract=False)
    enrich_fibo_explorer_classes(modules)
    ontology = [m for m in modules if m.profile == "ontology"]
    assert ontology
    spec = profile_spec("ontology")
    assert spec is not None
    warnings = check_publication_profiles(ontology)
    missing = [w for w in warnings if "missing required kinds" in w]
    assert missing == [], missing
