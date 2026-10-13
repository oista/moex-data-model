"""Repository-scoped L2 invariants (INV-058 global element_id uniqueness)."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterator
from typing import Any

from moex_modeling import (
    ConformancePhase,
    Diagnostic,
    DiagnosticDetail,
    DiagnosticSeverity,
)

# Max package locations shown per colliding id in diagnostic messages.
_MAX_LOCATIONS = 5

HIERARCHY_VIEW_LEVEL = "hierarchy-view"


def iter_element_id_locations(
    obj: Any, path: str = ""
) -> Iterator[tuple[str, str]]:
    """Yield ``(element_id, json-ish path)`` for every object with a non-empty id.

    Shared walk used by INV-050 (single package) and INV-058 (repository).
    """
    if isinstance(obj, dict):
        eid = obj.get("element_id")
        if eid is not None and str(eid).strip():
            yield str(eid), path or "$"
        for key, value in obj.items():
            if key == "element_id":
                continue
            child = f"{path}/{key}" if path else key
            yield from iter_element_id_locations(value, child)
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            child = f"{path}[{index}]"
            yield from iter_element_id_locations(item, child)


def collect_element_ids(obj: Any) -> dict[str, list[str]]:
    """Map each ``element_id`` to the list of paths where it appears in ``obj``."""
    out: dict[str, list[str]] = defaultdict(list)
    for eid, loc in iter_element_id_locations(obj):
        out[eid].append(loc)
    return dict(out)


def _diag(
    *,
    code: str,
    invariant_id: str,
    message: str,
    subject: str | None,
    remediation: str | None = None,
) -> Diagnostic:
    details: list[DiagnosticDetail] = [
        DiagnosticDetail(detail_key="finding", detail_value=message),
        DiagnosticDetail(detail_key="invariant_id", detail_value=invariant_id),
    ]
    parts = [message]
    if remediation:
        parts.append(f"Remediation: {remediation}")
        details.append(
            DiagnosticDetail(detail_key="remediation", detail_value=remediation)
        )
    return Diagnostic(
        diagnostic_code=code,
        severity=DiagnosticSeverity.ERROR,
        diagnostic_message=" ".join(parts),
        conformance_phase=ConformancePhase.CORPORATE_SEMANTICS,
        subject_ref=subject,
        diagnostic_details=tuple(details),
    )


def check_repository_element_id_uniqueness(
    composite: dict[str, Any],
    *,
    package_ids: list[str] | None = None,
) -> list[Diagnostic]:
    """INV-058: ``element_id`` unique across source packages in a composite.

    ``composite`` matches :meth:`RepositoryLoader.assemble` shape::

        {repository_id, model_packages: [body, ...]}

    Optional ``package_ids[i]`` labels ``model_packages[i]`` in diagnostics
    (manifest document id). When omitted, each package body's ``element_id``
    or index is used.

    Callers that exclude derived hierarchy views must omit those packages from
    ``model_packages`` before calling (see loader ``check_global_element_ids``).
    """
    packages = composite.get("model_packages")
    if not isinstance(packages, list):
        return []

    # element_id -> list of (package_label, path)
    locations: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for index, body in enumerate(packages):
        if not isinstance(body, dict):
            continue
        if package_ids is not None and index < len(package_ids):
            label = package_ids[index]
        else:
            label = str(body.get("element_id") or f"model_packages[{index}]")
        for eid, path in iter_element_id_locations(body):
            locations[eid].append((label, path))

    out: list[Diagnostic] = []
    for eid in sorted(locations):
        hits = locations[eid]
        packages_hit = {label for label, _ in hits}
        if len(packages_hit) < 2:
            continue
        shown = hits[:_MAX_LOCATIONS]
        loc_text = "; ".join(f"{pkg}@{path}" for pkg, path in shown)
        if len(hits) > _MAX_LOCATIONS:
            loc_text += f" (+{len(hits) - _MAX_LOCATIONS} more)"
        out.append(
            _diag(
                code="DAMS-INV-058",
                invariant_id="INV-058",
                message=(
                    f"Duplicate element_id {eid!r} across "
                    f"{len(packages_hit)} source packages: {loc_text}."
                ),
                subject=eid,
                remediation=(
                    "Assign distinct element_id values in source packages, "
                    "or keep intentional copies only in hierarchy-view packages "
                    "(excluded from this check). INV-058."
                ),
            )
        )
    return out
