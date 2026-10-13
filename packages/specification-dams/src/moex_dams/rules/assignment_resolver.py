"""Governance assignment override layer (ADR-049 / Wave D4).

Preferred import path for assignment resolution. Implementation helpers remain
in ``cascade.py`` next to the containment cascade they extend (shared parent
map / element id helpers); this module is the documented assignment API surface
so callers do not need to depend on the cascade module for ADR-049 behaviour.

Physical relocation of ``_apply_assignments`` into this file is deferred: it
shares private helpers with ``cascade`` and a naive move creates an import
cycle. Wave D4 establishes the module boundary and ships the policy-replace
conflict rule + consumer wiring.
"""

from __future__ import annotations

from moex_dams.rules.cascade import (  # noqa: F401
    GovernanceFinding,
    diagnose_governance,
    resolve_governed,
)

__all__ = [
    "GovernanceFinding",
    "diagnose_governance",
    "resolve_governed",
]
