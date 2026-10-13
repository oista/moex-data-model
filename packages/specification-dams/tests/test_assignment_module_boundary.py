"""R2-9: ADR-049 assignment logic lives in assignment_resolver, not cascade."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

RULES = Path(__file__).resolve().parents[1] / "src" / "moex_dams" / "rules"
CASCADE = RULES / "cascade.py"
ASSIGNMENT = RULES / "assignment_resolver.py"

# Symbols that must be defined in assignment_resolver (not re-exported stubs).
_ASSIGNMENT_DEFS = frozenset(
    {
        "GovernanceFinding",
        "_apply_assignments",
        "_collect_assignments",
        "resolve_governed",
        "diagnose_governance",
    }
)

# cascade.py must not define these (ADR-023 containment only).
_FORBIDDEN_IN_CASCADE = frozenset(
    {
        "_apply_assignments",
        "_collect_assignments",
        "_ASSIGNMENT_COLLECTIONS",
        "diagnose_governance",
    }
)


def _top_level_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    names.add(t.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


def test_assignment_resolver_defines_assignment_api() -> None:
    names = _top_level_names(ASSIGNMENT)
    missing = sorted(_ASSIGNMENT_DEFS - names)
    assert not missing, f"assignment_resolver.py missing definitions: {missing}"


def test_cascade_does_not_define_assignment_impl() -> None:
    names = _top_level_names(CASCADE)
    present = sorted(_FORBIDDEN_IN_CASCADE & names)
    assert not present, f"cascade.py still defines assignment symbols: {present}"


def _module_level_import_names(path: Path) -> set[str]:
    """Names imported at module top level (not inside functions)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def test_no_import_cycle_assignment_then_cascade() -> None:
    """assignment_resolver may import cascade; cascade must not import it at load."""
    top_imports = _module_level_import_names(CASCADE)
    assert not any("assignment_resolver" in m for m in top_imports), (
        "cascade.py must not import assignment_resolver at module top "
        "(lazy import inside find_redundant_overrides is OK)"
    )
    import moex_dams.rules.assignment_resolver as ar
    import moex_dams.rules.cascade as cascade

    assert callable(ar.resolve_governed)
    assert callable(ar.diagnose_governance)
    assert callable(cascade.find_redundant_overrides)
    assert "resolve_governed" not in _top_level_names(CASCADE)


def test_resolve_governed_still_behaves_without_assignments() -> None:
    from moex_dams.rules.assignment_resolver import resolve_governed

    body = {
        "element_id": "dams:model/boundary/1",
        "name": "boundary",
        "description": "boundary",
        "lifecycle_status": "draft",
        "api_version": "dams.moex/v0.1",
        "model_version": "1.0.0",
        "implementation_scope": "solution",
        "solution_ref": "eam:solution/B",
        "data_owner_ref": "org:role/OWNER_A",
        "governance_classification": "internal",
        "logical_entities": [],
    }
    resolved = resolve_governed(body)
    assert resolved["dams:model/boundary/1"]["data_owner_ref"].layer == "inline"
    assert resolved["dams:model/boundary/1"]["data_owner_ref"].value == "org:role/OWNER_A"
