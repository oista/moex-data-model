"""Source-level SXI-SRC-* rules."""

from __future__ import annotations

from collections import Counter

from moex_standard_linkml.solution_xlsx.diagnostics import Diagnostic, Severity
from moex_standard_linkml.solution_xlsx.ir import SolutionIR
from moex_standard_linkml.solution_xlsx.profile import SolutionXlsxProfile


def check_src_only(ir: SolutionIR, profile: SolutionXlsxProfile) -> list[Diagnostic]:
    out: list[Diagnostic] = []
    if not ir.src_only:
        return out
    by_sys = Counter(r.src_system for r in ir.src_only)
    detail = ", ".join(f"{k}={v}" for k, v in sorted(by_sys.items()))
    mode = profile.src_only
    out.append(
        Diagnostic(
            code="SXI-SRC-010",
            severity=Severity.INFO,
            message_ru=(
                f"Пропущено src-only строк (без ObjectCode+AttributeCode): "
                f"{len(ir.src_only)} ({detail}). Режим профиля src_only={mode}."
            ),
            remediation=(
                "Для режима B установите src_only: physical в профиле "
                "(roadmap). Сейчас строки только в отчёте."
            ),
            details={"counts": dict(by_sys), "src_only_mode": mode},
        )
    )
    return out
