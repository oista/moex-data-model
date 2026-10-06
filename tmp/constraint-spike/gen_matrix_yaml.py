"""Generate constraint-matrix.yaml for PR-C1 (run once; commit the output)."""
from __future__ import annotations

import hashlib
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

ROOT = Path(__file__).resolve().parents[2]
OUT = (
    ROOT
    / "model-assets"
    / "specifications"
    / "moex-dams"
    / "0.1"
    / "constraints"
    / "constraint-matrix.yaml"
)

BASELINE_COMMIT = "5b57c326432745fc61a7d2bd7de5c1721912f3ea"

BASELINE = [
    ("moex-core.yaml", "ConceptualProperty", 0, "INV-001"),
    ("moex-datatypes.yaml", "DataType", 0, "INV-002"),
    ("moex-datatypes.yaml", "DataType", 1, "INV-003"),
    ("moex-datatypes.yaml", "DataType", 2, "INV-004"),
    ("moex-datatypes.yaml", "DataType", 3, "INV-005"),
    ("moex-datatypes.yaml", "ValueDomain", 0, "INV-006"),
    ("moex-datatypes.yaml", "ValueDomain", 1, "INV-007"),
    ("moex-datatypes.yaml", "ValueDomain", 2, "INV-008"),
    ("moex-semantic.yaml", "ConceptualDomain", 0, "INV-009"),
    ("moex-structure.yaml", "DataStructure", 0, "INV-010"),
    ("moex-structure.yaml", "DataStructure", 1, "INV-011"),
    ("moex-structure.yaml", "SchemaNode", 0, "INV-012"),
    ("moex-structure.yaml", "SchemaNode", 1, "INV-013"),
    ("moex-structure.yaml", "SchemaNode", 2, "INV-014"),
    ("moex-technical.yaml", "DataCarrier", 0, "INV-015"),
    ("moex-technical.yaml", "AccessPoint", 0, "INV-016"),
    ("moex-technical.yaml", "AccessPoint", 1, "INV-017"),
]

