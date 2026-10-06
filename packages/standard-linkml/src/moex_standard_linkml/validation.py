"""Shared LinkML Validator factory (ADR-045 / PR-C1a).

``linkml.validator.Validator(schema)`` with default ``validation_plugins=None``
runs no plugins and never reports instance errors. Project scripts and
adapters must use this helper so validation matches ``linkml-validate``
(JsonschemaValidationPlugin, closed=True).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from linkml.validator import Validator
from linkml.validator.plugins import JsonschemaValidationPlugin


def make_linkml_validator(
    schema: str | Path,
    *,
    closed: bool = True,
) -> Validator:
    """Return a Validator that actually checks instances against the schema."""
    return Validator(
        str(schema),
        validation_plugins=[JsonschemaValidationPlugin(closed=closed)],
    )


def error_results(report: Any) -> list[Any]:
    """Filter report results to ERROR/FATAL severities."""
    out: list[Any] = []
    for item in getattr(report, "results", []) or []:
        sev = str(getattr(item, "severity", item)).upper()
        if "ERROR" in sev or "FATAL" in sev:
            out.append(item)
    return out
