"""Attribute / key SXI-ATTR-* and SXI-KEY-* rules."""

from __future__ import annotations

from collections import defaultdict

from moex_standard_linkml.solution_xlsx.diagnostics import Diagnostic, Severity
from moex_standard_linkml.solution_xlsx.ir import SolutionIR
from moex_standard_linkml.solution_xlsx.normalize import match_key
from moex_standard_linkml.solution_xlsx.profile import SystemDefaults


def check_attributes(ir: SolutionIR, system: SystemDefaults) -> list[Diagnostic]:
    out: list[Diagnostic] = []
    seen: dict[tuple[str, str], int] = {}

    for attr in ir.attributes:
        ok = match_key(attr.object_code)
        ak = match_key(attr.attribute_code)
        if ok is None or ak is None:
            continue

        if attr.code_normalized:
            out.append(
                Diagnostic(
                    code="SXI-ATTR-001",
                    severity=Severity.WARNING,
                    message_ru=(
                        f"Код атрибута/объекта нормализован "
                        f"(пробелы/NBSP): '{attr.attribute_code}' "
                        f"на {attr.object_code}."
                    ),
                    remediation="Уберите лишние пробелы и NBSP в исходном xlsx.",
                    source_ref=attr.source_ref,
                )
            )

        key = (ok, ak)
        if key in seen:
            out.append(
                Diagnostic(
                    code="SXI-ATTR-002",
                    severity=Severity.ERROR,
                    message_ru=(
                        f"Дубликат атрибута {attr.object_code}."
                        f"{attr.attribute_code} (также строка {seen[key]})."
                    ),
                    remediation="Оставьте одну строку на атрибут.",
                    source_ref=attr.source_ref,
                )
            )
        else:
            seen[key] = attr.source_ref.row

        if not attr.data_type:
            out.append(
                Diagnostic(
                    code="SXI-ATTR-003",
                    severity=Severity.WARNING,
                    message_ru=(
                        f"Нет DataType у {attr.object_code}.{attr.attribute_code}; "
                        f"будет string."
                    ),
                    remediation="Укажите DataType в ObjectAttribute.",
                    source_ref=attr.source_ref,
                )
            )
        elif not attr.pk:
            raw_key = attr.data_type.strip().upper()
            base = raw_key.split("(", 1)[0].strip()
            known = set(system.type_map)
            if raw_key not in known and base not in known:
                out.append(
                    Diagnostic(
                        code="SXI-ATTR-004",
                        severity=Severity.WARNING,
                        message_ru=(
                            f"Тип '{attr.data_type}' нет в type_map "
                            f"системы {system.src_system}; принят string."
                        ),
                        remediation="Добавьте тип в systems[].type_map профиля.",
                        source_ref=attr.source_ref,
                    )
                )

        if not attr.src_attribute_code:
            out.append(
                Diagnostic(
                    code="SXI-ATTR-005",
                    severity=Severity.WARNING,
                    message_ru=(
                        f"Нет SrcAttributeCode у "
                        f"{attr.object_code}.{attr.attribute_code}; "
                        f"physical field не создаётся."
                    ),
                    remediation="Заполните SrcAttributeCode для mapping.",
                    source_ref=attr.source_ref,
                )
            )

    return out


def check_keys(ir: SolutionIR) -> list[Diagnostic]:
    out: list[Diagnostic] = []
    by_obj: dict[str, list] = defaultdict(list)
    for attr in ir.attributes:
        key = match_key(attr.object_code) or attr.object_code
        by_obj[key].append(attr)

    for key, attrs in by_obj.items():
        has_pk = any(a.pk for a in attrs)
        is_link = sum(1 for a in attrs if a.fk) >= 2 and len(attrs) <= 4
        if not has_pk and not is_link:
            sample = attrs[0]
            out.append(
                Diagnostic(
                    code="SXI-KEY-001",
                    severity=Severity.WARNING,
                    message_ru=(
                        f"У объекта '{sample.object_code}' нет PK и он не похож "
                        f"на связующую сущность."
                    ),
                    remediation="Отметьте PK в ObjectAttribute или уточните ключ в YAML.",
                    source_ref=sample.source_ref,
                )
            )
    return out