# (id, title, statement, source, source_status, levels, req_refs, dams_validator, notes)
ROWS: list[tuple] = [
    (
        "INV-001",
        "ConceptualProperty identifying → is_identifying",
        "Если property_kind = identifying, то is_identifying должен быть задан как true.",
        "ADR-034:58; slot is_identifying",
        "aligned",
        ["L2", "L3"],
        [],
        "moex_dams.rules.semantic_layer",
        "В схеме есть L1 rule, но equals_string на boolean дефектен в JSON Schema (см. linkml-rules-support §3.1); целевые уровни L2+L3.",
    ),
    (
        "INV-002",
        "DataType.precision только для decimal",
        "Слот precision допустим только при type_family = decimal.",
        "slot precision; ADR-036",
        "aligned",
        ["L1", "L3"],
        [],
        "moex_dams.rules.semantic_layer",
        None,
    ),
    (
        "INV-003",
        "DataType.scale только для decimal",
        "Слот scale допустим только при type_family = decimal.",
        "slot scale",
        "partial",
        ["L1", "L3"],
        [],
        "moex_dams.rules.semantic_layer",
        None,
    ),
    (
        "INV-004",
        "DataType.max_length только для string/binary",
        "Слот max_length допустим только при type_family string или binary.",
        "slot max_length",
        "partial",
        ["L1", "L3"],
        [],
        "moex_dams.rules.semantic_layer",
        None,
    ),
    (
        "INV-005",
        "DataType.min_length только для string/binary",
        "Слот min_length допустим только при type_family string или binary.",
        "slot min_length",
        "partial",
        ["L1", "L3"],
        [],
        "moex_dams.rules.semantic_layer",
        None,
    ),
    (
        "INV-006",
        "ValueDomain enumerated → permissible_values",
        "Для value_domain_kind = enumerated обязательны permissible_values.",
        "ADR-035:28; slot value_domain_kind",
        "aligned",
        ["L1", "L3"],
        [],
        "moex_dams.rules.semantic_layer",
        None,
    ),
    (
        "INV-007",
        "ValueDomain described без permissible_values",
        "Для value_domain_kind = described слот permissible_values отсутствует.",
        "ADR-035:28",
        "aligned",
        ["L1", "L3"],
        [],
        "moex_dams.rules.semantic_layer",
        None,
    ),
    (
        "INV-008",
        "ValueDomain reference_set без permissible_values",
        "Для value_domain_kind = reference_set слот permissible_values отсутствует.",
        "ADR-035:28",
        "aligned",
        ["L1", "L3"],
        [],
        "moex_dams.rules.semantic_layer",
        None,
    ),
    (
        "INV-009",
        "ConceptualDomain described без value_meanings",
        "Для conceptual_domain_kind = described слот value_meanings отсутствует.",
        "ADR-035",
        "aligned",
        ["L1", "L3"],
        [],
        "moex_dams.rules.semantic_layer",
        None,
    ),
    (
        "INV-010",
        "DataStructure source_pointer → source_artifact_ref",
        "Наличие source_pointer требует source_artifact_ref.",
        "slot source_pointer; ADR-038",
        "partial",
        ["L1", "L3"],
        [],
        None,
        None,
    ),
    (
        "INV-011",
        "DataStructure schema_dialect только JSON Schema family",
        "schema_dialect допустим только для schema_format json_schema или openapi_schema.",
        "ADR-038:44-51",
        "divergent",
        ["L1", "L3"],
        [],
        None,
        "ADR допускает AsyncAPI Multi Format Schema; правило уже уже.",
    ),
    (
        "INV-012",
        "SchemaNode array|map → item_node, без children",
        "Для node_kind array или map обязателен item_node и запрещены children.",
        "ADR-038:31; PDM-020",
        "aligned",
        ["L1", "L2", "L3"],
        ["DAMS-REQ-PDM-020.c1", "DAMS-REQ-PDM-020.c2"],
        "moex_dams.rules.data_structure",
        None,
    ),
    (
        "INV-013",
        "SchemaNode scalar|enum без children и item_node",
        "Для node_kind scalar или enum запрещены children и item_node.",
        "PDM-020",
        "aligned",
        ["L1", "L2", "L3"],
        ["DAMS-REQ-PDM-020.c3", "DAMS-REQ-PDM-020.c4"],
        "moex_dams.rules.data_structure",
        "L1 multi-ABSENT ослаблен в JSON Schema (linkml-rules-support §3.2).",
    ),
    (
        "INV-014",
        "SchemaNode reference → reference_target",
        "Для node_kind = reference обязателен reference_target.",
        "ADR-038:32; slot reference_target",
        "partial",
        ["L1", "L3"],
        [],
        None,
        None,
    ),
    (
        "INV-015",
        "DataCarrier in_memory без location_uri и region",
        "Для asset_kind = in_memory запрещены location_uri и region.",
        "PDM-012",
        "aligned",
        ["L1", "L2", "L3"],
        ["DAMS-REQ-PDM-012.c1"],
        "moex_dams.rules.technical_assets",
        "L1 multi-ABSENT ослаблен в JSON Schema (linkml-rules-support §3.2).",
    ),
    (
        "INV-016",
        "AccessPoint operation → interface_ref",
        "Для access_point_kind = operation обязателен interface_ref.",
        "PDM-011; slot interface_ref",
        "aligned",
        ["L1", "L2", "L3"],
        ["DAMS-REQ-PDM-011.c1"],
        "moex_dams.rules.technical_assets",
        None,
    ),
    (
        "INV-017",
        "AccessPoint interface без operation-полей",
        "Для access_point_kind = interface запрещены operation_name, http_method, path_template, message_refs.",
        "ADR-040:40-41; PDM-018",
        "partial",
        ["L1", "L2", "L3"],
        ["DAMS-REQ-PDM-018.c1"],
        "moex_dams.rules.data_structure",
        "ADR явно называет только message_refs; L1 multi-ABSENT ослаблен.",
    ),
    (
        "INV-018",
        "direction запрещён для DataContainer и ExecutionAsset",
        "Слот direction не задаётся у DataContainer и ExecutionAsset.",
        "moex-technical.yaml; PDM-008",
        "aligned",
        ["L1", "L2"],
        ["DAMS-REQ-PDM-008.c1"],
        "moex_dams.rules.technical_assets",
        "В description заявлено LinkML rules, в схеме правила нет.",
    ),
    (
        "INV-019",
        "message_refs только у operation/channel",
        "message_refs допустимы только у AccessPoint kind operation или channel.",
        "moex-structure.yaml; ADR-040:40-41; PDM-018",
        "aligned",
        ["L2"],
        ["DAMS-REQ-PDM-018.c1"],
        "moex_dams.rules.data_structure",
        "L1 частично покрыт INV-017 (только interface).",
    ),
    (
        "INV-020",
        "SchemaNode без циклов children/item_node",
        "Рёбра children и item_node не образуют циклов.",
        "ADR-038:32; PDM-014",
        "aligned",
        ["L2", "L3"],
        ["DAMS-REQ-PDM-014.c1"],
        "moex_dams.rules.data_structure",
        None,
    ),
    (
        "INV-021",
        "Реляционные признаки только при relational",
        "Реляционные признаки узла допустимы только при schema_format = relational.",
        "ADR-038:40-42; PDM-016",
        "aligned",
        ["L2"],
        ["DAMS-REQ-PDM-016.c1"],
        "moex_dams.rules.data_structure",
        None,
    ),
    (
        "INV-022",
        "local_key уникален в DataStructure",
        "local_key уникален внутри одной DataStructure.",
        "ADR-038; PDM-013",
        "aligned",
        ["L2"],
        ["DAMS-REQ-PDM-013.c1"],
        "moex_dams.rules.data_structure",
        None,
    ),
    (
        "INV-023",
        "dams_model_level согласован с профилем",
        "dams_model_level допустим только для профиля dams-data-model; согласован с implementation_scope.",
        "ADR-021:32; moex-core.yaml",
        "partial",
        ["L2"],
        [],
        "moex_dams.rules.dams_levels",
        "Проверить покрытие в PR-C3.",
    ),
    (
        "INV-024",
        "scope_ref system ∈ member_system_refs",
        "При scope_kind = system значение scope_ref входит в ITSolution.member_system_refs.",
        "moex-governance.yaml; ADR-025:112",
        "partial",
        ["L2"],
        [],
        None,
        "Реализация не подтверждена чтением кода (PR-C3).",
    ),
    (
        "INV-025",
        "tags только из реестра переходных тегов",
        "Значения tags принадлежат реестру переходных тегов (ADR-043).",
        "ADR-043:28,35",
        "aligned",
        ["L2"],
        [],
        None,
        "Residue-тест по ADR-043; подтвердить в PR-C3.",
    ),
    (
        "INV-026",
        "URI префикса оканчивается на / или #",
        "URI префикса онтологии оканчивается на '/' или '#'.",
        "ADR-030:40",
        "aligned",
        ["L2"],
        [],
        "moex_dams.rules.ontology_uris",
        None,
    ),
    (
        "INV-027",
        "Владелец пакета и классификация сущности",
        "У пакета задан data_owner_ref; у логической сущности есть эффективная классификация.",
        "ADR-023:73-74",
        "partial",
        ["L2"],
        [],
        None,
        "Каскад; проверить в PR-C3.",
    ),
]


