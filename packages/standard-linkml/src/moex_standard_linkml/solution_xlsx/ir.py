"""Intermediate representation for solution-xlsx import."""

from __future__ import annotations

from dataclasses import dataclass, field

from moex_standard_linkml.solution_xlsx.diagnostics import Diagnostic, SourceRef


@dataclass
class ObjectDef:
    src_system: str
    object_code: str  # canonical spelling
    object_name: str | None
    src_object_code: str | None
    src_object_name: str | None
    src_description: str | None
    source_ref: SourceRef
    synthesized: bool = False
    case_matched: bool = False  # ObjectAttribute spelling differed by case


@dataclass
class AttributeDef:
    src_system: str
    object_code: str
    attribute_code: str
    attribute_description: str | None
    data_type: str | None
    mandatory: bool
    pk: bool
    ak: bool
    fk: str | None
    src_object_code: str | None
    src_attribute_code: str | None
    src_attribute_description: str | None
    src_data_type: str | None
    comments: str | None
    base_src_scode: str | None
    base_src_sname: str | None
    base_src_object_code: str | None
    source_ref: SourceRef
    sort_order: int | None = None
    code_normalized: bool = False


@dataclass
class SrcOnlyRow:
    src_system: str
    src_object_code: str | None
    src_object_name: str | None
    src_attribute_code: str | None
    src_attribute_description: str | None
    src_data_type: str | None
    base_src_scode: str | None
    base_src_sname: str | None
    base_src_object_code: str | None
    source_ref: SourceRef


@dataclass
class SolutionIR:
    """One system's IR after filtering by SrcSystem."""

    src_system: str
    objects: dict[str, ObjectDef] = field(default_factory=dict)  # match_key → def
    attributes: list[AttributeDef] = field(default_factory=list)
    src_only: list[SrcOnlyRow] = field(default_factory=list)
    diagnostics: list[Diagnostic] = field(default_factory=list)
    ignored_sheets: list[str] = field(default_factory=list)
    source_filename: str = ""
    source_sha256: str = ""

    def object_by_code(self, code: str) -> ObjectDef | None:
        from moex_standard_linkml.solution_xlsx.normalize import match_key

        return self.objects.get(match_key(code) or "")

    def attribute_keys(self) -> set[tuple[str, str]]:
        from moex_standard_linkml.solution_xlsx.normalize import match_key

        keys: set[tuple[str, str]] = set()
        for attr in self.attributes:
            ok = match_key(attr.object_code)
            ak = match_key(attr.attribute_code)
            if ok and ak:
                keys.add((ok, ak))
        return keys
