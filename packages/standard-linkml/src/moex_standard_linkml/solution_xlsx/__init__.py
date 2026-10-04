"""Object/ObjectAttribute xlsx → DAMS solution ModelPackage (ADR-022)."""

from moex_standard_linkml.solution_xlsx.convert import ConvertResult, convert_solution
from moex_standard_linkml.solution_xlsx.diagnostics import Diagnostic, Severity, SourceRef
from moex_standard_linkml.solution_xlsx.profile import (
    SolutionXlsxProfile,
    load_solution_profile,
)

__all__ = [
    "ConvertResult",
    "Diagnostic",
    "Severity",
    "SolutionXlsxProfile",
    "SourceRef",
    "convert_solution",
    "load_solution_profile",
]