def _seq(items):
    s = CommentedSeq(list(items))
    s.fa.set_flow_style()
    return s


def main() -> None:
    canon = "\n".join(f"{f}|{c}|{i}" for f, c, i, _ in BASELINE) + "\n"
    digest = hashlib.sha256(canon.encode("utf-8")).hexdigest()
    assert digest == "7c530bf111f5febf858f3f8e7d8a087d8cd20be7ebed1bdf4058f89ee915aa93"

    by_inv = {inv: (f, c, i) for f, c, i, inv in BASELINE}

    root = CommentedMap()
    root["matrix_id"] = "dams:constraint-matrix/0.1"
    root["title"] = "MOEX DAMS executable constraint matrix"
    root["description"] = (
        "Реестр инвариантов ADR-045. Тексты только здесь; схемы и документы ссылаются на INV-NNN."
    )

    baseline = CommentedMap()
    baseline["baseline_commit"] = BASELINE_COMMIT
    baseline["rules_sha256"] = digest
    rules = CommentedSeq()
    for f, c, i, inv in BASELINE:
        item = CommentedMap()
        item["schema_file"] = f
        item["class_name"] = c
        item["rule_index"] = i
        item["inv_id"] = inv
        rules.append(item)
    baseline["rules"] = rules
    root["baseline"] = baseline

    invs = CommentedSeq()
    for (
        iid,
        title,
        statement,
        source,
        source_status,
        levels,
        req_refs,
        dams_validator,
        notes,
    ) in ROWS:
        inv = CommentedMap()
        inv["id"] = iid
        inv["title"] = title
        inv["statement"] = statement
        inv["source"] = source
        inv["source_status"] = source_status
        inv["scope"] = "moex-dams"
        inv["levels"] = _seq(levels)
        inv["severity"] = "error"
        if iid in by_inv:
            inv["status"] = "implemented-untested"
        else:
            inv["status"] = "planned"
        if req_refs:
            inv["requirement_refs"] = _seq(req_refs)
        if notes:
            inv["notes"] = notes
        impl = CommentedMap()
        if iid in by_inv:
            f, c, i = by_inv[iid]
            lr = CommentedMap()
            lr["schema_file"] = f
            lr["class_name"] = c
            lr["rule_index"] = i
            impl["linkml_rule"] = lr
        if dams_validator:
            impl["dams_validator"] = dams_validator
        if impl:
            inv["implementation"] = impl
        invs.append(inv)
    root["invariants"] = invs

    y = YAML()
    y.default_flow_style = False
    y.width = 100
    y.indent(mapping=2, sequence=4, offset=2)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\n") as fh:
        y.dump(root, fh)
    print(f"wrote {OUT.relative_to(ROOT)} rules_sha256={digest}")


if __name__ == "__main__":
    main()
