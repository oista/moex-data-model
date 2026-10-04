"""Foreign-key SXI-FK-* rules."""

from __future__ import annotations

from moex_standard_linkml.solution_xlsx.diagnostics import Diagnostic, Severity
from moex_standard_linkml.solution_xlsx.ir import SolutionIR
from moex_standard_linkml.solution_xlsx.normalize import match_key


def parse_fk(fk: str) -> tuple[str, str] | None:
    text = fk.strip()
    if "." not in text:
        return None
    left, right = text.split(".", 1)
    left, right = left.strip(), right.strip()
    if not left or not right:
        return None
    return left, right


def check_foreign_keys(ir: SolutionIR) -> list[Diagnostic]:
    out: list[Diagnostic] = []
    attr_keys = ir.attribute_keys()
    obj_keys = set(ir.objects.keys())

    for attr in ir.attributes:
        if not attr.fk:
            continue
        parsed = parse_fk(attr.fk)
        if parsed is None:
            out.append(
                Diagnostic(
                    code="SXI-FK-001",
                    severity=Severity.ERROR,
                    message_ru=(
                        f"FK '{attr.fk}' у {attr.object_code}.{attr.attribute_code} "
                        f"не в формате Object.Attribute."
                    ),
                    remediation="Укажите FK как TargetObject.TargetAttribute.",
                    source_ref=attr.source_ref,
                )
            )
            continue

        target_obj, target_attr = parsed
        t_obj_key = match_key(target_obj)
        t_attr_key = match_key(target_attr)
        assert t_obj_key and t_attr_key

        if t_obj_key not in obj_keys:
            out.append(
                Diagnostic(
                    code="SXI-FK-002",
                    severity=Severity.ERROR,
                    message_ru=(
                        f"FK '{attr.fk}': целевой объект '{target_obj}' "
                        f"не найден в модели {ir.src_system}."
                    ),
                    remediation="Добавьте целевой объект или исправьте FK.",
                    source_ref=attr.source_ref,
                )
            )
            continue

        if (t_obj_key, t_attr_key) not in attr_keys:
            out.append(
                Diagnostic(
                    code="SXI-FK-003",
                    severity=Severity.ERROR,
                    message_ru=(
                        f"FK '{attr.fk}': целевой атрибут '{target_attr}' "
                        f"не найден на объекте '{target_obj}'."
                    ),
                    remediation="Добавьте целевой атрибут или исправьте FK.",
                    source_ref=attr.source_ref,
                )
            )

        # FK column itself must exist — it is the current attribute, so OK.
        # SXI-FK-004: if somehow attribute_code empty — already filtered.

    return out
