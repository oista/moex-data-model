"""SXI-* rule registry for solution-xlsx import."""

from __future__ import annotations

from moex_standard_linkml.solution_xlsx.diagnostics import (
    Diagnostic,
    Severity,
    apply_severity_overrides,
)
from moex_standard_linkml.solution_xlsx.ir import SolutionIR
from moex_standard_linkml.solution_xlsx.profile import SolutionXlsxProfile, SystemDefaults
from moex_standard_linkml.solution_xlsx.rules import attr_rules, fk_rules, obj_rules, src_rules


def run_rules(
    ir: SolutionIR,
    profile: SolutionXlsxProfile,
    system: SystemDefaults,
) -> list[Diagnostic]:
    """Mutate IR where needed (synthesize objects) and return all diagnostics."""
    diagnostics: list[Diagnostic] = list(ir.diagnostics)

    diagnostics.extend(src_rules.check_src_only(ir, profile))
    diagnostics.extend(obj_rules.ensure_objects(ir, profile))
    diagnostics.extend(attr_rules.check_attributes(ir, system))
    diagnostics.extend(fk_rules.check_foreign_keys(ir))
    diagnostics.extend(attr_rules.check_keys(ir))
    diagnostics.extend(
        [
            Diagnostic(
                code="SXI-PHY-001",
                severity=Severity.INFO,
                message_ru=(
                    f"Технология '{system.technology}' и system_ref "
                    f"'{system.system_ref}' взяты из профиля — подтвердите."
                ),
                remediation=(
                    "При необходимости измените systems[].technology / system_ref "
                    "в solution-xlsx.profile.yaml."
                ),
            )
        ]
    )

    diagnostics = apply_severity_overrides(diagnostics, profile.severity_overrides)
    ir.diagnostics = diagnostics
    return diagnostics


__all__ = ["run_rules"]
