"""Object-level SXI-OBJ-* rules."""

from __future__ import annotations

from moex_standard_linkml.solution_xlsx.diagnostics import Diagnostic, Severity, SourceRef
from moex_standard_linkml.solution_xlsx.ir import ObjectDef, SolutionIR
from moex_standard_linkml.solution_xlsx.normalize import match_key
from moex_standard_linkml.solution_xlsx.profile import SolutionXlsxProfile


def ensure_objects(ir: SolutionIR, profile: SolutionXlsxProfile) -> list[Diagnostic]:
    """Synthesize missing objects from attributes; emit OBJ-001."""
    del profile  # reserved for future profile-driven synthesis policy
    out: list[Diagnostic] = []
    titles: dict[str, str] = {}
    first_ref: dict[str, SourceRef] = {}
    for attr in ir.attributes:
        key = match_key(attr.object_code)
        if key is None:
            continue
        if key not in titles:
            # Prefer description-less title from attribute's object name later
            titles[key] = attr.object_code
            first_ref[key] = attr.source_ref
        if key not in ir.objects:
            pass

    for key, title in titles.items():
        if key in ir.objects:
            continue
        # Find a nicer name from any attribute row — ObjectName not on attr sheet
        # Use first attribute's object_code as name/title
        sample = next(a for a in ir.attributes if match_key(a.object_code) == key)
        # Prefer SrcObjectName if present for title
        display = sample.object_code
        ir.objects[key] = ObjectDef(
            src_system=ir.src_system,
            object_code=sample.object_code,
            object_name=display,
            src_object_code=sample.src_object_code,
            src_object_name=None,
            src_description=None,
            source_ref=first_ref[key],
            synthesized=True,
        )
        out.append(
            Diagnostic(
                code="SXI-OBJ-001",
                severity=Severity.WARNING,
                message_ru=(
                    f"ObjectCode '{sample.object_code}' есть в ObjectAttribute, "
                    f"но отсутствует на листе Object — синтезирован."
                ),
                remediation=(
                    "Добавьте объект на лист Object или подтвердите синтез."
                ),
                source_ref=first_ref[key],
            )
        )
    return out
