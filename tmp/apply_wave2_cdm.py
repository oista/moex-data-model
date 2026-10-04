"""Append commercial+HR wave-2 concepts/terms/relationships to enterprise CDM."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
PATH = (
    REPO
    / "model-assets"
    / "implementations"
    / "enterprise"
    / "moex-enterprise-conceptual-model"
    / "0.1"
    / "enterprise-conceptual-model.yaml"
)


def concept(**kw):
    base = {
        "lifecycle_status": "active",
        "genesis_kind": "native",
    }
    base.update(kw)
    return base


def term(name, title, desc, fwd, fwd_en, inv, inv_en, kind="association"):
    return {
        "element_id": f"dams:relterm/{name}",
        "name": name,
        "title": title,
        "description": desc,
        "lifecycle_status": "active",
        "forward_label": fwd,
        "forward_label_en": fwd_en,
        "inverse_label": inv,
        "inverse_label_en": inv_en,
        "symmetric": False,
        "default_relationship_kind": kind,
    }


def rel(
    eid_suffix,
    name,
    title,
    desc,
    src,
    tgt,
    srole,
    trole,
    term_ref,
    *,
    smin=0,
    smax=999,
    tmin=0,
    tmax=999,
    identifying=False,
    direction="forward",
    kind="association",
):
    r = {
        "element_id": f"dams:rel/{eid_suffix}",
        "name": name,
        "title": title,
        "description": desc,
        "lifecycle_status": "active",
        "source_entity_ref": src,
        "target_entity_ref": tgt,
        "source_role": srole,
        "target_role": trole,
        "source_min_cardinality": smin,
        "source_max_cardinality": smax,
        "target_min_cardinality": tmin,
        "target_max_cardinality": tmax,
        "relation_term_ref": term_ref,
        "term_direction": direction,
        "relationship_kind": kind,
    }
    if identifying:
        r["identifying"] = True
    return r


def dump_block(items: list[dict]) -> str:
    """Dump list items as YAML block with 2-space indent under parent list."""
    raw = yaml.dump(
        items,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=100,
    )
    # yaml.dump of a list starts with "- "; indent each line by 2 for nesting under key
    lines = []
    for line in raw.splitlines():
        if line.strip() == "":
            lines.append("")
        else:
            lines.append("  " + line)
    return "\n".join(lines) + "\n"


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    data = yaml.safe_load(text)

    new_concepts = [
        concept(
            element_id="dams:concept/Counterparty",
            name="Counterparty",
            title="Контрагент",
            description=(
                "Роль LegalEntity как контрагента по договорам и платежам. "
                "Reified role, не подкласс LegalEntity."
            ),
            entity_type="core",
            data_class="master_data",
            business_importance="high",
            entity_tier="dependent",
            dependency_kind="characteristic",
            depends_on_refs=["dams:concept/LegalEntity"],
        ),
        concept(
            element_id="dams:concept/Product",
            name="Product",
            title="Продукт",
            description="Коммерческий продукт биржи / группы, связанный с услугой и тарифом.",
            entity_type="core",
            data_class="reference_data",
            business_importance="high",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/Service",
            name="Service",
            title="Услуга",
            description="Услуга, оказываемая в рамках коммерческого каталога.",
            entity_type="reference",
            data_class="reference_data",
            business_importance="high",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/Tariff",
            name="Tariff",
            title="Тариф",
            description="Тариф / прайс для продукта или услуги.",
            entity_type="reference",
            data_class="reference_data",
            business_importance="medium",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/Payment",
            name="Payment",
            title="Платёж",
            description="Платёж по продукту с участием клиента и/или контрагента.",
            entity_type="core",
            data_class="transactional_data",
            business_importance="high",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/Sale",
            name="Sale",
            title="Продажа",
            description="Факт продажи продукта клиенту.",
            entity_type="core",
            data_class="transactional_data",
            business_importance="high",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/CostCenter",
            name="CostCenter",
            title="ЦФО",
            description="Центр финансовой ответственности.",
            entity_type="reference",
            data_class="reference_data",
            business_importance="medium",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/Income",
            name="Income",
            title="Доход",
            description="Доходная статья / факт дохода по ЦФО и группе компаний.",
            entity_type="core",
            data_class="transactional_data",
            business_importance="medium",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/Expense",
            name="Expense",
            title="Расход",
            description="Расходная статья / факт расхода по ЦФО и группе компаний.",
            entity_type="core",
            data_class="transactional_data",
            business_importance="medium",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/Budget",
            name="Budget",
            title="Бюджет",
            description="Бюджет, связанный с проектом.",
            entity_type="core",
            data_class="transactional_data",
            business_importance="medium",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/Project",
            name="Project",
            title="Проект",
            description="Проект / инициатива (управление работами и бюджетом).",
            entity_type="core",
            data_class="master_data",
            business_importance="medium",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/Task",
            name="Task",
            title="Задача",
            description="Задача проекта.",
            entity_type="core",
            data_class="transactional_data",
            business_importance="medium",
            entity_tier="dependent",
            dependency_kind="characteristic",
            depends_on_refs=["dams:concept/Project"],
        ),
        concept(
            element_id="dams:concept/TimeEntry",
            name="TimeEntry",
            title="Трудозатрата",
            description="Учёт трудозатрат сотрудника по задаче (associative).",
            entity_type="core",
            data_class="transactional_data",
            business_importance="medium",
            entity_tier="dependent",
            dependency_kind="associative",
            depends_on_refs=["dams:concept/Task", "dams:concept/Employee"],
        ),
        concept(
            element_id="dams:concept/Rating",
            name="Rating",
            title="Рейтинг",
            description="Рейтинг юридического лица.",
            entity_type="core",
            data_class="reference_data",
            business_importance="medium",
            entity_tier="dependent",
            dependency_kind="characteristic",
            depends_on_refs=["dams:concept/LegalEntity"],
        ),
        concept(
            element_id="dams:concept/FinancialReport",
            name="FinancialReport",
            title="Финансовая отчётность",
            description="Финансовая отчётность юридического лица.",
            entity_type="core",
            data_class="transactional_data",
            business_importance="medium",
            entity_tier="dependent",
            dependency_kind="characteristic",
            depends_on_refs=["dams:concept/LegalEntity"],
        ),
        concept(
            element_id="dams:concept/ContractAmendment",
            name="ContractAmendment",
            title="Дополнительное соглашение",
            description=(
                "Доп. соглашение к договору (Agreement); может быть связано с сотрудником."
            ),
            entity_type="core",
            data_class="transactional_data",
            business_importance="high",
            entity_tier="dependent",
            dependency_kind="characteristic",
            depends_on_refs=["dams:concept/Agreement"],
        ),
        concept(
            element_id="dams:concept/MarketingCampaign",
            name="MarketingCampaign",
            title="Маркетинговая кампания",
            description="Маркетинговая кампания.",
            entity_type="core",
            data_class="transactional_data",
            business_importance="medium",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/CampaignMembership",
            name="CampaignMembership",
            title="Участие в кампании",
            description=(
                "Ассоциация маркетинговой кампании и пользователя "
                "(Состав компаний в drawio)."
            ),
            entity_type="core",
            data_class="transactional_data",
            business_importance="low",
            entity_tier="dependent",
            dependency_kind="associative",
            depends_on_refs=["dams:concept/MarketingCampaign", "dams:concept/User"],
        ),
        concept(
            element_id="dams:concept/Department",
            name="Department",
            title="Департамент",
            description=(
                "Организационное подразделение; может относиться к группе компаний."
            ),
            entity_type="core",
            data_class="master_data",
            business_importance="high",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/StaffPosition",
            name="StaffPosition",
            title="Штатная единица",
            description="Позиция штатного расписания в департаменте.",
            entity_type="core",
            data_class="master_data",
            business_importance="high",
            entity_tier="dependent",
            dependency_kind="characteristic",
            depends_on_refs=["dams:concept/Department"],
        ),
        concept(
            element_id="dams:concept/Employee",
            name="Employee",
            title="Сотрудник",
            description=(
                "Роль Person как сотрудника (reified). Не подкласс Person. "
                "Связан со штатной единицей."
            ),
            entity_type="core",
            data_class="master_data",
            business_importance="high",
            entity_tier="dependent",
            dependency_kind="characteristic",
            depends_on_refs=["dams:concept/Person"],
        ),
        concept(
            element_id="dams:concept/EmploymentContract",
            name="EmploymentContract",
            title="Трудовой договор",
            description=(
                "Трудовой договор сотрудника. Специализация Agreement (parent_concept_ref)."
            ),
            entity_type="core",
            data_class="transactional_data",
            business_importance="high",
            parent_concept_ref="dams:concept/Agreement",
            entity_tier="dependent",
            dependency_kind="characteristic",
            depends_on_refs=["dams:concept/Employee"],
        ),
        concept(
            element_id="dams:concept/Role",
            name="Role",
            title="Роль",
            description=(
                "Роль доступа / полномочия в прикладных системах "
                "(без привязки к инфо-системе в этой волне)."
            ),
            entity_type="reference",
            data_class="reference_data",
            business_importance="medium",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/User",
            name="User",
            title="Пользователь",
            description=(
                "Учётная запись пользователя приложений (IAM). "
                "Связь с инфо-системами отложена."
            ),
            entity_type="core",
            data_class="master_data",
            business_importance="medium",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/RoleAssignment",
            name="RoleAssignment",
            title="Назначение роли",
            description="Ассоциация роли и пользователя (Состав ролей).",
            entity_type="core",
            data_class="master_data",
            business_importance="medium",
            entity_tier="dependent",
            dependency_kind="associative",
            depends_on_refs=["dams:concept/Role", "dams:concept/User"],
        ),
    ]

    existing_names = {c["name"] for c in data["conceptual_entities"]}
    for c in new_concepts:
        if c["name"] in existing_names:
            raise SystemExit(f"duplicate concept {c['name']}")

    new_terms = [
        term(
            "hasCounterpartyRole",
            "имеет роль контрагента / принадлежит",
            "Организация имеет роль контрагента.",
            "имеет роль контрагента",
            "has counterparty role",
            "принадлежит",
            "belongs to",
            "composition",
        ),
        term(
            "amends",
            "дополняет / дополняется",
            "Доп. соглашение дополняет договор.",
            "дополняет",
            "amends",
            "дополняется",
            "amended by",
        ),
        term(
            "hasEmployeeRole",
            "имеет роль сотрудника / принадлежит",
            "Физическое лицо имеет роль сотрудника.",
            "имеет роль сотрудника",
            "has employee role",
            "принадлежит",
            "belongs to",
            "composition",
        ),
        term(
            "holdsStaffPosition",
            "занимает должность / занята",
            "Сотрудник занимает штатную единицу.",
            "занимает должность",
            "holds staff position",
            "занята",
            "filled by",
        ),
        term(
            "ofDepartment",
            "относится к департаменту / включает",
            "Штатная единица относится к департаменту.",
            "относится к департаменту",
            "of department",
            "включает",
            "includes position",
            "composition",
        ),
        term(
            "soldTo",
            "продано / купил",
            "Продажа клиенту.",
            "продано",
            "sold to",
            "купил",
            "bought",
        ),
        term(
            "paidBy",
            "оплачен / оплачивает",
            "Платёж от клиента или контрагента.",
            "оплачен",
            "paid by",
            "оплачивает",
            "pays",
        ),
        term(
            "forProduct",
            "за продукт / имеет платежи",
            "Платёж или продажа по продукту.",
            "за продукт",
            "for product",
            "имеет платежи/продажи",
            "has payments or sales",
        ),
        term(
            "ofService",
            "предоставляет услугу / входит в",
            "Продукт связан с услугой.",
            "предоставляет услугу",
            "offers service",
            "входит в продукт",
            "part of product",
        ),
        term(
            "pricedBy",
            "тарифицируется / тарифицирует",
            "Продукт связан с тарифом.",
            "тарифицируется",
            "priced by",
            "тарифицирует",
            "prices",
        ),
        term(
            "rates",
            "оценивает / имеет рейтинг",
            "Рейтинг юридического лица.",
            "оценивает",
            "rates",
            "имеет рейтинг",
            "has rating",
        ),
        term(
            "reportsOn",
            "отчитывается по / имеет отчётность",
            "Финансовая отчётность юрлица.",
            "отчитывается по",
            "reports on",
            "имеет отчётность",
            "has financial report",
        ),
        term(
            "ofCostCenter",
            "относится к ЦФО / учитывает",
            "Доход/расход относится к ЦФО.",
            "относится к ЦФО",
            "of cost center",
            "учитывает",
            "records",
        ),
        term(
            "budgets",
            "бюджетирует / имеет бюджет",
            "Бюджет проекта.",
            "бюджетирует",
            "budgets",
            "имеет бюджет",
            "has budget",
        ),
        term(
            "ofProject",
            "относится к проекту / включает",
            "Задача или бюджет относится к проекту.",
            "относится к проекту",
            "of project",
            "включает",
            "includes",
        ),
        term(
            "loggedAgainst",
            "учтено по / имеет трудозатраты",
            "Трудозатрата по задаче / сотруднику.",
            "учтено по",
            "logged against",
            "имеет трудозатраты",
            "has time entries",
        ),
        term(
            "assignedRole",
            "назначена роль / назначена",
            "Назначение роли пользователю.",
            "назначена роль",
            "has assigned role",
            "назначена",
            "assigned to",
        ),
        term(
            "inCampaign",
            "в кампании / включает участника",
            "Участие пользователя в маркетинговой кампании.",
            "в кампании",
            "in campaign",
            "включает участника",
            "has member",
        ),
        term(
            "partyTo",
            "сторона / имеет сторону",
            "Договор со стороной-контрагентом или группой.",
            "сторона",
            "party to",
            "имеет сторону",
            "has as party",
        ),
        term(
            "signedBy",
            "подписано / подписывает",
            "Доп. соглашение связано с сотрудником.",
            "подписано",
            "signed by",
            "подписывает",
            "signs",
        ),
    ]

    existing_terms = {t["name"] for t in data["relation_terms"]}
    for t in new_terms:
        if t["name"] in existing_terms:
            raise SystemExit(f"duplicate term {t['name']}")

    ce = "dams:concept/"
    rt = "dams:relterm/"
    new_rels = [
        rel(
            "Counterparty/ofLegalEntity",
            "ofLegalEntity",
            "belongsTo / hasCounterpartyRole",
            "Counterparty принадлежит LegalEntity (mandatory owner).",
            ce + "Counterparty",
            ce + "LegalEntity",
            "counterparty",
            "legal_entity",
            rt + "hasCounterpartyRole",
            smin=1,
            smax=1,
            identifying=True,
            direction="inverse",
            kind="composition",
        ),
        rel(
            "Agreement/withCounterparty",
            "withCounterparty",
            "partyTo (counterparty)",
            "Договор со стороной-контрагентом.",
            ce + "Agreement",
            ce + "Counterparty",
            "agreement",
            "counterparty",
            rt + "partyTo",
            smin=0,
            smax=999,
        ),
        rel(
            "Agreement/withCorporateGroup",
            "withCorporateGroup",
            "partyTo (group)",
            "Договор с компанией группы.",
            ce + "Agreement",
            ce + "CorporateGroup",
            "agreement",
            "group",
            rt + "partyTo",
            smin=0,
            smax=1,
        ),
        rel(
            "ContractAmendment/ofAgreement",
            "ofAgreement",
            "amends",
            "Доп. соглашение дополняет Agreement (mandatory owner).",
            ce + "ContractAmendment",
            ce + "Agreement",
            "amendment",
            "agreement",
            rt + "amends",
            smin=1,
            smax=1,
            identifying=True,
        ),
        rel(
            "ContractAmendment/signedBy",
            "signedBy",
            "signedBy",
            "Доп. соглашение может быть связано с сотрудником.",
            ce + "ContractAmendment",
            ce + "Employee",
            "amendment",
            "employee",
            rt + "signedBy",
            smin=0,
            smax=1,
        ),
        rel(
            "Product/ofService",
            "ofService",
            "ofService",
            "Продукт связан с услугой.",
            ce + "Product",
            ce + "Service",
            "product",
            "service",
            rt + "ofService",
            smin=0,
            smax=1,
        ),
        rel(
            "Product/pricedBy",
            "pricedBy",
            "pricedBy",
            "Продукт связан с тарифом.",
            ce + "Product",
            ce + "Tariff",
            "product",
            "tariff",
            rt + "pricedBy",
            smin=0,
            smax=1,
        ),
        rel(
            "Payment/paidByClient",
            "paidByClient",
            "paidBy (client)",
            "Платёж от клиента.",
            ce + "Payment",
            ce + "Client",
            "payment",
            "client",
            rt + "paidBy",
            smin=0,
            smax=1,
        ),
        rel(
            "Payment/paidByCounterparty",
            "paidByCounterparty",
            "paidBy (counterparty)",
            "Платёж с участием контрагента.",
            ce + "Payment",
            ce + "Counterparty",
            "payment",
            "counterparty",
            rt + "paidBy",
            smin=0,
            smax=1,
        ),
        rel(
            "Payment/forProduct",
            "forProduct",
            "forProduct",
            "Платёж по продукту.",
            ce + "Payment",
            ce + "Product",
            "payment",
            "product",
            rt + "forProduct",
            smin=0,
            smax=1,
        ),
        rel(
            "Sale/soldTo",
            "soldTo",
            "soldTo",
            "Продажа клиенту.",
            ce + "Sale",
            ce + "Client",
            "sale",
            "client",
            rt + "soldTo",
            smin=1,
            smax=1,
        ),
        rel(
            "Sale/forProduct",
            "forProduct",
            "forProduct",
            "Продажа продукта.",
            ce + "Sale",
            ce + "Product",
            "sale",
            "product",
            rt + "forProduct",
            smin=1,
            smax=1,
        ),
        rel(
            "Rating/ofLegalEntity",
            "ofLegalEntity",
            "rates",
            "Рейтинг принадлежит LegalEntity (mandatory).",
            ce + "Rating",
            ce + "LegalEntity",
            "rating",
            "legal_entity",
            rt + "rates",
            smin=1,
            smax=1,
            identifying=True,
        ),
        rel(
            "FinancialReport/ofLegalEntity",
            "ofLegalEntity",
            "reportsOn",
            "Отчётность принадлежит LegalEntity (mandatory).",
            ce + "FinancialReport",
            ce + "LegalEntity",
            "report",
            "legal_entity",
            rt + "reportsOn",
            smin=1,
            smax=1,
            identifying=True,
        ),
        rel(
            "Income/ofCostCenter",
            "ofCostCenter",
            "ofCostCenter",
            "Доход относится к ЦФО.",
            ce + "Income",
            ce + "CostCenter",
            "income",
            "cost_center",
            rt + "ofCostCenter",
            smin=0,
            smax=1,
        ),
        rel(
            "Income/ofCorporateGroup",
            "ofCorporateGroup",
            "memberOf (group)",
            "Доход относится к группе компаний.",
            ce + "Income",
            ce + "CorporateGroup",
            "income",
            "group",
            rt + "memberOf",
            smin=0,
            smax=1,
        ),
        rel(
            "Expense/ofCostCenter",
            "ofCostCenter",
            "ofCostCenter",
            "Расход относится к ЦФО.",
            ce + "Expense",
            ce + "CostCenter",
            "expense",
            "cost_center",
            rt + "ofCostCenter",
            smin=0,
            smax=1,
        ),
        rel(
            "Expense/ofCorporateGroup",
            "ofCorporateGroup",
            "memberOf (group)",
            "Расход относится к группе компаний.",
            ce + "Expense",
            ce + "CorporateGroup",
            "expense",
            "group",
            rt + "memberOf",
            smin=0,
            smax=1,
        ),
        rel(
            "Budget/ofProject",
            "ofProject",
            "budgets",
            "Бюджет относится к проекту.",
            ce + "Budget",
            ce + "Project",
            "budget",
            "project",
            rt + "budgets",
            smin=0,
            smax=1,
        ),
        rel(
            "Task/ofProject",
            "ofProject",
            "ofProject",
            "Задача принадлежит проекту (mandatory owner).",
            ce + "Task",
            ce + "Project",
            "task",
            "project",
            rt + "ofProject",
            smin=1,
            smax=1,
            identifying=True,
            kind="composition",
        ),
        rel(
            "TimeEntry/ofTask",
            "ofTask",
            "loggedAgainst (task)",
            "Трудозатрата по задаче (mandatory).",
            ce + "TimeEntry",
            ce + "Task",
            "time_entry",
            "task",
            rt + "loggedAgainst",
            smin=1,
            smax=1,
            identifying=True,
        ),
        rel(
            "TimeEntry/ofEmployee",
            "ofEmployee",
            "loggedAgainst (employee)",
            "Трудозатрата сотрудника (mandatory).",
            ce + "TimeEntry",
            ce + "Employee",
            "time_entry",
            "employee",
            rt + "loggedAgainst",
            smin=1,
            smax=1,
            identifying=True,
        ),
        rel(
            "CampaignMembership/ofCampaign",
            "ofCampaign",
            "inCampaign",
            "Членство в кампании (mandatory).",
            ce + "CampaignMembership",
            ce + "MarketingCampaign",
            "membership",
            "campaign",
            rt + "inCampaign",
            smin=1,
            smax=1,
            identifying=True,
        ),
        rel(
            "CampaignMembership/ofUser",
            "ofUser",
            "inCampaign (user)",
            "Участник кампании — пользователь (mandatory).",
            ce + "CampaignMembership",
            ce + "User",
            "membership",
            "user",
            rt + "inCampaign",
            smin=1,
            smax=1,
            identifying=True,
        ),
        rel(
            "Department/ofCorporateGroup",
            "ofCorporateGroup",
            "memberOf",
            "Департамент может относиться к группе компаний.",
            ce + "Department",
            ce + "CorporateGroup",
            "department",
            "group",
            rt + "memberOf",
            smin=0,
            smax=1,
        ),
        rel(
            "StaffPosition/ofDepartment",
            "ofDepartment",
            "ofDepartment",
            "Штатная единица принадлежит департаменту (mandatory).",
            ce + "StaffPosition",
            ce + "Department",
            "position",
            "department",
            rt + "ofDepartment",
            smin=1,
            smax=1,
            identifying=True,
            kind="composition",
        ),
        rel(
            "Employee/ofPerson",
            "ofPerson",
            "belongsTo / hasEmployeeRole",
            "Сотрудник принадлежит Person (mandatory owner).",
            ce + "Employee",
            ce + "Person",
            "employee",
            "person",
            rt + "hasEmployeeRole",
            smin=1,
            smax=1,
            identifying=True,
            direction="inverse",
            kind="composition",
        ),
        rel(
            "Employee/holdsStaffPosition",
            "holdsStaffPosition",
            "holdsStaffPosition",
            "Сотрудник занимает штатную единицу.",
            ce + "Employee",
            ce + "StaffPosition",
            "employee",
            "position",
            rt + "holdsStaffPosition",
            smin=1,
            smax=1,
        ),
        rel(
            "EmploymentContract/ofEmployee",
            "ofEmployee",
            "ofEmployee",
            "Трудовой договор принадлежит сотруднику (mandatory).",
            ce + "EmploymentContract",
            ce + "Employee",
            "contract",
            "employee",
            rt + "concerns",
            smin=1,
            smax=1,
            identifying=True,
        ),
        rel(
            "RoleAssignment/ofRole",
            "ofRole",
            "assignedRole",
            "Назначение принадлежит роли (mandatory).",
            ce + "RoleAssignment",
            ce + "Role",
            "assignment",
            "role",
            rt + "assignedRole",
            smin=1,
            smax=1,
            identifying=True,
        ),
        rel(
            "RoleAssignment/ofUser",
            "ofUser",
            "assignedRole (user)",
            "Назначение принадлежит пользователю (mandatory).",
            ce + "RoleAssignment",
            ce + "User",
            "assignment",
            "user",
            rt + "assignedRole",
            smin=1,
            smax=1,
            identifying=True,
        ),
    ]

    existing_rel_ids = {r["element_id"] for r in data["relationships"]}
    for r in new_rels:
        if r["element_id"] in existing_rel_ids:
            raise SystemExit(f"duplicate rel {r['element_id']}")

    # Insert into source text at markers (preserve wave-1 formatting)
    new_desc = (
        "  Единая корпоративная концептуальная модель MOEX "
        "(Party + trading/TKS + commercial/HR slices).\n"
        "  TradingParticipation / Counterparty / Employee — reified roles, не подклассы.\n"
        "  ER-черновик концептуализирован без PK/FK-атрибутов (ADR-029). Physical layer\n"
        "  запрещён. ExternalTermSelection выравнивается сюда, не на таблицы решений.\n"
        "  Tier / genesis / relation terms — ADR-026. ABS/IT deferred."
    )
    old_desc_start = text.index("description: >\n")
    old_desc_end = text.index("\nlifecycle_status:", old_desc_start)
    text = text[:old_desc_start] + "description: >\n" + new_desc + text[old_desc_end:]

    marker_concepts = "\nrelation_terms:\n"
    if marker_concepts not in text:
        raise SystemExit("relation_terms marker missing")
    text = text.replace(
        marker_concepts,
        "\n  # --- commercial + HR slice (ADR-029 wave 2) ---\n\n"
        + dump_block(new_concepts)
        + marker_concepts,
        1,
    )

    marker_terms = "\nrelationships:\n"
    if marker_terms not in text:
        raise SystemExit("relationships marker missing")
    text = text.replace(
        marker_terms,
        "\n  # --- commercial + HR relation terms (wave 2) ---\n\n"
        + dump_block(new_terms)
        + marker_terms,
        1,
    )

    marker_maps = "\nmappings:\n"
    if marker_maps not in text:
        raise SystemExit("mappings marker missing")
    text = text.replace(
        marker_maps,
        "\n  # --- commercial + HR relationships (wave 2) ---\n\n"
        + dump_block(new_rels)
        + marker_maps,
        1,
    )

    PATH.write_text(text, encoding="utf-8")

    # Sync relation-terms.yaml from full body
    body = yaml.safe_load(PATH.read_text(encoding="utf-8"))
    rt_path = PATH.parent / "relation-terms.yaml"
    header = (
        "# Governed relation-term dictionary (ADR-026).\n"
        "# SoT is also inlined under ModelPackage.relation_terms in\n"
        "# enterprise-conceptual-model.yaml for package validation.\n"
    )
    rt_path.write_text(
        header
        + yaml.dump(
            {"relation_terms": body["relation_terms"]},
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
            width=100,
        ),
        encoding="utf-8",
    )

    print(
        "ok concepts",
        len(body["conceptual_entities"]),
        "terms",
        len(body["relation_terms"]),
        "rels",
        len(body["relationships"]),
    )


if __name__ == "__main__":
    main()
