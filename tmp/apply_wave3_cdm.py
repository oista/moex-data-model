"""Append wave-3 remainder concepts/terms/relationships to enterprise CDM."""

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
    base = {"lifecycle_status": "active", "genesis_kind": "native"}
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
    raw = yaml.dump(
        items,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=100,
    )
    return "\n".join(("  " + line) if line.strip() else "" for line in raw.splitlines()) + "\n"


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    data = yaml.safe_load(text)

    new_concepts = [
        concept(
            element_id="dams:concept/AccountingSystem",
            name="AccountingSystem",
            title="АБС",
            description="Автоматизированная банковская / учётная система (АБС).",
            entity_type="reference",
            data_class="reference_data",
            business_importance="high",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/LedgerAccount",
            name="LedgerAccount",
            title="Счёт АБС",
            description="Счёт в АБС / главной книге.",
            entity_type="core",
            data_class="master_data",
            business_importance="high",
            entity_tier="dependent",
            dependency_kind="characteristic",
            depends_on_refs=["dams:concept/AccountingSystem"],
        ),
        concept(
            element_id="dams:concept/SubledgerAccount",
            name="SubledgerAccount",
            title="Лицевой счёт",
            description="Лицевой счёт (субсчёт) при счёте АБС.",
            entity_type="core",
            data_class="master_data",
            business_importance="high",
            entity_tier="dependent",
            dependency_kind="characteristic",
            depends_on_refs=["dams:concept/LedgerAccount"],
        ),
        concept(
            element_id="dams:concept/Currency",
            name="Currency",
            title="Валюта",
            description="Валюта номинала / расчётов (из FK на счетах пользователя).",
            entity_type="reference",
            data_class="reference_data",
            business_importance="high",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/UserLedgerLink",
            name="UserLedgerLink",
            title="Счёт пользователя",
            description="Связь пользователя приложений со счётом АБС (associative).",
            entity_type="core",
            data_class="master_data",
            business_importance="medium",
            entity_tier="dependent",
            dependency_kind="associative",
            depends_on_refs=["dams:concept/User", "dams:concept/LedgerAccount"],
        ),
        concept(
            element_id="dams:concept/JournalEntry",
            name="JournalEntry",
            title="Проводка",
            description="Бухгалтерская / учётная проводка по счёту АБС.",
            entity_type="core",
            data_class="transactional_data",
            business_importance="high",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/InformationSystem",
            name="InformationSystem",
            title="Инфо-система",
            description="Информационная система / приложение корпоративного контура.",
            entity_type="reference",
            data_class="reference_data",
            business_importance="high",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/Act",
            name="Act",
            title="Акт",
            description=(
                "Акт (документальный факт). В ER-черновике — тонкая заглушка без "
                "атрибутов; концепт без PK/FK-колонок (ADR-029)."
            ),
            entity_type="core",
            data_class="transactional_data",
            business_importance="low",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/SalesFunnel",
            name="SalesFunnel",
            title="Воронка продаж",
            description=(
                "Воронка продаж / CRM-воронка. Атрибуты черновика (дата рождения) "
                "игнорируются — только концепт."
            ),
            entity_type="core",
            data_class="reference_data",
            business_importance="medium",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/Deposit",
            name="Deposit",
            title="Депозит",
            description="Депозит; в черновике связан со счётом.",
            entity_type="core",
            data_class="master_data",
            business_importance="medium",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/Curve",
            name="Curve",
            title="Кривая",
            description="Кривая (доходности / ставок и т.п.).",
            entity_type="reference",
            data_class="reference_data",
            business_importance="medium",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/Portfolio",
            name="Portfolio",
            title="Портфель",
            description="Портфель активов, связанный со счётом АБС.",
            entity_type="core",
            data_class="master_data",
            business_importance="high",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/ClearingPositionDetail",
            name="ClearingPositionDetail",
            title="ЧПД",
            description=(
                "ЧПД (черновик: счётоподобная сущность). Тонкий концепт; "
                "опциональная связь со счётом АБС."
            ),
            entity_type="core",
            data_class="transactional_data",
            business_importance="low",
            entity_tier="primary",
        ),
        concept(
            element_id="dams:concept/LoginEvent",
            name="LoginEvent",
            title="Событие логина",
            description="Событие логина ТКС; зависит от TradingLogin.",
            entity_type="core",
            data_class="transactional_data",
            business_importance="medium",
            entity_tier="dependent",
            dependency_kind="characteristic",
            depends_on_refs=["dams:concept/TradingLogin"],
        ),
        concept(
            element_id="dams:concept/TradingTerminal",
            name="TradingTerminal",
            title="Торговый терминал",
            description=(
                "Торговый терминал. В ER-черновике поля похожи на сделку — "
                "в КМД только концепт и опциональные связи."
            ),
            entity_type="core",
            data_class="master_data",
            business_importance="medium",
            entity_tier="primary",
        ),
    ]

    existing_names = {c["name"] for c in data["conceptual_entities"]}
    for c in new_concepts:
        if c["name"] in existing_names:
            raise SystemExit(f"duplicate concept {c['name']}")

    new_terms = [
        term(
            "hostedOn",
            "размещён в / хостит",
            "Пользователь размещён / работает в инфо-системе.",
            "размещён в",
            "hosted on",
            "хостит",
            "hosts",
        ),
        term(
            "ofLedger",
            "относится к счёту / имеет субсчёт",
            "Лицевой счёт или связь относится к счёту АБС.",
            "относится к счёту",
            "of ledger account",
            "имеет субсчёт/связь",
            "has subledger or link",
            "composition",
        ),
        term(
            "ofAccountingSystem",
            "в АБС / содержит счета",
            "Счёт принадлежит АБС.",
            "в АБС",
            "of accounting system",
            "содержит счета",
            "has ledger accounts",
            "composition",
        ),
        term(
            "ofSubledger",
            "по лицевому счёту / имеет проводки",
            "Проводка может относиться к лицевому счёту.",
            "по лицевому счёту",
            "of subledger",
            "имеет проводки",
            "has journal entries",
        ),
        term(
            "postsTo",
            "проводится на / принимает проводки",
            "Проводка проводится на счёт АБС.",
            "проводится на",
            "posts to",
            "принимает проводки",
            "receives postings",
        ),
        term(
            "denominatedIn",
            "номинирован в / номинирует",
            "Связь счёта пользователя номинирована в валюте.",
            "номинирован в",
            "denominated in",
            "номинирует",
            "denominates",
        ),
        term(
            "holdsAsset",
            "держит актив / входит в портфель",
            "Портфель держит актив.",
            "держит актив",
            "holds asset",
            "входит в портфель",
            "held in portfolio",
        ),
        term(
            "ofPortfolio",
            "относится к портфелю / включает",
            "Связь портфеля со счётом.",
            "относится к портфелю",
            "of portfolio",
            "включает",
            "includes",
        ),
        term(
            "ofTerminal",
            "на терминале / обслуживает",
            "Связь торгового терминала с участием / инструментом / площадкой.",
            "на терминале",
            "of terminal",
            "обслуживает",
            "serves",
        ),
        term(
            "occurredOnLogin",
            "произошло на логине / имеет события",
            "Событие логина относится к логину ТКС.",
            "произошло на логине",
            "occurred on login",
            "имеет события",
            "has login events",
            "composition",
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
            "LedgerAccount/ofAccountingSystem",
            "ofAccountingSystem",
            "ofAccountingSystem",
            "Счёт АБС принадлежит AccountingSystem (mandatory).",
            ce + "LedgerAccount",
            ce + "AccountingSystem",
            "ledger_account",
            "accounting_system",
            rt + "ofAccountingSystem",
            smin=1,
            smax=1,
            identifying=True,
            kind="composition",
        ),
        rel(
            "SubledgerAccount/ofLedger",
            "ofLedger",
            "ofLedger",
            "Лицевой счёт принадлежит счёту АБС (mandatory).",
            ce + "SubledgerAccount",
            ce + "LedgerAccount",
            "subledger",
            "ledger_account",
            rt + "ofLedger",
            smin=1,
            smax=1,
            identifying=True,
            kind="composition",
        ),
        rel(
            "UserLedgerLink/ofUser",
            "ofUser",
            "ofUser",
            "Связь принадлежит пользователю (mandatory).",
            ce + "UserLedgerLink",
            ce + "User",
            "link",
            "user",
            rt + "memberOf",
            smin=1,
            smax=1,
            identifying=True,
        ),
        rel(
            "UserLedgerLink/ofLedger",
            "ofLedger",
            "ofLedger",
            "Связь принадлежит счёту АБС (mandatory).",
            ce + "UserLedgerLink",
            ce + "LedgerAccount",
            "link",
            "ledger_account",
            rt + "ofLedger",
            smin=1,
            smax=1,
            identifying=True,
        ),
        rel(
            "UserLedgerLink/denominatedIn",
            "denominatedIn",
            "denominatedIn",
            "Связь может быть номинирована в валюте.",
            ce + "UserLedgerLink",
            ce + "Currency",
            "link",
            "currency",
            rt + "denominatedIn",
            smin=0,
            smax=1,
        ),
        rel(
            "JournalEntry/postsTo",
            "postsTo",
            "postsTo",
            "Проводка проводится на счёт АБС.",
            ce + "JournalEntry",
            ce + "LedgerAccount",
            "entry",
            "ledger_account",
            rt + "postsTo",
            smin=0,
            smax=1,
        ),
        rel(
            "JournalEntry/ofSubledger",
            "ofSubledger",
            "ofSubledger",
            "Проводка может относиться к лицевому счёту.",
            ce + "JournalEntry",
            ce + "SubledgerAccount",
            "entry",
            "subledger",
            rt + "ofSubledger",
            smin=0,
            smax=1,
        ),
        rel(
            "User/hostedOn",
            "hostedOn",
            "hostedOn",
            "Пользователь работает в инфо-системе.",
            ce + "User",
            ce + "InformationSystem",
            "user",
            "information_system",
            rt + "hostedOn",
            smin=0,
            smax=999,
        ),
        rel(
            "Portfolio/holdsAsset",
            "holdsAsset",
            "holdsAsset",
            "Портфель держит актив.",
            ce + "Portfolio",
            ce + "Asset",
            "portfolio",
            "asset",
            rt + "holdsAsset",
            smin=0,
            smax=999,
        ),
        rel(
            "Portfolio/ofLedger",
            "ofLedger",
            "ofLedger",
            "Портфель связан со счётом АБС.",
            ce + "Portfolio",
            ce + "LedgerAccount",
            "portfolio",
            "ledger_account",
            rt + "ofLedger",
            smin=0,
            smax=1,
        ),
        rel(
            "Deposit/ofLedger",
            "ofLedger",
            "ofLedger",
            "Депозит может относиться к счёту АБС.",
            ce + "Deposit",
            ce + "LedgerAccount",
            "deposit",
            "ledger_account",
            rt + "ofLedger",
            smin=0,
            smax=1,
        ),
        rel(
            "ClearingPositionDetail/ofLedger",
            "ofLedger",
            "ofLedger",
            "ЧПД может относиться к счёту АБС.",
            ce + "ClearingPositionDetail",
            ce + "LedgerAccount",
            "cpd",
            "ledger_account",
            rt + "ofLedger",
            smin=0,
            smax=1,
        ),
        rel(
            "LoginEvent/ofLogin",
            "ofLogin",
            "occurredOnLogin",
            "Событие принадлежит логину ТКС (mandatory).",
            ce + "LoginEvent",
            ce + "TradingLogin",
            "event",
            "login",
            rt + "occurredOnLogin",
            smin=1,
            smax=1,
            identifying=True,
            kind="composition",
        ),
        rel(
            "TradingTerminal/ofParticipation",
            "ofParticipation",
            "ofTerminal (participation)",
            "Терминал может относиться к участию в торгах.",
            ce + "TradingTerminal",
            ce + "TradingParticipation",
            "terminal",
            "participation",
            rt + "ofTerminal",
            smin=0,
            smax=1,
        ),
        rel(
            "TradingTerminal/ofInstrument",
            "ofInstrument",
            "ofTerminal (instrument)",
            "Терминал может относиться к инструменту (черновик).",
            ce + "TradingTerminal",
            ce + "Instrument",
            "terminal",
            "instrument",
            rt + "ofTerminal",
            smin=0,
            smax=1,
        ),
        rel(
            "TradingTerminal/ofVenue",
            "ofVenue",
            "ofTerminal (venue)",
            "Терминал может относиться к площадке (черновик).",
            ce + "TradingTerminal",
            ce + "TradingVenue",
            "terminal",
            "venue",
            rt + "ofTerminal",
            smin=0,
            smax=1,
        ),
    ]

    existing_rel_ids = {r["element_id"] for r in data["relationships"]}
    for r in new_rels:
        if r["element_id"] in existing_rel_ids:
            raise SystemExit(f"duplicate rel {r['element_id']}")

    new_desc = (
        "  Единая корпоративная концептуальная модель MOEX "
        "(Party + trading/TKS + commercial/HR + ABS/IT remainder).\n"
        "  Полное покрытие таблиц CModel_content04.drawio на концептуальном уровне "
        "(ADR-029).\n"
        "  Reified roles не подклассы. Без PK/FK-атрибутов. Physical layer запрещён.\n"
        "  ExternalTermSelection выравнивается сюда. Tier / genesis / relation terms — "
        "ADR-026."
    )
    old_desc_start = text.index("description: >\n")
    old_desc_end = text.index("\nlifecycle_status:", old_desc_start)
    text = text[:old_desc_start] + "description: >\n" + new_desc + text[old_desc_end:]

    marker_concepts = "\nrelation_terms:\n"
    text = text.replace(
        marker_concepts,
        "\n  # --- ABS/IT/ops remainder (ADR-029 wave 3) ---\n\n"
        + dump_block(new_concepts)
        + marker_concepts,
        1,
    )
    marker_terms = "\nrelationships:\n"
    text = text.replace(
        marker_terms,
        "\n  # --- remainder relation terms (wave 3) ---\n\n"
        + dump_block(new_terms)
        + marker_terms,
        1,
    )
    marker_maps = "\nmappings:\n"
    text = text.replace(
        marker_maps,
        "\n  # --- remainder relationships (wave 3) ---\n\n"
        + dump_block(new_rels)
        + marker_maps,
        1,
    )

    PATH.write_text(text, encoding="utf-8")

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
