"""Wire DTO mapping for diagnostics (IMPLEMENTATION_PLAN JSON shape)."""

from __future__ import annotations

from typing import Any

from moex_modeling.conformance.domain import Diagnostic


def diagnostic_to_wire(d: Diagnostic) -> dict[str, Any]:
    """
    Map kernel Diagnostic to the stable wire shape used by CLI/API.

    Kernel field names stay unchanged; wire uses IMPLEMENTATION_PLAN keys.
    """
    loc = d.source_location
    suggestion: str | None = None
    for detail in d.diagnostic_details:
        if detail.detail_key == "suggestion" and detail.detail_value:
            suggestion = detail.detail_value
            break
    return {
        "code": d.diagnostic_code,
        "severity": d.severity.value,
        "message": d.diagnostic_message,
        "path": loc.json_pointer if loc else None,
        "element_id": d.subject_ref,
        "source": loc.source_uri if loc else None,
        "line": loc.line if loc else None,
        "suggestion": suggestion,
    }


__all__ = ["diagnostic_to_wire"]
