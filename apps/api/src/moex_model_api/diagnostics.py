"""Map kernel Diagnostic → API DiagnosticRecord via wire shape."""

from __future__ import annotations

from moex_modeling import Diagnostic, diagnostic_to_wire

from moex_model_api.ports import DiagnosticRecord


def diagnostic_record(run_id: str, d: Diagnostic) -> DiagnosticRecord:
    wire = diagnostic_to_wire(d)
    return DiagnosticRecord(
        run_id=run_id,
        code=str(wire["code"]),
        severity=str(wire["severity"]),
        message=str(wire["message"]),
        path=wire.get("path"),
        element_id=wire.get("element_id"),
        source=wire.get("source"),
        line=wire.get("line"),
        suggestion=wire.get("suggestion"),
    )
